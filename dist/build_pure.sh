#!/bin/bash -e

VERSION=0.46

sudo apt-get install libgmp3-dev llvm g++
wget http://pure-lang.googlecode.com/files/pure-$VERSION.tar.gz
tar xfvz pure-$VERSION.tar.gz
rm pure-$VERSION.tar.gz
cd pure-$VERSION
./configure
make
sudo make install
sudo /sbin/ldconfig
