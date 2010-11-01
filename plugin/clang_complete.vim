"
" File: clang_complete.vim
" Author: Xavier Deguillard <deguilx@gmail.com>
"
" Description: Use of clang to complete in C/C++.
"
" Configuration: Each project can have a .clang_complete at his root,
"                containing the compiler options. This is useful if
"                you're using some non-standard include paths.
"                For simplicity, please don't put relative and
"                absolute include path on the same line. It is not
"                currently correctly handled.
"
" Options: g:clang_complete_auto: if equal to 1, automatically complete
"                                 after ->, ., ::
"                                 Default: 1
"          g:clang_complete_copen: if equal to 1, open quickfix window
"                                  on error. WARNING: segfault on
"                                  unpatched vim!
"                                  Default: 0
"
" Todo: - Fix bugs
"       - Add snippets on Pattern and OVERLOAD (is it possible?)
"       - Parse warnings, fix-its and highlight them with
"       Spell{Rare,Local,Cap}
"

au FileType c,cpp,objc,objcpp call s:ClangCompleteInit()

let b:clang_exec = ''
let b:clang_parameters = ''
let b:clang_user_options = ''

function s:ClangCompleteInit()
    let l:local_conf = findfile(".clang_complete", '.;')
    let b:clang_user_options = ''
    if l:local_conf != ""
        let l:opts = readfile(l:local_conf)
        for l:opt in l:opts
            " Better handling of absolute path
            " I don't know if those pattern will work on windows
            " platform
            if matchstr(l:opt, '-I\s*/') != ""
                let l:opt = substitute(l:opt, '-I\s*\(/\%(\w\|\\\s\)*\)',
                            \ '-I' . '\1', "g")
            else
                let l:opt = substitute(l:opt, '-I\s*\(\%(\w\|\\\s\)*\)',
                            \ '-I' . l:local_conf[:-16] . '\1', "g")
            endif
            let b:clang_user_options .= " " . l:opt
        endfor
    endif

    if !exists('g:clang_complete_auto')
        let g:clang_complete_auto = 1
    endif

    if !exists('g:clang_complete_copen')
        let g:clang_complete_copen = 0
    endif

    if g:clang_complete_auto == 1
        inoremap <expr> <buffer> <C-X><C-U> LaunchCompletion()
        inoremap <expr> <buffer> . CompleteDot()
        inoremap <expr> <buffer> > CompleteArrow()
        inoremap <expr> <buffer> : CompleteColon()
    endif

    let b:clang_exec = 'clang'
    let b:clang_parameters = '-x c'

    if &filetype == 'objc'
        let b:clang_parameters = '-x objective-c'
    endif

    if &filetype == 'cpp' || &filetype == 'objcpp'
        let b:clang_parameters .= '++'
    endif

    if expand('%:e') =~ 'h*'
        let b:clang_parameters .= '-header'
    endif

    setlocal completefunc=ClangComplete

    au CursorHold,CursorHoldI <buffer> call s:DoPeriodicQuickFix()

endfunction

function s:GetKind(proto)
    if a:proto == ""
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

function s:DoPeriodicQuickFix()
    let l:buf = getline(1, '$')
    let l:tempfile = expand('%:p:h') . '/' . localtime() . expand('%:t')
    call writefile(l:buf, l:tempfile)
    let l:escaped_tempfile = shellescape(l:tempfile)

    let l:command = b:clang_exec . " -cc1 -fsyntax-only "
                \ . l:escaped_tempfile
                \ . " " . b:clang_parameters . " " . b:clang_user_options . " -o -"

    let l:clang_output = split(system(l:command), "\n")
    call delete(l:tempfile)
    if v:shell_error
        call s:ClangQuickFix(l:clang_output)
    else
        call setqflist([])
    endif
endfunction

function s:ClangQuickFix(clang_output)
    let l:list = []
    for l:line in a:clang_output
        let l:erridx = stridx(l:line, "error:")
        if l:erridx == -1
            continue
        endif
        let l:bufnr = bufnr("%")
        let l:pattern = '\.*:\(\d*\):\(\d*\):'
        let tmp = matchstr(l:line, l:pattern)
        let l:lnum = substitute(tmp, l:pattern, '\1', '')
        let l:col = substitute(tmp, l:pattern, '\2', '')
        let l:text = l:line
        let l:type = 'E'
        let l:item = {
                    \ "bufnr": l:bufnr,
                    \ "lnum": l:lnum,
                    \ "col": l:col,
                    \ "text": l:text[l:erridx + 7:],
                    \ "type": l:type }
        let l:list = add(l:list, l:item)

        " Highlight the error
        let l:err_line = getline(l:lnum)
        let l:err_word = matchstr(l:err_line, '\i*', l:col - 1)
        if l:err_word != ""
            let l:pat = '/\%' . l:lnum . 'l' . l:err_word . '/'
            exe "syntax match SpellBad " . l:pat
        endif
    endfor
    call setqflist(l:list)
    " The following line cause vim to segfault. A patch is ready on vim
    " mailing list but not currently upstream, I will update it as soon
    " as it's upstream. If you want to have error reporting will you're
    " coding, you could open at hand the quickfix window, and it will be
    " updated.
    " http://groups.google.com/group/vim_dev/browse_thread/thread/5ff146af941b10da
    if g:clang_complete_copen == 1
        copen
    endif
