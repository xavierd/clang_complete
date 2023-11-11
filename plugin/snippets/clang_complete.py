import re
import vim

def getClangSnippetJumpKey(escapeForFeedkeys):
  snippet_jump_map = vim.eval("g:clang_complete_snippet_jump_map")
  if escapeForFeedkeys:
    snippet_jump_map = snippet_jump_map.replace('<', r'\<').replace('"', r'\"')
  return snippet_jump_map

def snippetsInit():
  python_cmd = vim.eval('s:py_cmd')
  vim.command("noremap <silent> <buffer> <Plug>ClangSnippetJumpN :{} updateSnips()<CR>".format(python_cmd))
  vim.command("snoremap <silent> <buffer> <Plug>ClangSnippetJumpS <ESC>:{} updateSnips()<CR>".format(python_cmd))
  snippet_jump_map = getClangSnippetJumpKey(False)
  if "" != snippet_jump_map:
    vim.command("map <silent> <buffer> {} <Plug>ClangSnippetJumpN".format(snippet_jump_map))
    vim.command("smap <silent> <buffer> {} <Plug>ClangSnippetJumpS".format(snippet_jump_map))
  if int(vim.eval("g:clang_conceal_snippets")) == 1:
    vim.command("syntax match placeHolder /\$`[^`]*`/ contains=placeHolderMark")
    vim.command("syntax match placeHolderMark contained /\$`/ conceal")
    vim.command("syntax match placeHolderMark contained /`/ conceal")

# The two following function are performance sensitive, do _nothing_
# more that the strict necessary.

def snippetsFormatPlaceHolder(word):
  return "$`%s`" % word

def snippetsAddSnippet(fullname, word, abbr):
  return word

r = re.compile('\$`[^`]*`')

def snippetsTrigger():
  if r.search(vim.current.line) is None:
    return
  # Using the Plug here works even if g:clang_complete_snippet_jump_map is empty.
  vim.command('call feedkeys("\<esc>^\<Plug>ClangSnippetJumpN")')

def snippetsReset():
  pass

def updateSnips():
  line = vim.current.line
  row, col = vim.current.window.cursor

  result = r.search(line, col)
  if result is None:
    result = r.search(line)
    if result is None:
      snippet_jump_map = getClangSnippetJumpKey(True)
      if "" != snippet_jump_map:
        vim.command('call feedkeys("{}", "n")'.format(snippet_jump_map))
      return

  start, end = result.span()
  vim.current.window.cursor = row, start
  isInclusive = vim.eval("&selection") == "inclusive"
  vim.command('call feedkeys("\<ESC>v%dl\<C-G>", "n")' % (end - start - isInclusive))

# vim: set ts=2 sts=2 sw=2 expandtab :
