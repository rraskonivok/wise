#!/bin/bash -e

VERSION=0.46

dpkg --status libgmp3-dev llvm | grep -q not-installed

if [ $? -eq 0 ]; then
    sudo apt-get install libgmp3-dev llvm
fi

wget http://pure-lang.googlecode.com/files/pure-$VERSION.tar.gz
tar xfvz pure-$VERSION.tar.gz
rm pure-$VERSION.tar.gz
cd pure-$VERSION
./configure
make
sudo make install
sudo /sbin/ldconfig
