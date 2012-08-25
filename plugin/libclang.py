from clang.cindex import *
import vim
import time
import threading
import psutil, os

def initClangComplete(clang_complete_flags):
  global index
  index = Index.create()
  global translationUnits
  translationUnits = []
  global complete_flags
  complete_flags = int(clang_complete_flags)
  global libclangLock
  libclangLock = threading.Lock()
  global process
  process = psutil.Process(os.getpid())
  global memory_percent
  memory_percent = vim.eval("g:clang_memory_percent")
  if memory_percent.isdigit() and 0 <= int(memory_percent) <= 100:
    memory_percent = int(memory_percent)
  else:
    memory_percent = 50

# Get a tuple (fileName, fileContent) for the file opened in the current
# vim buffer. The fileContent contains the unsafed buffer content.
def getCurrentFile():
  file = "\n".join(vim.eval("getline(1, '$')"))
  return (vim.current.buffer.name, file)

def getCurrentTranslationUnit(args, currentFile, fileName, update = False):
  fileNames = [name for name, tu in translationUnits]
  if fileName in fileNames:
    tu = translationUnits[fileNames.index(fileName)][1]
    if update:
      if debug:
        start = time.time()
      vim.command('echom "Parsing started"')
      tu.reparse([currentFile])
      vim.command('echom "Parsing done"')
      if debug:
        elapsed = (time.time() - start)
        print "LibClang - Reparsing: %.3f" % elapsed
    return tu

  if process.get_memory_percent() > memory_percent:
    translationUnits.pop()

  if debug:
    start = time.time()
  vim.command('echom "Parsing started"')
  flags = TranslationUnit.PARSE_PRECOMPILED_PREAMBLE
  tu = index.parse(fileName, args, [currentFile], flags)
  if debug:
    elapsed = (time.time() - start)
    print "LibClang - First parse: %.3f" % elapsed

  if tu == None:
    print "Cannot parse this source file. The following arguments " \
        + "are used for clang: " + " ".join(args)
    return None

  translationUnits.append((fileName, tu))

  # Reparse to initialize the PCH cache even for auto completion
  # This should be done by index.parse(), however it is not.
  # So we need to reparse ourselves.
  if debug:
    start = time.time()
  tu.reparse([currentFile])
  vim.command('echom "Parsing done"')
  if debug:
    elapsed = (time.time() - start)
    print "LibClang - First reparse (generate PCH cache): %.3f" % elapsed
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
  fileNames = [name for name, tu in translationUnits]
  if vim.current.buffer.name in fileNames:
    tu = translationUnits[fileNames.index(vim.current.buffer.name)][1]
    highlightDiagnostics(tu)

def getCurrentQuickFixList():
  fileNames = [name for name, tu in translationUnits]
  if vim.current.buffer.name in fileNames:
    tu = translationUnits[fileNames.index(vim.current.buffer.name)][1]
    return getQuickFixList(tu)
  return []

def evalArgs():
  userOptionsGlobal = splitOptions(vim.eval("g:clang_user_options"))
  userOptionsLocal = splitOptions(vim.eval("b:clang_user_options"))
  parametersLocal = splitOptions(vim.eval("b:clang_parameters"))
  return userOptionsGlobal + userOptionsLocal + parametersLocal

def updateCurrentDiagnostics():
  global debug
  debug = int(vim.eval("g:clang_debug")) == 1
  with libclangLock:
    getCurrentTranslationUnit(evalArgs(), getCurrentFile(), vim.current.buffer.name, update = True)

def getCurrentCompletionResults(line, column, args, currentFile, fileName):
  tu = getCurrentTranslationUnit(args, currentFile, fileName)
  if debug:
    start = time.time()
  cr = tu.codeComplete(fileName, line, column, [currentFile],
      complete_flags)
  if debug:
    elapsed = (time.time() - start)
    print "LibClang - Code completion time (library): %.3f" % elapsed
  return cr

def formatResult(result):
  completion = dict()

  returnValue = None
  abbr = ""
  chunks = filter(lambda x: not x.isKindInformative(), result.string)

  args_pos = []
  cur_pos = 0
  word = ""

  for chunk in chunks:

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
  completion['dup'] = 0

  # Replace the number that represents a specific kind with a better
  # textual representation.
  completion['kind'] = kinds[result.cursorKind]

  return completion

class CompleteThread(threading.Thread):
  def __init__(self, line, column, currentFile, fileName):
    threading.Thread.__init__(self)
    self.line = line
    self.column = column
    self.currentFile = currentFile
    self.fileName = fileName
    self.result = None
    self._args = None

  @property
  def args(self):
    if self._args == None:
      self._args = evalArgs()
    return self._args

  def run(self):
    try:
      libclangLock.acquire()
      if self.line == -1:
        # Warm up the caches. For this it is sufficient to get the current
        # translation unit. No need to retrieve completion results.
        # This short pause is necessary to allow vim to initialize itself.
        # Otherwise we would get: E293: block was not locked
        # The user does not see any delay, as we just pause a background thread.
        time.sleep(0.1)
        getCurrentTranslationUnit(self.args, self.currentFile, self.fileName)
      else:
        self.result = getCurrentCompletionResults(self.line, self.column,
                                          self.args, self.currentFile, self.fileName)
    except Exception:
      pass
    libclangLock.release()

def WarmupCache():
  global debug
  debug = int(vim.eval("g:clang_debug")) == 1
  t = CompleteThread(-1, -1, getCurrentFile(), vim.current.buffer.name)
  t.start()

class Completion:
  def __init__(self):
    self.base    = None
    self.basket  = None
    self.thread  = None
    self.sorting = None

  def start(self, base):
    self.base = base
    self.sorting = vim.eval("g:clang_sort_algo")
    line = int(vim.eval("line('.')"))
    column = int(vim.eval("b:col"))
    self.thread = CompleteThread(line, column, getCurrentFile(), vim.current.buffer.name)
    self.thread.start()

  def isReady(self, timeout):
    self.thread.join(timeout)
    if not self.thread.isAlive():
      self.basket = self.thread.result
      self.basket = self.basket.results if self.basket else []
      if self.base:
        self.basket = filter(lambda x: getAbbr(x.string).startswith(self.base), self.basket)
      if self.sorting == 'priority':
        getPriority = lambda x: x.string.priority
        self.basket = sorted(self.basket, None, getPriority)
      if self.sorting == 'alpha':
        getAbbrevation = lambda x: getAbbr(x.string).lower()
        self.basket = sorted(self.basket, None, getAbbrevation)
      return True
    return False

  def fetch(self, amount):
    handful = self.basket[0:amount]
    del self.basket[0:amount]
    return map(formatResult, handful)

def startCompletion(base):
  global debug
  global completion

  debug = int(vim.eval("g:clang_debug")) == 1
  completion = Completion()
  completion.start(base)

def isCompletionReady(timeout):
  return '1' if completion.isReady(timeout) else '0'

def fetchCompletions(amount):
  return str(completion.fetch(amount))

def endCompletion():
  global completion
  completion = None

def getAbbr(strings):
  for s in strings:
    if s.isKindTypedText():
      return s.spelling
  return ""

def sleepAndParse():
  time.sleep(0.1) # Needed to avoid E293. Is it safe?
  updateCurrentDiagnostics()

def backgroundParse():
  threading.Thread(target=sleepAndParse).start()

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
