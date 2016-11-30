#=============================================================================
# FILE: clang_complete.py
# AUTHOR: Joe Hermaszewski
#=============================================================================

from .base import Base

class Source(Base):
    def __init__(self, vim):
        Base.__init__(self, vim)

        self.name = 'clang_complete'
        self.mark = '[clang]'
        self.filetypes = ['c', 'cpp', 'objc', 'objcpp']
        self.is_bytepos = True
        self.input_pattern = '[^. \t0-9]\.\w*'

    def get_complete_position(self, context):
        return self.vim.call('ClangComplete', 1, 0)

    def gather_candidates(self, context):
        return self.vim.call('ClangComplete', 0, '')
