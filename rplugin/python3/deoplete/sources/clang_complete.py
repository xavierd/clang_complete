#=============================================================================
# FILE: clang_complete.py
# AUTHOR: Joe Hermaszewski
#=============================================================================

from .base import Base
from deoplete.util import error 

import os
import shlex

lib_clang_loaded = True

try:
  from clang.cindex import *
except:
  lib_clang_loaded = False

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
  except TranslationUnitLoadError as e:
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
      files = os.listdir(path)
      if len(files) >= 1:
        files = sorted(files)
        subDir = files[-1]
      else:
        subDir = '.'
      path = path + "/" + subDir + "/include/"
      arg = "-I" + path
      if canFindBuiltinHeaders(index, [arg]):
        return path
    except:
      pass

  return None

def initClangComplete(vim):

  clang_complete_flags = vim.eval('g:clang_complete_lib_flags')  
  clang_compilation_database = vim.eval('g:clang_compilation_database')
  library_path = vim.eval('g:clang_library_path')
  global index

  if library_path:
    if os.path.isdir(library_path):
      Config.set_library_path(library_path)
    else:
      Config.set_library_file(library_path)

  Config.set_compatibility_check(False)

  try:
    index = Index.create()
  except Exception as e:
    if library_path:
      suggestion = "Are you sure '%s' contains libclang?" % library_path
    else:
      suggestion = "Consider setting g:clang_library_path."

    exception_msg = str(e)

    error(vim, "Loading libclang failed, completion won't be available. " + suggestion + exception_msg)
    return 0

  global builtinHeaderPath
  builtinHeaderPath = None
  if not canFindBuiltinHeaders(index):
    builtinHeaderPath = getBuiltinHeaderPath(library_path)

    if not builtinHeaderPath:
      error(vim,"WARNING: libclang can not find the builtin includes.")
      error(vim,"         This will cause slow code completion.")
      error(vim,"         Please report the problem.")

  global translationUnits
  translationUnits = dict()
  global complete_flags
  complete_flags = int(clang_complete_flags)
  global compilation_database
  if clang_compilation_database != '':
    compilation_database = CompilationDatabase.fromDirectory(clang_compilation_database)
  else:
    compilation_database = None
  return 1

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

def splitOptions(options):
  # Use python's shell command lexer to correctly split the list of options in
  # accordance with the POSIX standard
  return shlex.split(options)

def getCompileParams(fileName):
  global builtinHeaderPath
  params = getCompilationDBParams(fileName)
  args = params['args']
  args += splitOptions(g_usr_opt)
  args += splitOptions(b_usr_opt)
  args += splitOptions(b_param)

  if builtinHeaderPath:
    args.append("-I" + builtinHeaderPath)

  return { 'args' : args,
           'cwd' : params['cwd'] }

def formatResult(result):
  completion = dict()
  returnValue = None
  abbr = ""
  word = ""
  info = ""

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

    # TODO find out why this is None sometimes
    # I doesn't seem like this ever happened with the python2 code
    if chunk_spelling == None:
      continue

    if chunk.isKindTypedText():
      abbr = chunk_spelling

    if chunk.isKindOptional():
      for optional_arg in roll_out_optional(chunk.string):
        if place_markers_for_optional_args:
          word += "$" + optional_arg
        info += optional_arg + "=?"

    if chunk.isKindPlaceHolder():
      word += "$" + chunk_spelling
    else:
      word += chunk_spelling

    info += chunk_spelling

  menu = info

  if returnValue:
    menu = returnValue.spelling + " " + menu

  completion['word'] = word
  completion['abbr'] = abbr
  completion['menu'] = menu
  completion['info'] = info
  completion['dup'] = 1

  # Replace the number that represents a specific kind with a better
  # textual representation.
  # TODO got a key error of "700" here, unknown type?
  if result.cursorKind in kinds:
    completion['kind'] = kinds[result.cursorKind]
  else:
    #We don't know what type it is so just add the number it had
    completion['kind'] = str(result.cursorKind)

  return completion


