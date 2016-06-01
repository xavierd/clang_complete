# generated file, do not edit
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
601 : 'ta', # CXCursor_TypeAliasTemplateDecl (Template alias declaration)......\
})
