let b:snipmate_snippets = {}

function! snippets#snipmate#init()
  call snippets#snipmate#reset()
endfunction

function! snippets#snipmate#add_snippet(word, proto)
  " Clean up prototype (remove return type and const)
  let l:word = substitute(a:proto, '\v^.*(\V' . a:word . '\v.{-})( *const *)?$', '\1', '')

  " Figure out trigger
  let l:trigger = substitute(a:word, '<#\([^#]*\)#>', '\1', 'g')

  " Create snipmate's snippet
  let l:snippet = s:CreateSnipmateSnippet(l:trigger, a:proto)
  call MakeSnip(&filetype, l:trigger, l:snippet, a:proto)

  " Store which overload we are going to complete
  if !has_key(b:snipmate_snippets, l:trigger)
    let b:snipmate_snippets[l:trigger] = []
  endif
  let b:snipmate_snippets[l:trigger] += [l:word]
endfunction

function! snippets#snipmate#trigger()
  " Check if the user really did chose an entry for the menu or just typed someting inexistant
  let l:col  = col('.')
  let l:line = getline('.')
  let l:word = strpart(l:line, b:col - 1, l:col - b:col)
  let l:trigger = matchstr(l:word, '\v^[^(<]+')
  if !has_key(b:snipmate_snippets, l:trigger)
    return
  endif

  " Rewrite line with snipmate's snippet trigger
  let l:corrected_line = strpart(l:line, 0, b:col + len(l:trigger) - 1) . strpart(l:line, l:col - 1)
  call setline('.', l:corrected_line)

  " Move cursor to where we want (there's probably a simpler way than this)
  call feedkeys("\<Esc>", 't')
  call cursor(0, b:col + len(l:trigger))
  call feedkeys('a', 't')

  " If we are already in a snipmate snippet, well not much we can do until snipmate supports nested snippets
  if exists('g:snipPos')
    return
  endif

  " Trigger snipmate
  call feedkeys("\<Tab>", 't')
  if len(b:snipmate_snippets[l:trigger]) > 1
    let l:index = index(b:snipmate_snippets[l:trigger], l:word) + 1
    if l:index == -1
      echoe 'clang_complete snipmate error'
    endif
    sleep 2
    call feedkeys(l:index . "\<CR>", 't')
  endif
endfunction

function! snippets#snipmate#reset()
  " Quick & Easy way to prevent snippets to be added twice
  " Ideally we should modify snipmate to be smarter about this
  call ReloadSnippets(&filetype)
  let b:snipmate_snippets = {}
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
