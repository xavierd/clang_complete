from clang.cindex import *
import vim
import time
import re
import threading

def initClangComplete(clang_complete_flags):
  global index
  index = Index.create()
  global translationUnits
  translationUnits = dict()
  global complete_flags
  complete_flags = int(clang_complete_flags)

# Get a tuple (fileName, fileContent) for the file opened in the current
# vim buffer. The fileContent contains the unsafed buffer content.
def getCurrentFile():
  file = "\n".join(vim.eval("getline(1, '$')"))
  return (vim.current.buffer.name, file)

def getCurrentTranslationUnit(args, update = False):
  currentFile = getCurrentFile()
  fileName = vim.current.buffer.name

  if fileName in translationUnits:
    tu = translationUnits[fileName]
    if update:
      if debug:
        start = time.time()
      tu.reparse([currentFile])
      if debug:
        elapsed = (time.time() - start)
        print "LibClang - Reparsing: " + str(elapsed)
    return tu

  if debug:
    start = time.time()
  flags = TranslationUnit.PrecompiledPreamble | TranslationUnit.CXXPrecompiledPreamble | TranslationUnit.CacheCompletionResults
  tu = index.parse(fileName, args, [currentFile], flags)
  if debug:
    elapsed = (time.time() - start)
    print "LibClang - First parse: " + str(elapsed)

  if tu == None:
    print "Cannot parse this source file. The following arguments " \
        + "are used for clang: " + " ".join(args)
    return None

  translationUnits[fileName] = tu

  # Reparse to initialize the PCH cache even for auto completion
  # This should be done by index.parse(), however it is not.
  # So we need to reparse ourselves.
  if debug:
    start = time.time()
  tu.reparse([currentFile])
  if debug:
    elapsed = (time.time() - start)
    print "LibClang - First reparse (generate PCH cache): " + str(elapsed)
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

  # Use this wired kind of iterator as the python clang libraries
        # have a bug in the range iterator that stops us to use:
        #
        # | for range in diagnostic.ranges
        #
  for i in range(len(diagnostic.ranges)):
    highlightRange(diagnostic.ranges[i], hlGroup)

def highlightDiagnostics(tu):
  map (highlightDiagnostic, tu.diagnostics)

def highlightCurrentDiagnostics():
  if vim.current.buffer.name in translationUnits:
    highlightDiagnostics(translationUnits[vim.current.buffer.name])

def getCurrentQuickFixList():
  if vim.current.buffer.name in translationUnits:
    return getQuickFixList(translationUnits[vim.current.buffer.name])
  return []

def updateCurrentDiagnostics():
  global debug
  debug = int(vim.eval("g:clang_debug")) == 1
  userOptionsGlobal = splitOptions(vim.eval("g:clang_user_options"))
  userOptionsLocal = splitOptions(vim.eval("b:clang_user_options"))
  args = userOptionsGlobal + userOptionsLocal
  getCurrentTranslationUnit(args, update = True)

def getCurrentCompletionResults(line, column, args):
  tu = getCurrentTranslationUnit(args)
  currentFile = getCurrentFile()
  if debug:
    start = time.time()
  cr = tu.codeComplete(vim.current.buffer.name, line, column, [currentFile],
      complete_flags)
  if debug:
    elapsed = (time.time() - start)
    print "LibClang - Code completion time: " + str(elapsed)
  return cr

def formatResult(result):
  completion = dict()

  abbr = getAbbr(result.string)
  word = filter(lambda x: not x.isKindInformative() and not x.isKindResultType(), result.string)

  args_pos = []
  cur_pos = 0
  for chunk in word:
    chunk_len = len(chunk.spelling)
    if chunk.isKindPlaceHolder():
      args_pos += [[ cur_pos, cur_pos + chunk_len ]]
    cur_pos += chunk_len

  word = "".join(map(lambda x: x.spelling, word))

  completion['word'] = word
  completion['abbr'] = abbr
  completion['menu'] = word
  completion['info'] = word
  completion['args_pos'] = args_pos
  completion['dup'] = 0

  # Replace the number that represents a specific kind with a better
  # textual representation.
  completion['kind'] = getTypeOfCursor(result.cursorKind)

  return completion


