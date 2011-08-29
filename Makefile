SHELL=/bin/bash

all: dist

dist:
	@vim -c 'r! git ls-files autoload bin doc plugin' \
	     -c '$$,$$d _' \
	     -c '%MkVimball! clang_complete.vba .' -c 'q!'

install: dist
	@vim clang_complete.vba -c 'so %' -c 'q'

clean:
	@rm -f clang_complete.vba
