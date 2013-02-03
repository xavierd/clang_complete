from clang.cindex import *
import vim
import time
import threading
import os

# Check if libclang is able to find the builtin include files.
#
# libclang sometimes fails to correctly locate its builtin include files. This
# happens especially if libclang is not installed at a standard location. This
# function checks if the builtin includes are available.
def canFindBuiltinHeaders(index, args = []):
  flags = 0
  currentFile = ("test.c", '#include "stddef.h"')
  tu = index.parse("test.c", args, [currentFile], flags)
  return len(tu.diagnostics) == 0

# Derive path to clang builtin headers.
#
# This function tries to derive a path to clang's builtin header files. We are
# just guessing, but the guess is very educated. In fact, we should be right
# for all manual installations (the ones where the builtin header path problem
# is very common).
def getBuiltinHeaderPath(library_path):
  path = library_path + "/../lib/clang"
  try:
    files = os.listdir(path)
  except:
    return None

  files = sorted(files)
  path = path + "/" + files[-1] + "/include/"
  arg = "-I" + path
  if canFindBuiltinHeaders(index, [arg]):
    return path
  return None

def initClangComplete(clang_complete_flags, clang_compilation_database, \
                      library_path, user_requested):
  global index

  debug = int(vim.eval("g:clang_debug")) == 1
  printWarnings = (user_requested != "0") or debug

  if library_path != "":
    Config.set_library_path(library_path)

  Config.set_compatibility_check(False)

  try:
    index = Index.create()
  except Exception, e:
    if printWarnings:
      print "Loading libclang failed, falling back to clang executable. ",
      if library_path == "":
        print "Consider setting g:clang_library_path"
      else:
        print "Are you sure '%s' contains libclang?" % library_path
    return 0

  global builtinHeaderPath
  builtinHeaderPath = None
  if not canFindBuiltinHeaders(index):
    builtinHeaderPath = getBuiltinHeaderPath(library_path)

    if not builtinHeaderPath and printWarnings:
      print "WARNING: libclang can not find the builtin includes."
      print "         This will cause slow code completion."
      print "         Please report the problem."
      print "         To work around this issue you can add the path of the"
      print "         clang builtin includes to g:clang_user_options."

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
  file = "\n".join(vim.current.buffer[:])
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

  flags = TranslationUnit.PARSE_PRECOMPILED_PREAMBLE
  tu = index.parse(fileName, args, [currentFile], flags)
  timer.registerEvent("First parse")

  if tu == None:
    return None

  translationUnits[fileName] = tu

  # Reparse to initialize the PCH cache even for auto completion
  # This should be done by index.parse(), however it is not.
  # So we need to reparse ourselves.
  tu.reparse([currentFile])
  timer.registerEvent("Generate PCH cache")
  return tu

def splitOptions(options):
  optsList = []
  opt = ""
  quoted = False

  for char in options:
    if char == ' ' and not quoted:
      if opt != "":
        optsList += [opt]
        opt = ""
      continue
    elif char == '"':
      quoted = not quoted
    opt += char

  if opt != "":
    optsList += [opt]
  return optsList

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
#            file, the input file and the '-c' arguments. Note : we behave
#            differently from cc_args.py which only keeps '-I', '-D' and
#            '-include' options.
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
        if arg == fileName or os.path.realpath(arg) == fileName:
          continue
        if arg == '-o':
          skip_next = 1;
          continue
        args.append(arg)
      getCompilationDBParams.last_query = { 'args': args, 'cwd': cwd }
  return getCompilationDBParams.last_query

getCompilationDBParams.last_query = { 'args': [], 'cwd': None }

