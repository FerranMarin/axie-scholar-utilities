# Install Using Poetry On MacOs

To run my tool you will need Python3 (the language it is written in) to be installed on your machine. Please do look up how to install it if you get stuck, but here there go a brief explanation on how to do so.

## Install Python and Poetry

0. As a pre-requisite you need to have Xcode. Just get it from the Apple appstore. Find it [here](https://apps.apple.com/us/app/xcode/id497799835?mt=12)

1. Now we can move on to installing python3. The easiest way is with [Homebrew](https://brew.sh/). To install it just run on the terminal:

        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

2. Once you have Homebrew installed, to get python3, just run:

        brew install python3

3. Add python to your PATH. This can be a bit tricky but you need to open the file (or create it). `~/.bash_profile`. Go to the bottom of it and add the line:

        export PATH="/usr/local/opt/python/libexec/bin:$PATH"
        # or this line if you have OS X 10.12 (Sierra or older)
        export PATH=/usr/local/bin:/usr/local/sbin:$PATH

4. Once you have done that, close your terminal and open it again. (So it refreshes and you trully have python in your path). If you want to check you have done it properly you can run this command and check the Path you added in step 3 is there.

        echo $PATH | tr ':' '\n'
        # Or alternatively
        python3 --version

5. Install [Poetry](https://python-poetry.org/docs/#windows-powershell-install-instructions). We could use the standard PIP package manager for Python, but I like Poetry more as it fixes the versions down in a better way. To do so you run this command:

        curl -sSL https://install.python-poetry.org | python3 -

6. Now it is time to download my code, there are multiple ways:

    - Use [git](https://git-scm.com/downloads). This is a method I would only recommend if you are already familiar with git. So you know, clone away this repo ;)
    - Go to releases and download the latest one. Check for the latest one [here](https://github.com/FerranMarin/axie-scholar-utilities/releases/). Then just Unzip it somewhere in your computer.

7. Wherever you have my code in your computer you will need to navigate using your Terminal to axie-scholar-utilities/source. If you are not comfortable with a terminal, you can just navigate using Finder, and drag and drop the folder to the Terminal window. It will copy the path. So first type `cd ` and then drag and drop the folder. Command you run should look something like:

        cd /Users/<your_user>/axie-scholar-utilities/README.md

8. Now, given you have Python and Poetry installed execute the following command to install all the extra dependencies you need:

        poetry install


To learn how to run the commands, please follow this [link](../pages/poetry_cmds.html)

TREZOR USERS, follow this other [LINK](../pages/trezor_cmds.html)