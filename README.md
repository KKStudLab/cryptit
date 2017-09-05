# CryptIt
[![Build Status](https://travis-ci.org/KKStudLab/cryptit.svg?branch=master)](https://travis-ci.org/KKStudLab/cryptit)
[![Code Health](https://landscape.io/github/KKStudLab/cryptit/master/landscape.svg?style=flat)](https://landscape.io/github/KKStudLab/cryptit/master)
[![Requirements Status](https://requires.io/github/KKStudLab/cryptit/requirements.svg?branch=master)](https://requires.io/github/KKStudLab/cryptit/requirements/?branch=master)
[![Python](https://img.shields.io/badge/python-2.7+,%203.5+-blue.svg)](https://github.com/KKStudLab/cryptit)
[![PyPI version](https://badge.fury.io/py/cryptit.svg)](https://badge.fury.io/py/cryptit)

## Installation

### PyPI
To install CryptIt, run this command in your terminal:
```sh
$ pip install cryptit
```
This is the preferred method to install CryptIt, as it will always install the most recent stable release.

### Source files
In case you downloaded or cloned the source code from [GitHub] or your own fork, you can run the following to install cameo for development:

```sh
$ git clone https://github.com/KKStudLab/cryptit.git
$ cd cryptit
$ vitualenv --python=python[version] venv
$ source venv/bin/active
$ pip install --editable .
```

## Basic Usage
Available command list:
```sh
$ cryptit -h
usage: cryptit [-h] [-e] [-d] [path]

positional arguments:
  path           path to target file or directory

optional arguments:
  -h, --help     show this help message and exit
  -e, --encrypt  encryption mode [by default]
  -d, --decrypt  decryption mode
```

### Encryption mode
For encrypt files on your PC open terminal and type following command use -e option and put just path to target file or directory.
```
root@kali:~/Pictures$ cryptit -e .
[*] Start time: 2017-09-05_21-36-30
[*] CryptIt mode: Encryption(AES-256 CBC mode)
[*] Path: .
[!] Enter your password: 
[#] Encrypting files: 3it [00:00, 47.33it/s]
[*] Encrypting was successful!!
[*] Enctyption time: 0.0646049976349 seconds
[*] Print archive info(y/n): y


Archive info:
(cryptit_2017-09-05_21-36-30.zip)

Screenshot from 2017-08-18 21-47-25.png.aes
[!] Comment:		
[!] Modified:		2017-09-05 21:36:32
[!] System:		3 (0 = Windows, 3 = Unix)
[!] ZIP version:	20
[!] Compressed:		244264 bytes
[!] Uncompressed:	244264 bytes
Wallpapers/36571921725_64b1d675cf_k.jpg.aes
[!] Comment:		
[!] Modified:		2017-09-05 21:36:32
[!] System:		3 (0 = Windows, 3 = Unix)
[!] ZIP version:	20
[!] Compressed:		666952 bytes
[!] Uncompressed:	666952 bytes
```

### Decryption mode
```
root@kali:~/Pictures$ cryptit -d cryptit_2017-09-05_21-36-30.zip 
[*] Start time: 2017-09-05_21-48-36
[*] CryptIt mode: Decryption(AES-256 CBC mode)
[*] Path: cryptit_2017-09-05_21-36-30.zip
[!] Enter your password: 
[#] Decrypting files: 2it [00:00, 102.09it/s]
[*] Decrypting was successful!!
[*] Dectyption time: 0.0205860137939 seconds
[!] Output dir: /Pictures/cryptit_2017-09-05_21-36-30
```

### Bugs, issues and contributing

If you find [bugs] or have [suggestions] about improving the module, don't hesitate to contact [us].


### License

This project is licensed under the MIT License - see the [LICENSE] file for details

Copyright (c) 2017 - [Maxim Krivich], [Ivan Kudryashov]

[maxkrivich.github.io](https://maxkrivich.github.io/)

[GitHub]: <https://github.com/KKStudLab/cryptit>
[bugs]: <https://github.com/KKStudLab/cryptit/issues>
[suggestions]: <https://github.com/KKStudLab/cryptit/issues>
[us]: <https://github.com/KKStudLab/cryptit/blob/master/AUTHORS.md>
[LICENSE]: <https://github.com/KKStudLab/cryptit/blob/master/LICENSE>
[Maxim Krivich]: <https://github.com/maxkrivich>
[Ivan Kudryashov]: <https://github.com/entick>
