call plug#begin('~/.config/nvim/plugged')
call plug#begin('~/.config/nvim/plugged')


Plug 'tpope/vim-fugitive'
Plug 'scrooloose/nerdTree'
Plug 'vim-airline/vim-airline'
Plug 'vim-airline/vim-airline-themes'
Plug 'flazz/vim-colorschemes'
Plug 'neoclide/coc.nvim', {'branch': 'release'}

call plug#end()

let g:airline_powerline_fonts = 1
let g:airline#extensions#tabline#enabled = 1


if (has("termguicolors"))
  set termguicolors
endif

let g:gruvbox_italic=1
set background=dark
colorscheme gruvbox

set number