def getCurrentTranslationUnit(args, currentFile, fileName, update = False):
  tu = translationUnits.get(fileName)
  if tu != None:
    if update:
      tu.reparse([currentFile])
    return tu

  flags = TranslationUnit.PARSE_PRECOMPILED_PREAMBLE | \
          TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD
  try:
    tu = index.parse(fileName, args, [currentFile], flags)
  except TranslationUnitLoadError as e:
    return None

  translationUnits[fileName] = tu

  # Reparse to initialize the PCH cache even for auto completion
  # This should be done by index.parse(), however it is not.
  # So we need to reparse ourselves.
  tu.reparse([currentFile])
  return tu

def getCurrentCompletionResults(line, column, args, currentFile, fileName):

  tu = getCurrentTranslationUnit(args, currentFile, fileName)

  if tu == None:
    return None

  cr = tu.codeComplete(fileName, line, column, [currentFile],
      complete_flags)
  return cr

def getAbbr(strings):
  for chunks in strings:
    if chunks.isKindTypedText():
      return chunks.spelling
  return ""

# Get a tuple (fileName, fileContent) for the file opened in the current
# vim buffer. The fileContent contains the unsafed buffer content.
def getCurrentFile(vim):
  file = "\n".join(vim.current.buffer[:] + ["\n"])
  return (vim.current.buffer.name, file)

class Source(Base):
  def __init__(self, vim):
    Base.__init__(self, vim)

    self.name = 'clang_complete'
    self.mark = '[clang]'
    self.filetypes = ['c', 'cpp']
    self.is_bytepos = True
    self.min_pattern_length = 0

    self.init_ret = 0
    self.inited = False
    #Define global variables for later
    global index
    global builtinHeaderPath
    global translationUnits
    global complete_flags
    global compilation_database
    #See if we failed to load the python3 clang lib
    if not lib_clang_loaded:
      error(self.vim, "Failed to load the py3 clang lib")
      error(self.vim, "It is available at:")
      error(self.vim, "https://pypi.python.org/pypi/libclang-py3")
      self.inited = True

  def get_complete_position(self, context):
    if not self.inited:
      #Init global variables and clang lib, returns 0 on error
      self.init_ret = initClangComplete(self.vim)
      self.inited = True
    
    if context['input'][-1].isspace():
      #Do not match empty lines
      return -1

    # 1 if it has init was successful
    if self.init_ret:
      return self.vim.call('ClangComplete', 1, 0)
    else:
      return -1

  def gather_candidates(self, context):
    if self.init_ret:
      global place_markers_for_optional_args
      global g_usr_opt
      global b_usr_opt
      global b_param

      place_markers_for_optional_args = int(self.vim.eval("g:clang_complete_optional_args_in_snippets")) == 1
      g_usr_opt = self.vim.eval("g:clang_user_options")
      b_usr_opt = self.vim.eval("b:clang_user_options")
      b_param = self.vim.eval("b:clang_parameters")

      sorting = self.vim.eval("g:clang_sort_algo")
      line = self.vim.current.window.cursor[0]
      column = int(self.vim.eval("b:col"))
      params = getCompileParams(self.vim.current.buffer.name)

      cr = getCurrentCompletionResults(line, column, params['args'], getCurrentFile(self.vim), self.vim.current.buffer.name)
      if cr is None:
        return []

      results = cr.results

      if sorting == 'priority':
        getPriority = lambda x: x.string.priority
        results = sorted(results, key=getPriority)
      if sorting == 'alpha':
        getAbbrevation = lambda x: getAbbr(x.string).lower()
        results = sorted(results, key=getAbbrevation)

      result = list(map(formatResult, results))

      return result
    else:
      return []

# Manually extracted from Index.h
# Doing it by hand is long, error prone and horrible, we must find a way
# to do that automatically.
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
35 : '35', # CXCursor_UsingDeclaration (A C++ using declaration)               \
36 : 't',  # CXCursor_TypeAliasDecl (A C++ alias declaration)                  \
37 : '37', # CXCursor_ObjCSynthesizeDecl (An Objective-C synthesize definition)\
38 : '38', # CXCursor_ObjCDynamicDecl (An Objective-C dynamic definition)      \
39 : '39', # CXCursor_CXXAccessSpecifier (An access specifier)                 \
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
50 : '50', # CXCursor_VariableRef                                              \
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
106 : '106',  # CXCursor_IntegerLiteral (An integer literal)                   \
107 : '107',  # CXCursor_FloatingLiteral (A floating point number literal)     \
108 : '108',  # CXCursor_ImaginaryLiteral (An imaginary number literal)        \
109 : '109',  # CXCursor_StringLiteral (A string literal)                      \
110 : '110',  # CXCursor_CharacterLiteral (A character literal)                \
111 : '111',  # CXCursor_ParenExpr (A parenthesized expression, e.g. "(1)")    \
112 : '112',  # CXCursor_UnaryOperator (This represents the unary-expression's \
              # (except sizeof and alignof))                                   \
