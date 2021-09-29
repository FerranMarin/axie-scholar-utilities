## Welcome to Axie Scholar Utilities Wiki
[![Build Status](https://app.travis-ci.com/FerranMarin/axie-scholar-utilities.svg?branch=main)](https://app.travis-ci.com/FerranMarin/axie-scholar-utilities)
[![Docker Image](https://img.shields.io/badge/docker%20image-available-blue)](https://hub.docker.com/r/epith/axie-scholar-utilities)

In these pages we will cover all the information you need to install and use axie scholar utilities tool.

# How to install this tool
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
- **Claim SLP**: This command will claim the SLP from all the scholar accounts in the payments.json file.
- **Payout**: This command will pay from the scholar account to Scholar, Trainer and Manager. Trainer is optional. It can be executed asking for approval for each set of transactions (each scholar account), or go in auto-mode, without asking for approval before executing transactions.
- **Transfer Axies**: This command will help you transfer multiple axies from multiple accounts to multiple accounts.

To read the instructions on how to run these commands:

- [Commands for Docker and Docker Hub](./pages/docker_hub_cmds.html)
- [Commands for Docker-compose](./pages/docker_compose_cmds.html)
- [Commands for Poetry](./pages/poetry_cmds.html)


# File Format
This tool depends on various files. Below find the format I expect them to be.

## Payments file format
It requires a JSON file like:

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

Let's define the concepts in that file.
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

## Secrets file format
This JSON file is much simpler, and you should never need to create it as you can use the secret generation command. But if you are curious, the format will be like:

```
{
    <AccountAddressRonin>:<PrivateKey>,
    ...
}
```

## Transfers file format
This JSON file defines the Axie transfers you wish to do. You define from which accounts you transfer which Axies to witch accounts. Here is an example:


```
    [
    {
        "AccountAddress": "ronin:<whohasanaxie>",
        "Transfers": [
            {
                "AxieId": "<axie_id_to_transfer>",
                "ReceiverAddress": "<ronin:<whowillgetanaxie>"
            },
            {
                "AxieId": "<axie_id_to_transfer>",
                "ReceiverAddress": "<ronin:<whowillgetanaxie>"
            },
            {
                "AxieId": "<axie_id_to_transfer>",
                "ReceiverAddress": "<ronin:<whowillgetanaxie>"
            },
            {
                "AxieId": "<axie_id_to_transfer>",
                "ReceiverAddress": "<ronin:<whowillgetanaxie>"
            }
            ...
        ]
    },
    {
        "AccountAddress": "ronin:<whohasanaxie>",
        "Transfers": [
            {
                "AxieId": "<axie_id_to_transfer>",
                "ReceiverAddress": "<ronin:<whowillgetanaxie>"
            },
            {
                "AxieId": "<axie_id_to_transfer>",
                "ReceiverAddress": "<ronin:<whowillgetanaxie>"
            },
            {
                "AxieId": "<axie_id_to_transfer>",
                "ReceiverAddress": "<ronin:<whowillgetanaxie>"
            }
        ]
    },
    ...
    {
        "AccountAddress": "ronin:<whohasanaxie>",
        "Transfers": [
            {
                "AxieId": "<axie_id_to_transfer>",
                "ReceiverAddress": "<ronin:<whowillgetanaxie>"
            },
            {
                "AxieId": "<axie_id_to_transfer>",
                "ReceiverAddress": "<ronin:<whowillgetanaxie>"
            },
            {
                "AxieId": "<axie_id_to_transfer>",
                "ReceiverAddress": "<ronin:<whowillgetanaxie>"
            }
        ]
    }
]

```

As you can see we put the account where we have the axies in `AccountAddress` and then inside `Transfers` we define the transfers we want to do from that account. In each we indicate the `AxieID` and the ronin `ReceiverAddress` to receive that Axie.


## Example Files

If after that you still unclear on how they look like. Please go to the folder sample_data to see sample files for how the payments file and the secrets file need to look like.

# Caution Messages

- In order to be able to do transactions, and claim SLP the scholar ronin account (the ones in Scholars Account ronin Addresses of the payments.json) will need to be registered on the Axie marketplace. (If you want to use this tool they should already be, but just in case!)

- **ALWAYS** keep your secrets.json save and never share them!

- This code complies with ToS and is safe to use.

# Support or Contact

Having trouble with Axie Scholar Utilities? These wiki pages not enough? Check out our [Discord](https://discord.gg/bmKvmhenvu) and I’ll happilly help you out. If you have trouble setting up, I can help you step by step for a fee.
