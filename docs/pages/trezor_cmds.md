# How to Execute Comands when you use Poetry

When you have installed this tool using poetry. You will need to add a 2 files into source (for easy of use, they can be in another folder too). These files are:

- payments.json
- trezor_config.json

Check the format on the index page of this wiki, but in general what I recommend you do is:

1. Download the payments file from [here](https://axie.management/tracker/payments). I recomend re-naming the file to payments.json. If you do not get it from there, you will need to build it yourself. If you are planning to use percent payments, in that case, please just have a payments.json that only contains this inside:

        { }

2. Have a trezor_config.json file that only contains this inside:

        { }


## Payments Generation

To help in generating payments json, you simply need to execute this command from the source folder.

    poetry run python trezor_axie_scholar_cli.py generate_payments payments.csv payments.json

This will ask for your manager ronin and then create a payments file according to what you setup in payments.csv. It can be named anything, just have it in the files folder and use the same name in the command.


## Trezor Config

To configure your trezor device to run the rest of commands, you simply need to execute this command from the source folder.

    poetry run python trezor_axie_scholar_cli.py config_trezor payments.json trezor_config.json

This will update the trezor_config.json either from an emtpy one with only {}, or one that already has some accounts in. I recommend ALWAYS running this one before doing claims or payouts.


## Claim SLP

To Claim SLP from the scholar accounts in the payments.json file. You need to run this command from the source folder.

    poetry run python trezor_axie_scholar_cli.py claim payments.json trezor_config.json

## Payout

To payout from the scholar accounts, you need to run this command from the source folder.

    poetry run python trezor_axie_scholar_cli.py payout payments.json trezor_config.json

This will execute the payments defined in payments.json. Results.log will be updated with the logs relevant to payments so you can easily copy paste them to send them to your scholars.

If you do not want to confirm account by account, you can run this other command (result will be the same):

    poetry run python trezor_axie_scholar_cli.py payout payments.json trezor_config.json -y

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



# Alternative Method

If instead of using this commands you are on **windows** (sorry macOs and Linux users!).
You can put this file in the source folder and simply click it.

[Download Link](../downloadables/poetry_trezor_script.ps1)

**Caution**: Be aware, for this file to work you must name the files exactly how I name them in my examples!
