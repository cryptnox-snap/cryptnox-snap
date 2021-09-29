# Cryptnox Card

**Warning: This is a beta release of the software. 
It is released for development purposes. 
Use at your own risk.**

A command line user interface to manage and use of [Cryptnox cards](https://www.cryptnox.com/).

This provides basic wallets for [Bitcoin](https://bitcoin.org) and [Ethereum](https://ethereum.org).  
It is able to execute [cleos](https://eos.io/for-developers/build/cleos/) commands and use the keys on the card for signing.

To buy NFC enabled cards that are supported by this library go to: [https://www.cryptnox.com/](https://www.cryptnox.com/)

## License

The library is available under dual licensing. You can use the library under the 
conditions of [GNU GENERAL PUBLIC LICENSE 3.0+](https://www.gnu.org/licenses/gpl-3.0.en.html) 
or [contact us](info@cryptnox.ch) to ask about commercial licensing. 

## Installation and requirements

The package can be installed using pip package manager with:  
`pip install cryptnoxcard`  

The application can also be installed from source as python package.  
In the root of the project, execute:
`pip install .`

This installs the application into your python packages and makes the 
`crytpnoxcard` available as executable.  
If during python installation its path was added to system path the executable, 
e.g. command is available system wide.

### Linux additional packages

On some Debian/Ubuntu Linux systems there binaries for sme libraries are not 
delivered with the installed package. In this case install the following tools, 
so that they can be compiled during installation process.   
`sudo apt-get install build-essential autoconf libtool pkg-config python3-dev swig libpcsclite-dev`

### MacOS missing certificates

If you're using macOS and the command CLI is showing issues of missing 
certificates, open Macintosh HD > Applications > Python3.6 folder 
(or other version of python you're using) > 
double click on `Install Certificates.command` file.

## Running the application

The application can receive commands directly in any command line, or can be 
started in [Interactive Mode](#interactive-mode) by starting without any 
arguments or options. The later will also start if the executable is called 
from a GUI, like Windows Explorer.

For commands options refer to [Command Line Interface](#command-line-interface) 
chapter.

## Development environment

For development purposes or for running separately from the system environment 
pipenv configuration files are provided.

To set it up, use, from the root folder of the project:
`pipenv install` or `pipenv install --dev` if you want libraries for development 
purposes like pylint.

To enter the new environment use: `pipenv shell`

This will open a new terminal inside the one it was called from. From here all 
packages will be available to run the application.

From here the CLI is available as a script:  
`python cryptnoxcard/main.py`  
or as a module  
`python -m cryptnoxcard.main`

## Secrets
Each card is protected by two secrets only known to the owner of the card.

### PIN code
The PIN code must be 4 to 9 number characters ('0'-'9').  
After entering the wrong PIN code 3 times the card PIN code is
locked, and it must be [unlocked](#unlock-pin-code) using the PUK code.  
Entering the correct PIN code resets the number of times the wrong PIN code 
can be entered. 

### PUK code
The PUK code must be 15 number characters ('0'-'9').  
Entering the wrong PUK code for 5 times will lock the card, effectively the 
card is lost.
 
## Demo mode

**Warning:** Only use for testing purposes.

The card can be initialized in demo mode. This is done for convenience of the 
user as you don't have to enter the card secrets. For this reason it comes at 
the expense of security.  
The card is initialized with following infomation:
- Owner name: "DEMO"
- Owner email: "DEMO"
- PIN code 000000000
- PIK code 000000000000000

When the application asks for any secret, PIN or PUK code, press "ENTER" key. 
The application will use the predefined information to fill it for you.  
Demo mode on card is determined from the owner name and email.

## Interactive mode

An interactive mode is available if the command is entered without any arguments 
and options.
In this mode the user will get a similar interface as a command line with its 
own prompt accepting same commands as regular call.
When the mode starts it will show useful information to the user:
- Help of the top level commands
- List of available cards.

The prompt is also showing useful information:
- `cryptnoxcard` indicates that the user is in interactive mode
- Serial number of the selected card on which the command will be executed
- Indication that the card is in demo mode

## Command Line Interface

Named Arguments:
- `-h, --help` Show help for the command
- `-v, --version` Show program’s version number and exit
- `--verbose` Turn on logging

Available in regular call:
- `-s, --serial` Serial number of the card to be used for the command  

### Change PIN code

Change PIN code of the selected card.

Command:
`change_pin [-h]`

### Config

List and change configuration for the application.  

Command:  
`config [-h] [section] [key] [value]`

Positional Arguments:
- `section` Define a section to use 
- `key` Define a key to use
- `value` Define a new value for the given section and key

The command execution depends on the number of arguments in the following way:
- 0 arguments: List all values in the configuration
- 1 arguments: List all values under the given section
- 2 arguments: List value under given section and key
- 3 arguments: Modify value for the given section and key

#### Location

The configuration file is a regular ini file that can be edited with any text editor to change its values.

Configuration file for the application can be found in the user configuration folder.
- Windows: `C:\Users\{username}\AppData\Local\CryptnoxCard\cryptnoxcard.ini`
- Linux: `/home/{username}/.config/CryptnoxCard/cryptnoxcard.ini`


### Eosio

Executes cleos commands.

Command:  
`cleos [-h] [-u [URL]] [-k {K1, R1}] [-P [path]] [-s [coin_symbol]] {pay,push,get,transfer} ...`


Positional Arguments:
- `action` The only argument is the cleos command to execute. Possible choices: 
  - `pay` 
  - `push` 
  - `get` 
  - `transfer`

Named Arguments:
- `-u, --url` URL of the API node
- `-k, --key_type` Key type to use. Possible choices: 
  - `K1` 
  - `R1`
- `-P, --path` BIP32 path from Cryptnox seed for the EC keypair. 
  Default: “m/44’/194’/0’/0”
- `-s, --symbol` Coin symbol

#### Pay

Pay, in other words, send funds from an account to account.

Command:  
`cleos pay [-h] toaccount amount [memo]`

Positional Arguments:
- `toaccount` The account to send tokens to
- `amount` The amount of tokens to send
- `memo` The memo for the transfer. Default: “”

#### Push

Push an action connected to account or transaction to the network.
These commands accept JSON strings generated through the website.

Command:  
`cleos push [-h] {action,transaction} ...`

##### Action

Execute an action on the contract.

Command:  
`cleos push action [-h] contract action_name data`

Positional Arguments:
- `contract` Target contract of the action
- `action_name` The action name to execute on the contract
- `data` JSON string of the arguments to the contract

##### Transaction

Push a transaction to the network.

Command:  
`cleos push transaction [-h] transaction`

Positional Arguments:
- `transaction` Transaction to push in JSON format string

#### Get

Get information from the network and display it in JSON format.

Command:
`cleos get [-h] {info,block,account,code,currency,accounts,servants,transaction,pubkey} ...`

##### Info

List various information about the used network.

Command: 
`cleos get info [-h]`

##### Block

Information about a block in the blockchain.

Command:  
`cleos get block [-h] block`

Positional Arguments:
- `block` The number or ID of the block to retrieve

##### Account

Get information about the given account. 

Command:  
`cleos get account [-h] account`

Positional Arguments:
- `account` The name of the account to retrieve

##### Code

Retrieve code of the given account

Command:  
`cleos get code [-h] account`

Positional Arguments:
- `account` The name of the account whose code should be retrieved

##### Currency

Retrieve information about currency for contracts

Command:  
`cleos get currency [-h] {balance,stats} ...`

Positional Arguments:
- `currency` Possible choices: 
  - `balance`
  - `stats`

##### Balance

Retrieve information for balance.

Command:  
`cleos get currency balance [-h] contract account [symbol]`

Positional Arguments:
- `contract` The contract that operates the currency
- `account` The account to query balances
- `symbol` The symbol for the currency if the contract operates multiple currencies. Default: “EOS”

##### Statistics

Retrieve statistics about a contract.

Command:  
`cleos get currency stats [-h] contract [symbol]`

Positional Arguments:
- `contract` The contract that operates the currency
- `symbol` The symbol for the currency if the contract operates multiple currencies. Default: “EOS”

##### Accounts

Retrieve information about accounts that have public ley attached to them.

Command:  
`cleos get accounts [-h] public_key`

Positional Arguments:
- `public_key` The public key to retrieve accounts for

##### Servants

Retrieve sub-accounts created by the given account.

Command:  
`cleos get servants [-h] account`

Positional Arguments:
- `account` Reference account to return accounts created by this account

##### Transaction

Retrieve information about a transaction.

Command:  
`cleos get transaction [-h] txid`

Positional Arguments:
- `txid` ID of the transaction to retrieve information about

##### Pubkey

Retrieve the public key.

Command:  
`cleos get pubkey [-h]`

#### Transfer

Trunsfer funds between accounts. Best used when there are multiple accounts 
attached to same key.

Command:  
`cleos transfer [-h] sender recipient amount [memo]`

Positional Arguments:
- `sender` The account sending tokens
- `recipient` The account receiving tokens
- `amount` The amount of tokens to send, and the token symbol
- `memo` The memo for the transfer. Default: “”

### Exit

Exit the [Interactive Mode](#interactive-mode)

Command:
`exit [-h]`

### Info

Get information about accounts connected to the selected card.

Command:  
`info [-h]`

Result of running the command is a table containing:
- Service: The service to which the account is connected (supported: BTC, ETH, EOSIO)
- Network: The network to which the CLI is connecting to for information
- Account: The account which is used
- Balance: Current balance on the account
- Currency: Currency on the network

### Initialize

Initialize a card with owner information (name and email) and secrets (PIN and PUK codes)

Command:  
`init [-h] [-d]`

Named Arguments:
- `-d, --demo` Initialize card in demo mode. [More infomation](#demo-mode)

### Key

Generate keys for the selected card.

Command:  
`key [-h] {upload,chip,recover}`

There are three methods that can be used to put keys in the card.

- `chip` Generate keys directly in the chip. This way the private key is the most secure as it never leaves the chip
- `upload` Generate a key word list in this host and upload it in the cryptnox card
- `recover` Recover a key from a BIP39 word list

### List

List table containing all available cards with information about: 
- Serial number
- Applet version
- Owner (name and email)
- Initialized
- Seed

Command:  
`list [-h]`

### Reset card

Reset the content of the card to factory settings.  
This operation requires PUK code to execute.  
**Warning:** This will delete the keys from the card and you might loose access to your accounts. 

Command:  
`reset [-h]`

### Send

Command for sending funds over blockchain networks using keys from the card.

Command:  
`send [-h] {btc,eth} ...`

#### Send BTC

Command for sending coins on the Bitcoin network.

Command:  
`send btc [-h] [-n {mainnet,testnet}] [-f FEES] address amount`

Positional Arguments:
- `address` Address where to send funds
- `amount` Amount to send

Named Arguments:
- `-n, --network` Network to use for transaction. Possible choices: 
  - `mainnet` 
  - `testnet`
- `-f, --fees` Fees to pay for the transaction

#### Send ETH

Command for sending coins on the Ethereum network.

Command:
`send eth [-h] [-t TOKEN] [-n {mainnet,ropsten,rinkeby,goerli,kovan}] [-p PRICE] [-l LIMIT] address amount`

Positional Arguments:
- `address` Address where to send funds
- `amount` Amount to send

Named Arguments:
- `-t, --token` Api key token for connecting to network
- `-n, --network` Network to use for transaction. Possible choices: 
  - `mainnet` 
  - `ropsten` 
  - `rinkeby` 
  - `goerli` 
  - `kovan`
- `-p, --price` Gas price
- `-l, --limit` Gas limit

### Unlock PIN code

When the PIN code is locked after failing three times to enter the correct one this allows to set a new PIN code.   
This operation requires PUK code to execute.  

Command:
`unlock_pin [-h]`

### Use card

In [Interactive Mode](#interactive-mode) select card to be used for subsequent commands.

Command:
`use [-h] serial`

Positional arguments:
- `serial` Serial number of card to be used for subsequent commands
