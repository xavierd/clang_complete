
" Prepare the snippet engine
function! snippets#ultisnips#init()
endfunction

" Add a snippet to be triggered
function! snippets#ultisnips#add_snippet(word, proto)
  " Clean up prototype (remove return type and const)
  let l:word = substitute(a:proto, '\v^.*(\V' . a:word . '\v.{-})( *const *)?$', '\1', '')

  " Figure out trigger
  let l:trigger = substitute(a:word, '<#\([^#]*\)#>', '\1', 'g')

  " Create ultisnips's snippet
  let l:snippet = s:CreateUltiSnipsSnippet(l:trigger, a:proto)
  call UltiSnips_AddSnippet(a:word, l:snippet, a:proto, '!i', &filetype)
endfunction

" Trigger the snippet
function! snippets#ultisnips#trigger()
  call UltiSnips_ExpandSnippet()
endfunction

" Remove all snippets
function! snippets#ultisnips#reset()
  UltiSnipsReset
endfunction


" ---------------- Helpers ----------------

function! s:CreateUltiSnipsSnippet(trigger, proto)
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
