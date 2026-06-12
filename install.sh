make clean
sudo make install
sudo cp ./sxiv.desktop /usr/share/applications 
mkdir -p $HOME/.config/sxiv/
ln -s $(pwd)/exec $HOME/.config/sxiv/exec
