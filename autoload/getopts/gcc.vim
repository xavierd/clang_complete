" clang_complete gcc's include paths finder
" Author: leszekswirski

function! getopts#gcc#getopts()
  let l:optfunc = 'echo | gcc -v -E -x ' . getopts#cache#getlangname() . ' -'
  call getopts#cache#getopts('gcc', l:optfunc)
endfunction

" vim: set ts=2 sts=2 sw=2 expandtab :
