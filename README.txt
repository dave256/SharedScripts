instructions for Dave:
have person install git (Xcode from Mac App Store includes it)
have person download this from:
https://github.com/dave256/SharedScripts
git clone https://github.com/dave256/SharedScripts

instructions for person using the scripts:

if using codepost.io,  get an API key
https://codepost.io/settings

we will need to upload rosters to codepost.io after students
add/drop the first few days of classes

edit codepost-config.txt and put it on first line after the colon
edit the semester and year as necessary

if not using codepost.io, continue here:

create directories for each course roster and then edit zshenv and
update the two environment variables

then execute:
./install.zsh

quit Terminal and restart it

in Safari Preferences -> General, turn off "Open safe files after
downloading" so it does not unzip iLearn submissions


