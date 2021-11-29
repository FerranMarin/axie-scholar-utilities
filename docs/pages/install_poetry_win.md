# Install Using Poetry On Windows

To run my tool you will need Python3 (the language it is written in) to be installed on your machine. Please do look up how to install it if you get stuck, but here there go a brief explanation on how to do so.

## Install Python and Poetry

1. Go to the [Official Python Webiste](https://www.python.org/downloads/windows/) and download python3. I personally run Python 3.8.2 in my development machine, but this should work in any 3.8 or higher version. (Maybe any version from 3.6?? -- If you decide to go with those versions and have issues, please do report and I will try and fix them)

2. During installation, just follow the installer instructions but remmember to tick the box on the 1st window that says **"Add Python 3.9 to PATH"**. If you do no do that, you will need to remmember the full path of where you have Python installed everytime you want to execute it (which is annoying!). By just ticking that you will have a nicer way to call python just using its name "python".

3. To avoid issues down the line. Download Visual C++ Build tools from [here](https://visualstudio.microsoft.com/visual-cpp-build-tools/)

4. Install [Poetry](https://python-poetry.org/docs/#windows-powershell-install-instructions). We could use the standard PIP package manager for Python, but I like Poetry more as it fixes the versions down in a better way. To do so you need to open your Powershell and execute:

        (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -

5. Now it is time to download my code, there are multiple ways:

    - Use [git](https://git-scm.com/downloads). This is a method I would only recommend if you are already familiar with git. So you know, clone away this repo ;)
    - Go to releases and download the latest one. Check for the latest one [here](https://github.com/FerranMarin/axie-scholar-utilities/releases/). Then just Unzip it somewhere in your computer.

6. Wherever you have my code in your computer you will need to navigate using your Powershell or Terminal to axie-scholar-utilities/source. If you are not comfortable with a terminal, you can just navigate using the file explorer, right click the folder, go to properties and copy the full path or location. It will be something like `C:\Users\<myUser>\Documents\axie-scholar-utilitiesv0.1\axie-scholar-utilities\source`. With that, just open your power shell and execute (change the path to the folder location in YOUR computer):

        cd C:\Users\<myUser>\Documents\axie-scholar-utilitiesv0.1\axie-scholar-utilities\source

7. Now, given you have Python and Poetry installed execute the following command to install all the extra dependencies you need:

        poetry install


To learn how to run the commands, please follow this [link](../pages/poetry_cmds.html)

TREZOR USERS, follow this other [LINK](../pages/trezor_cmds.html)