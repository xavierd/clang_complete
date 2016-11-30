# !! GENERATED FILE, DO NOT EDIT
kinds = {
1 : 't', # CXCursor_UnexposedDecl A declaration whose specific kind is not exposed via this interface.
2 : 't', # CXCursor_StructDecl A C or C++ struct.
3 : 't', # CXCursor_UnionDecl A C or C++ union.
4 : 't', # CXCursor_ClassDecl A C++ class.
5 : 't', # CXCursor_EnumDecl An enumeration.
6 : 'm', # CXCursor_FieldDecl A field (in C) or non-static data member (in C++) in a struct, union, or C++ class.
7 : 'e', # CXCursor_EnumConstantDecl An enumerator constant.
8 : 'f', # CXCursor_FunctionDecl A function.
9 : 'v', # CXCursor_VarDecl A variable.
10 : 'a', # CXCursor_ParmDecl A function or method parameter.
11 : '11', # CXCursor_ObjCInterfaceDecl An Objective-C @interface.
12 : '12', # CXCursor_ObjCCategoryDecl An Objective-C @interface for a category.
13 : '13', # CXCursor_ObjCProtocolDecl An Objective-C @protocol declaration.
14 : '14', # CXCursor_ObjCPropertyDecl An Objective-C @property declaration.
15 : '15', # CXCursor_ObjCIvarDecl An Objective-C instance variable.
16 : '16', # CXCursor_ObjCInstanceMethodDecl An Objective-C instance method.
17 : '17', # CXCursor_ObjCClassMethodDecl An Objective-C class method.
18 : '18', # CXCursor_ObjCImplementationDecl An Objective-C @implementation.
19 : '19', # CXCursor_ObjCCategoryImplDecl An Objective-C @implementation for a category.
20 : 't', # CXCursor_TypedefDecl A typedef.
21 : 'f', # CXCursor_CXXMethod A C++ class method.
22 : 'n', # CXCursor_Namespace A C++ namespace.
23 : '23', # CXCursor_LinkageSpec A linkage specification, e.g. 'extern "C"'.
24 : '+', # CXCursor_Constructor A C++ constructor.
25 : '~', # CXCursor_Destructor A C++ destructor.
26 : '26', # CXCursor_ConversionFunction A C++ conversion function.
27 : 'a', # CXCursor_TemplateTypeParameter A C++ template type parameter.
28 : 'a', # CXCursor_NonTypeTemplateParameter A C++ non-type template parameter.
29 : 'a', # CXCursor_TemplateTemplateParameter A C++ template template parameter.
30 : 'f', # CXCursor_FunctionTemplate A C++ function template.
31 : 'p', # CXCursor_ClassTemplate A C++ class template.
32 : '32', # CXCursor_ClassTemplatePartialSpecialization A C++ class template partial specialization.
33 : 'n', # CXCursor_NamespaceAlias A C++ namespace alias declaration.
34 : '34', # CXCursor_UsingDirective A C++ using directive.
35 : '35', # CXCursor_UsingDeclaration A C++ using declaration.
36 : 't', # CXCursor_TypeAliasDecl A C++ alias declaration
37 : '37', # CXCursor_ObjCSynthesizeDecl An Objective-C @synthesize definition.
38 : '38', # CXCursor_ObjCDynamicDecl An Objective-C @dynamic definition.
39 : '39', # CXCursor_CXXAccessSpecifier An access specifier.
40 : '40', # CXCursor_ObjCSuperClassRef An access specifier.
41 : '41', # CXCursor_ObjCProtocolRef An access specifier.
42 : '42', # CXCursor_ObjCClassRef An access specifier.
43 : '43', # CXCursor_TypeRef A reference to a type declaration.
44 : '44', # CXCursor_CXXBaseSpecifier A reference to a type declaration.
45 : '45', # CXCursor_TemplateRef A reference to a class template, function template, template template parameter, or class template partial specialization.
46 : '46', # CXCursor_NamespaceRef A reference to a namespace or namespace alias.
47 : '47', # CXCursor_MemberRef A reference to a member of a struct, union, or class that occurs in some non-expression context, e.g., a designated initializer.
48 : '48', # CXCursor_LabelRef A reference to a labeled statement.
49 : '49', # CXCursor_OverloadedDeclRef A reference to a set of overloaded functions or function templates that has not yet been resolved to a specific function or function template.
50 : '50', # CXCursor_VariableRef A reference to a variable that occurs in some non-expression context, e.g., a C++ lambda capture list.
70 : '70', # CXCursor_InvalidFile A reference to a variable that occurs in some non-expression context, e.g., a C++ lambda capture list.
71 : '71', # CXCursor_NoDeclFound A reference to a variable that occurs in some non-expression context, e.g., a C++ lambda capture list.
72 : 'u', # CXCursor_NotImplemented A reference to a variable that occurs in some non-expression context, e.g., a C++ lambda capture list.
73 : '73', # CXCursor_InvalidCode A reference to a variable that occurs in some non-expression context, e.g., a C++ lambda capture list.
100 : '100', # CXCursor_UnexposedExpr An expression whose specific kind is not exposed via this interface.
101 : '101', # CXCursor_DeclRefExpr An expression that refers to some value declaration, such as a function, variable, or enumerator.
102 : '102', # CXCursor_MemberRefExpr An expression that refers to a member of a struct, union, class, Objective-C class, etc.
103 : '103', # CXCursor_CallExpr An expression that calls a function.
104 : '104', # CXCursor_ObjCMessageExpr An expression that sends a message to an Objective-C object or class.
105 : '105', # CXCursor_BlockExpr An expression that represents a block literal.
106 : '106', # CXCursor_IntegerLiteral An integer literal.
107 : '107', # CXCursor_FloatingLiteral A floating point number literal.
108 : '108', # CXCursor_ImaginaryLiteral An imaginary number literal.
109 : '109', # CXCursor_StringLiteral A string literal.
110 : '110', # CXCursor_CharacterLiteral A character literal.
111 : '111', # CXCursor_ParenExpr A parenthesized expression, e.g. "(1)".
112 : '112', # CXCursor_UnaryOperator This represents the unary-expression's (except sizeof and alignof).
113 : '113', # CXCursor_ArraySubscriptExpr [C99 6.5.2.1] Array Subscripting.
114 : '114', # CXCursor_BinaryOperator A builtin binary operation expression such as "x + y" or "x <= y".
115 : '115', # CXCursor_CompoundAssignOperator Compound assignment such as "+=".
116 : '116', # CXCursor_ConditionalOperator The ?: ternary operator.
117 : '117', # CXCursor_CStyleCastExpr An explicit cast in C (C99 6.5.4) or a C-style cast in C++ (C++ [expr.cast]), which uses the syntax (Type)expr.
118 : '118', # CXCursor_CompoundLiteralExpr [C99 6.5.2.5]
119 : '119', # CXCursor_InitListExpr Describes an C or C++ initializer list.
120 : '120', # CXCursor_AddrLabelExpr The GNU address of label extension, representing &&label.
121 : '121', # CXCursor_StmtExpr This is the GNU Statement Expression extension: ({int X=4; X;})
122 : '122', # CXCursor_GenericSelectionExpr Represents a C11 generic selection.
123 : '123', # CXCursor_GNUNullExpr Implements the GNU __null extension, which is a name for a null pointer constant that has integral type (e.g., int or long) and is the same size and alignment as a pointer.
124 : '124', # CXCursor_CXXStaticCastExpr C++'s static_cast<> expression.
125 : '125', # CXCursor_CXXDynamicCastExpr C++'s dynamic_cast<> expression.
126 : '126', # CXCursor_CXXReinterpretCastExpr C++'s reinterpret_cast<> expression.
127 : '127', # CXCursor_CXXConstCastExpr C++'s const_cast<> expression.
128 : '128', # CXCursor_CXXFunctionalCastExpr Represents an explicit C++ type conversion that uses "functional" notion (C++ [expr.type.conv]).
129 : '129', # CXCursor_CXXTypeidExpr A C++ typeid expression (C++ [expr.typeid]).
130 : '130', # CXCursor_CXXBoolLiteralExpr [C++ 2.13.5] C++ Boolean Literal.
131 : '131', # CXCursor_CXXNullPtrLiteralExpr [C++0x 2.14.7] C++ Pointer Literal.
132 : '132', # CXCursor_CXXThisExpr Represents the "this" expression in C++
133 : '133', # CXCursor_CXXThrowExpr [C++ 15] C++ Throw Expression.
134 : '134', # CXCursor_CXXNewExpr A new expression for memory allocation and constructor calls, e.g: "new CXXNewExpr(foo)".
135 : '135', # CXCursor_CXXDeleteExpr A delete expression for memory deallocation and destructor calls, e.g. "delete[] pArray".
136 : '136', # CXCursor_UnaryExpr A unary expression.
137 : '137', # CXCursor_ObjCStringLiteral An Objective-C string literal i.e. "foo".
138 : '138', # CXCursor_ObjCEncodeExpr An Objective-C @encode expression.
139 : '139', # CXCursor_ObjCSelectorExpr An Objective-C @selector expression.
140 : '140', # CXCursor_ObjCProtocolExpr An Objective-C @protocol expression.
141 : '141', # CXCursor_ObjCBridgedCastExpr An Objective-C "bridged" cast expression, which casts between Objective-C pointers and C pointers, transferring ownership in the process.
142 : '142', # CXCursor_PackExpansionExpr Represents a C++0x pack expansion that produces a sequence of expressions.
143 : '143', # CXCursor_SizeOfPackExpr Represents an expression that computes the length of a parameter pack.
144 : '144', # CXCursor_LambdaExpr None
145 : '145', # CXCursor_ObjCBoolLiteralExpr Objective-c Boolean Literal.
146 : '146', # CXCursor_ObjCSelfExpr Represents the "self" expression in an Objective-C method.
147 : '147', # CXCursor_OMPArraySectionExpr OpenMP 4.0 [2.4, Array Section].
200 : '200', # CXCursor_UnexposedStmt A statement whose specific kind is not exposed via this interface.
201 : '201', # CXCursor_LabelStmt A labelled statement in a function.
202 : '202', # CXCursor_CompoundStmt A group of statements like { stmt stmt }.
203 : '203', # CXCursor_CaseStmt A case statement.
204 : '204', # CXCursor_DefaultStmt A default statement.
205 : '205', # CXCursor_IfStmt An if statement
206 : '206', # CXCursor_SwitchStmt A switch statement.
207 : '207', # CXCursor_WhileStmt A while statement.
208 : '208', # CXCursor_DoStmt A do statement.
209 : '209', # CXCursor_ForStmt A for statement.
210 : '210', # CXCursor_GotoStmt A goto statement.
211 : '211', # CXCursor_IndirectGotoStmt An indirect goto statement.
212 : '212', # CXCursor_ContinueStmt A continue statement.
213 : '213', # CXCursor_BreakStmt A break statement.
214 : '214', # CXCursor_ReturnStmt A return statement.
215 : '215', # CXCursor_GCCAsmStmt A GCC inline assembly statement extension.
215 : '215', # CXCursor_AsmStmt A GCC inline assembly statement extension.
216 : '216', # CXCursor_ObjCAtTryStmt Objective-C's overall @try-@catch-@finally statement.
217 : '217', # CXCursor_ObjCAtCatchStmt Objective-C's @catch statement.
218 : '218', # CXCursor_ObjCAtFinallyStmt Objective-C's @finally statement.
219 : '219', # CXCursor_ObjCAtThrowStmt Objective-C's @throw statement.
220 : '220', # CXCursor_ObjCAtSynchronizedStmt Objective-C's @synchronized statement.
221 : '221', # CXCursor_ObjCAutoreleasePoolStmt Objective-C's autorelease pool statement.
222 : '222', # CXCursor_ObjCForCollectionStmt Objective-C's collection statement.
223 : '223', # CXCursor_CXXCatchStmt C++'s catch statement.
224 : '224', # CXCursor_CXXTryStmt C++'s try statement.
225 : '225', # CXCursor_CXXForRangeStmt C++'s for (* : *) statement.
226 : '226', # CXCursor_SEHTryStmt Windows Structured Exception Handling's try statement.
227 : '227', # CXCursor_SEHExceptStmt Windows Structured Exception Handling's except statement.
228 : '228', # CXCursor_SEHFinallyStmt Windows Structured Exception Handling's finally statement.
229 : '229', # CXCursor_MSAsmStmt A MS inline assembly statement extension.
230 : '230', # CXCursor_NullStmt The null statement ";": C99 6.8.3p3.
231 : '231', # CXCursor_DeclStmt Adaptor class for mixing declarations with statements and expressions.
232 : '232', # CXCursor_OMPParallelDirective OpenMP parallel directive.
233 : '233', # CXCursor_OMPSimdDirective OpenMP SIMD directive.
234 : '234', # CXCursor_OMPForDirective OpenMP for directive.
235 : '235', # CXCursor_OMPSectionsDirective OpenMP sections directive.
236 : '236', # CXCursor_OMPSectionDirective OpenMP section directive.
237 : '237', # CXCursor_OMPSingleDirective OpenMP single directive.
238 : '238', # CXCursor_OMPParallelForDirective OpenMP parallel for directive.
239 : '239', # CXCursor_OMPParallelSectionsDirective OpenMP parallel sections directive.
240 : '240', # CXCursor_OMPTaskDirective OpenMP task directive.
241 : '241', # CXCursor_OMPMasterDirective OpenMP master directive.
242 : '242', # CXCursor_OMPCriticalDirective OpenMP critical directive.
243 : '243', # CXCursor_OMPTaskyieldDirective OpenMP taskyield directive.
244 : '244', # CXCursor_OMPBarrierDirective OpenMP barrier directive.
245 : '245', # CXCursor_OMPTaskwaitDirective OpenMP taskwait directive.
246 : '246', # CXCursor_OMPFlushDirective OpenMP flush directive.
247 : '247', # CXCursor_SEHLeaveStmt Windows Structured Exception Handling's leave statement.
248 : '248', # CXCursor_OMPOrderedDirective OpenMP ordered directive.
249 : '249', # CXCursor_OMPAtomicDirective OpenMP atomic directive.
250 : '250', # CXCursor_OMPForSimdDirective OpenMP for SIMD directive.
251 : '251', # CXCursor_OMPParallelForSimdDirective OpenMP parallel for SIMD directive.
252 : '252', # CXCursor_OMPTargetDirective OpenMP target directive.
253 : '253', # CXCursor_OMPTeamsDirective OpenMP teams directive.
254 : '254', # CXCursor_OMPTaskgroupDirective OpenMP taskgroup directive.
255 : '255', # CXCursor_OMPCancellationPointDirective OpenMP cancellation point directive.
256 : '256', # CXCursor_OMPCancelDirective OpenMP cancel directive.
257 : '257', # CXCursor_OMPTargetDataDirective OpenMP target data directive.
258 : '258', # CXCursor_OMPTaskLoopDirective OpenMP taskloop directive.
259 : '259', # CXCursor_OMPTaskLoopSimdDirective OpenMP taskloop simd directive.
260 : '260', # CXCursor_OMPDistributeDirective OpenMP distribute directive.
300 : '300', # CXCursor_TranslationUnit Cursor that represents the translation unit itself.
400 : '400', # CXCursor_UnexposedAttr An attribute whose specific kind is not exposed via this interface.
401 : '401', # CXCursor_IBActionAttr An attribute whose specific kind is not exposed via this interface.
402 : '402', # CXCursor_IBOutletAttr An attribute whose specific kind is not exposed via this interface.
403 : '403', # CXCursor_IBOutletCollectionAttr An attribute whose specific kind is not exposed via this interface.
404 : '404', # CXCursor_CXXFinalAttr An attribute whose specific kind is not exposed via this interface.
405 : '405', # CXCursor_CXXOverrideAttr An attribute whose specific kind is not exposed via this interface.
406 : '406', # CXCursor_AnnotateAttr An attribute whose specific kind is not exposed via this interface.
407 : '407', # CXCursor_AsmLabelAttr An attribute whose specific kind is not exposed via this interface.
408 : '408', # CXCursor_PackedAttr An attribute whose specific kind is not exposed via this interface.
409 : '409', # CXCursor_PureAttr An attribute whose specific kind is not exposed via this interface.
410 : '410', # CXCursor_ConstAttr An attribute whose specific kind is not exposed via this interface.
411 : '411', # CXCursor_NoDuplicateAttr An attribute whose specific kind is not exposed via this interface.
412 : '412', # CXCursor_CUDAConstantAttr An attribute whose specific kind is not exposed via this interface.
413 : '413', # CXCursor_CUDADeviceAttr An attribute whose specific kind is not exposed via this interface.
414 : '414', # CXCursor_CUDAGlobalAttr An attribute whose specific kind is not exposed via this interface.
415 : '415', # CXCursor_CUDAHostAttr An attribute whose specific kind is not exposed via this interface.
416 : '416', # CXCursor_CUDASharedAttr An attribute whose specific kind is not exposed via this interface.
417 : '417', # CXCursor_VisibilityAttr An attribute whose specific kind is not exposed via this interface.
418 : '418', # CXCursor_DLLExport An attribute whose specific kind is not exposed via this interface.
419 : '419', # CXCursor_DLLImport An attribute whose specific kind is not exposed via this interface.
500 : '500', # CXCursor_PreprocessingDirective An attribute whose specific kind is not exposed via this interface.
501 : 'd', # CXCursor_MacroDefinition An attribute whose specific kind is not exposed via this interface.
502 : '502', # CXCursor_MacroExpansion An attribute whose specific kind is not exposed via this interface.
502 : '502', # CXCursor_MacroInstantiation An attribute whose specific kind is not exposed via this interface.
503 : '503', # CXCursor_InclusionDirective An attribute whose specific kind is not exposed via this interface.
600 : '600', # CXCursor_ModuleImportDecl A module import declaration.
601 : 'ta', # CXCursor_TypeAliasTemplateDecl A module import declaration.
700 : 'oc', # CXCursor_OverloadCandidate A code completion overload candidate.
}
