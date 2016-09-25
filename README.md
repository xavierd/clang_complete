This plugin uses clang for accurately completing C and C++ code.

## Installation

- To build and install in one step, type: `$ make install`

- To build and install in two steps, type:

```
$ make
$ vim clang_complete.vmb -c 'so %' -c 'q'
```

- Alternatively, you can also put the files in `~/.vim/`

You need Vim 7.3 or higher, compiled with python support and ideally, with
the conceal feature.

## Minimum Configuration

- Set the `clang_library_path` to the directory containing file named
  libclang.{dll,so,dylib} (for Windows, Unix variants and OS X respectively) or
  the file itself, example:

```vim
 " path to directory where library can be found
 let g:clang_library_path='/usr/lib/llvm-3.8/lib'
 " or path directly to the library file
 let g:clang_library_path='/usr/lib64/libclang.so.3.8'
```

- Compiler options can be configured in a `.clang_complete` file in each project
  root.  Example of `.clang_complete` file:

```
-DDEBUG
-include ../config.h
-I../common
-I/usr/include/c++/4.5.3/
-I/usr/include/c++/4.5.3/x86_64-slackware-linux/
```

## Usage

The plugin provides list of matches, after that you pick completion from a
generic completion menu where <kbd>Ctrl+N</kbd>, <kbd>Ctrl+P</kbd> and alike
work and wrap around ends of list.

## License

See doc/clang_complete.txt for help and license.

## Troubleshooting

The first step is to check values of `'omnifunc'` and `'completefunc'` options
in a C++ buffer where completion doesn't work (the value should be
`ClangComplete`).  This can be done with the following command:
`:set omnifunc? completefunc?`

Output of `:messages` command after startup could also show something useful in
case there were problems with plugin initialization.

If everything is fine, next step might be to load only clang_complete plugin
and see if anything changes.
