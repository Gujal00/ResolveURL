"""
A pure python implementation of RC4 decryption
"""

import struct
import base64
import six


def decrypt(cipher_text, key):
    def compat_ord(c):
        return c if isinstance(c, int) else ord(c)

    res = six.ensure_binary('')
    cipher_text = base64.b64decode(cipher_text)
    key_len = len(key)
    S = list(range(256))

    j = 0
    for i in range(256):
        j = (j + S[i] + ord(key[i % key_len])) % 256
        S[i], S[j] = S[j], S[i]

    i = 0
    j = 0
    for m in range(len(cipher_text)):
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        k = S[(S[i] + S[j]) % 256]
        res += struct.pack('B', k ^ compat_ord(cipher_text[m]))

    return six.ensure_str(res)
