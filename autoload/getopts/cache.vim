" clang_complete include paths caching helper
" Author: xaizek, leszekswirski

let s:scr = expand('<sfile>')
let s:cache_path = fnamemodify(s:scr, ':p:h')

function! getopts#cache#getcachedopts(ext, optfunc)
  let s:cache = s:cache_path . '/' . &filetype . '.' . a:ext . '.cache'
  if !s:CacheExists()
    call s:CreateCache(a:optfunc)
  endif
  call s:ReadCache()
  call s:AppendOptions()
endfunction

function! ClearIncludeCaches()
  let l:cache_files = split(globpath(s:cache_path, '*.cache', 1), "\n")
  for l:cache_file in l:cache_files
    call delete(l:cache_file)
  endfor
  unlet! s:opts
endfunction

function! getopts#cache#getlangname()
  if &filetype == 'c'
    let l:lang_name = 'c'
  elseif &filetype == 'cpp'
    let l:lang_name = 'c++'
  elseif &filetype == 'objc'
    let l:lang_name = 'objective-c'
  elseif &filetype == 'objcpp'
    let l:lang_name = 'objective-c++'
  elseif
    let l:lang_name = 'none'
  endif
  return l:lang_name
endfunction

function! s:CacheExists()
  if !filereadable(s:cache)
    return 0
  endif

  let l:lines = readfile(s:cache)

  for l:line in l:lines
    let l:line = substitute(l:line, '^\s\+', '', '')
    if l:line =~ '^-I' && !isdirectory(l:line[2:])
      return 0
    endif
  endfor

  return len(l:lines) > 0
endfunction

function! s:CreateCache(optfunc)
  let s:opts = s:GetOptions(a:optfunc)
  call writefile(s:opts, s:cache)
endfunction

function! s:GetOptions(optfunc)
  let l:out = split(system(a:optfunc), "\n")

  while !empty(l:out) && l:out[0] !~ '^#include <...>'
    let l:out = l:out[1:]
  endwhile
  if !empty(l:out)
    let l:out = l:out[1:]
  endif

  let l:result = []
  while !empty(l:out) && l:out[0] !~ '^End of search list.$'
    let l:inc_path = substitute(l:out[0], '^\s*', '', '')
    let l:inc_path = fnamemodify(l:inc_path, ':p')
    let l:inc_path = substitute(l:inc_path, '\', '/', 'g')

    if isdirectory(l:inc_path)
      call add(l:result, '-I' . l:inc_path)
    endif

    let l:out = l:out[1:]
  endwhile
  return l:result
endfunction

function! s:ReadCache()
  let s:opts = readfile(s:cache)
endfunction

function! s:AppendOptions()
  let b:clang_user_options .= ' ' . join(s:opts, ' ')
endfunction