113 : '113',  # CXCursor_ArraySubscriptExpr ([C99 6.5.2.1] Array Subscripting) \
114 : '114',  # CXCursor_BinaryOperator (A builtin binary operation expression \
              # such as "x + y" or "x <= y")                                   \
115 : '115',  # CXCursor_CompoundAssignOperator (Compound assignment such as   \
              # "+=")                                                          \
116 : '116',  # CXCursor_ConditionalOperator (The ?: ternary operator)         \
117 : '117',  # CXCursor_CStyleCastExpr (An explicit cast in C (C99 6.5.4) or a\
              # C-style cast in C++ (C++ [expr.cast]), which uses the syntax   \
              # (Type)expr)                                                    \
118 : '118',  # CXCursor_CompoundLiteralExpr ([C99 6.5.2.5])                   \
119 : '119',  # CXCursor_InitListExpr (Describes an C or C++ initializer list) \
120 : '120',  # CXCursor_AddrLabelExpr (The GNU address of label extension,    \
              # representing &&label)                                          \
121 : '121',  # CXCursor_StmtExpr (This is the GNU Statement Expression        \
              # extension: ({int X=4; X;})                                     \
122 : '122',  # CXCursor_GenericSelectionExpr (brief Represents a C11 generic  \
              # selection)                                                     \
123 : '123',  # CXCursor_GNUNullExpr (Implements the GNU __null extension)     \
124 : '124',  # CXCursor_CXXStaticCastExpr (C++'s static_cast<> expression)    \
125 : '125',  # CXCursor_CXXDynamicCastExpr (C++'s dynamic_cast<> expression)  \
126 : '126',  # CXCursor_CXXReinterpretCastExpr (C++'s reinterpret_cast<>      \
              # expression)                                                    \
127 : '127',  # CXCursor_CXXConstCastExpr (C++'s const_cast<> expression)      \
128 : '128',  # CXCursor_CXXFunctionalCastExpr (Represents an explicit C++ type\
              # conversion that uses "functional" notion                       \
              # (C++ [expr.type.conv]))                                        \
129 : '129',  # CXCursor_CXXTypeidExpr (A C++ typeid expression                \
              # (C++ [expr.typeid]))                                           \
130 : '130',  # CXCursor_CXXBoolLiteralExpr (brief [C++ 2.13.5] C++ Boolean    \
              # Literal)                                                       \
131 : '131',  # CXCursor_CXXNullPtrLiteralExpr ([C++0x 2.14.7] C++ Pointer     \
              # Literal)                                                       \
132 : '132',  # CXCursor_CXXThisExpr (Represents the "this" expression in C+)  \
133 : '133',  # CXCursor_CXXThrowExpr ([C++ 15] C++ Throw Expression)          \
134 : '134',  # CXCursor_CXXNewExpr (A new expression for memory allocation    \
              # and constructor calls)                                         \
135 : '135',  # CXCursor_CXXDeleteExpr (A delete expression for memory         \
              # deallocation and destructor calls)                             \
136 : '136',  # CXCursor_UnaryExpr (A unary expression)                        \
137 : '137',  # CXCursor_ObjCStringLiteral (An Objective-C string literal      \
              # i.e. @"foo")                                                   \
138 : '138',  # CXCursor_ObjCEncodeExpr (An Objective-C \@encode expression)   \
139 : '139',  # CXCursor_ObjCSelectorExpr (An Objective-C \@selector expression)\
140 : '140',  # CXCursor_ObjCProtocolExpr (An Objective-C \@protocol expression)\
141 : '141',  # CXCursor_ObjCBridgedCastExpr (An Objective-C "bridged" cast    \
              # expression, which casts between Objective-C pointers and C     \
              # pointers, transferring ownership in the process)               \
142 : '142',  # CXCursor_PackExpansionExpr (Represents a C++0x pack expansion  \
              # that produces a sequence of expressions)                       \
143 : '143',  # CXCursor_SizeOfPackExpr (Represents an expression that computes\
              # the length of a parameter pack)                                \
