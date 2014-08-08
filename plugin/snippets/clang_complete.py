import re
import vim

def snippetsInit():
  vim.command("noremap <silent> <buffer> <tab> :python updateSnips()<CR>")
  vim.command("snoremap <silent> <buffer> <tab> <ESC>:python updateSnips()<CR>")
  if int(vim.eval("g:clang_conceal_snippets")) == 1:
    vim.command("syntax match placeHolder /\$`[^`]*`/ contains=placeHolderMark")
    vim.command("syntax match placeHolderMark contained /\$`/ conceal")
    vim.command("syntax match placeHolderMark contained /`/ conceal")

  # Check if there is a mapping for <tab> in insert mode (e.g. supertab)
  vim.command("let oldmap=maparg(\"<tab>\", \"i\")")
  oldmap = vim.eval("oldmap")

  # and only use insert mode <tab> mapping if there is none
  if (len(oldmap) == 0):
    vim.command("inoremap <expr> <silent> <buffer> <tab> InsertModeTabHelper()")

# The two following function are performance sensitive, do _nothing_
# more than the strict necessary.

def snippetsFormatPlaceHolder(word):
  return "$`%s`" % word

def snippetsAddSnippet(fullname, word, abbr):
  return word

r = re.compile('\$`[^`]*`')

def snippetsTrigger():
  if r.search(vim.current.line) is None:
    return
  vim.command('call feedkeys("\<esc>^\<tab>")')

def snippetsReset():
  pass

def updateSnips():
  line = vim.current.line
  row, col = vim.current.window.cursor

  result = r.search(line, col)
  if result is None:
    result = r.search(line)
    if result is None:
      vim.command('call feedkeys("\<c-i>", "n")')
      return

  start, end = result.span()
  vim.current.window.cursor = row, start
  isInclusive = vim.eval("&selection") == "inclusive"
  vim.command('call feedkeys("\<ESC>v%dl\<C-G>", "n")' % (end - start - isInclusive))

def insertModeTab():
  line = vim.current.line
  row, col = vim.current.window.cursor

  # look for argument completion strings (denoted by $` `)
  r = re.compile('\$`[^`]*`')
  result = r.search(line)

  if result is None:
    # if none found, perform a normal tab or jump to the end of the line
    # if the symbol under the cursor is a closing bracket

    # strange, we need +1 here if called as :python insertModeTab
    # col = col + 1

    # is the symbol under the cursor a closing bracket?
    if col < len(line) and ( line[col] == ')' or line[col] == '>'):
      # if so, jump to the end of the line
      vim.command('let s:insertModeTabTmp="\<ESC>A"')
    else:
      vim.command('let s:insertModeTabTmp="\<TAB>"') 
  else:
    # line contains argument completion strings, perform a normal-mode tab
    vim.command('call feedkeys("\<ESC>\<TAB>")')
    vim.command('let s:insertModeTabTmp=""')
# vim: set ts=2 sts=2 sw=2 expandtab :
