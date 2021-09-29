# How to Execute Comands when you use Poetry

When you have installed this tool using poetry. You will need to add a 2 files into source (for easy of use, they can be in another folder too). These files are:

- payments.json
- secrets.json

Check the format on the index page of this wiki, but in general what I recommend you do is:

1. Download the payments file from [here](https://axie.management/tracker/payments). I recomend re-naming the file to payments.json. If you do not get it from there, you will need to build it yourself.

2. Have a secrets.json file that only contains this inside:

        { }

## Secret Generation

To help in generating secrets, you simply need to execute this command from the source folder.

    poetry run python axie_scholar_cli.py generate_secrets payments.json secrets.json

This will update the secrets.json either from an emtpy one with only {}, to one that already has some accounts in. I recommend ALWAYS running this one before doing claims or payouts.

## Claim SLP

To Claim SLP from the scholar accounts in the payments.json file. You need to run this command from the source folder.

    poetry run python axie_scholar_cli.py claim payments.json secrets.json

## Payout

To payout from the scholar accounts, you need to run this command from the source folder.

    poetry run python axie_scholar_cli.py payout payments.json secrets.json

This will execute the payments defined in payments.json. Results.log will be updated with the logs relevant to payments so you can easily copy paste them to send them to your scholars.

If you do now want to confirm account by account, you can run this other command (result will be the same):

    poetry run python axie_scholar_cli.py payout payments.json secrets.json

## Axie Transfers

For this command to work, remmember you will need to have in the source folder (or the folder you use for the rest of files) the json file called transfers.json. The command will be as follows:

    poetry run python axie_scholar_cli.py transfer_axies transfers.json secrets.json
