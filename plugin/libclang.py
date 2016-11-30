from clang.cindex import *
import vim
import time
import threading
import os
import shlex

from kinds import kinds

# Check if libclang is able to find the builtin include files.
#
# libclang sometimes fails to correctly locate its builtin include files. This
# happens especially if libclang is not installed at a standard location. This
# function checks if the builtin includes are available.
def canFindBuiltinHeaders(index, args = []):
  flags = 0
  currentFile = ("test.c", '#include "stddef.h"')
  try:
    tu = index.parse("test.c", args, [currentFile], flags)
  except TranslationUnitLoadError, e:
    return 0
  return len(tu.diagnostics) == 0

# Derive path to clang builtin headers.
#
# This function tries to derive a path to clang's builtin header files. We are
# just guessing, but the guess is very educated. In fact, we should be right
# for all manual installations (the ones where the builtin header path problem
# is very common) as well as a set of very common distributions.
def getBuiltinHeaderPath(library_path):
  if os.path.isfile(library_path):
    library_path = os.path.dirname(library_path)

  knownPaths = [
          library_path + "/../lib/clang",  # default value
          library_path + "/../clang",      # gentoo
          library_path + "/clang",         # opensuse
          library_path + "/",              # Google
          "/usr/lib64/clang",              # x86_64 (openSUSE, Fedora)
          "/usr/lib/clang"
  ]

  for path in knownPaths:
    try:
      subDirs = [f for f in os.listdir(path) if os.path.isdir(path + "/" + f)]
      subDirs = sorted(subDirs) or ['.']
      path = path + "/" + subDirs[-1] + "/include"
      if canFindBuiltinHeaders(index, ["-I" + path]):
        return path
    except:
      pass

  return None

def initClangComplete(clang_complete_flags, clang_compilation_database, \
                      library_path):
  global index

  debug = int(vim.eval("g:clang_debug")) == 1

  if library_path:
    if os.path.isdir(library_path):
      Config.set_library_path(library_path)
    else:
      Config.set_library_file(library_path)

  Config.set_compatibility_check(False)

  try:
    index = Index.create()
  except Exception, e:
    if library_path:
      suggestion = "Are you sure '%s' contains libclang?" % library_path
    else:
      suggestion = "Consider setting g:clang_library_path."

    if debug:
      exception_msg = str(e)
    else:
      exception_msg = ''

    print '''Loading libclang failed, completion won't be available. %s
    %s
    ''' % (suggestion, exception_msg)
    return 0

  global builtinHeaderPath
  builtinHeaderPath = None
  if not canFindBuiltinHeaders(index):
    builtinHeaderPath = getBuiltinHeaderPath(library_path)

    if not builtinHeaderPath:
      print "WARNING: libclang can not find the builtin includes."
      print "         This will cause slow code completion."
      print "         Please report the problem."

  global translationUnits
  translationUnits = dict()
  global complete_flags
  complete_flags = int(clang_complete_flags)
  global compilation_database
  if clang_compilation_database != '':
    compilation_database = CompilationDatabase.fromDirectory(clang_compilation_database)
  else:
    compilation_database = None
  global libclangLock
  libclangLock = threading.Lock()
  return 1

# Get a tuple (fileName, fileContent) for the file opened in the current
# vim buffer. The fileContent contains the unsafed buffer content.
def getCurrentFile():
  file = "\n".join(vim.current.buffer[:] + ["\n"])
  return (vim.current.buffer.name, file)

class CodeCompleteTimer:
  def __init__(self, debug, file, line, column, params):
    self._debug = debug

    if not debug:
      return

    content = vim.current.line
    print " "
    print "libclang code completion"
    print "========================"
    print "Command: clang %s -fsyntax-only " % " ".join(params['args']),
    print "-Xclang -code-completion-at=%s:%d:%d %s" % (file, line, column, file)
    print "cwd: %s" % params['cwd']
    print "File: %s" % file
    print "Line: %d, Column: %d" % (line, column)
    print " "
    print "%s" % content

    print " "

    current = time.time()
    self._start = current
    self._last = current
    self._events = []

  def registerEvent(self, event):
    if not self._debug:
      return

    current = time.time()
    since_last = current - self._last
    self._last = current
    self._events.append((event, since_last))

  def finish(self):
    if not self._debug:
      return

    overall = self._last - self._start

    for event in self._events:
      name, since_last = event
      percent = 1 / overall * since_last * 100
      print "libclang code completion - %25s: %.3fs (%5.1f%%)" % \
        (name, since_last, percent)

    print " "
    print "Overall: %.3f s" % overall
    print "========================"
    print " "