144 : '144',  # CXCursor_LambdaExpr (Represents a C++ lambda expression that   \
              # produces a local function object)                              \
145 : '145',  # CXCursor_ObjCBoolLiteralExpr (Objective-c Boolean Literal)     \
                                                                               \
# Statements                                                                   \
200 : '200',  # CXCursor_UnexposedStmt (A statement whose specific kind is not \
              # exposed via this interface)                                    \
201 : '201',  # CXCursor_LabelStmt (A labelled statement in a function)        \
202 : '202',  # CXCursor_CompoundStmt (A group of statements like              \
              # { stmt stmt }.                                                 \
203 : '203',  # CXCursor_CaseStmt (A case statment)                            \
204 : '204',  # CXCursor_DefaultStmt (A default statement)                     \
205 : '205',  # CXCursor_IfStmt (An if statemen)                               \
206 : '206',  # CXCursor_SwitchStmt (A switch statement)                       \
207 : '207',  # CXCursor_WhileStmt (A while statement)                         \
208 : '208',  # CXCursor_DoStmt (A do statement)                               \
209 : '209',  # CXCursor_ForStmt (A for statement)                             \
210 : '210',  # CXCursor_GotoStmt (A goto statement)                           \
211 : '211',  # CXCursor_IndirectGotoStmt (An indirect goto statement)         \
212 : '212',  # CXCursor_ContinueStmt (A continue statement)                   \
213 : '213',  # CXCursor_BreakStmt (A break statement)                         \
214 : '214',  # CXCursor_ReturnStmt (A return statement)                       \
215 : '215',  # CXCursor_GCCAsmStmt (A GCC inline assembly statement extension)\
216 : '216',  # CXCursor_ObjCAtTryStmt (Objective-C's overall try-catch-finally\
              # statement.                                                     \
217 : '217',  # CXCursor_ObjCAtCatchStmt (Objective-C's catch statement)       \
218 : '218',  # CXCursor_ObjCAtFinallyStmt (Objective-C's finally statement)   \
219 : '219',  # CXCursor_ObjCAtThrowStmt (Objective-C's throw statement)       \
220 : '220',  # CXCursor_ObjCAtSynchronizedStmt (Objective-C's synchronized    \
              # statement)                                                     \
221 : '221',  # CXCursor_ObjCAutoreleasePoolStmt (Objective-C's autorelease    \
              # pool statement)                                                \
222 : '222',  # CXCursor_ObjCForCollectionStmt (Objective-C's collection       \
              # statement)                                                     \
223 : '223',  # CXCursor_CXXCatchStmt (C++'s catch statement)                  \
224 : '224',  # CXCursor_CXXTryStmt (C++'s try statement)                      \
225 : '225',  # CXCursor_CXXForRangeStmt (C++'s for (* : *) statement)         \
226 : '226',  # CXCursor_SEHTryStmt (Windows Structured Exception Handling's   \
              # try statement)                                                 \
227 : '227',  # CXCursor_SEHExceptStmt (Windows Structured Exception Handling's\
              # except statement.                                              \
228 : '228',  # CXCursor_SEHFinallyStmt (Windows Structured Exception          \
              # Handling's finally statement)                                  \
229 : '229',  # CXCursor_MSAsmStmt (A MS inline assembly statement extension)  \
230 : '230',  # CXCursor_NullStmt (The null satement ";": C99 6.8.3p3)         \
231 : '231',  # CXCursor_DeclStmt (Adaptor class for mixing declarations with  \
              # statements and expressions)                                    \
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
404 : '404',  # CXCursor_CXXFinalAttr                                          \
405 : '405',  # CXCursor_CXXOverrideAttr                                       \
406 : '406',  # CXCursor_AnnotateAttr                                          \
407 : '407',  # CXCursor_AsmLabelAttr                                          \
                                                                               \
# Preprocessing                                                                \
500 : '500', # CXCursor_PreprocessingDirective                                 \
501 : 'd',   # CXCursor_MacroDefinition                                        \
502 : '502', # CXCursor_MacroInstantiation                                     \
503 : '503', # CXCursor_InclusionDirective                                     \
                                                                               \
# Modules                                                                      \
600 : '600', # CXCursor_ModuleImportDecl (A module import declaration)         \
})

# vim: set ts=2 sts=2 sw=2 expandtab :
