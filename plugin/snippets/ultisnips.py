import vim
import re

ultisnips_idx = 0

def snippetsInit():
  UltiSnips_Manager.add_buffer_filetypes('%s.clang_complete' % vim.eval('&filetype'))

def snippetsFormatPlaceHolder(word):
  # Better way to do that?
  ultisnips_idx++
  return '${%d:%s}' % ultisnips_idx, word

def snippetsAddSnippet(fullname, word):
  ultisnips_idx = 0
  # FIXME: required?
  snippet_id = re.sub(' ', '_', fullname)
  UltiSnips_Manager.add_snippet(snippet_id, word, fullname, "i", "clang_complete")
  return snippet_id

def snippetsTrigger():
  UltiSnips_Manager.expand()

def snippetsReset():
  UltiSnips_Manager.clear_snippets(ft="clang_complete")

# vim: set ts=2 sts=2 sw=2 expandtab :
