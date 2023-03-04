"""
    Copyright (C) 1999 Masanao Izumo <iz@onicos.co.jp>
    Version: 1.0
    LastModified: Dec 25 1999
    This library is free. You can redistribute it and/or modify it.
    Source code: http://www33146ue.sakura.ne.jp/staff/iz/amuse/javascript/expert/base64.txt

    Adapted for use in ResolveURL
"""

base64_encode_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"

base64_decode_chars = [
    -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
    -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
    -1, -1, -1, 62, -1, -1, -1, 63, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, -1, -1,
    -1, -1, -1, -1, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
    15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, -1, -1, -1, -1, -1, -1, 26, 27, 28,
    29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48,
    49, 50, 51, -1, -1, -1, -1, -1
]


def base64_encode(text):
    length = len(text)
    i = 0
    out = []
    while i < length:
        c1 = ord(text[i]) & 0xff
        i += 1
        if i == length:
            out.append(base64_encode_chars[c1 >> 2])
            out.append(base64_encode_chars[(c1 & 0x3) << 4])
            out.append('==')
            break
        c2 = ord(text[i])
        i += 1
        if i == length:
            out.append(base64_encode_chars[c1 >> 2])
            out.append(base64_encode_chars[((c1 & 0x3) << 4) | ((c2 & 0xF0) >> 4)])
            out.append(base64_encode_chars[(c2 & 0xF) << 2])
            out.append('=')
            break
        c3 = ord(text[i])
        i += 1
        out.append(base64_encode_chars[c1 >> 2])
        out.append(base64_encode_chars[((c1 & 0x3) << 4) | ((c2 & 0xF0) >> 4)])
        out.append(base64_encode_chars[((c2 & 0xF) << 2) | ((c3 & 0xC0) >> 6)])
        out.append(base64_encode_chars[c3 & 0x3F])
    return ''.join(out)


def base64_decode(text):
    length = len(text)
    i = 0
    out = []
    while i < length:
        while True:
            c1 = base64_decode_chars[ord(text[i]) & 0xff]
            i += 1
            if not (i < length and c1 == -1):
                break
        if c1 == -1:
            break
        while True:
            c2 = base64_decode_chars[ord(text[i]) & 0xff]
            i += 1
            if not (i < length and c2 == -1):
                break
        if c2 == -1:
            break
        out.append(chr((c1 << 2) | ((c2 & 0x30) >> 4)))
        while True:
            c3 = ord(text[i]) & 0xff
            i += 1
            if c3 == 61:
                return ''.join(out)
            c3 = base64_decode_chars[c3]
            if not (i < length and c3 == -1):
                break
        if c3 == -1:
            break
        out.append(chr(((c2 & 0XF) << 4) | ((c3 & 0x3C) >> 2)))
        while True:
            c4 = ord(text[i]) & 0xff
            i += 1
            if c4 == 61:
                return ''.join(out)
            c4 = base64_decode_chars[c4]
            if not (i < length and c4 == -1):
                break
        if c4 == -1:
            break
        out.append(chr(((c3 & 0x03) << 6) | c4))
    return ''.join(out)
