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
    return a:keyword
  endif

  " Construct a snippet id
  let l:snippet_id = substitute(a:proto, '\v^.*(\V' . a:keyword . '\v.{-})( *const *)?$', '\1', '')
  let l:snippet_id = substitute(l:snippet_id, ' ', '_', 'g')

  " Create the snippet
  let l:snippet = s:CreateSnipmateSnippet(a:keyword, a:proto)
  call MakeSnip(&filetype, l:snippet_id, l:snippet, a:proto)

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


" ---------------- Helpers ----------------

function! s:CreateSnipmateSnippet(trigger, proto)
  " Try to parse parameters
  let l:matches = matchlist(a:proto, '\v^.*\V' . a:trigger . '\v([(<])(.*)([)>])')

  " Check if it's a type without template params
  if empty(l:matches)
    " Clean up prototype (remove return type and const)
    let l:proto = substitute(a:proto, '\v^.*(\V' . a:trigger . '\v.{-})( *const *)?$', '\1', '')
    return l:proto . ' ${1:obj};${2}'
  endif

  " Get parameters
  let l:delim_start = l:matches[1]
  let l:params = split(l:matches[2], '\v\s*,\s*')
  let l:delim_end = l:matches[3]

  " Construct snippet
  let l:tmp = 1
  let l:snippet = a:trigger . l:delim_start
  for param in l:params
    let l:snippet .= '${' . l:tmp . ':' . param . '}'
    if l:tmp != len(l:params)
      let l:snippet .= ', '
    endif
    let l:tmp += 1
  endfor
  let l:snippet .= l:delim_end
  if l:delim_start == '('
    " Function
    let l:snippet .= '${' . l:tmp . ':;}${' . (l:tmp+1) . '}'
  else
    " Template
    let l:snippet .= ' ${' . l:tmp . ':obj};${' . (l:tmp+1) . '}'
  endif

  return l:snippet
endfunction
