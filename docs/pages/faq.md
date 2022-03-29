# F.A.Q.

## How do I get my private keys?

**Please keep these always safe and private!**

You will need to open your ronin wallet extension in Chrome or Firefox. And follow these steps:


![Image 1](../assets/wallet_1.jpg)

![Image 2](../assets/wallet_2.jpg)

![Image 3](../assets/wallet_3.jpg)

![Image 4](../assets/wallet_4.jpg)


## Is it safe to use?

What do you expect me to say? I'd say of course yes, but do not take me at my word.
Please do get your coder/progammer friends to read and check my code. Look for people who has used it already and ask them (hint: a lot are in the <a href="https://discord.gg/bmKvmhenvu">Discord</a>).

And if you still do not trust it, please do not use it.
I want you only using this tool/software if you are comfortable doing so.

## How to update to a newer version?

Depends on the method you use to run the tool. For those of you using the docker-hub image is as simple as pulling it again.
Remember that is done with the following command:

    docker pull epith/axie-scholar-utilities

If you use either poetry or docker-compose you will need to get the new code either by downloading it from the [releases page](https://github.com/FerranMarin/axie-scholar-utilities/releases) or by using the git pull command. Later one, only reserved to those who know how to use git.
Remember for this one to move your files folder from the old unziped code to the new one and re-build the image / re-install dependencies!

## Which is the recommended way of installing / setting up this tool?

If you are using Windows, I recommend downloading the code and going the docker-compose route (where you build the image locally).
If you are using MacOs, I recommend simply pulling the image and using the aliases.
Despite that, one can use whatever feels is best for their use case.

## What are these messages I get when using Trezor?

When using trezor you will see this text and diagram on your terminal:

![Trezor Image](../assets/trezor_instructions.jpg)

First, you will type your PIN that is on your screen. You can type the letters as shown on the screen, as each letter corresponds to a number. Just do not type it how it looks on the terminal.
If introduced correctly, it will after ask for the device passphrase, if you did not set one up, simply press enter, else please introduce it and press enter.

This should be the only different bits you should face when using trezor.


## Which Trezor devices and versions you support?

As per the library we are using, this is what it says:

    Current trezorlib version supports Trezor One version 1.8.0 and up, and Trezor T version 2.1.0 and up.

For more info, please visit their [PyPi page](https://pypi.org/project/trezor/)

## Can I use my free tx instead? Does the tool use RON?

From v.3 onwards tool uses RON for all transactions, before it was using free tx. Feel free to try use an older version if you wish to use the tool and your free transactions.
I cannot guarantee that versions older than the latest work tho!