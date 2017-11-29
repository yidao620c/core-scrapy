#!/bin/bash

cd gitbook

# install the plugins and build the static site
gitbook install && gitbook build

cd ..

# checkout to the gh-pages branch
git checkout -b gh-pages

# pull the latest updates
git pull origin gh-pages --rebase

# copy the static site files into the current directory.
cp -R gitbook/_book/* .

# remove 'node_modules' and '_book' directory
git clean -fx gitbook/node_modules
git clean -fx gitbook/_book

# add all files
git add .

# commit
git commit -a -m "Update docs"

# push to the origin
git push origin gh-pages

# checkout to the master branch
git checkout master

