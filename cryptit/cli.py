#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MIT License

Copyright (c) 2017 Maxim Krivich

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import os
import time
import struct
import getpass
import zipfile
import argparse

from datetime import datetime
from tqdm import tqdm, trange
from Crypto.Cipher import AES
from Crypto.Hash import SHA3_256
from Crypto.Random import get_random_bytes

from __init__ import logger


def is_valid_path(parser, arg):
    if not os.path.exists(arg):
        parser.error("The path {} does not exist!".format(arg))
    else:
        return arg


def parse_args():
    parser = argparse.ArgumentParser(add_help=True, description='')
    parser.add_argument('-e', '--encrypt',
                        action='store_false', help='encryption mode')
    parser.add_argument('-d', '--decrypt',
                        action='store_true', help='decryption mode')
    parser.add_argument('path', nargs='?', type=lambda x: is_valid_path(
        parser, x), default=os.getcwd(), help='path to target file or directory')

    return parser.parse_args()


def walkdir(folder):  # TODO handle os access excetions
    for dirpath, dirs, files in os.walk(folder):
        for filename in files:
            yield os.path.join(dirpath, filename)


def encrypt_file(filepath, sfilepath, encryptor, iv, chunksize=64 * 1024):
    filesize = os.path.getsize(filepath)
    with open(filepath, 'rb') as infile:
        with open(filepath.replace(sfilepath,'')+ '.aes', 'wb') as outfile:
            outfile.write(struct.pack('<Q', filesize))
            outfile.write(iv)

            while True:
                chunk = infile.read(chunksize)
                if len(chunk) == 0:
                    break
                elif len(chunk) % 16 != 0:
                    chunk += ' ' * (16 - len(chunk) % 16)

                outfile.write(encryptor.encrypt(chunk))


def decrypt_file():
    # TODO implement this function
    pass


def print_info(archive_name):
    zf = zipfile.ZipFile(archive_name)
    for info in zf.infolist():
        print(info.filename)
        print('[!] Comment:\t\t{}'.format(info.comment))
        print('[!] Modified:\t\t{}'.format(datetime(*info.date_time)))
        print('[!] System:\t\t{} (0 = Windows, 3 = Unix)'.format(info.create_system))
        print('[!] ZIP version:\t{}'.format(info.create_version))
        print('[!] Compressed:\t\t{} bytes'.format(info.compress_size))
        print('[!] Uncompressed:\t{} bytes'.format(info.file_size))


def main():
    try:
        arg = parse_args()
        is_file, is_dir = False, False
        if os.path.isfile(arg.path):
            is_file = True
        elif os.path.isdir(arg.path):
            is_dir = True
        else:
            raise ValueError(
                'The path {} does not file and directory!'.format(arg.path))

        d = datetime.strftime(datetime.now(), "%Y-%m-%d_%H-%M-%S")

        print('[*] Start time: {}'.format(d))
        print('[*] CryptIt mode: {}(AES-256 CBC mode)'.format('Decryption' if arg.decrypt else 'Encryption'))
        print('[*] Path: {}'.format(arg.path))

        passwd = ''

        while not len(passwd):
            passwd = getpass.getpass('[!] Enter your password: ')

        if arg.decrypt:
            pass
        else:
            # init aes-256
            h_obj = SHA3_256.new()
            h_obj.update(passwd)
            key = h_obj.digest()
            iv = get_random_bytes(16)
            encryptor = AES.new(key, AES.MODE_CBC, IV=iv)
            new_dir = 'cryptit_{}'.format(d)

            zf = zipfile.ZipFile(new_dir + '.zip', mode='w')

            if is_dir:
                start_time = time.time()
                sfilepath = arg.path.rstrip(os.sep) + os.sep
                for filepath in tqdm(walkdir(arg.path), desc='[#] Encrypting files'):
                    if not new_dir in filepath:
                        encrypt_file(filepath, sfilepath, encryptor, iv)
                        zf.write(filepath.replace(sfilepath,'') + '.aes')
                        try:
                            os.remove(filepath + '.aes')
                        except OSError:
                            pass
                end_time = time.time()
                print('[*] Encrypting was successful!!')
                print('[*] Enctyption time: {} seconds'.format(end_time - start_time))
            else:
                start_time = time.time()
                encrypt_file(arg.path, encryptor, iv)
                zf.write(os.path.join(new_dir, arg.path) + '.aes')
                end_time = time.time()
                print('[*] Encrypting was successful!!')
                print('[*] Enctyption time: {} seconds'.format(end_time - start_time))
            zf.close()

            try:
                input = raw_input
            except NameError:
                pass

            ans = input('[*] Print archive info(y/n): ')
            if ans in ('y', 'Y'):
                print('\n\nArchive info:\n({})\n'.format(new_dir + '.zip'))
                print_info(new_dir + '.zip')

    except Exception as e:
        logger.exception(e)


if __name__ == '__main__':
    main()
