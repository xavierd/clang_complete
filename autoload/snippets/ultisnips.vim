" clang_complete ultisnips's snippet generator
" Author: Philippe Vaucher

function! snippets#ultisnips#init()
  UltiSnipsAddFiletypes &filetype.clang_complete
  call snippets#ultisnips#reset()
endfunction

" fullname = strcat(char *dest, const char *src)
" args_pos = [ [8, 17], [20, 34] ]
function! snippets#ultisnips#add_snippet(fullname, args_pos)
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

  call UltiSnips_AddSnippet(l:snippet_id, l:snip, a:fullname, 'i', "clang_complete")

  return l:snippet_id
endfunction

function! snippets#ultisnips#trigger()
  call UltiSnips_ExpandSnippet()
endfunction

function! snippets#ultisnips#reset()
  python UltiSnips_Manager.clear_snippets(ft="clang_complete")
endfunction

" vim: set ts=2 sts=2 sw=2 expandtab :
