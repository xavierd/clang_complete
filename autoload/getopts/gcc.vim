" clang_complete gcc's include paths finder
" Author: xaizek

let s:scr = expand('<sfile>')
let s:cache_path = fnamemodify(s:scr, ':p:h')

function! getopts#gcc#getopts()
  call s:DetemineFileType()
  if !s:CacheExists()
    call s:CreateCache()
  endif
  call s:ReadCache()
  call s:AppendOptions()
endfunction

function! s:DetemineFileType()
  let b:cache = s:cache_path . '/' . &filetype . '.cache'
  if &filetype == 'c'
    let b:lang_name = 'c'
  elseif &filetype == 'cpp'
    let b:lang_name = 'c++'
  elseif &filetype == 'objc'
    let b:lang_name = 'objective-c'
  elseif &filetype == 'objcpp'
    let b:lang_name = 'objective-c++'
  elseif
    let b:lang_name = 'none'
  endif
endfunction

function! s:CacheExists()
  if !filereadable(b:cache)
    return 0
  endif

  let l:lines = readfile(b:cache)
  return len(l:lines) > 0
endfunction

function! s:CreateCache()
  let b:gcc_opts = s:GetGCCOptions()
  call writefile([b:gcc_opts], b:cache)
endfunction

function! s:GetGCCOptions()
  let l:out = split(system('echo | cpp -v -x ' . b:lang_name), "\n")

  while !empty(l:out) && l:out[0] !~ '^#include <...>'
    let l:out = l:out[1:]
  endwhile
  if !empty(l:out)
    let l:out = l:out[1:]
  endif

  let l:result = ''
  while !empty(l:out) && l:out[0] !~ '^End of search list.$'
    let l:inc_path = substitute(l:out[0], '^\s*', '', '')
    let l:inc_path = fnamemodify(l:inc_path, ':p')
    let l:inc_path = substitute(l:inc_path, '\', '/', 'g')
    let l:result .= ' -I' . l:inc_path

    let l:out = l:out[1:]
  endwhile
  return l:result
endfunction

function! s:ReadCache()
  let b:gcc_opts = join(readfile(b:cache), ' ')
endfunction

function! s:AppendOptions()
  let b:clang_user_options .= ' ' . b:gcc_opts
endfunction

function! ClearGCCIncludeCaches()
  let l:cache_files = split(globpath(s:cache_path, '*.cache', 1), "\n")
  for l:cache_file in l:cache_files
    call delete(l:cache_file)
  endfor
  unlet! b:gcc_opts
endfunction

" vim: set ts=2 sts=2 sw=2 expandtab :
