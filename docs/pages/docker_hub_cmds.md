# How to Execute Comands when you use Docker image downloaded form Docker Hub

This one is one of the easiest ways to execute commands. All you need is to have a folder with 3 files:

- payments.json
- secrets.json
- results.log

Check the format on the index page of this wiki, but in general what I recommend you do is:

1. Download the payments file from [here](https://axie.management/tracker/payments). I recomend re-naming the file to payments.json. If you do not get it from there, you will need to build it yourself. If you are planning to use percent payments, in that case, please just have a payments.json that only contains this inside:

        { }

2. Have a secrets.json file that only contains this inside:

        { }

3. A file named results.log that is empty.

## Secret Generation

To help in generating secrets, you simply need to execute this command from the folder you have the previously mentioned 3 files.

    axie-utils-gen-secrets payments.json secrets.json

This will update the secrets.json either from an emtpy one with only {}, to one that already has some accounts in. I recommend ALWAYS running this one before doing claims or payouts.

## Payments Generation

To help in generating payments json, you simply need to execute this command from the folder you have the 2 files mentioned below payments.csv and payments.json.

    axie-utils-gen-payments payments.csv payments.json

This will ask for your manager ronin and then create a payments file according to what you setup in payments.csv. 

## Mass Update Secrets

For this command you will need a file called update.csv. It needs to be inside the files folder. Then the command is as follows:

    axie-utils-mass-update update.csv secrets.json

This will update the secrets.json and add any missing secrets that are present in update.csv and not in secrets.json yet.

## Claim SLP

To Claim SLP from the scholar accounts in the payments.json file. You need to run this command from the folder where you have the previously mentioned 3 files.

    axie-utils-claim payments.json secrets.json

## Payout

To payout from the scholar accounts, the command is the following (You need to run this command from the folder where you have the previously mentioned 3 files):

    axie-utils-payout payments.json secrets.json results.log

This will execute the payments defined in payments.json. Results.log will be updated with the logs relevant to payments so you can easily copy paste them to send them to your scholars.

If you do now want to confirm account by account, you can run this other command (result will be the same):

    axie-utils-auto-payout payments.json secrets.json results.log

## Axie Transfers

For this command to work, remmember you will need to have in the folder the json file called transfers.json. The command will be as follows:

    axie-utils-transfer-axies transfers.json secrets.json
