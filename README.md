# Axie Scholars Utilities

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
- **Donations**: Optional list of donations, in case you want to support other projects sharing with them part of your earnings. This percent will be calculated from the Manager Payout and rounded in favour of the manager. **Donations to me do NOT go in this place, they are in the code itself!**
    - **Name**: Name of the entity you want to donate to. This is only for identification purposes.
    - **Account Address**: Public ronin address of the entity or project you want to donate to.
    - **Percent**: Percent you want to donate to that entity. **Caution!** Be aware that to donate 1% you need to input: 0.01. If you write a 1, you would be donating 100% of your manager payments! Total percent of all donations added cannot be over 1 (100%). If that is the case, the software will throw an error and ask you to correct it.


**WARNING!** All addresses in the previous file are the PUBLIC ones. Remember to always keep your private ones safe.

Also, to note, this software will not calculate how much you pay, as the input file it expects has the amounts already.

This next bit is why we need you to run this software locally. And that reason is the private keys for the scholar accounts. To do the payments we need them, but of course you do **NOT** share that with anyone. All this software will do is read those from a file and use them for payments, but none other than you will have access to those keys.

This configuration file will be in the form of:
```
{
    <AccountAddressRonin>:<PrivateKey>,
    ...
}
```

# How to install and run?

## CLI (Command Line Interface)

TBD

## Docker

TBD

## Desktop App

TBD

# How is this and future developments financed?

There is embedded in the code a 1% fee. I believe this is a fair charge for this automation. It allows us to dedicate time and effort on bettering this software and add more features! Please do not remove it as it is the only way I have to support this project.

# Roadmap

- Add support to help create the secrets configuration file
- Add functionality to claim SLP
- Add functionality to get QR codes
- Release a dockerized version (No need to install anything other than docker)
- Release a desktop app (even more convenient)
- ...

Feel free to open issues requesting features. I will consider all of them and maybe add them in the future!

# Donations

If you want to donate to thank me, feel free to do so at this ronin address:

    ronin:cac6cb4a85ba1925f96abc9a302b4a34dbb8c6b0
