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
import sys
import uuid
import time
import struct
import getpass
import zipfile
import argparse
import logging.config

from tqdm import tqdm
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Hash import SHA3_256, HMAC, SHA256
from Crypto.Random import get_random_bytes

logger = logging.getLogger(__name__)
logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,  # this fixes the problem
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': True
        }
    }
})


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
        parser, x), default=None, help='path to target file or directory')

    res = parser.parse_args()

    if res.path is None:
        parser.print_help()
        sys.exit(-1)

    return res


def walkdir(folder):  # TODO handle os access excetions
    a = 1
    for dirpath, dirs, files in os.walk(folder):
        if len(dirs):
            a += 1
        for filename in files:
            yield os.path.join(dirpath, filename)


def encrypt_file(key, filepath, sfilepath, iv, chunksize=AES.block_size * 1024):
    filesize = os.path.getsize(filepath)
    encryptor = AES.new(key, AES.MODE_CBC, IV=iv)
    h = HMAC.new(key, digestmod=SHA256)

    with open(filepath, 'rb') as infile:
        with open(filepath.replace(sfilepath, '') + '.aes', 'wb') as outfile:
            outfile.seek(32, 0)
            outfile.write(struct.pack('<Q', filesize))
            outfile.write(iv)

            while True:
                chunk = infile.read(chunksize)
                if len(chunk) == 0:
                    break
                elif len(chunk) % AES.block_size != 0:
                    chunk += b' ' * (AES.block_size - len(chunk) % AES.block_size)
                enc = encryptor.encrypt(chunk)
                h.update(enc)
                outfile.write(enc)
            outfile.seek(0, 0)
            outfile.write(h.digest())


def decrypt_file(key, filename, chunksize=AES.block_size * 1024):
    if os.path.splitext(filename)[1] != '.aes':
        raise ValueError('File {} does not a .aes'.format(filename))

    h = HMAC.new(key, digestmod=SHA256)

    with open(filename, 'rb') as infile:
        mac = infile.read(32)
        origsize = struct.unpack('<Q', infile.read(struct.calcsize('Q')))[0]
        iv = infile.read(AES.block_size)
        decryptor = AES.new(key, AES.MODE_CBC, IV=iv)

        with open(filename.rstrip('.aes'), 'wb') as outfile:
            while True:
                chunk = infile.read(chunksize)
                if not len(chunk):
                    break
                h.update(chunk)
                outfile.write(decryptor.decrypt(chunk))
            outfile.truncate(origsize)

        try:
            h.verify(mac)
        except ValueError:
            logger.info("The file or the key is wrong")
            os.remove(filename)
            sys.exit(-1)


def print_info(archive_name):
    zf = zipfile.ZipFile(archive_name)
    for info in zf.infolist():
        print(info.filename)
        print('[!] Modified:\t\t{}'.format(datetime(*info.date_time)))
        print('[!] System:\t\t{} (0 = Windows, 3 = Unix)'.format(
            info.create_system))
        print('[!] ZIP version:\t{}'.format(info.create_version))
        print('[!] Compressed:\t\t{} bytes'.format(info.compress_size))
        print('[!] Uncompressed:\t{} bytes'.format(info.file_size))


def print_started_info(arg):
    d = datetime.strftime(datetime.now(), "%Y-%m-%d_%H-%M-%S")
    print('[*] Start time: {}'.format(d))
    print('[*] CryptIt mode: {}(AES-256 CBC mode)'.format(
        'Decryption' if arg.decrypt else 'Encryption'))
    print('[*] Path: {}'.format(arg.path))


def get_pswd():
    passwd = ''
    while not len(passwd):
        passwd = getpass.getpass('[!] Enter your password: ')
    return passwd


def decryption(arg, is_file, key):
    if is_file and zipfile.is_zipfile(arg.path):
        zf = zipfile.ZipFile(arg.path, mode='r')
        new_path = os.path.join(
            os.getcwd(), arg.path.replace('.zip', ''))
        zf.extractall(new_path)
        zf.close()
        start_time = time.time()
        for filepath in tqdm(walkdir(new_path), desc='[#] Decrypting files'):
            decrypt_file(key, filepath)
            try:
                os.remove(filepath)
            except OSError:
                pass
        end_time = time.time()
        print('[*] Decrypting was successful!!')
        print('[*] Dectyption time: {} seconds'.format(end_time - start_time))
        print('[!] Output dir: {}'.format(new_path))


def encryption(arg, is_dir, key):
    u = uuid.uuid1()
    d = str(u.hex)
    iv = get_random_bytes(AES.block_size)
    new_dir = 'cryptit_{}'.format(d)

    zf = zipfile.ZipFile(new_dir + '.zip', mode='w')

    if is_dir:
        start_time = time.time()
        sfilepath = arg.path.rstrip(os.sep) + os.sep
        for filepath in tqdm(walkdir(arg.path), desc='[#] Encrypting files'):
            if new_dir not in filepath:
                encrypt_file(key, filepath, sfilepath, iv)
                zf.write(filepath.replace(sfilepath, '') + '.aes')
                try:
                    for file in walkdir(os.getcwd()):
                        if str(os.path.abspath(file)).split('.')[-1] == 'aes':
                            os.remove(file)
                except OSError:
                    pass
        end_time = time.time()
        print('[*] Encrypting was successful!!')
        print('[*] Enctyption time: {} seconds'.format(end_time - start_time))
    else:
        start_time = time.time()
        encrypt_file(key, arg.path, os.getcwd(), iv)
        zf.write(arg.path + '.aes')
        end_time = time.time()
        try:
            os.remove(arg.path + '.aes')
        except OSError:
            pass
        print('[*] Encrypting was successful!!')
        print('[*] Enctyption time: {} seconds'.format(end_time - start_time))
    zf.close()

    sys.stdout.write('[*] Print archive info(y/n): ')
    sys.stdout.flush()
    ans = sys.stdin.readline().rstrip()
    if ans in ('y', 'Y'):
        print('\n\nArchive info:\n({})\n'.format(new_dir + '.zip'))
        print_info(new_dir + '.zip')


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

        print_started_info(arg)

        passwd = str.encode(get_pswd())

        h_obj = SHA3_256.new()
        h_obj.update(passwd)
        key = h_obj.digest()

        if arg.decrypt:
            decryption(arg, is_file, key)
        else:
            encryption(arg, is_dir, key)

    except Exception as e:
        logger.exception(e)


if __name__ == '__main__':
    main()
