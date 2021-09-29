# How to Execute Comands when you build your own Docker image from the Code

For this to work, you will need a folder called **files** inside the docker folder with these files:

- payments.json
- secrets.json
- results.log

Check the format on the index page of this wiki, but in general what I recommend you do is:

1. Download the payments file from [here](https://axie.management/tracker/payments). I recomend re-naming the file to payments.json. If you do not get it from there, you will need to build it yourself.

2. Have a secrets.json file that only contains this inside:

        { }

3. A file named results.log that is empty.

## Secret Generation

To help in generating secrets, you simply need to execute this command from the docker folder.

    docker-compose run scholar-utilities generate_secrets files/payments.json files/secrets.json

This will update the secrets.json either from an emtpy one with only {}, to one that already has some accounts in. I recommend ALWAYS running this one before doing claims or payouts. If no file was present, this would create a new one.

## Claim SLP

To Claim SLP from the scholar accounts in the payments.json file. You need to run this command from the docker folder.

    docker-compose run scholar-utilities claim files/payments.json files/secrets.json

## Payout

To payout from the scholar accounts, you need to run this command from the docker folder.

    docker-compose run scholar-utilities payout files/payments.json files/secrets.json

This will execute the payments defined in payments.json. Results.log will be updated with the logs relevant to payments so you can easily copy paste them to send them to your scholars.

If you do not want to confirm account by account, you can run this other command (result will be the same):

    docker-compose run scholar-utilities payout files/payments.json files/secrets.json -y

## Axie Transfers

For this command to work, remmember you will need to have in the same files folder the json file called transfers.json. The command will be as follows:

    docker-compose run scholar-utilities transfer_axies files/transfers.json files/secrets.json
