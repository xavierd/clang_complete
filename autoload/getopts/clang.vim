" clang_complete clang's include paths finder
" Author: leszekswirski

function! getopts#clang#getopts()
  let l:all_options = g:clang_user_options . ' ' . b:clang_user_options
  let l:stdlib = matchstr(l:all_options, '\C\M^\(\.\*\s\)\?\zs-stdlib=\S\+')

  let l:lang_name = getopts#cache#getlangname()

  let l:optfunc = 'echo | clang -v -E ' . l:stdlib . ' -x ' . l:lang_name . ' -'
  let l:prefix = empty(l:stdlib) ? '' : (matchstr(l:stdlib, '\M=\zs\.\*') . '.')
  call getopts#cache#getcachedopts(l:prefix . 'clang', l:optfunc)
endfunction

" vim: set ts=2 sts=2 sw=2 expandtab :
