SHELL	:= /bin/bash
FILES	:= $(shell git ls-files autoload bin doc plugin)

all: clang_complete.vmb

clang_complete.vmb: $(FILES)
	vim -c "r! git ls-files autoload bin doc plugin" \
	     -c '$$,$$d _' \
	     -c "%MkVimball! $@ ." -c 'q!'

.PHONY: install
install: clang_complete.vmb
	vim $< -c 'so %' -c 'q'

.PHONY: clean
clean:
	rm -f clang_complete.vmb
