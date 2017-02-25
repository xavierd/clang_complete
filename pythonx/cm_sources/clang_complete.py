# -*- coding: utf-8 -*-

# For debugging
# NVIM_PYTHON_LOG_FILE=nvim.log NVIM_PYTHON_LOG_LEVEL=INFO nvim

# clang python bindings only supports python2
# https://github.com/llvm-mirror/clang/commit/abdad67b94ad4dad2d655d48ff5f81d6ccf3852e

from cm import register_source, get_src
register_source(name='clang_complete',
                   priority=9,
                   abbreviation='c',
                   scopes=['c','cpp'],
                   events=['BufEnter'],
                   detach=1,
                   python='python2',
                   cm_refresh_patterns=[r'[0-9a-zA-Z_#]{3,}$',r'(-\>|\.|::)[\w_]*$'],
                   )

import sys
import os
import re
import logging

logger = logging.getLogger(__name__)

class Source:

    def __init__(self,nvim):

        self._nvim = nvim

        libclang_base = nvim.eval("globpath(&rtp,'plugin/clang',1)").split("\n")[0]
        libclang_base = os.path.dirname(libclang_base)
        logger.info("libclang_base: %s", libclang_base)
        sys.path.append(libclang_base)

        # hack, libclang has 'import vim'
        sys.modules['vim'] = nvim
        import libclang
        self._libclang = libclang

        # init global variables for plugin/clang_complete.vim
        nvim.call('g:ClangCompleteInit')

        libclang.initClangComplete()
        
    def cm_refresh(self,info,ctx,*args):

        lnum = ctx['lnum']
        col = ctx['col']
        typed = ctx['typed']
        path = ctx['filepath']

        debug = False

        kwtyped = re.search(r'[0-9a-zA-Z_]*?$',typed).group(0)
        startcol = col-len(kwtyped)

        src = get_src(self._nvim,ctx)
        if not src.strip():
            return

        file = (path, str(src))

        params = self._libclang.getCompileParams(path,ctx['scope'])
        timer = self._libclang.CodeCompleteTimer(debug, path, lnum, startcol, params)
        t = self._libclang.CompleteThread(lnum, startcol, file, path, params, timer)
        t.run()
        cr = t.result

        cr = t.result
        if cr is None:
            logger.error("Cannot parse this source file. The following arguments are used for clang: %s", params['args'])
            return (str([]), timer)

        results = cr.results

        base = typed[startcol-1:]
        if base != "":
            results = [x for x in results if self._libclang.getAbbr(x.string).startswith(base)]

        sorting = self._nvim.eval("g:clang_sort_algo")
        if sorting == 'priority':
            getPriority = lambda x: x.string.priority
            results = sorted(results, key=getPriority)
        if sorting == 'alpha':
            getAbbrevation = lambda x: self._libclang.getAbbr(x.string).lower()
            results = sorted(results, key=getAbbrevation)

        matches = list(map(self._libclang.formatResult, results))

        # logger.info("src: %s", src)
        logger.info("completion result: %s", matches)

        self._nvim.call('cm#complete', info['name'], ctx, startcol, matches, True, async=True)


