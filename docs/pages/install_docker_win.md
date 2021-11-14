# Install Using Docker On Windows

# Install Docker
Best thing I can do for this bit is send you to follow the instructions in the official docker documentation.

- [Docker on Windows](https://docs.docker.com/desktop/windows/install/)

# Use the image from docker-hub

Every successful build of my code produces a Docker image that is stored [here](https://hub.docker.com/r/epith/axie-scholar-utilities).

After you've downloaded docker, you simply need to execute this command to download the latest image:

    docker pull epith/axie-scholar-utilities

If you go this route, I recomend also setting up these alias in your terminal to execute commands easier:

    # Alias to generate secrets
    function axie-utils-gen-secrets {
        docker run -it -v $pwd\payments.json:/opt/app/files/payments.json -v $pwd\secrets.json:/opt/app/files/secrets.json epith/axie-scholar-utilities generate_secrets files/payments.json files/secrets.json
    }
    # Alias to generate payments
    function axie-utils-gen-payments {
        docker run -it -v $pwd\payments.csv:/opt/app/files/payments.csv -v $pwd\payments.json:/opt/app/files/payments.json epith/axie-scholar-utilities generate_payments files/payments.csv files/payments.json
    }
    # Alias to mass update secrets
    function axie-utils-mass-update {
        docker run -it -v $pwd\update.csv:/opt/app/files/update.csv -v $pwd\secrets.json:/opt/app/files/secrets.json epith/axie-scholar-utilities mass_update_secrets files/update.csv files/secrets.json
    }
    # Alias to execute claims
    function axie-utils-claim {
        docker run -it -v $pwd\payments.json:/opt/app/files/payments.json -v $pwd\secrets.json:/opt/app/files/secrets.json -v $pwd\logs:/opt/app/logs epith/axie-scholar-utilities claim files/payments.json files/secrets.json
    }
    # Alias to execute payments
    function axie-utils-payout {
        docker run -it -v $pwd\payments.json:/opt/app/files/payments.json  -v $pwd\secrets.json:/opt/app/files/secrets.json -v $pwd\logs:/opt/app/logs epith/axie-scholar-utilities payout files/payments.json files/secrets.json
    }
    # Alias to execute auto-payments (no confirmation)
    function axie-utils-auto-payout {
        docker run -it -v $pwd\payments.json:/opt/app/files/payments.json -v $pwd\secrets.json:/opt/app/files/secrets.json -v $pwd\logs:/opt/app/logs epith/axie-scholar-utilities payout files/payments.json files/secrets.json -y
    }
    # Alias to execute axie transfers
    function axie-utils-transfer-axies {
        docker run -it -v $pwd\payments.json:/opt/app/files/transfers.json -v $pwd\secrets.json:/opt/app/files/secrets.json -v $pwd\logs:/opt/app/logs epith/axie-scholar-utilities transfer_axies files/transfers.json files/secrets.json
    }
    #Alias to generate transfers file
    function axie-utils-gen-transfers {
        docker run -it -v $pwd\transfers.csv:/opt/app/files/transfers.csv -v $pwd\transfers.json:/opt/app/files/transfers.json epith/axie-scholar-utilities generate_transfer_axies files/transfers.csv files/transfers.json
    }
    # Alias to execute generate_qr
    function axie-utils-gen-QR {
        docker run -it -v $pwd\transfers.json:/opt/app/files/transfers.json -v $pwd\secrets.json:/opt/app/files/secrets.json -v ${pwd}:/opt/app/files epith/axie-scholar-utilities generate_QR files/payments.json files/secrets.json
    }
    #Alias to generate breedings file
    function axie-utils-gen-breedings {
        docker run -it -v $pwd\breedings.csv:/opt/app/files/breedings.csv -v $pwd\breedings.json:/opt/app/files/breedings.json epith/axie-scholar-utilities generate_breedings files/breedings.csv files/breedings.json
    }
    # Alias to breed axies
    function axie-utils-axie-breeding {
        docker run -it -v $pwd\breedings.json:/opt/app/files/breedings.json -v $pwd\secrets.json:/opt/app/files/secrets.json -v $pwd\logs:/opt/app/logs epith/axie-scholar-utilities axie_breeding files/breedings.json files/secrets.json
    }
    # Alias to morph axies
    function axie-utils-axie-morphing {
        docker run -it -v $pwd\secrets.json:/opt/app/files/secrets.json -v $pwd\logs:/opt/app/logs epith/axie-scholar-utilities axie_morphing files/secrets.json
    }

Be aware, that this aliases will require the EXACT file names to work.
To learn how to run the commands, please follow this [link](../pages/docker_hub_cmds.html)

# Build docker image from repository

To build the docker image from the code, first you need to download my code, either download it as a zip and unzip it, or git clone it (whatever is easier for you).

Once we have done that, you can use your file explorer to go into that code and inside axie-scholar-utilities\docker. Once there create a folder named **files** (this is where we will place our payments and secret file and a file called results.log which is empty), we will link that folder from our host to the docker container.

After that, navigate using your terminal (for example PowerShell) to the docker folder (the one inside axie-scholar-utilities/docker). The easiest way to do so, is copy the path from your file explorer navigation bar to have the path. You can also right, click the docker folder and press "copy as path".

When I say navigate, I mean use the cd command. CD stands for change directory. TO do so, you need to write cd space and the path you want to go. So for this case, you want to do:

    cd <path_to_docker_folder_inside_unziped_code>

In my case it looks something like this. I extracted the code to my Desktop:

    cd C:\Users\FerranMarin\Desktop\axie-scholar-utilities-main\axie-scholar-utilities\docker

If there are spaces in your path, please enclose it in quotes something like:

    cd 'C:\Users\Ferran Marin\Desktop\axie-scholar-utilities-main\axie-scholar-utilities\docker'

Once we reach this point. Use the following command to build the docker image:

    docker-compose build scholar-utilities

To learn how to run the commands, please follow this [link](../pages/docker_compose_cmds.html)