endfunction

function s:DemangleProto(prototype)
    let l:proto = substitute(a:prototype, '[#', "", "g")
    let l:proto = substitute(l:proto, '#]', ' ', "g")
    let l:proto = substitute(l:proto, '#>', "", "g")
    let l:proto = substitute(l:proto, '<#', "", "g")
    " TODO: add a candidate for each optional parameter
    let l:proto = substitute(l:proto, '{#', "", "g")
    let l:proto = substitute(l:proto, '#}', "", "g")

    return l:proto
endfunction

let b:should_overload = 0

function ClangComplete(findstart, base)
    if a:findstart
        let l:line = getline('.')
        let l:start = col('.') - 1
        let l:wsstart = l:start
        if l:line[l:wsstart - 1] =~ '\s'
            while l:wsstart > 0 && l:line[l:wsstart - 1] =~ '\s'
                let l:wsstart -= 1
            endwhile
        endif
        if l:line[l:wsstart - 1] =~ '[(,]'
            let b:should_overload = 1
            return l:wsstart
        endif
        let b:should_overload = 0
        while l:start > 0 && l:line[l:start - 1] =~ '\i'
            let l:start -= 1
        endwhile
        return l:start
    else
        let l:buf = getline(1, '$')
        let l:tempfile = expand('%:p:h') . '/' . localtime() . expand('%:t')
        call writefile(l:buf, l:tempfile)
        let l:escaped_tempfile = shellescape(l:tempfile)

        let l:command = b:clang_exec . " -cc1 -fsyntax-only -code-completion-at="
                    \ . l:escaped_tempfile . ":" . line('.') . ":" . col('.')
                    \ . " " . l:escaped_tempfile
                    \ . " " . b:clang_parameters . " " . b:clang_user_options . " -o -"
        let l:clang_output = split(system(l:command), "\n")
        call delete(l:tempfile)

        " Clear the bad spell, the user may have corrected them.
        syntax clear SpellBad
        if v:shell_error
            call s:ClangQuickFix(l:clang_output)
            return {}
        else
            call setqflist([])
        endif
        if l:clang_output == []
            return {}
        endif
        for l:line in l:clang_output
            if l:line[:11] == 'COMPLETION: ' && b:should_overload != 1
                let l:value = l:line[12:]

                if l:value !~ '^' . a:base
                    continue
                endif

                " We can do something smarter for Pattern.
                " My idea is to have some sort of snippets.
                " It could be great if it can be done.
                if l:value =~ 'Pattern'
                    let l:value = l:value[10:]
                endif

                let l:colonidx = stridx(l:value, " : ")
                if l:colonidx == -1
                    let l:word = s:DemangleProto(l:value)
                    let l:proto = l:value
                else
                    let l:word = l:value[:l:colonidx - 1]
                    let l:proto = l:value[l:colonidx + 3:]
                endif

                " WTF is that?
                if l:word =~ '(Hidden)'
                    let l:word = l:word[:-10]
                endif

                let l:kind = s:GetKind(l:proto)
                let l:proto = s:DemangleProto(l:proto)

            elseif l:line[:9] == 'OVERLOAD: ' && b:should_overload == 1

                " The comment on Pattern also apply here.
                let l:value = l:line[10:]
                let l:word = substitute(l:value, '.*<#', "", "g")
                let l:word = substitute(l:word, '#>.*', "", "g")
                let l:proto = s:DemangleProto(l:value)
                let l:kind = ""

            else
                continue
            endif

            let l:item = {
                        \ "word": l:word,
                        \ "menu": l:proto,
                        \ "info": l:proto,
                        \ "dup": 1,
                        \ "kind": l:kind }

            if complete_add(l:item) == 0
                return {}
            endif
            if complete_check()
                return {}
            endif
        endfor
    endif
endfunction

function ShouldComplete()
    if (getline(".") =~ '#\s*\(include\|import\)')
        return 0
    else
        return match(synIDattr(synID(line("."), col(".") - 1, 1), "name"),
                    \'\C\<cComment\|\<cCppString\|\<cString') == -1
endfunction

function LaunchCompletion()
    if ShouldComplete()
        return "\<C-X>\<C-U>"
    else
        return ""
    endif
endfunction

function CompleteDot()
    return '.' . LaunchCompletion()
endfunction

function CompleteArrow()
    if getline('.')[col('.') - 2] != '-'
        return '>'
    endif
    return '>' . LaunchCompletion()
endfunction

function CompleteColon()
    if getline('.')[col('.') - 2] != ':'
        return ':'
    endif
    return ':' . LaunchCompletion()
endfunction