# A context manager to handle directory changes safely
from contextlib import contextmanager
@contextmanager
def workingDir(dir):
  savedPath = None
  if dir != None:
    savedPath = os.getcwd()
    os.chdir(dir)
  try:
    yield
  finally:
    if savedPath != None:
      os.chdir(savedPath)

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

  with workingDir(params['cwd']):
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
  args_pos = []
  cur_pos = 0
  word = ""

  for chunk in result.string:

    if chunk.isKindInformative():
      continue

    if chunk.isKindResultType():
      returnValue = chunk
      continue

    chunk_spelling = chunk.spelling

    if chunk.isKindTypedText():
      abbr = chunk_spelling

    chunk_len = len(chunk_spelling)
    if chunk.isKindPlaceHolder():
      args_pos += [[ cur_pos, cur_pos + chunk_len ]]
    cur_pos += chunk_len
    word += chunk_spelling

  menu = word

  if returnValue:
    menu = returnValue.spelling + " " + menu

  completion['word'] = word
  completion['abbr'] = abbr
  completion['menu'] = menu
  completion['info'] = word
  completion['args_pos'] = args_pos
  completion['dup'] = 1

  # Replace the number that represents a specific kind with a better
  # textual representation.
  completion['kind'] = kinds[result.cursorKind]

  return completion


class CompleteThread(threading.Thread):
  def __init__(self, line, column, currentFile, fileName, params, timer):
    threading.Thread.__init__(self)
    self.line = line
    self.column = column
    self.currentFile = currentFile
    self.fileName = fileName
    self.result = None
    self.args = params['args']
    self.cwd = params['cwd']
    self.timer = timer

  def run(self):
    with workingDir(self.cwd):
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