def getCurrentTranslationUnit(args, currentFile, fileName, timer,
                              update = False):
  tu = translationUnits.get(fileName)
  if tu != None:
    if update:
      tu.reparse([currentFile])
      timer.registerEvent("Reparsing")
    return tu

  flags = TranslationUnit.PARSE_PRECOMPILED_PREAMBLE | \
          TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD
  try:
    tu = index.parse(fileName, args, [currentFile], flags)
    timer.registerEvent("First parse")
  except TranslationUnitLoadError, e:
    return None

  translationUnits[fileName] = tu

  # Reparse to initialize the PCH cache even for auto completion
  # This should be done by index.parse(), however it is not.
  # So we need to reparse ourselves.
  tu.reparse([currentFile])
  timer.registerEvent("Generate PCH cache")
  return tu

def splitOptions(options):
  # Use python's shell command lexer to correctly split the list of options in
  # accordance with the POSIX standard
  return shlex.split(options)

def getQuickFix(diagnostic):
  # Some diagnostics have no file, e.g. "too many errors emitted, stopping now"
  if diagnostic.location.file:
    filename = diagnostic.location.file.name
  else:
    filename = ""

  if diagnostic.severity == diagnostic.Ignored:
    type = 'I'
  elif diagnostic.severity == diagnostic.Note:
    type = 'I'
  elif diagnostic.severity == diagnostic.Warning:
    if "argument unused during compilation" in diagnostic.spelling:
      return None
    type = 'W'
  elif diagnostic.severity == diagnostic.Error:
    type = 'E'
  elif diagnostic.severity == diagnostic.Fatal:
    type = 'E'
  else:
    return None

  return dict({ 'bufnr' : int(vim.eval("bufnr('" + filename + "', 1)")),
    'lnum' : diagnostic.location.line,
    'col' : diagnostic.location.column,
    'text' : diagnostic.spelling,
    'type' : type})

def getQuickFixList(tu):
  return filter (None, map (getQuickFix, tu.diagnostics))

def highlightRange(range, hlGroup):
  pattern = '/\%' + str(range.start.line) + 'l' + '\%' \
      + str(range.start.column) + 'c' + '.*' \
      + '\%' + str(range.end.column) + 'c/'
  command = "exe 'syntax match' . ' " + hlGroup + ' ' + pattern + "'"
  vim.command(command)

def highlightDiagnostic(diagnostic):
  if diagnostic.severity == diagnostic.Warning:
    hlGroup = 'SpellLocal'
  elif diagnostic.severity == diagnostic.Error:
    hlGroup = 'SpellBad'
  else:
    return

  pattern = '/\%' + str(diagnostic.location.line) + 'l\%' \
      + str(diagnostic.location.column) + 'c./'
  command = "exe 'syntax match' . ' " + hlGroup + ' ' + pattern + "'"
  vim.command(command)

  for range in diagnostic.ranges:
    highlightRange(range, hlGroup)

def highlightDiagnostics(tu):
  map (highlightDiagnostic, tu.diagnostics)

def highlightCurrentDiagnostics():
  if vim.current.buffer.name in translationUnits:
    highlightDiagnostics(translationUnits[vim.current.buffer.name])

def getCurrentQuickFixList():
  if vim.current.buffer.name in translationUnits:
    return getQuickFixList(translationUnits[vim.current.buffer.name])
  return []

