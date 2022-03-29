# How to Execute Comands when you build your own Docker image from the Code

For this to work, you will need a folder called **files** inside the docker folder with these files:

- payments.json (optional, if you do not use axie.management integration)
- secrets.json

To avoid issues, create a `logs` folder.

Check the format on the index page of this wiki, but in general what I recommend you do is:

1. If you want to not use the axie.management integration, you will need to have a payments.json that only contains this inside:

        {}

and before running any other command you will need to generate the payments file. So go to `Payments Generation`.

2. You need a secrets.json file that only contains this inside:

        { }

3. Result log files will be placed inside a folder `logs` inside files folder. No need to create it before hand, but creating it avoids issues.


## Payments Generation

To help in generating payments json, you simply need to execute this command from the docker folder.

    docker-compose run scholar-utilities generate_payments files/payments.csv files/payments.json

This will ask for your manager ronin and then create a payments file according to what you setup in payments.csv. It can be named anything, just have it in the files folder and use the same name in the command.

If you are using the axie.management integration, this step is not needed.

## Secret Generation

To help in generating secrets, you simply need to execute this command from the docker folder.

    docker-compose run scholar-utilities generate_secrets files/payments.json files/secrets.json

This will update the secrets.json either from an emtpy one with only {}, to one that already has some accounts in. I recommend ALWAYS running this one before doing claims or payouts. If no file was present, this would create a new one.

If you are using the axie.management integration, the command is as follows:

    docker-compose run scholar-utilities managed_generate_secrets files/secrets.json TOKEN

Change the TOKEN for the one you receive from axie.management. Find it following this [link](https://tracker.axie.management/profile).

## Mass Update Secrets

For this command you will need a file called anything you want, for this example let's call it update.csv. It needs to be inside the files folder. Then the command is as follows:

    docker-compose run scholar-utilities mass_update_secrets files/update.csv files/secrets.json

This will update the secrets.json and add any missing secrets that are present in update.csv and not in secrets.json yet.

## Claim SLP

To Claim SLP from the scholar accounts in the payments.json file. You need to run this command from the docker folder.

    docker-compose run scholar-utilities claim files/payments.json files/secrets.json

If you are using the axie.management integrataion, the command is as follows:

    docker-compose run scholar-utilities managed_claim files/secrets.json TOKEN

Change the TOKEN for the one you receive from axie.management. Find it following this [link](https://tracker.axie.management/profile).

You can allways append `--force` at the end of the command to force the execution. This will make the command ignore the last time an account was claimed and still try to claim it. (Useful in some cases where errors occurred)

## Payout

To payout from the scholar accounts, you need to run this command from the docker folder.

    docker-compose run scholar-utilities payout files/payments.json files/secrets.json

This will execute the payments defined in payments.json. A log file will be generated with the logs relevant to payments so you can easily copy paste them to send them to your scholars.

If you do not want to confirm account by account, you can run this other command (result will be the same):

    docker-compose run scholar-utilities payout files/payments.json files/secrets.json -y

If you are using the axie.management integration, the commands are as folows:

    docker-compose run scholar-utilities managed_payout files/secrets.json TOKEN

or

    docker-compose run scholar-utilities managed_payout files/secrets.json TOKEN -y

Change the TOKEN for the one you receive from axie.management. Find it following this [link](https://tracker.axie.management/profile).

Remmember this command has a cost of 1% of the total ammount of SLP transfered of each account.

## Axie Transfers

For this command to work, remmember you will need to have in the same files folder the json file called transfers.json. The command will be as follows:

    docker-compose run scholar-utilities transfer_axies files/transfers.json files/secrets.json

If you want to be extra safe, you can use the `--safe-mode` flag to only allow transfers to accounts that are present in secrets.json. Command would loke like:

    docker-compose run scholar-utilities transfer_axies files/transfers.json files/secrets.json --safe-mode

## Generate Transfers File

This command will need a csv file to generate the final transfers.json file. It needs to be inside the files folder. Then the command is as follows:

    docker-compose run scholar-utilities generate_transfer_axies files/transfers.csv files/transfers.json

For ease of use, please have a transfers.json file only containing `{}` in it. (Same as the empty secrets.json or payments.json)

## Generate QR

For this command we need to have a generated payments file and secrets file. Then the command will be as follows:

    docker-compose run scholar-utilities generate_QR files/payments.json files/secrets.json

The resulting QR codes will be placed in same folder as secrets.json (in this case the files folder).

If you are using the axie.management integration, the command is as follows:

    docker-compose run scholar-utilities managed_generate_QR files/secrets.json TOKEN

Change the TOKEN for the one you receive from axie.management. Find it following this [link](https://tracker.axie.management/profile).

## Axie Generate Breedings

This command will need a csv file to generate the final breedsings.json file. It needs to be inside the files folder. Then the command is as follows:

    docker-compose run scholar-utilities generate_breedings files/breedings.csv files/breedings.json

For ease of use, please have a breedings.json file only containing `{}` in it. (Same as the empty secrets.json or payments.json)

## Axie Breeding

To execute breedings, you need a generated breedings.json, explained in the previous step. Then the command is as follows:

    docker-compose run scholar-utilities axie_breeding files/breedings.json files/secrets.json

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

    docker-compose run scholar-utilities axie_morphing files/secrets.json ronin:abc1,ronin:abc2

Be careful when writing the accounts, if multiple they need to be separeted only by a comma (NO SPACES!)

## RON Scattering

This command will scatter RON to your scholars. You need to set the min RON you want those accounts to hold, the tool will check which ones need some RON and top them off. Then execute the Scatter conctract to distribute the funds.

    docker-compose run scholar-utilities scatter_ron files/payments.json files/secrets.json MIN_RON

or

    docker-compose run scholar-utilities managed_scatter_ron files/secrets.json TOKEN MIN_RON


Replace MIN_RON with a number (can be decimal) of the minumum RON you want the scholars accounts in payments.json to have!
Change the TOKEN for the one you receive from axie.management. Find it following this [link](https://tracker.axie.management/profile).

# Alternative Method

If instead of using this commands you are on **windows** (sorry macOs and Linux users!).
You can put this file in the docker folder and simply click it.


[Download Link](../downloadables/docker_compose_script.ps1)

**Caution**: Be aware, for this file to work you must name the files exactly how I name them in my examples!