" clang_complete clang_complete's snippet generator
" Author: Xavier Deguillard, Philippe Vaucher

function! snippets#clang_complete#init()
  noremap <expr> <buffer> <tab> UpdateSnips()
  snoremap <expr> <buffer> <tab> UpdateSnips()
  syntax match Conceal /<#/ conceal
  syntax match Conceal /#>/ conceal
endfunction

" We want to generate a format like [#std::basic_string<char> &#]append(<#const std::basic_string<char> &__str#>, <#size_type __pos#>, <#size_type __n#>)
function! snippets#clang_complete#add_snippet(keyword, proto)
  let l:snippet_id = substitute(a:proto, '\v(^.{-})' . a:keyword . '>', a:keyword , '')
  let l:snippet_id = substitute(l:snippet_id, '<', '<<#', 'g')
  let l:snippet_id = substitute(l:snippet_id, '>', '#>>', 'g')
  let l:snippet_id = substitute(l:snippet_id, ',', '#>, <#', 'g')

  " A function with no arguments shouldn't have snippets for the argument list.
  if match(l:snippet_id, '()') != -1
    return l:snippet_id
  endif
  let l:snippet_id = substitute(l:snippet_id, '(', '(<#', 'g')
  let l:snippet_id = substitute(l:snippet_id, ')', '#>)', 'g')
  return l:snippet_id
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
  let l:linenb = line('.')
  if &selection == "exclusive"
    return "\<esc>/\\%" . l:linenb . "l<#\<CR>v/#>\<CR>ll\<C-G>"
  else
    return "\<esc>/\\%" . l:linenb . "l<#\<CR>v/#>\<CR>l\<C-G>"
  endif
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
