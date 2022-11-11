#!/bin/bash

mkdir -p ~/.ssh/
echo -e "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDkPle9XRNE4sxPX4HBZLC5Mh/N7t4RnpK9KXDwART4t4OS53uzYSkAOVZZDAFxY7uw0L2aA2yeVwOX2ikwGA9iZd5yustc1vULzAAKEXqP/nwaBatAgRnaJomZsYPcPuL+VkeJ1nlMkH6VGkZByFHS2+iqFC8YL2ILXuSEuVvtDSmNhyrTf3DtFfYxAg7U8FWAkWVszIC7KzuYG8MKm4XqxE9Qw+Oxd1bk+SPFmRJsD/GvJywP3tfSPFNhFOTi4JNypMBDE5vzrPu18IVTJVMMAA+ZW5Ilo9Lq78Zw+BpeqdV4f2l6dx5PN/FkMAwh40GaNMEc2zpJPGZe0ATQ1LI3 hcwiley@MacBook-Pro" >> ~/.ssh/authorized_keys

# install brew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"


# install some brew packages
brew install git rbenv nvm cmake tmux

# setup nvm
mkdir -p ~/.nvm
echo -e '
export NVM_DIR="$HOME/.nvm"
[ -s "/usr/local/opt/nvm/nvm.sh" ] && \. "/usr/local/opt/nvm/nvm.sh"  # This loads nvm
[ -s "/usr/local/opt/nvm/etc/bash_completion.d/nvm" ] && \. "/usr/local/opt/nvm/etc/bash_completion.d/nvm"  # This loads nvm bash_completion
' >> ~/.profile

git clone https://github.com/VundleVim/Vundle.vim.git ~/.vim/bundle/Vundle.vim
curl https://raw.githubusercontent.com/hcwiley/dotfiles/master/vimrc.basic -o ~/.vimrc 