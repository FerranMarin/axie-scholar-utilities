# Install Using Docker On Windows

# Install Docker
Best thing I can do for this bit is send you to follow the instructions in the official docker documentation.

- [Docker on Windows](https://docs.docker.com/desktop/windows/install/)

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