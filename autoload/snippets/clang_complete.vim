" clang_complete clang_complete's snippet generator
" Author: Xavier Deguillard, Philippe Vaucher

function! snippets#clang_complete#init()
  noremap <expr> <silent> <buffer> <tab> UpdateSnips()
  snoremap <expr> <silent> <buffer> <tab> UpdateSnips()
  if g:clang_conceal_snippets == 1
    augroup ClangCompleteSnippets
      " the check for b:clang_user_options is to do not define anything on
      " buffers that are not supported by clang_complete
      autocmd! Syntax *
             \ if exists('b:clang_user_options') |
             \   call <SID>UpdateConcealSyntax() |
             \ endif
    augroup END
    call s:UpdateConcealSyntax()
  endif
endfunction

function! s:UpdateConcealSyntax()
  syntax match Conceal /<#/ conceal
  syntax match Conceal /#>/ conceal
endfunction

" fullname = strcat(char *dest, const char *src)
" args_pos = [ [8, 17], [20, 34] ]
function! snippets#clang_complete#add_snippet(fullname, args_pos)
  let l:res = ''
  let l:prev_idx = 0
  for elt in a:args_pos
    let l:res .= a:fullname[l:prev_idx : elt[0] - 1] . '<#' . a:fullname[elt[0] : elt[1] - 1] . '#>'
    let l:prev_idx = elt[1]
  endfor

  let l:res .= a:fullname[l:prev_idx : ]
  if g:clang_trailing_placeholder == 1 && len(a:args_pos) > 0
    let l:res .= '<##>'
  endif

  return l:res
endfunction

function! snippets#clang_complete#trigger()
  call s:BeginSnips()
endfunction

function! snippets#clang_complete#reset()
endfunction


" ---------------- Helpers ----------------

function! UpdateSnips()
  let l:line = getline('.')
  let l:pattern = '<#[^#]*#>'
  if match(l:line, l:pattern) == -1
    return "\<c-i>"
  endif

  let l:commands = ""
  if mode() != 'n'
      let l:commands .= "\<esc>"
  endif

  let l:commands .= ":call MoveToCCSnippetBegin()\<CR>"
  let l:commands .= "m'"
  let l:commands .= ":call MoveToCCSnippetEnd()\<CR>"

  if &selection == "exclusive"
    let l:commands .= "ll"
  else
    let l:commands .= "l"
  endif

  let l:commands .= "v`'o\<C-G>"

  return l:commands
endfunction

function! MoveToCCSnippetBegin()
  let l:pattern = '<#'
  let l:line = getline('.')
  let l:startpos = col('.') + 1
  let l:ind = match(l:line, l:pattern, l:startpos)
  if l:ind == -1
    let l:ind = match(l:line, l:pattern, 0)
  endif
  call cursor(line('.'), l:ind + 1)
endfunction

function! MoveToCCSnippetEnd()
  let l:line = getline('.')
  let l:pattern = '#>'
  let l:startpos = col('.') + 1

  call cursor(line('.'), match(l:line, l:pattern, l:startpos) + 1)
endfunction

function! s:BeginSnips()
  if pumvisible() != 0
    return
  endif

  " Do we need to launch UpdateSnippets()?
  let l:line = getline('.')
  let l:pattern = '<#[^#]*#>'
  if match(l:line, l:pattern) == -1
    return
  endif
  call feedkeys("\<esc>^\<tab>")
endfunction

" vim: set ts=2 sts=2 sw=2 expandtab :
