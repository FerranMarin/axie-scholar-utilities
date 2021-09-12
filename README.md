# Axie Scholars Utilities
[![Build Status](https://app.travis-ci.com/FerranMarin/axie-scholar-utilities.svg?branch=main)](https://app.travis-ci.com/FerranMarin/axie-scholar-utilities)
[![Docker Image](https://img.shields.io/badge/docker%20image-available-blue)](https://hub.docker.com/r/epith/axie-scholar-utilities)


This software's intent is to automate all activities related to manage Scholars. It is specially aimed to mangers with large scholar roasters.
I will try to automate some of the tasks like payments to scholars, QR generation and SLP claiming. I am also very open to new ideas, so please leave them in Issues.

## Payments Utility

This utility to help with payments for Axie Infinity managers who have large scholar roasters.
It requires a JSON input like:

```
{
    "Manager": "ronin:<Manager address here>",
    "Scholars":[
        {
            "Name": "Scholar 1",
            "AccountAddress": "ronin:<account_address>",
            "ScholarPayoutAddress": "ronin:<scholar_address>",
            "ScholarPayout": 10,
            "TrainerPayoutAddress": "ronin:<trainer_address>",
            "TrainerPayout": 1,
            "ManagerPayout": 9
        },
        {...},
        ...
    ],
    "Donations": [
        {
            "Name": "Entity 1",
            "AccountAddress": "ronin:<donation_entity_address>",
            "Percent": 0.01
        },
        {
            ...
        }
    ]
}
```

Let us define the concepts in that file.
- **Manager**: There we input the "manager's" ronin address. This means all manager payments will be paid to that address.
- **Scholars**: This is the list of all scholar accounts we need to make payments to each element in this list contains:
    - **Name**: Name of this account, it is only for identification purposes.
    - **Account Address**: Public ronin address of this scholar account.
    - **Scholar Payout Address**: Scholar's ronin address. This is where we will pay the scholar.
    - **Scholar Payout**: This is the amount of SLP we will pay to the scholar
    - **Trainer Payout Address**: This is an optional parameter. It is the public ronin address of the trainer (otherwise known as investor) for this particular scholar account.
    - **Trainer Payout**: If previous parameter is present, this is the amount of SLP it will be paid to that address.
    - **Manager Payout**: This is the amount of SLP that will be transferred to the manager account.
- **Donations**: Optional list of donations, in case you want to support other projects sharing with them part of your earnings. This percent will be calculated from the Manager Payout and rounded. **Donations to me do NOT go in this place, they are in the code itself!** If any donations or the fee does not reach a minumum of 1 SLP it will not be paid out.
    - **Name**: Name of the entity you want to donate to. This is only for identification purposes.
    - **Account Address**: Public ronin address of the entity or project you want to donate to.
    - **Percent**: Percent you want to donate to that entity. **Caution!** Be aware that to donate 1% you need to input: 0.01. If you write a 1, you would be donating 100% of your manager payments! Total percent of all donations added cannot be over 1 (100%). If that is the case, the software will throw an error and ask you to correct it.


**WARNING!** All addresses in the previous file are the PUBLIC ones. Remember to always keep your private ones safe.

Also, to note, this software will not calculate how much you pay (except for donations and the fee), as the input file it expects has the amounts already.

This next bit is why we need you to run this software locally. And that reason is the private keys for the scholar accounts. To do the payments we need them, but of course you do **NOT** share that with anyone. All this software will do is read those from a file and use them for payments, but none other than you will have access to those keys.

This configuration file will be in the form of:
```
{
    <AccountAddressRonin>:<PrivateKey>,
    ...
}
```

Command looks like:

    axie_scholar_cli.py payout <payments_file> <secrets_file>

This means you need to provide the path to a payments_file and to secrets_file. After that, just follow instructions in the terminal to complete payouts. It will ask for confirmation for each account.

**CAUTION!** In order to be able to do transactions, the sending ronin account (in this case the Scholars Account ronin Addresses) will need to be registered on the Axie marketplace. (If you want to use this tool they should already be, but just in case!)

## Generate Secrets Utility

This utility helps you generate and make sure your secrets file will hold all the needed private keys to execute the payments. That is why it will ask for a payments file and optionally an already created secrets file. Even if you have a generated secrets file, I recommend running this utility for the sake of making sure you have all the needed secrets. Do not worry if you do not, but that will prevent your payouts to be executed and you will need to edit the secrets file anyway.

Command looks like:

    axie_scholar_cli.py generate_secrets <payments_file> [<secrets_file>]

This means it needs a payments_file path and optionally a secrets_file path. **Do not provide a secrets_file path if you do not have a valid secrets json previously created.** Command will simply generate and save a json called secrets.json on the current folder.

GIF example:
- without Docker:
    [![asciicast](https://asciinema.org/a/432830.svg)](https://asciinema.org/a/432830)
- with Docker:
    [![asciicast](https://asciinema.org/a/432831.svg)](https://asciinema.org/a/432831)


## Claim SLP Utility

This utility will claim all the claimable SLP from all the accounts configured in secrets.json. So pleae, run first the secret_gen command to make sure you are not missing any account or private key. After that, simply execute the command and it will attempt to claim from all accounts. If some cannot be claimed, it will let you know, but won't interfere with the rest of claims.

Command looks like:

    axie_scholar_cli.py claim <payments_file> <secrets_file>


## Example Files

Please go to the folder [sample_data](sample_data/) to see sample files for how the [payments file](sample_data/sample_payments_file.json) and the [secrets file](sample_data/sample_payments_file.json) need to look like.

# How to install and run?

## CLI (Command Line Interface)

To run my tool you will need Python3 (the language it is written in) to be installed on your machine. Please do look up how to install it if you get stuck, but here there go a brief explanation on how to do so.

### Windows Installation

1. Go to the [Official Python Webiste](https://www.python.org/downloads/windows/) and download python3. I personally run Python 3.8.2 in my development machine, but this should work in any 3.8 or higher version. (Maybe any version from 3.6?? -- If you decide to go with those versions and have issues, please do report and I will try and fix them)

2. During installation, just follow the installer instructions but remmember to tick the box on the 1st window that says **"Add Python 3.9 to PATH"**. If you do no do that, you will need to remmember the full path of where you have Python installed everytime you want to execute it (which is annoying!). By just ticking that you will have a nicer way to call python just using its name "python".

3. Install [Poetry](https://python-poetry.org/docs/#windows-powershell-install-instructions). We could use the standard PIP package manager for Python, but I like Poetry more as it fixes the versions down in a better way. To do so you need to open your Powershell and execute:

        (Invoke-WebRequest -Uri https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py -UseBasicParsing).Content | python -


4. Now it is time to download my code, there are multiple ways:

    - Use [git](https://git-scm.com/downloads). This is a method I would only recommend if you are already familiar with git. So you know, clone away this repo ;)
    - Go to releases and download the latest one. Currently [v0.1](https://github.com/FerranMarin/axie-scholar-utilities/releases/tag/v0.1). Then just Unzip it somewhere in your computer.

5. Wherever you have my code in your computer you will need to navigate using your Powershell or Terminal to [axie-scholar-utilities/source](axie-scholar-utilities/source). If you are not comfortable with a terminal, you can just navigate using the file explorer, right click the folder, go to properties and copy the full path or location. It will be something like `C:\Users\<myUser>\Documents\axie-scholar-utilitiesv0.1\axie-scholar-utilities\source`. With that, just open your power shell and execute (change the path to the folder location in YOUR computer):

        cd C:\Users\<myUser>\Documents\axie-scholar-utilitiesv0.1\axie-scholar-utilities\source

6. Now, given you have Python and Poetry installed execute the following command to install all the extra dependencies you need:

        poetry install

7. You are ready to go! To run the CLI program, you will just need to execute any of the following commands:

        # This one will execute the payouts
        poetry run python axie_scholar_cli.py payout <payments_file>
        <secrets_file>

        # This one will auto-claim SLP
        poetry run python axie_scholar_cli.py claim <secrets_file>

        # This one will help you generate the secrets file
        poetry run python axie_scholar_cli.py generate_secrets <payments_file>

        # If you give the previous one the location of a generated secrets file, it will update it if needed!
        poetry run python axie_scholar_cli.py generate_secrets <payments_file> <secrets_file>

For the last step, modify the <payments_file> and <secrets_file> with the location of your JSON files. If they are in the same folder, just giving the name of the file .json will be enough. If they are in another folder, give the full location. To find that, use the Properties tip from step 5.


**Any issues in any step, please contact me but sometimes a quick google search or reading the pages I linked above should solve 90% of your problems. Again, I am happy to asist you, so leave an issue here in Github, send me an email or for a faster contact join my Discord**

------
### MacOs Installation

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

        curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -

6. Now it is time to download my code, there are multiple ways:

    - Use [git](https://git-scm.com/downloads). This is a method I would only recommend if you are already familiar with git. So you know, clone away this repo ;)
    - Go to releases and download the latest one. Currently [v0.1](https://github.com/FerranMarin/axie-scholar-utilities/releases/tag/v0.1). Then just Unzip it somewhere in your computer.

7. Wherever you have my code in your computer you will need to navigate using your Terminal to [axie-scholar-utilities/source](axie-scholar-utilities/source). If you are not comfortable with a terminal, you can just navigate using Finder, and drag and drop the folder to the Terminal window. It will copy the path. So first type `cd ` and then drag and drop the folder. Command you run should look something like:

        cd /Users/<your_user>/axie-scholar-utilities/README.md

8. Now, given you have Python and Poetry installed execute the following command to install all the extra dependencies you need:

        poetry install

9. You are ready to go! To run the CLI program, you will just need to execute any of the following commands:

        # This one will execute the payouts
        poetry run python axie_scholar_cli.py payout <payments_file> <secrets_file>

        # This one will auto-claim SLP
        poetry run python axie_scholar_cli.py claim <secrets_file>

        # This one will help you generate the secrets file
        poetry run axie_scholar_cli.py generate_secrets <payments_file>

        # If you give the previous one the location of a generated secrets file, it will update it if needed!
        poetry run axie_scholar_cli.py generate_secrets <payments_file> <secrets_file>

For the last step, modify the <payments_file> and <secrets_file> with the location of your JSON files. If they are in the same folder, just giving the name of the file .json will be enough. If they are in another folder, give the full location. Remmember you can use the trick explained on step 7.


**Any issues in any step, please contact me but sometimes a quick google search or reading the pages I linked above should solve 90% of your problems. Again, I am happy to asist you, so leave an issue here in Github, send me an email or for a faster contact join my Discord**

------
### Linux Installation

TBD

------
------
## Docker

How to install docker?

- [Docker on Windows](https://docs.docker.com/desktop/windows/install/)
- [Docker on Mac](https://docs.docker.com/desktop/mac/install/)
- [Docker on Ubuntu](https://docs.docker.com/engine/install/ubuntu/)
- [Docker on Debian](https://docs.docker.com/engine/install/debian/)
- Check the website for more Linux distros.

I also recommend having docker-compose. It comes by default with Windows and MacOs Desktop versions, so only Linux user will need to:

        # Download it
        sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        # Add execution perms
        sudo chmod +x /usr/local/bin/docker-compose
        # In case you need to create a symlink
        sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose
        # Finally just check it works with
        docker-compose --version

Once we have docker installed and docker-compose we are done. To use the tool we only need to build and run the image. To do so, please navigate using your terminal to the [docker folder](axie-scholar-utilities/docker). Once there create a folder named files (this is where we will place our payments and secret file), we will link that folder from our host to the docker container.

Once all this preparation is done, just use this commands as needed:

        # Builds the image
        docker-compose build scholar-utilities
        # If we want to generate the secrets
        docker-compose run scholar-utilities generate_secrets files/payments.json
        # If you want to claim SLP
        docker-compose run scholar-utilities claim files/secrets.json
        # If we want to do payments in auto mode
        docker-compose run scholar-utilities payout files/payments.json files/secrets.json -y
        # As a general rule
        docker-compose run scholar-utilities <here whatever command and arguments you want to run>

If you do not want to build the image yourself, pleaes download it from my [docker hub](https://hub.docker.com/r/epith/axie-scholar-utilities).

        docker pull epith/axie-scholar-utilities

I recommend setting up this aliases right after pulling the image, so it makes everyones life easier.

For MAC/Linux:

        # Alias to generate secrets
        axie-utils-gen-secrets() {docker run -it -v ${PWD}/${1}:/opt/app/files/payments.json -v ${PWD}/${2}:/opt/app/files/secrets.json epith/axie-scholar-utilities generate_secrets files/payments.json files/secrets.json}
        # Alias to execute claims
        axie-utils-claim() {docker run -it -v ${PWD}/${1}:/opt/app/files/payments.json -v ${PWD}/${1}:/opt/app/files/secrets.json epith/axie-scholar-utilities claim files/secrets.json}
        # Alias to execute payments
        axie-utils-payout() {docker run -it -v ${PWD}/${1}:/opt/app/files/payments.json  -v ${PWD}/${2}:/opt/app/files/secrets.json epith/axie-scholar-utilities payout files/payments.json files/secrets.json}
        # Alias to execute auto-payments (no confirmation)
        axie-utils-auto-payout() {docker run -it -v ${PWD}/${1}:/opt/app/files/payments.json -v ${PWD}/${2}:/opt/app/files/secrets.json epith/axie-scholar-utilities payout files/payments.json files/secrets.json -y}

For Windows (PowerShell):

        # Alias to generate secrets
        function axie-utils-gen-secrets {docker run -it -v ${PWD}/${1}:/opt/app/files/payments.json  -v ${PWD}/${2}:/opt/app/files/secrets.json epith/axie-scholar-utilities generate_secrets files/payments.json files/secrets.json}
        # Alias to execute claims
        function axie-utils-claim {docker run -it -v ${PWD}/${1}:/opt/app/files/payments.json -v ${PWD}/${1}:/opt/app/files/secrets.json epith/axie-scholar-utilities claim files/secrets.json}
        # Alias to execute payments
        function axie-utils-payout {docker run -it -v ${PWD}/${1}:/opt/app/files/payments.json -v ${PWD}/${2}:/opt/app/files/secrets.json epith/axie-scholar-utilities payout files/payments.json files/secrets.json}
        # Alias to execute auto-payments (no confirmation)
        function axie-utils-auto-payout {docker run -it -v ${PWD}/${1}:/opt/app/files/payments.json -v ${PWD}/${2}:/opt/app/files/secrets.json epith/axie-scholar-utilities payout files/payments.json files/secrets.json -y}

With these alias all you need is the payments file and a secret file (if you have not yet generate it, please create a file with just '{}' inside and save it as .json). Then the commands you will need to execute are the following:

        #To generate/update secret file
        axie-utils-gen-secrets name_of_your_payments_file.json name_of_your_secrets_file.json
        #To claim SLP
        axie-utils-claim name_of_your_secrets_file.json
        #To execute payments
        axie-utils-payout name_of_your_payments_file.json name_of_your_secrets_file.json
        #To execute automatic payments
        axie-utils-auto-payout name_of_your_payments_file.json name_of_your_secrets_file.json

Once executed, please follow the insturctions that will appear on your terminal (if any).

## Desktop App

TBD

# How is this and future developments financed?

There is embedded in the code a 1% fee. I believe this is a fair charge for this automation. It allows us to dedicate time and effort on bettering this software and add more features! Please do not remove it as it is the only way I have to support this project.

# Roadmap

- Integrate with Discord (via a bot, maybe?)
- Add transfer axies capabilities (will need an axie to transfer from account to account)
- Release a desktop app (even more convenient)
- ...
- Add functionality to get QR codes, maybe(?)

Feel free to open issues requesting features. I will consider all of them and maybe add them in the future!

# Donations

If you want to donate to thank me, feel free to do so at this ronin address:

    ronin:9fa1bc784c665e683597d3f29375e45786617550
    
# Discord

Feel free to join this project's <a href="https://discord.gg/bmKvmhenvu">Discord</a>
