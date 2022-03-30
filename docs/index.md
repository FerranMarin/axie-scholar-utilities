# Axie Scholar Utilities Tool - Information Page

Welcome to the Axie Scholars Utilities Tool Wiki page. Here you will find information about the tool, who is it for, how to install it and how to use it. 
You will also find some other sections such as FAQ and links to different sources  as our discord server, how to contribute to the proyect and some relevant news or information that may impact the project. 


<h2>What is the Axie Scholar Utilities Tool and how does it work?</h2>
It is a tool created to automate frequent activities related to manage scholars. It is specially aimed to Axie Infinity account owners (managers)  with large amount of scholars and tasks to execute.  

This tool allows managers to carry out different activities such as:
<li> Claiming SLPs from scholar accounts </li>
<li>Paying scholars and established entities (if added) such as Trainers and Managers. </li>
<li>Transferring Axies</li>
<li>Breeding Axies</li>
<li>Morphing Axies</li>
<li>Scatter RON</li>
<br>
The tool is a software that has to be installed in your computer and so far, it can only be executed from the command line. Depending on your operating sistem and installation method , it may requires the use of supportive platform Docker. If you have already experience with python, you will be able to customize some of the commands. However, if you are not a techy person, do not worry!, every detail of how to install it and use it will be explained in the guidelines. 

Due to the fact that the tool requires access to scholars accounts info (private keys) in order to pay them, you will be instructed to create a secret files. These private keys will be stored in this secret file in your computer and the tool will basically just read the information from that file and use it to pay the scholars. Other than that, no one (besides yourself) will (nor should) have access to those keys. If you have some more questions regarding security or safety issues, we invite you to find out some more information in our FAQ section where we share some more advice. 

We are constantly working to keep the tool up to date and dedicate time and effort to develop more features. In order to support this project and finance any future development, there is a fee of 1% embedded in the code for Payouts. There are also fees for the task of Breeding (find out more about these fees in the Breeding section). 
Any other task executed is free.<br>
If you wish to contribute with a donation to the project, feel free to do so at: <br>
<i>
Ronin address: 9fa1bc784c665e683597d3f29375e45786617550 <br>
Ko-fi: https://ko-fi.com/ferranmarin <br>
Or contacting directly [Ferran](mailto:ferran.marin.llobet@gmail.com) for more options
<br><br>
We trully appreciate any donation and support for the project. 
</i>
<br><br>
# How to install this tool
If you are planning to use TREZOR, you must follow the Poetry installation.

## Install Using Docker
This is the recomended way of installing and using my tool. Follow one of these links for installing with docker:

- [Windows and Docker installation](./pages/install_docker_win.html)
- [MacOs and Docker installation](./pages/install_docker_mac.html)

## Install Using Poetry
If for some reason you want to install using python and poetry, you will need to follow these links:

- [Windows and Poetry installation](./pages/install_poetry_win.html)
- [MacOs and Poetry installation](./pages/install_poetry_mac.html)


# How to use the tool
Depending on how you've installed the tool, to run the commands you will need to do different things, thus why I have strucuted the instructions depending on how you installed the tool. All available actions at the moment are:

- **Generate Secrets**: This is a helper command so you can easily create the secrets.json file.
- **Mass Secret Update**: This command helps mass update the secrets.json file using a csv file that contains public ronin and private keys. This is an alternate method to generate secerts.
- **Claim SLP**: This command will claim the SLP from all the scholar accounts in the payments.json file.
- **Payout**: This command will pay from the scholar account to Scholar, Trainer and Manager. Trainer is optional. It can be executed asking for approval for each set of transactions (each scholar account), or go in auto-mode, without asking for approval before executing transactions.
- **Transfer Axies**: This command will help you transfer multiple axies from multiple accounts to multiple accounts.
- **Generate QR**: This command will generate QR codes for the accounts setup in payments.json. It will store them in the same folder those files are.
- **Axie Morphing**: This command will morph all axies in one or multiple accounts. It will find and morph them automatically.
- **Axie Breeding**: This command will breed the axies defined in axie breedings file. It will charge a fee at the end depending on the ammount of axies breed.
- **Generate Breedings**: This command helps you generate the breedings file from a csv file.
- **Scatter RON**: This command scatters RON to your scholars.

To read the instructions on how to run these commands:

- [Commands for Docker and Docker Hub](./pages/docker_hub_cmds.html)
- [Commands for Docker-compose](./pages/docker_compose_cmds.html)
- [Commands for Poetry](./pages/poetry_cmds.html)
- [Commands for Trezor (Poetry)](./pages/trezor_cmds.html)

# File Format
This tool depends on various files. To learn more about them follow this [link](./pages/file_formats.html).

# F.A.Q

For the FAQ (Frequent Asked Questions), follow this [link](./pages/faq.html)

# Caution Messages

- In order to be able to do transactions, and claim SLP the scholar ronin account (the ones in Scholars Account ronin Addresses of the payments.json) will need to be registered on the Axie marketplace. (If you want to use this tool they should already be, but just in case!)

- **ALWAYS** keep your secrets.json save and never share them!

- This code complies with ToS and is safe to use.

# Support or Contact

Having trouble with Axie Scholar Utilities? These wiki pages not enough? Check out our [Discord](https://discord.gg/bmKvmhenvu) and I’ll happilly help you out. If you have trouble setting up, I can help you step by step for a fee.
