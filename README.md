# Axie Scholars Utilities
[![CI to Docker Hub](https://github.com/FerranMarin/axie-scholar-utilities/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/FerranMarin/axie-scholar-utilities/actions/workflows/test.yml)
[![Docker Image](https://img.shields.io/badge/docker%20image-available-blue)](https://hub.docker.com/r/epith/axie-scholar-utilities)

This software's intent is to automate all activities related to manage Scholars. It is specially aimed to mangers with large scholar roasters.
As of now it has the following commands:

- Generate Secrets (Helper to generate secrets.json file)
- Mass Generate Secrets (Helper to generate secrets.json file from a csv file, for bulk creation)
- Generate Payout file (Helper to generate payments.json file from a csv file)
- SLP Claim
- Automatic Payouts
- Axie Transfers
- Axie Morphing
- Axie Breeding
- QR Code Generation
- Scatter RON to your scholar accounts

**Disclaimer!**

From v.3 onwards all transactions will cost RON and will no longer use your free tx. Be aware of that!

**WITH TREZOR SUPORT!**

To know how to use it, install it, please visit the [wiki](https://ferranmarin.github.io/axie-scholar-utilities/)

# How is this and future developments financed?

There is embedded in the code a 1% fee. I believe this is a fair charge for this automation. It allows me to dedicate time and effort on bettering this software and add more features! Please do not remove it as it is the only way I have to support this project.

There is also a fee for breeding. This one is charged at once and the pricing is as follows. Each breed costs:

| Range          | Price  |
|:-------------- |:------:|
| Until 15       | 30 SLP |
| From 16 to 30  | 25 SLP |
| From 31 to 50  | 20 SLP |
| From 51        | 15 SLP |

So if you want to breed 22 Axies the fee would be:

(15 * 30) + (7 * 25) = 625 SLP

The more you breed at once, the cheaper it gets per axie. Be careful with the max amount of tx per account!
You can breed using multiple accounts and pay the fee with another one. More instructions, in the [wiki](https://ferranmarin.github.io/axie-scholar-utilities/pages/poetry_cmds#axiebreeding),


# Roadmap

- Project archived as I will no longer actively mantain it and have not done so for a few months already!

# Donations

If you want to donate to thank me, feel free to do so at this ronin address:

    ronin:9fa1bc784c665e683597d3f29375e45786617550
