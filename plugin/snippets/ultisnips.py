import vim
import re

try:
  from UltiSnips import UltiSnips_Manager
except:
  from UltiSnips import SnippetManager

  UltiSnips_Manager = SnippetManager(
      vim.eval('g:UltiSnipsExpandTrigger'),
      vim.eval('g:UltiSnipsJumpForwardTrigger'),
      vim.eval('g:UltiSnipsJumpBackwardTrigger'))

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
  if "clang_complete" in UltiSnips_Manager._added_snippets_source._snippets:
    UltiSnips_Manager._added_snippets_source._snippets["clang_complete"].clear_snippets([])

# vim: set ts=2 sts=2 sw=2 expandtab :
