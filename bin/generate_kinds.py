#!/usr/bin/env python2
#-*- coding: utf-8 -*-

import re
import sys
import os.path
import clang.cindex

# you can use this dictionary to map some kinds to better
# textual representation than just the number
mapping = {
    1 : 't' ,  # CXCursor_UnexposedDecl (A declaration whose specific kind is not
               # exposed via this interface)
    2 : 't' ,  # CXCursor_StructDecl (A C or C++ struct)
    3 : 't' ,  # CXCursor_UnionDecl (A C or C++ union)
    4 : 't' ,  # CXCursor_ClassDecl (A C++ class)
    5 : 't' ,  # CXCursor_EnumDecl (An enumeration)
    6 : 'm' ,  # CXCursor_FieldDecl (A field (in C) or non-static data member
               # (in C++) in a struct, union, or C++ class)
    7 : 'e' ,  # CXCursor_EnumConstantDecl (An enumerator constant)
    8 : 'f' ,  # CXCursor_FunctionDecl (A function)
    9 : 'v' ,  # CXCursor_VarDecl (A variable)
   10 : 'a' ,  # CXCursor_ParmDecl (A function or method parameter)
   20 : 't' ,  # CXCursor_TypedefDecl (A typedef)
   21 : 'f' ,  # CXCursor_CXXMethod (A C++ class method)
   22 : 'n' ,  # CXCursor_Namespace (A C++ namespace)
   24 : '+' ,  # CXCursor_Constructor (A C++ constructor)
   25 : '~' ,  # CXCursor_Destructor (A C++ destructor)
   27 : 'a' ,  # CXCursor_TemplateTypeParameter (A C++ template type parameter)
   28 : 'a' ,  # CXCursor_NonTypeTemplateParameter (A C++ non-type template
               # parameter)
   29 : 'a' ,  # CXCursor_TemplateTemplateParameter (A C++ template template
               # parameter)
   30 : 'f' ,  # CXCursor_FunctionTemplate (A C++ function template)
   31 : 'p' ,  # CXCursor_ClassTemplate (A C++ class template)
   33 : 'n' ,  # CXCursor_NamespaceAlias (A C++ namespace alias declaration)
   36 : 't' ,  # CXCursor_TypeAliasDecl (A C++ alias declaration)
   72 : 'u' ,  # CXCursor_NotImplemented
  501 : 'd' ,  # CXCursor_MacroDefinition
  601 : 'ta',  # CXCursor_TypeAliasTemplateDecl (Template alias declaration).
  700 : 'oc',  # CXCursor_OverloadCandidate A code completion overload candidate.
}

if len(sys.argv) != 2:
  print "Usage:", sys.argv[0], "<path-to-Index.h>"
  exit(-1)

index = clang.cindex.Index.create()
tu = index.parse(sys.argv[1])

kinds = None
for child in tu.cursor.get_children():
  if (child.spelling == "CXCursorKind"):
    kinds = child
    break
else:
  print "Index.h doesn't contain CXCursorKind where it is expected, please report a bug."
  exit(-1)

kinds_py_path = os.path.join(
  os.path.dirname(
    os.path.dirname(
      os.path.abspath(__file__)
    )
  ),
  "plugin",
  "kinds.py"
)

with open(kinds_py_path, "w") as f:
  # First/Last pattern
  fl = re.compile("CXCursor_(First|Last)[A-Z].*")

  f.write("# !! GENERATED FILE, DO NOT EDIT\n")
  f.write("kinds = {\n")

  for kind in kinds.get_children():
    # filter out First/Last markers from the enum
    if fl.match(kind.spelling) is not None:
      continue

    text = mapping.get(kind.enum_value, kind.enum_value)
    f.write("{0} : '{1}', # {2} {3}\n".format(kind.enum_value, text, kind.spelling, kind.brief_comment))

  f.write("}\n")

# vim: set ts=2 sts=2 sw=2 expandtab :
