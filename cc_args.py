#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import sys

CONFIG_NAME = ".clang_complete"

def readConfiguration():
  try:
    f = open(CONFIG_NAME, "r")
  except IOError:
    return []

  result = []
  for line in f.readlines():
    strippedLine = line.strip()
    if len(strippedLine) > 0:
      result += [strippedLine]
  f.close()
  return result

def writeConfiguration(lines):
  f = open(CONFIG_NAME, "w")
  f.writelines(lines)
  f.close()

def parseArguments(arguments):
  nextIsInclude = False
  nextIsDefine = False

  includes = []
  defines = []

  for arg in arguments:
    if nextIsInclude:
      includes += [arg]
      nextIsInclude = False
    elif nextIsDefine:
      defines += [arg]
      nextIsDefine = False
    elif arg == "-I":
      nextIsInclude = True
    elif arg == "-D":
      nextIsDefine = True
    elif arg[:2] == "-I":
      includes += [arg[2:]]
    elif arg[:2] == "-D":
      defines += [arg[2:]]

  result = map(lambda x: "-I" + x, includes)
  result += map(lambda x: "-D" + x, defines)

  return result

def mergeLists(base, new):
  result = list(base)
  for newLine in new:
    try:
      result.index(newLine)
    except ValueError:
      result += [newLine]
  return result

configuration = readConfiguration()
args = parseArguments(sys.argv)
result = mergeLists(configuration, args)
writeConfiguration(map(lambda x: x + "\n", result))

exit(os.system(" ".join(sys.argv[1:])))

# vim: set ts=2 sts=2 sw=2 expandtab :
