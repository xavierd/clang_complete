from clang.cindex import *
import vim
import time
import re

def initClangComplete():
  global index
  index = Index.create()
  global translationUnits
  translationUnits = dict()

# Get a tuple (fileName, fileContent) for the file opened in the current
# vim buffer. The fileContent contains the unsafed buffer content.
def getCurrentFile():
  file = "\n".join(vim.eval("getline(1, '$')"))
  return (vim.current.buffer.name, file)

def getCurrentTranslationUnit(update = False):
  userOptionsGlobal = vim.eval("g:clang_user_options").split(" ")
  userOptionsLocal = vim.eval("b:clang_user_options").split(" ")
  args = userOptionsGlobal + userOptionsLocal

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
  tu = index.parse(fileName, args, [currentFile], 0x14)
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

def getQuickFix(diagnostic):
  filename = diagnostic.location.file.name
  if diagnostic.severity == diagnostic.Warning:
    type = 'W'
  elif diagnostic.severity == diagnostic.Error:
    type = 'E'
  else:
    return None

  # TODO: Get the correct buffer number.
  return dict({ 'bufnr' : 1, #vim.eval("bufnr(" + filename + ", 1)"),
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
  getCurrentTranslationUnit(update = True)

def getCurrentCompletionResults(line, column):
  tu = getCurrentTranslationUnit()
  currentFile = getCurrentFile()
  if debug:
    start = time.time()
  cr = tu.codeComplete(vim.current.buffer.name, line, column, [currentFile])
  if debug:
    elapsed = (time.time() - start)
    print "LibClang - Code completion time: " + str(elapsed)
  return cr

def completeCurrentAt(line, column):
  print "\n".join(map(str, getCurrentCompletionResults().results))

def formatChunkForWord(chunk):
  if chunk.isKindPlaceHolder():
    return "<#" + chunk.spelling + "#>"
  else:
    return chunk.spelling

def formatResult(result):
  completion = dict()

  abbr = filter(lambda x: x.isKindTypedText(), result.string)[0].spelling
  info = filter(lambda x: not x.isKindInformative(), result.string)
  word = filter(lambda x: not x.isKindResultType(), info)
  returnValue = filter(lambda x: x.isKindResultType(), info)

  if len(returnValue) > 0:
    returnStr = returnValue[0].spelling + " "
  else:
    returnStr = ""

  info = returnStr + "".join(map(lambda x: x.spelling, word))
  word = "".join(map(formatChunkForWord, word))

  completion['word'] = word
  completion['abbr'] = abbr
  completion['menu'] = info
  completion['info'] = info
  completion['dup'] = 1

  # Replace the number that represants a specific kind with a better
  # textual representation.
  completion['kind'] = str(result.cursorKind)
  return completion

def getCurrentCompletions(base):
  global debug
  debug = int(vim.eval("g:clang_debug")) == 1
  priority = vim.eval("g:clang_sort_algo") == 'priority'
  line = int(vim.eval("line('.')"))
  column = int(vim.eval("b:col"))
  cr = getCurrentCompletionResults(line, column)

  regexp = re.compile("^" + base)
  filteredResult = filter(lambda x: regexp.match(x.string[0].spelling), cr.results)

  getPriority = lambda x: x.string.priority
  getAbbrevation = lambda x: filter(lambda y: y.isKindTypedText(), x.string)[0].spelling.lower()
  sortedResult = sorted(filteredResult, key = getPriority if priority else getAbbrevation)
  return map(formatResult, sortedResult)