class CompleteThread(threading.Thread):
  lock = threading.Lock()

  def __init__(self, line, column):
    threading.Thread.__init__(self)
    self.line = line
    self.column = column
    self.result = None
    userOptionsGlobal = splitOptions(vim.eval("g:clang_user_options"))
    userOptionsLocal = splitOptions(vim.eval("b:clang_user_options"))
    self.args = userOptionsGlobal + userOptionsLocal

  def run(self):
    try:
      CompleteThread.lock.acquire()
      if self.line == -1:
        # Warm up the caches. For this it is sufficient to get the current
        # translation unit. No need to retrieve completion results.
        # This short pause is necessary to allow vim to initialize itself.
        # Otherwise we would get: E293: block was not locked
        # The user does not see any delay, as we just pause a background thread.
        time.sleep(0.1)
        getCurrentTranslationUnit(self.args)
      else:
        self.result = getCurrentCompletionResults(self.line, self.column,
                                                  self.args)
    except Exception:
      pass
    CompleteThread.lock.release()

def WarmupCache():
  global debug
  debug = int(vim.eval("g:clang_debug")) == 1
  t = CompleteThread(-1, -1)
  t.start()
  return


def getCurrentCompletions(base):
  global debug
  debug = int(vim.eval("g:clang_debug")) == 1
  priority = vim.eval("g:clang_sort_algo") == 'priority'
  line = int(vim.eval("line('.')"))
  column = int(vim.eval("b:col"))

  t = CompleteThread(line, column)
  t.start()
  while t.isAlive():
    t.join(0.01)
    cancel = int(vim.eval('complete_check()'))
    if cancel != 0:
      return []
  cr = t.result
  if cr is None:
    return []

  regexp = re.compile("^" + base)
  filteredResult = filter(lambda x: regexp.match(getAbbr(x.string)), cr.results)

  getPriority = lambda x: x.string.priority
  getAbbrevation = lambda x: getAbbr(x.string).lower()
  if priority:
    key = getPriority
  else:
    key = getAbbrevation
  sortedResult = sorted(filteredResult, None, key)
  return map(formatResult, sortedResult)

def getAbbr(strings):
  tmplst = filter(lambda x: x.isKindTypedText(), strings)
  if len(tmplst) == 0:
    return ""
  else:
    return tmplst[0].spelling

def getTypeOfCursor(id):
  kind = CursorKind.from_id(id)
  repr = knownKinds.get(kind)
  if repr == None:
    return str(id)
  return repr

knownKinds = dict({
  CursorKind.UNEXPOSED_DECL : 't',
  CursorKind.STRUCT_DECL : 't',
  CursorKind.UNION_DECL : 't',
  CursorKind.CLASS_DECL : 't',
  CursorKind.ENUM_DECL : 't',
  CursorKind.FIELD_DECL : 'm',
  CursorKind.ENUM_CONSTANT_DECL : 'e',
  CursorKind.FUNCTION_DECL : 'f',
  CursorKind.VAR_DECL : 'v',
  CursorKind.PARM_DECL : 'a',
  CursorKind.TYPEDEF_DECL : 't',
  CursorKind.CXX_METHOD : 'f',
  CursorKind.NAMESPACE : 'n',
  CursorKind.CONSTRUCTOR : '+',
  CursorKind.DESTRUCTOR : '~',
  CursorKind.TEMPLATE_TYPE_PARAMETER : 'a',
  CursorKind.TEMPLATE_NON_TYPE_PARAMETER : 'a',
  CursorKind.TEMPLATE_TEMPLATE_PARAMTER : 'a',
  CursorKind.FUNCTION_TEMPLATE : 'f',
  CursorKind.CLASS_TEMPLATE : 'p',
  CursorKind.NAMESPACE_ALIAS : 'n',
  CursorKind.NOT_IMPLEMENTED : 'u'})

# vim: set ts=2 sts=2 sw=2 expandtab :