# Get the compilation parameters from the compilation database for source
# 'fileName'. The parameters are returned as map with the following keys :
#
#   'args' : compiler arguments.
#            Compilation database returns the complete command line. We need
#            to filter at least the compiler invocation, the '-o' + output
#            file, the input file and the '-c' arguments. We alter -I paths
#            to make them absolute, so that we can launch clang from wherever
#            we are.
#            Note : we behave differently from cc_args.py which only keeps
#            '-I', '-D' and '-include' options.
#
#    'cwd' : the compiler working directory
#
# The last found args and cwd are remembered and reused whenever a file is
# not found in the compilation database. For example, this is the case for
# all headers. This achieve very good results in practice.
def getCompilationDBParams(fileName):
  if compilation_database:
    cmds = compilation_database.getCompileCommands(fileName)
    if cmds != None:
      cwd = cmds[0].directory
      args = []
      skip_next = 1 # Skip compiler invocation
      for arg in cmds[0].arguments:
        if skip_next:
          skip_next = 0;
          continue
        if arg == '-c':
          continue
        if arg == fileName or \
           os.path.realpath(os.path.join(cwd, arg)) == fileName:
          continue
        if arg == '-o':
          skip_next = 1;
          continue
        if arg.startswith('-I'):
          includePath = arg[2:]
          if not os.path.isabs(includePath):
            includePath = os.path.normpath(os.path.join(cwd, includePath))
          args.append('-I'+includePath)
          continue
        args.append(arg)
      getCompilationDBParams.last_query = { 'args': args, 'cwd': cwd }

  # Do not directly return last_query, but make sure we return a deep copy.
  # Otherwise users of that result may accidently change it and store invalid
  # values in our cache.
  query = getCompilationDBParams.last_query
  return { 'args': list(query['args']), 'cwd': query['cwd']}

getCompilationDBParams.last_query = { 'args': [], 'cwd': None }

def getCompileParams(fileName):
  global builtinHeaderPath
  params = getCompilationDBParams(fileName)
  args = params['args']
  args += splitOptions(vim.eval("g:clang_user_options"))
  args += splitOptions(vim.eval("b:clang_user_options"))
  args += splitOptions(vim.eval("b:clang_parameters"))

  if builtinHeaderPath:
    args.append("-I" + builtinHeaderPath)

  return { 'args' : args,
           'cwd' : params['cwd'] }

def updateCurrentDiagnostics():
  global debug
  debug = int(vim.eval("g:clang_debug")) == 1
  params = getCompileParams(vim.current.buffer.name)
  timer = CodeCompleteTimer(debug, vim.current.buffer.name, -1, -1, params)

  with libclangLock:
    getCurrentTranslationUnit(params['args'], getCurrentFile(),
                              vim.current.buffer.name, timer, update = True)
  timer.finish()

def getCurrentCompletionResults(line, column, args, currentFile, fileName,
                                timer):

  tu = getCurrentTranslationUnit(args, currentFile, fileName, timer)
  timer.registerEvent("Get TU")

  if tu == None:
    return None

  cr = tu.codeComplete(fileName, line, column, [currentFile],
      complete_flags)
  timer.registerEvent("Code Complete")
  return cr

def formatResult(result):
  completion = dict()
  returnValue = None
  abbr = ""
  word = ""
  info = ""
  place_markers_for_optional_args = int(vim.eval("g:clang_complete_optional_args_in_snippets")) == 1

  def roll_out_optional(chunks):
    result = []
    word = ""
    for chunk in chunks:
      if chunk.isKindInformative() or chunk.isKindResultType() or chunk.isKindTypedText():
        continue

      word += chunk.spelling
      if chunk.isKindOptional():
        result += roll_out_optional(chunk.string)

    return [word] + result

  for chunk in result.string:

    if chunk.isKindInformative():
      continue

    if chunk.isKindResultType():
      returnValue = chunk
      continue

    chunk_spelling = chunk.spelling

    if chunk.isKindTypedText():
      abbr = chunk_spelling

    if chunk.isKindOptional():
      for optional_arg in roll_out_optional(chunk.string):
        if place_markers_for_optional_args:
          word += snippetsFormatPlaceHolder(optional_arg)
        info += optional_arg + "=?"

    if chunk.isKindPlaceHolder():
      word += snippetsFormatPlaceHolder(chunk_spelling)
    else:
      word += chunk_spelling

    info += chunk_spelling

  menu = info

  if returnValue:
    menu = returnValue.spelling + " " + menu

  completion['word'] = snippetsAddSnippet(info, word, abbr)
  completion['abbr'] = abbr
  completion['menu'] = menu
  completion['info'] = info
  completion['dup'] = 1

  # Replace the number that represents a specific kind with a better
  # textual representation.
  completion['kind'] = kinds[result.cursorKind]

  return completion


