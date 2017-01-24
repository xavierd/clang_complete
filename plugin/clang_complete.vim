"
" File: clang_complete.vim
" Author: Xavier Deguillard <deguilx@gmail.com>
"
" Description: Use of clang to complete in C/C++.
"
" Help: Use :help clang_complete
"

if exists('g:clang_complete_loaded')
  finish
endif
let g:clang_complete_loaded = 1

au FileType c,cpp,objc,objcpp call <SID>ClangCompleteInit()
au FileType c.*,cpp.*,objc.*,objcpp.* call <SID>ClangCompleteInit()

let b:clang_parameters = ''
let b:clang_user_options = ''
let b:my_changedtick = 0

" Store plugin path, as this is available only when sourcing the file,
" not during a function call.
let s:plugin_path = escape(expand('<sfile>:p:h'), '\')

" Older versions of Vim can't check if a map was made with <expr>
let s:use_maparg = v:version > 703 || (v:version == 703 && has('patch32'))

if has('python')
  let s:py_cmd = 'python'
  let s:pyfile_cmd = 'pyfile'
elseif has('python3')
  let s:py_cmd = 'python3'
  let s:pyfile_cmd = 'py3file'
endif

function! s:ClangCompleteInit()
  let l:bufname = bufname("%")
  if l:bufname == ''
    return
  endif

  if exists('g:clang_use_library') && g:clang_use_library == 0
    echoe "clang_complete: You can't use clang binary anymore."
    echoe 'For more information see g:clang_use_library help.'
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

  if !exists('g:clang_snippets') || g:clang_snippets == 0
    let g:clang_snippets_engine = 'dummy'
  endif

  if !exists('g:clang_snippets_engine')
    let g:clang_snippets_engine = 'clang_complete'
  endif

  if !exists('g:clang_user_options')
    let g:clang_user_options = ''
  endif

  if !exists('g:clang_conceal_snippets')
    let g:clang_conceal_snippets = has('conceal')
  elseif g:clang_conceal_snippets == 1 && !has('conceal')
    echoe 'clang_complete: conceal feature not available but requested'
  endif

  if !exists('g:clang_complete_optional_args_in_snippets')
    let g:clang_complete_optional_args_in_snippets = 0
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
    let g:clang_auto_user_options = '.clang_complete, path'
  endif

  if !exists('g:clang_jumpto_declaration_key')
    let g:clang_jumpto_declaration_key = '<C-]>'
  endif

  if !exists('g:clang_jumpto_declaration_in_preview_key')
    let g:clang_jumpto_declaration_in_preview_key = '<C-W>]'
  endif

  if !exists('g:clang_jumpto_back_key')
    let g:clang_jumpto_back_key = '<C-T>'
  endif

  if !exists('g:clang_make_default_keymappings')
    let g:clang_make_default_keymappings = 1
  endif

  if !exists('g:clang_restore_cr_imap')
    let g:clang_restore_cr_imap = 'iunmap <buffer> <CR>'
  endif

  if !exists('g:clang_omnicppcomplete_compliance')
    let g:clang_omnicppcomplete_compliance = 0
  endif

  if g:clang_omnicppcomplete_compliance == 1
    let g:clang_complete_auto = 0
    let g:clang_make_default_keymappings = 0
  endif

  call LoadUserOptions()

  let b:my_changedtick = b:changedtick
  let b:clang_parameters = '-x c'

  if &filetype =~ 'objc'
    let b:clang_parameters = '-x objective-c'
  endif

  if &filetype == 'cpp' || &filetype == 'objcpp' || &filetype =~ 'cpp.*' || &filetype =~ 'objcpp.*'
    let b:clang_parameters .= '++'
  endif

  if expand('%:e') =~ 'h.*'
    let b:clang_parameters .= '-header'
  endif

  let g:clang_complete_lib_flags = 0

  if g:clang_complete_macros == 1
    let g:clang_complete_lib_flags = 1
  endif

  if g:clang_complete_patterns == 1
    let g:clang_complete_lib_flags += 2
  endif

  if s:initClangCompletePython() != 1
    return
  endif

  execute s:py_cmd 'snippetsInit()'

  if g:clang_make_default_keymappings == 1
    inoremap <expr> <buffer> <C-X><C-U> <SID>LaunchCompletion()
    inoremap <expr> <buffer> . <SID>CompleteDot()
    inoremap <expr> <buffer> > <SID>CompleteArrow()
    inoremap <expr> <buffer> : <SID>CompleteColon()
    execute "nnoremap <buffer> <silent> " . g:clang_jumpto_declaration_key . " :call <SID>GotoDeclaration(0)<CR><Esc>"
    execute "nnoremap <buffer> <silent> " . g:clang_jumpto_declaration_in_preview_key . " :call <SID>GotoDeclaration(1)<CR><Esc>"
    execute "nnoremap <buffer> <silent> " . g:clang_jumpto_back_key . " <C-O>"
  endif

  if g:clang_omnicppcomplete_compliance == 1
    inoremap <expr> <buffer> <C-X><C-U> <SID>LaunchCompletion()
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

  if g:clang_periodic_quickfix == 1
    augroup ClangComplete
      au CursorHold,CursorHoldI <buffer> call <SID>DoPeriodicQuickFix()
    augroup end
  endif

  setlocal completefunc=ClangComplete
  if g:clang_omnicppcomplete_compliance == 0
    setlocal omnifunc=ClangComplete
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

" Used to tell if a flag needs a space between the flag and file
let s:flagInfo = {
\   '-I': {
\     'pattern': '-I\s*',
\     'output': '-I'
\   },
\   '-F': {
\     'pattern': '-F\s*',
\     'output': '-F'
\   },
\   '-iquote': {
\     'pattern': '-iquote\s*',
\     'output': '-iquote'
\   },
\   '-include': {
\     'pattern': '-include\s\+',
\     'output': '-include '
\   }
\ }

let s:flagPatterns = []
for s:flag in values(s:flagInfo)
  let s:flagPatterns = add(s:flagPatterns, s:flag.pattern)
endfor
let s:flagPattern = '\%(' . join(s:flagPatterns, '\|') . '\)'


function! s:processFilename(filename, root)
  " Handle Unix absolute path
  if matchstr(a:filename, '\C^[''"\\]\=/') != ''
    let l:filename = a:filename
  " Handle Windows absolute path
  elseif s:isWindows() 
       \ && matchstr(a:filename, '\C^"\=[a-zA-Z]:[/\\]') != ''
    let l:filename = a:filename
  " Convert relative path to absolute path
  else
    " If a windows file, the filename may need to be quoted.
    if s:isWindows()
      let l:root = substitute(a:root, '\\', '/', 'g')
      if matchstr(a:filename, '\C^".*"\s*$') == ''
        let l:filename = substitute(a:filename, '\C^\(.\{-}\)\s*$'
                                            \ , '"' . l:root . '\1"', 'g')
      else
        " Strip first double-quote and prepend the root.
        let l:filename = substitute(a:filename, '\C^"\(.\{-}\)"\s*$'
                                            \ , '"' . l:root . '\1"', 'g')
      endif
      let l:filename = substitute(l:filename, '/', '\\', 'g')
    else
      " For Unix, assume the filename is already escaped/quoted correctly
      let l:filename = shellescape(a:root) . a:filename
    endif
  endif
  
  return l:filename
endfunction

function! s:parseConfig()
  let l:local_conf = findfile('.clang_complete', getcwd() . ',.;')
  if l:local_conf == '' || !filereadable(l:local_conf)
    return
  endif

  let l:sep = '/'
  if s:isWindows()
    let l:sep = '\'
  endif

  let l:root = fnamemodify(l:local_conf, ':p:h') . l:sep

  let l:opts = readfile(l:local_conf)
  for l:opt in l:opts
    " Ensure passed filenames are absolute. Only performed on flags which
    " require a filename/directory as an argument, as specified in s:flagInfo
    if matchstr(l:opt, '\C^\s*' . s:flagPattern . '\s*') != ''
      let l:flag = substitute(l:opt, '\C^\s*\(' . s:flagPattern . '\).*'
                            \ , '\1', 'g')
      let l:flag = substitute(l:flag, '^\(.\{-}\)\s*$', '\1', 'g')
      let l:filename = substitute(l:opt,
                                \ '\C^\s*' . s:flagPattern . '\(.\{-}\)\s*$',
                                \ '\1', 'g')
      let l:filename = s:processFilename(l:filename, l:root)
      let l:opt = s:flagInfo[l:flag].output . l:filename
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
  let l:dirs = map(split(&path, '\\\@<![, ]'), 'substitute(v:val, ''\\\([, ]\)'', ''\1'', ''g'')')
  for l:dir in l:dirs
    if len(l:dir) == 0 || !isdirectory(l:dir)
      continue
    endif

    " Add only absolute paths
    if matchstr(l:dir, '\s*/') != ''
      let l:opt = '-I' . shellescape(l:dir)
      let b:clang_user_options .= ' ' . l:opt
    endif
  endfor
endfunction

function! s:initClangCompletePython()
  if !has('python') && !has('python3')
    echoe 'clang_complete: No python support available.'
    echoe 'Cannot use clang library'
    echoe 'Compile vim with python support to use libclang'
    return 0
  endif

  " Only parse the python library once
  if !exists('s:libclang_loaded')
    execute s:py_cmd 'import sys'

    execute s:py_cmd 'sys.path = ["' . s:plugin_path . '"] + sys.path'
    execute s:pyfile_cmd fnameescape(s:plugin_path) . '/libclang.py'

    try
      execute s:py_cmd 'from snippets.' . g:clang_snippets_engine . ' import *'
      let l:snips_loaded = 1
    catch
      let l:snips_loaded = 0
    endtry
    if l:snips_loaded == 0
      " Oh yeah, vimscript rocks!
      " Putting that echoe inside the catch, will throw an error, and
      " display spurious unwanted errors…
      echoe 'Snippets engine ' . g:clang_snippets_engine . ' not found'
      return 0
    endif

    execute s:py_cmd "vim.command('let l:res = ' + str(initClangComplete(vim.eval('g:clang_complete_lib_flags'),"
                                                    \."vim.eval('g:clang_compilation_database'),"
                                                    \."vim.eval('g:clang_library_path'))))"
    if l:res == 0
      return 0
    endif
    let s:libclang_loaded = 1
  endif
  execute s:py_cmd 'WarmupCache()'
  return 1
endfunction

function! s:DoPeriodicQuickFix()
  " Don't do any superfluous reparsing.
  if b:my_changedtick == b:changedtick
    return
  endif
  let b:my_changedtick = b:changedtick

  execute s:py_cmd 'updateCurrentDiagnostics()'
  call s:ClangQuickFix()
endfunction

function! s:ClangQuickFix()
  " Clear the bad spell, the user may have corrected them.
  syntax clear SpellBad
  syntax clear SpellLocal

  execute s:py_cmd "vim.command('let l:list = ' + str(getCurrentQuickFixList()))"
  execute s:py_cmd 'highlightCurrentDiagnostics()'

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

function! s:escapeCommand(command)
    return s:isWindows() ? a:command : escape(a:command, '()')
endfunction

function! s:isWindows()
  " Check for win32 is enough since it's true on win64
  return has('win32')
endfunction

let b:col = 0

function! ClangComplete(findstart, base)
  if a:findstart
    let l:line = getline('.')
    let l:start = col('.') - 1
    let l:wsstart = l:start
    if l:line[l:wsstart - 1] =~ '\s'
      while l:wsstart > 0 && l:line[l:wsstart - 1] =~ '\s'
        let l:wsstart -= 1
      endwhile
    endif
    while l:start > 0 && l:line[l:start - 1] =~ '\i'
      let l:start -= 1
    endwhile
    let b:col = l:start + 1
    return l:start
  else
    if g:clang_debug == 1
      let l:time_start = reltime()
    endif

    execute s:py_cmd 'snippetsReset()'

    execute s:py_cmd "completions, timer = getCurrentCompletions(vim.eval('a:base'))"
    execute s:py_cmd "vim.command('let l:res = ' + completions)"
    execute s:py_cmd "timer.registerEvent('Load into vimscript')"

    if g:clang_make_default_keymappings == 1
      if s:use_maparg
        let s:old_cr = maparg('<CR>', 'i', 0, 1)
      else
        let s:old_snr = matchstr(maparg('<CR>', 'i'), '<SNR>\d\+_')
      endif
      inoremap <expr> <buffer> <C-Y> <SID>HandlePossibleSelectionCtrlY()
      inoremap <expr> <buffer> <CR> <SID>HandlePossibleSelectionEnter()
    endif
    augroup ClangComplete
      au CursorMovedI <buffer> call <SID>TriggerSnippet()
      if exists('##CompleteDone')
        au CompleteDone,InsertLeave <buffer> call <SID>StopMonitoring()
      else
        au InsertLeave <buffer> call <SID>StopMonitoring()
      endif
    augroup end
    let b:snippet_chosen = 0

    execute s:py_cmd 'timer.finish()'

    if g:clang_debug == 1
      echom 'clang_complete: completion time ' . split(reltimestr(reltime(l:time_start)))[0]
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

function! s:StopMonitoring()
  if b:snippet_chosen
    call s:TriggerSnippet()
    return
  endif

  if g:clang_make_default_keymappings == 1
    " Restore original return and Ctrl-Y key mappings

    if s:use_maparg
      if get(s:old_cr, 'buffer', 0)
        silent! execute s:old_cr.mode.
            \ (s:old_cr.noremap ? 'noremap '  : 'map').
            \ (s:old_cr.buffer  ? '<buffer> ' : '').
            \ (s:old_cr.expr    ? '<expr> '   : '').
            \ (s:old_cr.nowait  ? '<nowait> ' : '').
            \ s:old_cr.lhs.' '.
            \ substitute(s:old_cr.rhs, '<SID>', '<SNR>'.s:old_cr.sid.'_', 'g')
      else
        silent! iunmap <buffer> <CR>
      endif
    else
      silent! execute substitute(g:clang_restore_cr_imap, '<SID>', s:old_snr, 'g')
    endif

    silent! iunmap <buffer> <C-Y>
  endif

  augroup ClangComplete
    au! CursorMovedI,InsertLeave <buffer>
    if exists('##CompleteDone')
      au! CompleteDone <buffer>
    endif
  augroup END
endfunction

function! s:TriggerSnippet()
  " Dont bother doing anything until we're sure the user exited the menu
  if !b:snippet_chosen
    return
  endif

  " Stop monitoring as we'll trigger a snippet
  let b:snippet_chosen = 0
  call s:StopMonitoring()

  " Trigger the snippet
  execute s:py_cmd 'snippetsTrigger()'

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

function! s:GotoDeclaration(preview)
  try
    execute s:py_cmd "gotoDeclaration(vim.eval('a:preview') == '1')"
  catch /^Vim\%((\a\+)\)\=:E37/
    echoe "The current file is not saved, and 'hidden' is not set."
          \ "Either save the file or add 'set hidden' in your vimrc."
  endtry
  return ''
endfunction

" May be used in a mapping to update the quickfix window.
function! g:ClangUpdateQuickFix()
  call s:DoPeriodicQuickFix()
  return ''
endfunction

function! g:ClangGotoDeclaration()
  call s:GotoDeclaration(0)
  return ''
endfunction

function! g:ClangGotoDeclarationPreview()
  call s:GotoDeclaration(1)
  return ''
endfunction

" vim: set ts=2 sts=2 sw=2 expandtab :
