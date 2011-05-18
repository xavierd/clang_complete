" Prepare the snippet engine
function! snippets#dummy#init()
  echo 'Initializing stuffs'
endfunction

" Add a snippet to be triggered
" Returns: text to be inserted for when trigger() is called
function! snippets#dummy#add_snippet(keyword, proto)
  echo 'Creating snippet for "' . proto . '" using "' . keyword . '"'
  return keyword
endfunction

" Trigger the snippet
" Note: usually as simple as triggering the tab key
function! snippets#dummy#trigger()
  echo 'Triggering snippet'
endfunction

" Remove all snippets
function! snippets#dummy#reset()
  echo 'Resetting all snippets'
endfunction