kinds = dict({                                                                 \
# Declarations                                                                 \
 1 : 't',  # CXCursor_UnexposedDecl (A declaration whose specific kind is not  \
           # exposed via this interface)                                       \
 2 : 't',  # CXCursor_StructDecl (A C or C++ struct)                           \
 3 : 't',  # CXCursor_UnionDecl (A C or C++ union)                             \
 4 : 't',  # CXCursor_ClassDecl (A C++ class)                                  \
 5 : 't',  # CXCursor_EnumDecl (An enumeration)                                \
 6 : 'm',  # CXCursor_FieldDecl (A field (in C) or non-static data member      \
           # (in C++) in a struct, union, or C++ class)                        \
 7 : 'e',  # CXCursor_EnumConstantDecl (An enumerator constant)                \
 8 : 'f',  # CXCursor_FunctionDecl (A function)                                \
 9 : 'v',  # CXCursor_VarDecl (A variable)                                     \
10 : 'a',  # CXCursor_ParmDecl (A function or method parameter)                \
11 : '11', # CXCursor_ObjCInterfaceDecl (An Objective-C @interface)            \
12 : '12', # CXCursor_ObjCCategoryDecl (An Objective-C @interface for a        \
           # category)                                                         \
13 : '13', # CXCursor_ObjCProtocolDecl (An Objective-C @protocol declaration)  \
14 : '14', # CXCursor_ObjCPropertyDecl (An Objective-C @property declaration)  \
15 : '15', # CXCursor_ObjCIvarDecl (An Objective-C instance variable)          \
16 : '16', # CXCursor_ObjCInstanceMethodDecl (An Objective-C instance method)  \
17 : '17', # CXCursor_ObjCClassMethodDecl (An Objective-C class method)        \
18 : '18', # CXCursor_ObjCImplementationDec (An Objective-C @implementation)   \
19 : '19', # CXCursor_ObjCCategoryImplDecll (An Objective-C @implementation    \
           # for a category)                                                   \
20 : 't',  # CXCursor_TypedefDecl (A typedef)                                  \
21 : 'f',  # CXCursor_CXXMethod (A C++ class method)                           \
22 : 'n',  # CXCursor_Namespace (A C++ namespace)                              \
23 : '23', # CXCursor_LinkageSpec (A linkage specification, e.g. 'extern "C"') \
24 : '+',  # CXCursor_Constructor (A C++ constructor)                          \
25 : '~',  # CXCursor_Destructor (A C++ destructor)                            \
26 : '26', # CXCursor_ConversionFunction (A C++ conversion function)           \
27 : 'a',  # CXCursor_TemplateTypeParameter (A C++ template type parameter)    \
28 : 'a',  # CXCursor_NonTypeTemplateParameter (A C++ non-type template        \
           # parameter)                                                        \
29 : 'a',  # CXCursor_TemplateTemplateParameter (A C++ template template       \
           # parameter)                                                        \
30 : 'f',  # CXCursor_FunctionTemplate (A C++ function template)               \
31 : 'p',  # CXCursor_ClassTemplate (A C++ class template)                     \
32 : '32', # CXCursor_ClassTemplatePartialSpecialization (A C++ class template \
           # partial specialization)                                           \
33 : 'n',  # CXCursor_NamespaceAlias (A C++ namespace alias declaration)       \
34 : '34', # CXCursor_UsingDirective (A C++ using directive)                   \
35 : '35', # CXCursor_UsingDeclaration (A using declaration)                   \
                                                                               \
# References                                                                   \
40 : '40', # CXCursor_ObjCSuperClassRef                                        \
41 : '41', # CXCursor_ObjCProtocolRef                                          \
42 : '42', # CXCursor_ObjCClassRef                                             \
43 : '43', # CXCursor_TypeRef                                                  \
44 : '44', # CXCursor_CXXBaseSpecifier                                         \
45 : '45', # CXCursor_TemplateRef (A reference to a class template, function   \
           # template, template template parameter, or class template partial  \
           # specialization)                                                   \
46 : '46', # CXCursor_NamespaceRef (A reference to a namespace or namespace    \
           # alias)                                                            \
47 : '47', # CXCursor_MemberRef (A reference to a member of a struct, union,   \
           # or class that occurs in some non-expression context, e.g., a      \
           # designated initializer)                                           \
48 : '48', # CXCursor_LabelRef (A reference to a labeled statement)            \
49 : '49', # CXCursor_OverloadedDeclRef (A reference to a set of overloaded    \
           # functions or function templates that has not yet been resolved to \
           # a specific function or function template)                         \
                                                                               \
# Error conditions                                                             \
#70 : '70', # CXCursor_FirstInvalid                                            \
70 : '70',  # CXCursor_InvalidFile                                             \
71 : '71',  # CXCursor_NoDeclFound                                             \
72 : 'u',   # CXCursor_NotImplemented                                          \
73 : '73',  # CXCursor_InvalidCode                                             \
                                                                               \
# Expressions                                                                  \
100 : '100',  # CXCursor_UnexposedExpr (An expression whose specific kind is   \
              # not exposed via this interface)                                \
101 : '101',  # CXCursor_DeclRefExpr (An expression that refers to some value  \
              # declaration, such as a function, varible, or enumerator)       \
102 : '102',  # CXCursor_MemberRefExpr (An expression that refers to a member  \
              # of a struct, union, class, Objective-C class, etc)             \
103 : '103',  # CXCursor_CallExpr (An expression that calls a function)        \
104 : '104',  # CXCursor_ObjCMessageExpr (An expression that sends a message   \
              # to an Objective-C object or class)                             \
105 : '105',  # CXCursor_BlockExpr (An expression that represents a block      \
              # literal)                                                       \
                                                                               \
# Statements                                                                   \
200 : '200',  # CXCursor_UnexposedStmt (A statement whose specific kind is not \
              # exposed via this interface)                                    \
201 : '201',  # CXCursor_LabelStmt (A labelled statement in a function)        \
                                                                               \
# Translation unit                                                             \
300 : '300',  # CXCursor_TranslationUnit (Cursor that represents the           \
              # translation unit itself)                                       \
                                                                               \
# Attributes                                                                   \
400 : '400',  # CXCursor_UnexposedAttr (An attribute whose specific kind is    \
              # not exposed via this interface)                                \
401 : '401',  # CXCursor_IBActionAttr                                          \
402 : '402',  # CXCursor_IBOutletAttr                                          \
403 : '403',  # CXCursor_IBOutletCollectionAttr                                \
                                                                               \
# Preprocessing                                                                \
500 : '500', # CXCursor_PreprocessingDirective                                 \
501 : 'd',   # CXCursor_MacroDefinition                                        \
502 : '502', # CXCursor_MacroInstantiation                                     \
503 : '503'  # CXCursor_InclusionDirective                                     \
})

# vim: set ts=2 sts=2 sw=2 expandtab :
