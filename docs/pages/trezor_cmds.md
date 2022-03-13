# How to Execute Comands when you use Poetry

When you have installed this tool using poetry. You will need to add a 2 files into source (for easy of use, they can be in another folder too). These files are:

- payments.json (optional, if you do not use axie.management integration)
- trezor_config.json


To avoid issues, create a `logs` folder.

Check the format on the index page of this wiki, but in general what I recommend you do is:

1. If you want to not use the axie.management integration, you will need to have a payments.json that only contains this inside:

        {}

and before running any other command you will need to generate the payments file. So go to `Payments Generation`.

2. You need a secrets.json file that only contains this inside:

        { }

3. Result log files will be placed inside a folder `logs` inside files folder. No need to create it before hand, but creating it avoids issues.


## Payments Generation

To help in generating payments json, you simply need to execute this command from the source folder.

    poetry run python trezor_axie_scholar_cli.py generate_payments payments.csv payments.json

This will ask for your manager ronin and then create a payments file according to what you setup in payments.csv. It can be named anything, just have it in the files folder and use the same name in the command.

If you are using the axie.management integration, this step is not needed.

## Trezor Config

To configure your trezor device to run the rest of commands, you simply need to execute this command from the source folder.

    poetry run python trezor_axie_scholar_cli.py config_trezor payments.json trezor_config.json

This will update the trezor_config.json either from an emtpy one with only {}, or one that already has some accounts in. I recommend ALWAYS running this one before doing claims or payouts.

If you are using the axie.management integration, the command is as follows:

     poetry run python trezor_axie_scholar_cli.py managed_config_trezor trezor_config.json TOKEN

Change the TOKEN for the one you receive from axie.management. Find it following this [link](https://tracker.axie.management/profile).


## Claim SLP

To Claim SLP from the scholar accounts in the payments.json file. You need to run this command from the source folder.

    poetry run python trezor_axie_scholar_cli.py claim payments.json trezor_config.json

If you are using the axie.management integrataion, the command is as follows:

   poetry run python trezor_axie_scholar_cli.py managed_claim secrets.json TOKEN

Change the TOKEN for the one you receive from axie.management. Find it following this [link](https://tracker.axie.management/profile).

You can allways append `--force` at the end of the command to force the execution. This will make the command ignore the last time an account was claimed and still try to claim it. (Useful in some cases where errors occurred)

## Payout

To payout from the scholar accounts, you need to run this command from the source folder.

    poetry run python trezor_axie_scholar_cli.py payout payments.json trezor_config.json

This will execute the payments defined in payments.json. Results.log will be updated with the logs relevant to payments so you can easily copy paste them to send them to your scholars.

If you do not want to confirm account by account, you can run this other command (result will be the same):

    poetry run python trezor_axie_scholar_cli.py payout payments.json trezor_config.json -y

If you are using the axie.management integration, the commands are as folows:

    poetry run python trezor_axie_scholar_cli.py managed_payout secrets.json TOKEN

or
    poetry run python trezor_axie_scholar_cli.py managed_payout secrets.json TOKEN -y

Change the TOKEN for the one you receive from axie.management. Find it following this [link](https://tracker.axie.management/profile).

Remmember this command has a cost of 1% of the total ammount of SLP transfered of each account.

## Axie Transfers

For this command to work, remmember you will need to have in the source folder (or the folder you use for the rest of files) the json file called transfers.json. The command will be as follows:

    poetry run python trezor_axie_scholar_cli.py transfer_axies transfers.json trezor_config.json

If you want to be extra safe, you can use the `--safe-mode` flag to only allow transfers to accounts that are present in trezor_config.json. Command would loke like:

    poetry run python trezor_axie_scholar_cli.py transfers.json trezor_config.json --safe-mode

## Generate Transfers File

This command will need a csv file to generate the final transfers.json file. It needs to be inside the source folder. Then the command is as follows:

    poetry run python trezor_axie_scholar_cli.py generate_transfer_axies transfers.csv transfers.json

If you do not provide a transfers.json it will be generated for you in the same folder transfers.csv is.

## Generate QR

For this command we need to have a generated payments file and secrets file. Then the command will be as follows:

    poetry run python trezor_axie_scholar_cli.py generate_QR payments.json trezor_config.json

The resulting QR codes will be placed in same folder as trezor_config.json (in this case the source folder)

The resulting QR codes will be placed in same folder as secrets.json (in this case the files folder).

If you are using the axie.management integration, the command is as follows:

    poetry run python trezor_axie_scholar_cli.py managed_generate_QR secrets.json TOKEN

Change the TOKEN for the one you receive from axie.management. Find it following this [link](https://tracker.axie.management/profile).

## Axie Generate Breedings

This command will need a csv file to generate the final breedsings.json file. It needs to be inside the source folder. Then the command is as follows:

    poetry run python trezor_axie_scholar_cli.py generate_breedings breedings.csv breedings.json

If you do not provide a breedings.json it will be generated for you in the same folder breedsings.csv is.

## Axie Breeding

To execute breedings, you need a generated breedings.json, explained in the previous step. Then the command is as follows:

    poetry run python trezor_axie_scholar_cli.py axie_breeding breedsings.json trezor_config.json

This command will ask you to introduce a ronin account where you would like to pay the SLP fee for breeding. Pricing for this command will be charged all at once in a unique transaction once all breeds have been done.
Each breed costs:

| Range          | Price  |
|:-------------- |:------:|
| Until 15       | 30 SLP |
| From 16 to 30  | 25 SLP |
| From 31 to 50  | 20 SLP |
| From 51        | 15 SLP |

So if you want to breed 22 Axies the fee would be:

(15 * 30) + (7 * 25) = 625 SLP

The more you breed at once, the cheaper it gets per axie. Be careful with the max amount of tx per account!
You can breed using multiple accounts and pay the fee with another one.

## Axie Morphing

This command will automatically find your axies to morph and morph them. It needs to have such account private keys in trezor_config.json. Then the command is as follows:

    poetry run python trezor_axie_scholar_cli.py axie_morphing trezor_config.json ronin:abc1,ronin:abc2

Be careful when writing the accounts, if multiple they need to be separeted only by a comma (NO SPACE!)