class CompleteThread(threading.Thread):
  def __init__(self, line, column, currentFile, fileName, params, timer):
    threading.Thread.__init__(self)
    # Complete threads are daemon threads. Python and consequently vim does not
    # wait for daemon threads to finish execution when existing itself. As
    # clang may compile for a while, we do not have to wait for the compilation
    # to finish before vim can quit. Before adding this flags, vim was hanging
    # for a couple of seconds before it exited.
    self.daemon = True
    self.line = line
    self.column = column
    self.currentFile = currentFile
    self.fileName = fileName
    self.result = None
    self.args = params['args']
    self.cwd = params['cwd']
    self.timer = timer

  def run(self):
    with libclangLock:
      if self.line == -1:
        # Warm up the caches. For this it is sufficient to get the
        # current translation unit. No need to retrieve completion
        # results.  This short pause is necessary to allow vim to
        # initialize itself.  Otherwise we would get: E293: block was
        # not locked The user does not see any delay, as we just pause
        # a background thread.
        time.sleep(0.1)
        getCurrentTranslationUnit(self.args, self.currentFile, self.fileName,
                                  self.timer)
      else:
        self.result = getCurrentCompletionResults(self.line, self.column,
                                                  self.args, self.currentFile,
                                                  self.fileName, self.timer)

def WarmupCache():
  params = getCompileParams(vim.current.buffer.name)
  timer = CodeCompleteTimer(0, "", -1, -1, params)
  t = CompleteThread(-1, -1, getCurrentFile(), vim.current.buffer.name,
                     params, timer)
  t.start()

def getCurrentCompletions(base):
  global debug
  debug = int(vim.eval("g:clang_debug")) == 1
  sorting = vim.eval("g:clang_sort_algo")
  line, _ = vim.current.window.cursor
  column = int(vim.eval("b:col"))
  params = getCompileParams(vim.current.buffer.name)

  timer = CodeCompleteTimer(debug, vim.current.buffer.name, line, column,
                            params)

  t = CompleteThread(line, column, getCurrentFile(), vim.current.buffer.name,
                     params, timer)
  t.start()
  while t.isAlive():
    t.join(0.01)
    cancel = int(vim.eval('complete_check()'))
    if cancel != 0:
      return (str([]), timer)

  cr = t.result
  if cr is None:
    print "Cannot parse this source file. The following arguments " \
        + "are used for clang: " + " ".join(params['args'])
    return (str([]), timer)

  results = cr.results

  timer.registerEvent("Count # Results (%s)" % str(len(results)))

  if base != "":
    results = filter(lambda x: getAbbr(x.string).startswith(base), results)

  timer.registerEvent("Filter")

  if sorting == 'priority':
    getPriority = lambda x: x.string.priority
    results = sorted(results, None, getPriority)
  if sorting == 'alpha':
    getAbbrevation = lambda x: getAbbr(x.string).lower()
    results = sorted(results, None, getAbbrevation)

  timer.registerEvent("Sort")

  result = map(formatResult, results)

  timer.registerEvent("Format")
  return (str(result), timer)

def getAbbr(strings):
  for chunks in strings:
    if chunks.isKindTypedText():
      return chunks.spelling
  return ""

def jumpToLocation(filename, line, column, preview):
  filenameEscaped = filename.replace(" ", "\\ ")
  if preview:
    command = "pedit +%d %s" % (line, filenameEscaped)
  elif filename != vim.current.buffer.name:
    command = "edit %s" % filenameEscaped
  else:
    command = "normal m'"
  try:
    vim.command(command)
  except:
    # For some unknown reason, whenever an exception occurs in
    # vim.command, vim goes crazy and output tons of useless python
    # errors, catch those.
    return
  if not preview:
    vim.current.window.cursor = (line, column - 1)

def gotoDeclaration(preview=True):
  global debug
  debug = int(vim.eval("g:clang_debug")) == 1
  params = getCompileParams(vim.current.buffer.name)
  line, col = vim.current.window.cursor
  timer = CodeCompleteTimer(debug, vim.current.buffer.name, line, col, params)

  with libclangLock:
    tu = getCurrentTranslationUnit(params['args'], getCurrentFile(),
                                   vim.current.buffer.name, timer,
                                   update = True)
    if tu is None:
      print "Couldn't get the TranslationUnit"
      return

    f = File.from_name(tu, vim.current.buffer.name)
    loc = SourceLocation.from_position(tu, f, line, col + 1)
    cursor = Cursor.from_location(tu, loc)
    defs = [cursor.get_definition(), cursor.referenced]

    for d in defs:
      if d is not None and loc != d.location:
        loc = d.location
        if loc.file is not None:
          jumpToLocation(loc.file.name, loc.line, loc.column, preview)
        break

  timer.finish()

# vim: set ts=2 sts=2 sw=2 expandtab :
