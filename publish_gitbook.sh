#!/bin/bash

cd document

# gitbook install
# install the plugins and build the static site
gitbook build

cd ..

# checkout to the gh-pages branch
git checkout gh-pages

# pull the latest updates
git pull origin gh-pages

# copy the static site files into the current directory.
\cp -Rf gitbook/_book/* .

# remove 'node_modules' and '_book' directory
# git clean -fx gitbook/node_modules
# git clean -fx gitbook/_book
rm -rf gitbook/_book/

# add all files
git add .

# commit
git commit -a -m "Update docs"

# push to the origin
git push origin gh-pages

# checkout to the master branch
git checkout master

