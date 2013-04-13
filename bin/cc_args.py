#!/usr/bin/env python
#-*- coding: utf-8 -*-

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
    if strippedLine:
      result.append(strippedLine)
  f.close()
  return result

def writeConfiguration(lines):
  f = open(CONFIG_NAME, "w")
  f.writelines(lines)
  f.close()

def parseArguments(arguments):
  nextIsInclude = False
  nextIsDefine = False
  nextIsIncludeFile = False

  includes = []
  defines = []
  include_file = []
  options = []

  for arg in arguments:
    if nextIsInclude:
      includes += [arg]
      nextIsInclude = False
    elif nextIsDefine:
      defines += [arg]
      nextIsDefine = False
    elif nextIsIncludeFile:
      include_file += [arg]
      nextIsIncludeFile = False
    elif arg == "-I":
      nextIsInclude = True
    elif arg == "-D":
      nextIsDefine = True
    elif arg[:2] == "-I":
      includes += [arg[2:]]
    elif arg[:2] == "-D":
      defines += [arg[2:]]
    elif arg == "-include":
      nextIsIncludeFile = True
    elif arg.startswith('-std='):
      options.append(arg)
    elif arg.startswith('-W'):
      options.append(arg)

  result = list(map(lambda x: "-I" + x, includes))
  result.extend(map(lambda x: "-D" + x, defines))
  result.extend(map(lambda x: "-include " + x, include_file))
  result.extend(options)

  return result

def mergeLists(base, new):
  result = list(base)
  for newLine in new:
    if newLine not in result:
      result.append(newLine)
  return result

configuration = readConfiguration()
args = parseArguments(sys.argv)
result = mergeLists(configuration, args)
writeConfiguration(map(lambda x: x + "\n", result))


import subprocess
proc = subprocess.Popen(sys.argv[1:])
ret = proc.wait()

if ret is None:
  sys.exit(1)
sys.exit(ret)

# vim: set ts=2 sts=2 sw=2 expandtab :
