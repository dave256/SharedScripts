#!/bin/zsh

pushd ~/

git clone https://github.com/dave256/FileLabs.git
git clone https://github.com/dave256/CodePostScripts.git
mkdir DaveScripts

popd


/bin/cp -f zshenv.txt ~/.zshenv
/bin/cp -f codepost-config.txt ~/.codepost-config.yaml

files=(`ls *.py`)
for f in $files
do
	/bin/cp -f $f ~/DaveScripts
done

cd ~/DaveScripts
ln -s mycap.py mycap2att.py
ln -s mycap.py mycap2ga.py 
