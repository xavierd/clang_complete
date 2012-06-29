" clang_complete clang's include paths finder
" Author: leszekswirski

function! getopts#clang#getopts()
  let l:optfunc = 'echo | clang -v -E -x ' . getopts#cache#getlangname() . ' -'
  call getopts#cache#getopts('clang', l:optfunc)
endfunction

" vim: set ts=2 sts=2 sw=2 expandtab :
