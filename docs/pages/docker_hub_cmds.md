# How to Execute Comands when you use Docker image downloaded form Docker Hub

This one is one of the easiest ways to execute commands. All you need is to have a folder with 2 files (and any csv files you might use to create any json file):

- payments.json
- secrets.json

Check the format on the index page of this wiki, but in general what I recommend you do is:

1. Download the payments file from [here](https://axie.management/tracker/payments). I recomend re-naming the file to payments.json. If you do not get it from there, you will need to build it yourself.For that you need to have a payments.json that only contains this inside:

        { }

2. Have a secrets.json file that only contains this inside:

        { }

3. Result log files will be placed inside a folder `logs` where you ran this code. No need to create it before hand.

## Payments Generation

To help in generating payments json, you simply need to execute this command from the folder you have the 2 files mentioned below payments.csv and payments.json.

    axie-utils-gen-payments payments.csv payments.json

This will ask for your manager ronin and then create a payments file according to what you setup in payments.csv. 

## Secret Generation

To help in generating secrets, you simply need to execute this command from the folder you have the previously mentioned 3 files.

    axie-utils-gen-secrets payments.json secrets.json

This will update the secrets.json either from an emtpy one with only {}, to one that already has some accounts in. I recommend ALWAYS running this one before doing claims or payouts.

## Mass Update Secrets

For this command you will need a file called update.csv. It needs to be inside the folder that holds your json and csv files. Then the command is as follows:

    axie-utils-mass-update update.csv secrets.json

This will update the secrets.json and add any missing secrets that are present in update.csv and not in secrets.json yet.

## Claim SLP

To Claim SLP from the scholar accounts in the payments.json file. You need to run this command from the folder where you have the previously mentioned 3 files.

    axie-utils-claim payments.json secrets.json

## Payout

To payout from the scholar accounts, the command is the following (You need to run this command from the folder where you have the previously mentioned 3 files):

    axie-utils-payout payments.json secrets.json

This will execute the payments defined in payments.json. A log file will be generatted with the logs relevant to payments so you can easily copy paste them to send them to your scholars.

If you do not want to confirm account by account, you can run this other command (result will be the same):

    axie-utils-auto-payout payments.json secrets.json

Remmember this command has a cost of 1% of the total ammount of SLP transfered of each account.

## Axie Transfers

For this command to work, remmember you will need to have in the folder the json file called transfers.json. The command will be as follows:

    axie-utils-transfer-axies transfers.json secrets.json

If you want to be extra safe, you can use the `--safe-mode` flag to only allow transfers to accounts that are present in secrets.json. Command would loke like:

    axie-utils-transfer-axies transfers.json secrets.json --safe-mode

## Generate Transfers File

This command will need a csv file to generate the final transfers.json file. It needs to be inside the same folder where you have the rest of files. Then the command is as follows:

    axie-utils-gen-transfers transfers.csv transfers.json

## Generate QR

For this command we need to have a generated payments file and secrets file. Then the command will be as follows:

    axie-utils-gen-QR payments.json secrets.json

The resulting QR codes will be placed in same folder as secrets.json (in this case the same folder you have the rest of files)

## Axie Generate Breedings

This command will need a csv file to generate the final breedsings.json file. It needs to be inside the same folder where you have the rest of files. Then the command is as follows:

    axie-utils-gen-breedings breedings.csv breedings.json

For ease of use, please have a breedings.json file only containing `{}` in it. (Same as the empty secrets.json or payments.json)

## Axie Breeding

To execute breedings, you need a generated breedings.json, explained in the previous step. Then the command is as follows:

    axie-utils-axie-breeding breedsings.json secrets.json

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

This command will automatically find your axies to morph and morph them. It needs to have such account private keys in secrets.json. Then the command is as follows:

    axie-utils-axie-morphing secrets.json ronin:abc1,ronin:abc2

Be careful when writing the accounts, if multiple they need to be separeted only by a comma (NO SPACE!)

# Alternative Method

If instead of using this commands you are on **windows** (sorry macOs and Linux users!).
You can put this file in the folder with the rest of the files and simply click it.

[Download Link](../assets/downloads/docker_hub_script.ps1)

**Caution**: Be aware, for this file to work you must name the files exactly how I name them in my examples!