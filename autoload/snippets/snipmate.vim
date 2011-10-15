" clang_complete snipmate's snippet generator
" Author: Philippe Vaucher

function! snippets#snipmate#init()
  call snippets#snipmate#reset()
endfunction

" fullname = strcat(char *dest, const char *src)
" args_pos = [ [8, 17], [20, 34] ]
function! snippets#snipmate#add_snippet(fullname, args_pos)
  " If we are already in a snipmate snippet, well not much we can do until snipmate supports nested snippets
  if exists('g:snipPos')
    return a:fullname
  endif

  let l:snip = ''
  let l:prev_idx = 0
  let l:snip_idx = 1
  for elt in a:args_pos
    let l:snip .= a:fullname[l:prev_idx : elt[0] - 1] . '${' . l:snip_idx . ':' . a:fullname[elt[0] : elt[1] - 1] . '}'
    let l:snip_idx += 1
    let l:prev_idx = elt[1]
  endfor

  let l:snip .= a:fullname[l:prev_idx : ] . '${' . l:snip_idx . '}'

  let l:snippet_id = substitute(a:fullname, ' ', '_', 'g')

  call MakeSnip(&filetype, l:snippet_id, l:snip)

  return l:snippet_id
endfunction

function! snippets#snipmate#trigger()
  " If we are already in a snipmate snippet, well not much we can do until snipmate supports nested snippets
  if exists('g:snipPos')
    return
  endif

  " Trigger snipmate
  call feedkeys("\<Tab>", 't')
endfunction

function! snippets#snipmate#reset()
  " Quick & Easy way to prevent snippets to be added twice
  " Ideally we should modify snipmate to be smarter about this
  call ReloadSnippets(&filetype)
endfunction

" vim: set ts=2 sts=2 sw=2 expandtab :
