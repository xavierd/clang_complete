"
" File: clang_complete.vim
" Author: Xavier Deguillard <deguilx@gmail.com>
"
" Description: Use of clang to complete in C/C++.
"
" Help: Use :help clang_complete
"

au FileType c,cpp,objc,objcpp call <SID>ClangCompleteInit()

let b:clang_parameters = ''
let b:clang_user_options = ''
let b:my_changedtick = 0

" Store plugin path, as this is available only when sourcing the file,
" not during a function call.
let s:plugin_path = escape(expand('<sfile>:p:h'), ' \')

function! s:ClangCompleteInit()
  let l:bufname = bufname("%")
  if l:bufname == ''
    return
  endif

  if !exists('g:clang_auto_select')
    let g:clang_auto_select = 0
  endif

  if !exists('g:clang_complete_auto')
    let g:clang_complete_auto = 1
  endif

  if !exists('g:clang_close_preview')
    let g:clang_close_preview = 0
  endif

  if !exists('g:clang_complete_copen')
    let g:clang_complete_copen = 0
  endif

  if !exists('g:clang_hl_errors')
    let g:clang_hl_errors = 1
  endif

  if !exists('g:clang_periodic_quickfix')
    let g:clang_periodic_quickfix = 0
  endif

  if !exists('g:clang_snippets')
    let g:clang_snippets = 0
  endif

  if !exists('g:clang_snippets_engine')
    let g:clang_snippets_engine = 'clang_complete'
  endif

  if !exists('g:clang_exec')
    let g:clang_exec = 'clang'
  endif

  if !exists('g:clang_user_options')
    let g:clang_user_options = ''
  endif

  if !exists('g:clang_conceal_snippets')
    let g:clang_conceal_snippets = has('conceal')
  elseif g:clang_conceal_snippets == 1 && !has('conceal')
    echoe 'clang_complete: conceal feature not available but requested'
  endif

  if !exists('g:clang_trailing_placeholder')
    let g:clang_trailing_placeholder = 0
  endif

  if !exists('g:clang_compilation_database')
    let g:clang_compilation_database = ''
  endif

  if !exists('g:clang_library_path')
    let g:clang_library_path = ''
  endif

  if !exists('g:clang_complete_macros')
    let g:clang_complete_macros = 0
  endif

  if !exists('g:clang_complete_patterns')
    let g:clang_complete_patterns = 0
  endif

  if !exists('g:clang_debug')
    let g:clang_debug = 0
  endif

  if !exists('g:clang_sort_algo')
    let g:clang_sort_algo = 'priority'
  endif

  if !exists('g:clang_auto_user_options')
    let g:clang_auto_user_options = 'path, .clang_complete'
  endif

  call LoadUserOptions()

  inoremap <expr> <buffer> <C-X><C-U> <SID>LaunchCompletion()
  inoremap <expr> <buffer> . <SID>CompleteDot()
  inoremap <expr> <buffer> > <SID>CompleteArrow()
  inoremap <expr> <buffer> : <SID>CompleteColon()
  inoremap <expr> <buffer> <CR> <SID>HandlePossibleSelectionEnter()

  if g:clang_snippets == 1
    call g:ClangSetSnippetEngine(g:clang_snippets_engine)
  endif

  " Force menuone. Without it, when there's only one completion result,
  " it can be confusing (not completing and no popup)
  if g:clang_auto_select != 2
    set completeopt-=menu
    set completeopt+=menuone
  endif

  " Disable every autocmd that could have been set.
  augroup ClangComplete
    autocmd!
  augroup end

  let b:should_overload = 0
  let b:my_changedtick = b:changedtick
  let b:clang_parameters = '-x c'

  if &filetype == 'objc'
    let b:clang_parameters = '-x objective-c'
  endif

  if &filetype == 'cpp' || &filetype == 'objcpp'
    let b:clang_parameters .= '++'
  endif

  if expand('%:e') =~ 'h.*'
    let b:clang_parameters .= '-header'
  endif

  let g:clang_complete_lib_flags = 0

  if g:clang_complete_macros == 1
    let b:clang_parameters .= ' -code-completion-macros'
    let g:clang_complete_lib_flags = 1
  endif

  if g:clang_complete_patterns == 1
    let b:clang_parameters .= ' -code-completion-patterns'
    let g:clang_complete_lib_flags += 2
  endif

  setlocal completefunc=ClangComplete
  setlocal omnifunc=ClangComplete

  if g:clang_periodic_quickfix == 1
    augroup ClangComplete
      au CursorHold,CursorHoldI <buffer> call <SID>DoPeriodicQuickFix()
    augroup end
  endif

  if !exists('g:clang_use_library') || g:clang_use_library == 1
    " Try to use libclang. On failure, we fall back to the clang executable.
    let l:initialized = s:initClangCompletePython(exists('g:clang_use_library'))
    let g:clang_use_library = l:initialized
  endif

  if g:clang_use_library != 1
    echoe 'clang_complete: Not using libclang is deprecated,'
    echoe 'You should switch to libclang now and report all the bugs.'

    if g:clang_compilation_database != ''
      echoe 'The use of the compile_commands.json file is only available'
      echoe 'when using libclang.'
    endif
  endif

endfunction

function! LoadUserOptions()
  let b:clang_user_options = ''

  let l:option_sources = split(g:clang_auto_user_options, ',')
  let l:remove_spaces_cmd = 'substitute(v:val, "\\s*\\(.*\\)\\s*", "\\1", "")'
  let l:option_sources = map(l:option_sources, l:remove_spaces_cmd)

  for l:source in l:option_sources
    if l:source == 'gcc' || l:source == 'clang'
      echo "'" . l:source . "' in clang_auto_user_options is deprecated."
      continue
    endif
    if l:source == 'path'
      call s:parsePathOption()
    elseif l:source == 'compile_commands.json'
      call s:findCompilationDatase(l:source)
    elseif l:source == '.clang_complete'
      call s:parseConfig()
    else
      let l:getopts = 'getopts#' . l:source . '#getopts'
      silent call eval(l:getopts . '()')
    endif
  endfor
endfunction

function! s:parseConfig()
  let l:local_conf = findfile('.clang_complete', getcwd() . ',.;')
  if l:local_conf == '' || !filereadable(l:local_conf)
    return
  endif

  let l:root = substitute(fnamemodify(l:local_conf, ':p:h'), '\', '/', 'g')

  let l:opts = readfile(l:local_conf)
  for l:opt in l:opts
    " Use forward slashes only
    let l:opt = substitute(l:opt, '\', '/', 'g')
    " Handling of absolute path
    if matchstr(l:opt, '\C-I\s*/') != ''
      let l:opt = substitute(l:opt, '\C-I\s*\(/\%(\w\|\\\s\)*\)',
            \ '-I' . '\1', 'g')
    elseif s:isWindows() && matchstr(l:opt, '\C-I\s*[a-zA-Z]:/') != ''
      let l:opt = substitute(l:opt, '\C-I\s*\([a-zA-Z:]/\%(\w\|\\\s\)*\)',
            \ '-I' . '\1', 'g')
    else
      let l:opt = substitute(l:opt, '\C-I\s*\(\%(\w\|\.\|/\|\\\s\)*\)',
            \ '-I' . l:root . '/\1', 'g')
    endif
    let b:clang_user_options .= ' ' . l:opt
  endfor
endfunction

function! s:findCompilationDatase(cdb)
  if g:clang_compilation_database == ''
    let l:local_conf = findfile(a:cdb, getcwd() . ',.;')
    if l:local_conf != '' && filereadable(l:local_conf)
      let g:clang_compilation_database = fnamemodify(l:local_conf, ":p:h")
    endif
  endif
endfunction

function! s:parsePathOption()
  let l:dirs = split(&path, ',')
  for l:dir in l:dirs
    if len(l:dir) == 0 || !isdirectory(l:dir)
      continue
    endif

    " Add only absolute paths
    if matchstr(l:dir, '\s*/') != ''
      let l:opt = '-I' . l:dir
      let b:clang_user_options .= ' ' . l:opt
    endif
  endfor
endfunction

function! s:initClangCompletePython(user_requested)
  if !has('python')
    if a:user_requested || g:clang_debug
      echoe 'clang_complete: No python support available.'
      echoe 'Cannot use clang library, using executable'
      echoe 'Compile vim with python support to use libclang'
    endif
    return 0
  endif

  " Only parse the python library once
  if !exists('s:libclang_loaded')
    python import sys

    exe 'python sys.path = ["' . s:plugin_path . '"] + sys.path'
    exe 'pyfile ' . fnameescape(s:plugin_path) . '/libclang.py'
    py vim.command('let l:res = ' + str(initClangComplete(vim.eval('g:clang_complete_lib_flags'), vim.eval('g:clang_compilation_database'), vim.eval('g:clang_library_path'), vim.eval('a:user_requested'))))
    if l:res == 0
      return 0
    endif
    let s:libclang_loaded = 1
  endif
  python WarmupCache()
  return 1
endfunction

function! s:GetKind(proto)
  if a:proto == ''
    return 't'
  endif
  let l:ret = match(a:proto, '^\[#')
  let l:params = match(a:proto, '(')
  if l:ret == -1 && l:params == -1
    return 't'
  endif
  if l:ret != -1 && l:params == -1
    return 'v'
  endif
  if l:params != -1
    return 'f'
  endif
  return 'm'
endfunction

function! s:CallClangBinaryForDiagnostics(tempfile)
  let l:escaped_tempfile = shellescape(a:tempfile)
  let l:buf = getline(1, '$')
  try
    call writefile(l:buf, a:tempfile)
  catch /^Vim\%((\a\+)\)\=:E482/
    return
  endtry

  let l:command = g:clang_exec . ' -fsyntax-only'
        \ . ' -fno-caret-diagnostics -fdiagnostics-print-source-range-info'
        \ . ' ' . l:escaped_tempfile
        \ . ' ' . b:clang_parameters . ' ' . b:clang_user_options . ' ' . g:clang_user_options

  let l:clang_output = split(system(s:escapeCommand(l:command)), "\n")
  call delete(a:tempfile)
  return l:clang_output
endfunction

function! s:CallClangForDiagnostics(tempfile)
  if g:clang_use_library == 1
    python updateCurrentDiagnostics()
  else
    return s:CallClangBinaryForDiagnostics(a:tempfile)
  endif
endfunction

function! s:DoPeriodicQuickFix()
  " Don't do any superfluous reparsing.
  if b:my_changedtick == b:changedtick
    return
  endif
  let b:my_changedtick = b:changedtick

  " Create tempfile name for clang/clang++ executable mode
  let b:my_changedtick = b:changedtick
  let l:tempfile = expand('%:p:h') . '/' . localtime() . expand('%:t')

  let l:clang_output = s:CallClangForDiagnostics(l:tempfile)

  call s:ClangQuickFix(l:clang_output, l:tempfile)
endfunction

function! s:ClangQuickFix(clang_output, tempfname)
  " Clear the bad spell, the user may have corrected them.
  syntax clear SpellBad
  syntax clear SpellLocal

  if g:clang_use_library == 0
    let l:list = s:ClangUpdateQuickFix(a:clang_output, a:tempfname)
  else
    python vim.command('let l:list = ' + str(getCurrentQuickFixList()))
    python highlightCurrentDiagnostics()
  endif

  if g:clang_complete_copen == 1
    " We should get back to the original buffer
    let l:bufnr = bufnr('%')

    " Workaround:
    " http://vim.1045645.n5.nabble.com/setqflist-inconsistency-td1211423.html
    if l:list == []
      cclose
    else
      copen
    endif

    let l:winbufnr = bufwinnr(l:bufnr)
    exe l:winbufnr . 'wincmd w'
  endif
  call setqflist(l:list)
  silent doautocmd QuickFixCmdPost make
endfunction

function! s:ClangUpdateQuickFix(clang_output, tempfname)
  let l:list = []
  for l:line in a:clang_output
    let l:erridx = match(l:line, '\%(error\|warning\|note\): ')
    if l:erridx == -1
      " Error are always at the beginning.
      if l:line[:11] == 'COMPLETION: ' || l:line[:9] == 'OVERLOAD: '
        break
      endif
      continue
    endif
    let l:pattern = '^\(.*\):\(\d*\):\(\d*\):\(\%({\d\+:\d\+-\d\+:\d\+}\)*\)'
    let l:tmp = matchstr(l:line, l:pattern)
    let l:fname = substitute(l:tmp, l:pattern, '\1', '')
    if l:fname == a:tempfname
      let l:fname = '%'
    endif
    let l:bufnr = bufnr(l:fname, 1)
    let l:lnum = substitute(l:tmp, l:pattern, '\2', '')
    let l:col = substitute(l:tmp, l:pattern, '\3', '')
    let l:errors = substitute(l:tmp, l:pattern, '\4', '')
    if l:line[l:erridx] == 'e'
      let l:text = l:line[l:erridx + 7:]
      let l:type = 'E'
      let l:hlgroup = ' SpellBad '
    elseif l:line[l:erridx] == 'w'
      let l:text = l:line[l:erridx + 9:]
      let l:type = 'W'
      let l:hlgroup = ' SpellLocal '
    else
      let l:text = l:line[l:erridx + 6:]
      let l:type = 'I'
      let l:hlgroup = ' '
    endif
    let l:item = {
          \ 'bufnr': l:bufnr,
          \ 'lnum': l:lnum,
          \ 'col': l:col,
          \ 'text': l:text,
          \ 'type': l:type }
    let l:list = add(l:list, l:item)

    if g:clang_hl_errors == 0 || l:fname != '%' || l:type == 'I'
      continue
    endif

    " Highlighting the ^
    let l:pat = '/\%' . l:lnum . 'l' . '\%' . l:col . 'c./'
    exe 'syntax match' . l:hlgroup . l:pat

    if l:errors == ''
      continue
    endif
    let l:ranges = split(l:errors, '}')
    for l:range in l:ranges
      " Doing precise error and warning handling.
      " The highlight will be the same as clang's carets.
      let l:pattern = '{\%(\d\+\):\(\d\+\)-\%(\d\+\):\(\d\+\)'
      let l:tmp = matchstr(l:range, l:pattern)
      let l:startcol = substitute(l:tmp, l:pattern, '\1', '')
      let l:endcol = substitute(l:tmp, l:pattern, '\2', '')
      " Highlighting the ~~~~
      let l:pat = '/\%' . l:lnum . 'l'
            \ . '\%' . l:startcol . 'c'
            \ . '.*'
            \ . '\%' . l:endcol . 'c/'
      exe 'syntax match' . l:hlgroup . l:pat
    endfor
  endfor
  return l:list
endfunction

function! s:DemangleProto(prototype)
  let l:proto = substitute(a:prototype, '\[#[^#]*#\]', '', 'g')
  let l:proto = substitute(l:proto, '{#.*#}', '', 'g')
  return l:proto
endfunction

let b:col = 0

function! s:ClangCompleteBinary(base)
  let l:buf = getline(1, '$')
  let l:tempfile = expand('%:p:h') . '/' . localtime() . expand('%:t')
  try
    call writefile(l:buf, l:tempfile)
  catch /^Vim\%((\a\+)\)\=:E482/
    return {}
  endtry
  let l:escaped_tempfile = shellescape(l:tempfile)

  let l:command = g:clang_exec . ' -fsyntax-only'
        \ . ' -fno-caret-diagnostics -fdiagnostics-print-source-range-info'
        \ . ' -Xclang -code-completion-at=' . l:escaped_tempfile . ':'
        \ . line('.') . ':' . b:col . ' ' . l:escaped_tempfile
        \ . ' ' . b:clang_parameters . ' ' . b:clang_user_options . ' ' . g:clang_user_options

  let l:clang_output = split(system(s:escapeCommand(l:command)), "\n")
  call delete(l:tempfile)

  call s:ClangQuickFix(l:clang_output, l:tempfile)
  if v:shell_error
    return []
  endif
  if l:clang_output == []
    return []
  endif

  let l:filter_str = "v:val =~ '^COMPLETION: " . a:base . "\\|^OVERLOAD: '"
  call filter(l:clang_output, l:filter_str)

  let l:res = []
  for l:line in l:clang_output

    if l:line[:11] == 'COMPLETION: ' && b:should_overload != 1

      let l:value = l:line[12:]

      let l:colonidx = stridx(l:value, ' : ')
      if l:colonidx == -1
        let l:wabbr = s:DemangleProto(l:value)
        let l:word = l:value
        let l:proto = l:value
      else
        let l:word = l:value[:l:colonidx - 1]
        " WTF is that?
        if l:word =~ '(Hidden)'
          let l:word = l:word[:-10]
        endif
        let l:wabbr = l:word
        let l:proto = l:value[l:colonidx + 3:]
      endif

      let l:kind = s:GetKind(l:proto)
      if l:kind == 't' && b:clang_complete_type == 0
        continue
      endif

      let l:word = l:wabbr
      let l:menu = substitute(l:proto, '\[#\([^#]*\)#\]', '\1 ', 'g')
      let l:menu = substitute(l:menu, '<#\([^#]*\)#>', '\1', 'g')
      let l:menu = substitute(l:menu, '{#[^#]*#}', '', 'g')

      let l:proto = s:DemangleProto(l:proto)

    elseif l:line[:9] == 'OVERLOAD: ' && b:should_overload == 1

      let l:value = l:line[10:]
      if match(l:value, '<#') == -1
        continue
      endif
      let l:word = substitute(l:value, '.*<#', '<#', 'g')
      let l:word = substitute(l:word, '#>.*', '#>', 'g')
      let l:wabbr = substitute(l:word, '<#\([^#]*\)#>', '\1', 'g')
      let l:menu = l:wabbr
      let l:proto = s:DemangleProto(l:value)
      let l:kind = ''
    else
      continue
    endif

    let l:args_pos = []
    if g:clang_snippets == 1
      let l:startidx = match(l:proto, '<#')
      while l:startidx != -1
        let l:proto = substitute(l:proto, '<#', '', '')
        let l:endidx = match(l:proto, '#>')
        let l:proto = substitute(l:proto, '#>', '', '')
        let l:args_pos += [[ l:startidx, l:endidx ]]
        let l:startidx = match(l:proto, '<#')
      endwhile
    endif

    let l:item = {
          \ 'word': l:word,
          \ 'abbr': l:wabbr,
          \ 'menu': l:menu,
          \ 'info': l:proto,
          \ 'dup': 1,
          \ 'kind': l:kind,
          \ 'args_pos': l:args_pos }

    call add(l:res, l:item)
  endfor
  return l:res
endfunction

function! s:escapeCommand(command)
    return s:isWindows() ? a:command : escape(a:command, '()')
endfunction

function! s:isWindows()
  " Check for win32 is enough since it's true on win64
  return has('win32')
endfunction

function! ClangComplete(findstart, base)
  if a:findstart
    let l:line = getline('.')
    let l:start = col('.') - 1
    let b:clang_complete_type = 1
    let l:wsstart = l:start
    if l:line[l:wsstart - 1] =~ '\s'
      while l:wsstart > 0 && l:line[l:wsstart - 1] =~ '\s'
        let l:wsstart -= 1
      endwhile
    endif
    if l:line[l:wsstart - 1] =~ '[(,]'
      let b:should_overload = 1
      let b:col = l:wsstart + 1
      return l:wsstart
    endif
    let b:should_overload = 0
    while l:start > 0 && l:line[l:start - 1] =~ '\i'
      let l:start -= 1
    endwhile
    if l:line[l:start - 2:] =~ '->' || l:line[l:start - 1] == '.'
      let b:clang_complete_type = 0
    endif
    let b:col = l:start + 1
    return l:start
  else
    if g:clang_debug == 1
      let l:time_start = reltime()
    endif

    if g:clang_snippets == 1
      call b:ResetSnip()
    endif

    if g:clang_use_library == 1
      python completions, timer = getCurrentCompletions(vim.eval('a:base'))
      python vim.command('let l:res = ' + completions)
      python timer.registerEvent("Load into vimscript")
    else
      let l:res = s:ClangCompleteBinary(a:base)
    endif

    for item in l:res
      if g:clang_snippets == 1
        let item['word'] = b:AddSnip(item['info'], item['args_pos'])
      else
        let item['word'] = item['abbr']
      endif
    endfor

    inoremap <expr> <buffer> <C-Y> <SID>HandlePossibleSelectionCtrlY()
    augroup ClangComplete
      au CursorMovedI <buffer> call <SID>TriggerSnippet()
    augroup end
    let b:snippet_chosen = 0

  if g:clang_use_library == 1
    python timer.registerEvent("vimscript + snippets")
    python timer.finish()
  endif

  if g:clang_debug == 1
    echom 'clang_complete: completion time (' . (g:clang_use_library == 1 ? 'library' : 'binary') . ') '. split(reltimestr(reltime(l:time_start)))[0]
  endif
  return l:res
endif
endfunction

function! s:HandlePossibleSelectionEnter()
  if pumvisible()
    let b:snippet_chosen = 1
    return "\<C-Y>"
  end
  return "\<CR>"
endfunction

function! s:HandlePossibleSelectionCtrlY()
  if pumvisible()
    let b:snippet_chosen = 1
  end
  return "\<C-Y>"
endfunction

function! s:TriggerSnippet()
  " Dont bother doing anything until we're sure the user exited the menu
  if !b:snippet_chosen
    return
  endif

  if g:clang_snippets == 1
    " Stop monitoring as we'll trigger a snippet
    silent! iunmap <buffer> <C-Y>
    augroup ClangComplete
      au! CursorMovedI <buffer>
    augroup end

    " Trigger the snippet
    call b:TriggerSnip()
  endif

  if g:clang_close_preview
    pclose
  endif
endfunction

function! s:ShouldComplete()
  if (getline('.') =~ '#\s*\(include\|import\)')
    return 0
  else
    if col('.') == 1
      return 1
    endif
    for l:id in synstack(line('.'), col('.') - 1)
      if match(synIDattr(l:id, 'name'), '\CComment\|String\|Number')
            \ != -1
        return 0
      endif
    endfor
    return 1
  endif
endfunction

function! s:LaunchCompletion()
  let l:result = ""
  if s:ShouldComplete()
    let l:result = "\<C-X>\<C-U>"
    if g:clang_auto_select != 2
      let l:result .= "\<C-P>"
    endif
    if g:clang_auto_select == 1
      let l:result .= "\<C-R>=(pumvisible() ? \"\\<Down>\" : '')\<CR>"
    endif
  endif
  return l:result
endfunction

function! s:CompleteDot()
  if g:clang_complete_auto == 1
    return '.' . s:LaunchCompletion()
  endif
  return '.'
endfunction

function! s:CompleteArrow()
  if g:clang_complete_auto != 1 || getline('.')[col('.') - 2] != '-'
    return '>'
  endif
  return '>' . s:LaunchCompletion()
endfunction

function! s:CompleteColon()
  if g:clang_complete_auto != 1 || getline('.')[col('.') - 2] != ':'
    return ':'
  endif
  return ':' . s:LaunchCompletion()
endfunction

" May be used in a mapping to update the quickfix window.
function! g:ClangUpdateQuickFix()
  call s:DoPeriodicQuickFix()
  return ''
endfunction

function! g:ClangSetSnippetEngine(engine_name)
  try
    call eval('snippets#' . a:engine_name . '#init()')
    let b:AddSnip = function('snippets#' . a:engine_name . '#add_snippet')
    let b:ResetSnip = function('snippets#' . a:engine_name . '#reset')
    let b:TriggerSnip = function('snippets#' . a:engine_name . '#trigger')
  catch /^Vim\%((\a\+)\)\=:E117/
    echoe 'Snippets engine ' . a:engine_name . ' not found.'
    let g:clang_snippets = 0
  endtry
endfunction

" vim: set ts=2 sts=2 sw=2 expandtab :
