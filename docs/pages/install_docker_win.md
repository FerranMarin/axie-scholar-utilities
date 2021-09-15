# Install Using Docker On Windows

# Install Docker
Best thing I can do for this bit is send you to follow the instructions in the official docker documentation.

- [Docker on Windows](https://docs.docker.com/desktop/windows/install/)


# Use the image from docker-hub

Currently under revision! Sorry!


# Build docker image from repository

If you do not want to rely on the image I provide on docker hub, you can build it from the repository.
To do that, first you need to download my code, either download it as a zip and unzip it, or git clone it (whatever is easier for you).

After that, navigate using your terminal to the docker folder.Once there create a folder named **files** (this is where we will place our payments and secret file and a file called results.log which is empty), we will link that folder from our host to the docker container.

Once we reach this point. Use the following command to build the docker image:

    docker-compose build scholar-utilities

To learn how to run the commands, please follow this [link](../pages/docker_compose_cmds.html)