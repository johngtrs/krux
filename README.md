# Krux ✝
Krux is an open-source, airgapped bitcoin hardware signer built with off-the-shelf parts that never stores your keys to disk and functions solely as a signer for multisignature and single-key wallets. 

Every time you use Krux, you need to tell it your key to proceed. When you shut it down, it fully wipes its memory. This means that it's possible to act on behalf of every cosigner in a multisig with one device.

<p align="center">
<img src="https://user-images.githubusercontent.com/87289655/126738716-518cb99c-ca3e-405d-b7ba-55b6edd34ac3.png" width="195">
</p>

---
## Disclaimer
**WARNING**: *This is currently beta-quality software and has not yet been audited by a third party. Use at your own risk!*

---

To use Krux, you will need to buy an [M5StickV](https://shop.m5stack.com/products/stickv). The M5StickV was chosen because it has everything you would need for a hardware wallet in one small device (processor, battery, buttons, screen, camera, and SD card slot), has no WiFi or Bluetooth functionality (for security), and is cheap (< $50).

All operations in Krux are done via QR code. It loads your BIP-39 mnemonic, imports a wallet descriptor, and signs transactions all via QR code. It reads QR codes in with its camera and writes QR codes out to its screen or [to paper via an optional thermal printer attachment](#printing-qrs).

We don't want users to rely on Krux for anything except being a safe way to sign off on a transaction when supplied a key. To this end, Krux will not generate new keys for you. Good random number generation is frought with peril, so we're sidestepping the issue by expecting you to [generate your own offline](https://vault12.rebelmouse.com/seed-phrase-generation-2650084084.html).

Krux is built to work with both desktop and mobile coordinator software and currently has support for:
- [Specter Desktop](https://specter.solutions/)
- [Sparrow Wallet](https://www.sparrowwallet.com/)
- [BlueWallet](https://bluewallet.io/)
- [Electrum](https://electrum.org/)

These applications let you create and manage your multisig or single-key wallets, generate receive addresses, and send funds by creating partially signed bitcoin transactions (PSBTs) that you can sign with your hardware wallets and signers, such as Krux.

# Cloning and updating the repo
This repo has some external dependencies that it manages as [submodules](https://www.git-scm.com/book/en/v2/Git-Tools-Submodules). By default, performing a `git clone` of a repo like this will not pull down the submodule code. Therefore, make sure to run the following the first time you clone this repo:
```bash
git clone --recurse-submodules https://github.com/jreesun/krux
```
This will pull down this repo's code as well as the code for all submodules.

If you already cloned the repo and don't have the submodule code, or if you wish to update the submodules, run:
```bash
git submodule update --init --recursive
```

When pulling down updates to this repo, run:
```bash
git pull --recurse-submodules
```

# Getting Started

## Requirements
Vagrant

## Initialize Vagrant
After you have installed Vagrant, run the following in this directory to spin up a new VM:
```bash
vagrant up
```

## Build the firmware
Run the following:
```bash
vagrant ssh -c 'cd /vagrant; ./krux build-firmware'
```

## Flash the firmware onto an M5StickV
Connect the M5StickV to your computer via USB, power it on (left-side button), and run the following:
```bash
vagrant reload && vagrant ssh -c 'cd /vagrant; ./krux flash-firmware'
```
Note: `vagrant reload` is necessary in order for the newly-inserted USB device to be detected and passed through to the Vagrant VM on startup.

If this command fails with the error `Failed to find device via USB. Is it connected and powered on?`, make sure that the user who needs to access the M5StickV via USB has been added to the group `vboxusers`. Either use the OS user management tools or run the following command:

```
sudo usermod -a -G vboxusers username
```

## Build the software
To build the software, run the following:
```
vagrant ssh -c 'cd /vagrant; ./krux build-software en-US'
```

Prefer a different language? You can replace `en-US` in the command above with one of the following supported locales:

- en-US (English)
- de-DE (German)
- Are we missing one? Make a PR!

Note that due to memory constraints of the device, the translations for the language you wish to use must be baked into the software at this step and can't be changed at runtime.

## Flash the software onto a microSD card
Plug a [supported microSD card](https://github.com/m5stack/m5-docs/blob/master/docs/en/core/m5stickv.md#tf-cardmicrosd-test) into your computer and make sure to format it as FAT-32. Take note of its path (after mounting), for example `/Volumes/SD`.

To install, simply copy over the *contents* of the `build` directory onto the root of the card, or run:
```bash
./krux flash-software /Volumes/SD
```

## Boot it up
Unmount and remove the SD card from your machine, insert it into the M5StickV, and long-press its power button (left side) to boot it up! You should soon see the Krux logo appear on the screen. If after 30 seconds you still see a black screen, try power cycling the device by holding down the power button for six seconds.

Congrats, you're now running Krux!

# Using
## Loading your mnemonic
As stated above, Krux does not† generate a BIP-39 mnemonic for you, but it does expect you to have one in order to use it. You can use either a 12 or 24 word mnemonic.

† If you're using a mnemonic you just generated by hand and want Krux to randomly choose a final word that has a valid checksum of the previous 11 or 23 words, you can enter the appropriate sentinel value (per your input method, defined below) as the 12th or 24th word and one will be generated for you.

### Method: Text
Enter each word of your BIP-39 mnemonic one at a time. Krux will attempt to autocomplete your word to speed up the process. 

Final word sentinel: `zzzzz`

### Method: Numbers
Enter each word of your BIP-39 mnemonic as a number from 1 to 2048 one at a time.

Final word sentinel: `99999`

### Method: Bits
Enter each word of your BIP-39 mnemonic as an [11-bit bitstring](https://github.com/hatgit/BIP39-wordlist-printable-en/blob/master/BIP39-en-printable.txt) one at a time.

### Method: QR
It's unpleasant having to manually enter 12 or 24 words each time you want to use Krux. To remedy this you can instead use the device's camera to read a QR code containing the words (encoded as a single space-separated text string). You can either use an offline QR code generator for this (ideally on an airgapped device), or you can attach a thermal printer to your Krux and print out the mnemonic after opening your wallet via one of the manual methods first. Check out the [Printing QRs section](#printing-qrs) below for more information.

## Importing a Wallet
### Instructions for Specter Desktop
To setup a new wallet, you will need to first add Krux as a new device in Specter by exporting your Extended Master Public Key (xpub) to it. When adding to Specter, choose the `Other` device type and click `Scan QR Code`. On your Krux, once you enter your mnemonic you will be asked if you want to proceed with a `Single-key` or `Multisig` key. Once you have selected which you want, on the following menu select `Public Key (xpub)`, and scan the QR code that appears. It should import as either a `#0 Single Sig (Segwit)` or `#0 Multisig Sig (Segwit)` key based on what you chose in Krux earlier. Repeat this process for as many keys / devices as you want to be in the wallet.

Once you've added all your devices to Specter, add a new wallet and select the devices you want to be in it. A new wallet will then be created, which you will want to load into your Krux via the `Wallet` menu item. In Specter, navigate to the `Advanced` section and find `Export to Wallet` to display a QR code that Krux can read. Once loaded, you can then print this QR code to have as a backup.

## Signing PSBTs
Krux can sign transactions (PSBTs) for multisig and single-key wallets, but they must first be created by one of the supported desktop or mobile coordinators above. 

Note: Krux can sign the inputs of a PSBT that correspond to the given private key (mnemonic) regardless of whether or not the wallet for that key has been loaded. However, without the loaded wallet, Krux cannot validate that the multisig cosigners match or that the script type matches the one defined in your wallet. If you trust your coordinator software, this should be fine. Otherwise, loading the wallet via the `Wallet` menu item before signing is the safest option as it allows for stricter checks to be performed.

### Instructions for Specter Desktop
Signing is straightforward, you just need to create a transaction to send funds somewhere in Specter via the `Send` section, then select to sign off on it with your Krux. Specter will display a QR code for the unsigned PSBT that you can read in with your Krux at which point you will see details about the transaction to confirm they match. It will then ask you for confirmation to sign the PSBT and will then generate its own QR code that you can either display directly back to Specter or print for use at a later time. Once all necessary cosigners have signed the PSBT, you can choose to broadcast it from Specter to the Bitcoin network.

## Checking Addresses
Once you have loaded a wallet, you can use Krux's QR code reader to check that a receive address belongs to it. Normally, you would just copy a receive address shown by your coordinator software and send coins to that address; this option exists as a way to independently verify that your coordinator is giving you a valid address before you move coins.

## Printing QRs
Krux has the ability to print all QR codes it generates, including mnemonic, xpub, wallet backup, and signed PSBT, via a locally-connected thermal printer over its serial port. Any of [these printers from Adafruit](https://www.adafruit.com/?q=thermal+printer) should do, but [this starter pack](https://www.adafruit.com/product/600) would be the quickest way to get started. You'll also need a conversion cable with a 4-pin female Grove connector on one end (to connect to the Krux) and 4-pin male jumpers on the other end (to connect to the printer).

Note: Printers can come with different baudrates from the manufacturer. By default, Krux assumes the connected printer will have a baudrate of `9600`. If yours is different, you can override this by adding a `printer.baudrate.txt` file under `src/settings` with the correct rate, for example `19200`.

Once connected and powered on, all screens that display a QR code will begin showing a follow-up screen asking if you want to `Print to QR?`. You can use the middle button to confirm or the right-side button to cancel.

Originally, the idea was to print out a QR code of the BIP-39 mnemonic to enable faster wallet opening over the manual method of having to input each word. Then, we realized it would be useful to backup a wallet's multisig configuration on paper as well since you need knowledge of all xpubs in a multisig wallet in order to spend from it. After that, we decided to just make it a feature across the board. Want to make a "multisig paper wallet" with codes for your mnemonic, xpub, and multisig wallet on one sheet? You can! Want to print out a signed PSBT and send it in the mail? You can!

Just be careful what you do with the codes, since most smartphones can now quickly and easily read QR codes. Treat your QR mnemonic the same way you would treat a plaintext copy of it.

# Inspired by these similar projects:
- https://github.com/SeedSigner/seedsigner for Raspberry Pi (Zero)
- https://github.com/diybitcoinhardware/f469-disco for the F469-Discovery board

# Contributing
Issues and pull requests welcome! Let's make this as good as it can be.

# Support the Project
If you would like to support the project, BTC is kindly accepted!

`19f8HVt8LZKzBv8CuBYnxCqn5sd75V658J`
