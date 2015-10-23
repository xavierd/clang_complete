#=============================================================================
# FILE: clang_complete.py
# AUTHOR: Joe Hermaszewski
#=============================================================================

from .base import Base
import deoplete.util
import re

class Source(Base):
    def __init__(self, vim):
        Base.__init__(self, vim)

        self.name = 'clang_complete'
        self.mark = '[clang]'
        self.filetypes = ['c', 'cpp']
        self.is_bytepos = True
        self.min_pattern_length = 1

    def get_complete_position(self, context):
        return self.vim.eval("ClangComplete(1, 0)")

    def gather_candidates(self, context):
        return self.vim.eval("ClangComplete(0, \"\")")
