import vim
import re
from UltiSnips import UltiSnips_Manager

def snippetsInit():
  global ultisnips_idx
  ultisnips_idx = 0
  UltiSnips_Manager.add_buffer_filetypes('%s.clang_complete' % vim.eval('&filetype'))

def snippetsFormatPlaceHolder(word):
  # Better way to do that?
  global ultisnips_idx
  ultisnips_idx += 1
  return '${%d:%s}' % (ultisnips_idx, word)

def snippetsAddSnippet(fullname, word, abbr):
  global ultisnips_idx
  ultisnips_idx = 0
  UltiSnips_Manager.add_snippet(fullname, word, fullname, "i", "clang_complete")
  return fullname

def snippetsTrigger():
  print vim.current.line
  UltiSnips_Manager.expand()

def snippetsReset():
  UltiSnips_Manager.clear_snippets(ft="clang_complete")

# vim: set ts=2 sts=2 sw=2 expandtab :
