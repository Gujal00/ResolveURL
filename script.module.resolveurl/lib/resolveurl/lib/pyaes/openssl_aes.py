# The MIT License (MIT)
#
# Copyright (c) 2017 Diego Fernando Nieto
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# This is a pure-Python implementation of the AES algorithm and AES common
# modes of operation.

# See: https://en.wikipedia.org/wiki/Advanced_Encryption_Standard

# Honestly, the best description of the modes of operations are the wonderful
# diagrams on Wikipedia. They explain in moments what my words could never
# achieve. Hence the inline documentation here is sparer than I'd prefer.
# See: https://en.wikipedia.org/wiki/Block_cipher_mode_of_operation

# Supported key sizes:
#   128-bit
#   192-bit
#   256-bit


# Supported modes of operation:
#   ECB - Electronic Codebook
#   CBC - Cipher-Block Chaining
#   CFB - Cipher Feedback
#   OFB - Output Feedback
#   CTR - Counter


# See the README.md for API details and general information.

import random
import math
import base64
import hashlib
from resolveurl.lib.pyaes.aes import AES, AESModeOfOperationCTR, AESModeOfOperationCBC, AESModeOfOperationCFB, AESModeOfOperationECB, AESModeOfOperationOFB, AESModesOfOperation, Counter
from os import urandom
# Python 3 compatibility
import six


BS = 32


def pad(s):
    return s + (BS - len(s) % BS) * chr(BS - len(s) % BS)


def unpad(s):
    return s[:-ord(s[len(s) - 1:])]


"""
    AES: http://csrc.nist.gov/publications/fips/fips197/fips-197.pdf

    JavaScript: https://github.com/mdp/gibberish-aes

    Python: https://stackoverflow.com/questions/12221484/how-come-i-cant-decrypted-my-aes-encrypted-message-on-someone-elses-aes-decrypt
            https://stackoverflow.com/questions/13907841/implement-openssl-aes-encryption-in-python
            https://stackoverflow.com/questions/16761458/how-to-aes-encrypt-decrypt-files-using-python-pycrypto-in-an-openssl-compatible


"""


def randArr(num):
    """
        JavaScript Code:

        var result = [], i;
        for (i = 0; i < num; i++) {
            result = result.concat(Math.floor(Math.random() * 256));
        }
        return result;
    """
    return map(lambda i: math.floor(random.random() * 256), six.moves.range(num))


def s2a(s, binary):
    """
        JavaScript Code:

        var array = [], i;
        if (! binary) {
            string = enc_utf8(string);
        }
        for (i = 0; i < string.length; i++) {
            array[i] = string.charCodeAt(i);
        }
        return array;
    """
    return map(lambda s: ord(s), list(s))


def openSSLKey(passwordArr, saltArr, Nr, Nk):
    # Nr: Default to 256 Bit Encryption
    # // Number of rounds depends on the size of the AES in use
    # // 3 rounds for 256
    # //        2 rounds for the key, 1 for the IV
    # // 2 rounds for 128
    # //        1 round for the key, 1 round for the IV
    # // 3 rounds for 192 since it's not evenly divided by 128 bits

    # if !Nr: Nr = 14
    # if !Nk: Nk = 8

    # if Nr >= 12: rounds = 3
    # else: rounds = 2

    # key = []
    # iv = []
    # md5_hash = []
    # result = []
    # data00 = passwordArr + saltArr
    """
    JavaScript Code:

        var rounds = Nr >= 12 ? 3: 2,
        key = [],
        iv = [],
        md5_hash = [],
        result = [],
        data00 = passwordArr.concat(saltArr),
        i;
        md5_hash[0] = MD5(data00);
        result = md5_hash[0];
        for (i = 1; i < rounds; i++) {
            md5_hash[i] = MD5(md5_hash[i - 1].concat(data00));
            result = result.concat(md5_hash[i]);
        }
        key = result.slice(0, 4 * Nk);
        iv = result.slice(4 * Nk, 4 * Nk + 16);
        return {
            key: key,
            iv: iv
        };

    """
    pass


def derive_key_and_iv(password, salt, key_length, iv_length):
    d = d_i = six.ensure_binary('')
    password = six.ensure_binary(password)
    while len(d) < key_length + iv_length:
        d_i = hashlib.md5(d_i + password + salt).digest()
        d += d_i
    return d[:key_length], d[key_length:key_length + iv_length]


class AESCipher:
    def __init__(self):
        pass

    def encrypt(self, plaintext, password, key_length=32):
        data = ""
        bs = 16
        salt = urandom(bs - len('Salted__'))

        key, iv = derive_key_and_iv(password, salt, key_length, bs)
        cipher = AESModeOfOperationCBC(key, iv)

        data += 'Salted__' + salt
        chunk = plaintext

        if len(chunk) == 0 or len(chunk) % bs != 0:
            padding_length = (bs - len(chunk) % bs) or bs
            chunk += padding_length * chr(padding_length)

        data += cipher.encrypt(chunk)
        return base64.b64encode(data)

    def decrypt(self, data, password, key_length=32):
        data = base64.b64decode(data)
        bs = 16
        salt = data[len("Salted__"): 16]
        data = data[len("Salted__") + len(salt):]

        key, iv = derive_key_and_iv(password, salt, key_length, bs)
        cipher = AESModeOfOperationCBC(key, iv)

        decryptedBytes = six.ensure_binary('')
        for x in range(len(data) // 16):
            # Decrypt it
            blockBytes = data[x * 16: (x * 16) + 16]
            decryptedBytes += cipher.decrypt(blockBytes)

        padding = decryptedBytes[-1]
        padding_length = ord(padding) if isinstance(padding, six.string_types) else padding

        return six.ensure_str(decryptedBytes[:-padding_length])
