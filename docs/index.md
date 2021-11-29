## Welcome to Axie Scholar Utilities Wiki
[![CI to Docker Hub](https://github.com/FerranMarin/axie-scholar-utilities/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/FerranMarin/axie-scholar-utilities/actions/workflows/test.yml)
[![Docker Image](https://img.shields.io/badge/docker%20image-available-blue)](https://hub.docker.com/r/epith/axie-scholar-utilities)

In these pages we will cover all the information you need to install and use axie scholar utilities tool.

# How to install this tool
If you are planning to use TREZOR, you must follow the Poetry installation.

## Install Using Docker
This is the recomended way of installing and using my tool. Follow one of these links for installing with docker:

- [Windows and Docker installation](./pages/install_docker_win.html)
- [MacOs and Docker installation](./pages/install_docker_mac.html)

## Install Using Poetry
If for some reason you want to install using python and poetry, you will need to follow these links:

- [Windows and Poetry installation](./pages/install_poetry_win.html)
- [MacOs and Poetry installation](./pages/install_poetry_mac.html)


# How to use the tool
Depending on how you've installed the tool, to run the commands you will need to do different things, thus why I have strucuted the instructions depending on how you installed the tool. All available actions at the moment are:

- **Generate Secrets**: This is a helper command so you can easily create the secrets.json file.
- **Mass Secret Update**: This command helps mass update the secrets.json file using a csv file that contains public ronin and private keys. This is an alternate method to generate secerts.
- **Claim SLP**: This command will claim the SLP from all the scholar accounts in the payments.json file.
- **Payout**: This command will pay from the scholar account to Scholar, Trainer and Manager. Trainer is optional. It can be executed asking for approval for each set of transactions (each scholar account), or go in auto-mode, without asking for approval before executing transactions.
- **Transfer Axies**: This command will help you transfer multiple axies from multiple accounts to multiple accounts.
- **Generate QR**: This command will generate QR codes for the accounts setup in payments.json. It will store them in the same folder those files are.
- **Axie Morphing**: This command will morph all axies in one or multiple accounts. It will find and morph them automatically.
- **Axie Breeding**: This command will breed the axies defined in axie breedings file. It will charge a fee at the end depending on the ammount of axies breed.
- **Generate Breedings**: This command helps you generate the breedings file from a csv file.

To read the instructions on how to run these commands:

- [Commands for Docker and Docker Hub](./pages/docker_hub_cmds.html)
- [Commands for Docker-compose](./pages/docker_compose_cmds.html)
- [Commands for Poetry](./pages/poetry_cmds.html)


# File Format
This tool depends on various files. To learn more about them follow this [link](./pages/file_formats.html).

# F.A.Q

For the FAQ (Frequent Asked Questions), follow this [link](./pages/faq.html)

# Caution Messages

- In order to be able to do transactions, and claim SLP the scholar ronin account (the ones in Scholars Account ronin Addresses of the payments.json) will need to be registered on the Axie marketplace. (If you want to use this tool they should already be, but just in case!)

- **ALWAYS** keep your secrets.json save and never share them!

- This code complies with ToS and is safe to use.

# Support or Contact

Having trouble with Axie Scholar Utilities? These wiki pages not enough? Check out our [Discord](https://discord.gg/bmKvmhenvu) and I’ll happilly help you out. If you have trouble setting up, I can help you step by step for a fee.
