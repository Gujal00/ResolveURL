# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector for openload.io
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
# by DrZ3r0
# ------------------------------------------------------------
# Modified by Shani 
import re
from resolveurl import common


class AADecoder(object):
    def __init__(self, aa_encoded_data):
        self.encoded_str = aa_encoded_data.replace('/*´∇｀*/', '')

        self.b = ["(c^_^o)", "(ﾟΘﾟ)", "((o^_^o) - (ﾟΘﾟ))", "(o^_^o)",
                  "(ﾟｰﾟ)", "((ﾟｰﾟ) + (ﾟΘﾟ))", "((o^_^o) +(o^_^o))", "((ﾟｰﾟ) + (o^_^o))",
                  "((ﾟｰﾟ) + (ﾟｰﾟ))", "((ﾟｰﾟ) + (ﾟｰﾟ) + (ﾟΘﾟ))", "(ﾟДﾟ) .ﾟωﾟﾉ", "(ﾟДﾟ) .ﾟΘﾟﾉ",
                  "(ﾟДﾟ) ['c']", "(ﾟДﾟ) .ﾟｰﾟﾉ", "(ﾟДﾟ) .ﾟДﾟﾉ", "(ﾟДﾟ) [ﾟΘﾟ]"]

    def is_aaencoded(self):
        idx = self.encoded_str.find("ﾟωﾟﾉ= /｀ｍ´）ﾉ ~┻━┻   //*´∇｀*/ ['_']; o=(ﾟｰﾟ)  =_=3; c=(ﾟΘﾟ) =(ﾟｰﾟ)-(ﾟｰﾟ); ")
        if idx == -1:
            return False

        is_encoded = self.encoded_str.find("(ﾟДﾟ)[ﾟoﾟ]) (ﾟΘﾟ)) ('_');", idx) != -1
        return is_encoded

    def base_repr(self, number, base=2, padding=0):
        digits = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        if base > len(digits):
            base = len(digits)

        num = abs(number)
        res = []
        while num:
            res.append(digits[num % base])
            num //= base
        if padding:
            res.append('0' * padding)
        if number < 0:
            res.append('-')
        return ''.join(reversed(res or '0'))

    def decode_char(self, enc_char, radix):
        end_char = "+ "
        str_char = ""
        while enc_char != '':
            found = False
            # for i in range(len(self.b)):
            #    print self.b[i], enc_char.find(self.b[i])
            #    if enc_char.find(self.b[i]) == 0:
            #        str_char += self.base_repr(i, radix)
            #        enc_char = enc_char[len(self.b[i]):]
            #        found = True
            #        break

            # print 'found', found, enc_char
            if not found:
                for i in range(len(self.b)):
                    enc_char = enc_char.replace(self.b[i], str(i))
                # enc_char = enc_char.replace('(ﾟΘﾟ)', '1').replace('(ﾟｰﾟ)', '4').replace('(c^_^o)', '0').replace('(o^_^o)', '3')
                # print 'enc_char', enc_char
                startpos = 0
                findClose = True
                balance = 1
                result = []
                if enc_char.startswith('('):
                    l = 0

                    for t in enc_char[1:]:
                        l += 1
                        # print 'looping', findClose, startpos, t, balance
                        if findClose and t == ')':
                            balance -= 1
                            if balance == 0:
                                result += [enc_char[startpos:l + 1]]
                                findClose = False
                                continue
                        elif not findClose and t == '(':
                            startpos = l
                            findClose = True
                            balance = 1
                            continue
                        elif t == '(':
                            balance += 1

                if result is None or len(result) == 0:
                    return ""
                else:
                    for r in result:
                        value = self.decode_digit(r, radix)
                        # print 'va', value
                        str_char += value
                        if value == "":
                            return ""

                    return str_char

            enc_char = enc_char[len(end_char):]

        return str_char

    def parseJSString(self, s):
        try:
            # print s
            # offset = 1 if s[0] == '+' else 0
            tmp = (s.replace('!+[]', '1').replace('!![]', '1').replace('[]', '0'))  # .replace('(','str(')[offset:])
            val = int(eval(tmp))
            return val
        except:
            pass

    def decode_digit(self, enc_int, radix):
        # enc_int = enc_int.replace('(ﾟΘﾟ)', '1').replace('(ﾟｰﾟ)', '4').replace('(c^_^o)', '0').replace('(o^_^o)', '3')
        # print 'enc_int before', enc_int
        # for i in range(len(self.b)):
        # print self.b[i], enc_char.find(self.b[i])
        # if enc_char.find(self.b[i]) > 0:
        #    str_char += self.base_repr(i, radix)
        #    enc_char = enc_char[len(self.b[i]):]
        #    found = True
        #    break
        #    enc_int=enc_int.replace(self.b[i], str(i))
        # print 'enc_int before', enc_int

        try:
            return str(eval(enc_int))
        except: pass
        rr = '(\(.+?\)\))\+'
        rerr = enc_int.split('))+')  # re.findall(rr, enc_int)
        v = ""
        # print rerr
        for c in rerr:
            if len(c) > 0:
                # print 'v', c
                if c.strip().endswith('+'):
                    c = c.strip()[:-1]
                # print 'v', c
                startbrackets = len(c) - len(c.replace('(', ''))
                endbrackets = len(c) - len(c.replace(')', ''))
                if startbrackets > endbrackets:
                    c += ')' * (startbrackets - endbrackets)
                if '[' in c:
                    v += str(self.parseJSString(c))
                else:
                    # print c
                    v += str(eval(c))
        return v

        # unreachable code
        # mode 0=+, 1=-
        # mode = 0
        # value = 0

        # while enc_int != '':
        #     found = False
        #     for i in range(len(self.b)):
        #         if enc_int.find(self.b[i]) == 0:
        #             if mode == 0:
        #                 value += i
        #             else:
        #                 value -= i
        #             enc_int = enc_int[len(self.b[i]):]
        #             found = True
        #             break

        #     if not found:
        #         return ""

        #     enc_int = re.sub('^\s+|\s+$', '', enc_int)
        #     if enc_int.find("+") == 0:
        #         mode = 0
        #     else:
        #         mode = 1

        #     enc_int = enc_int[1:]
        #     enc_int = re.sub('^\s+|\s+$', '', enc_int)

        # return self.base_repr(value, radix)

    def decode(self):
        self.encoded_str = re.sub('^\s+|\s+$', '', self.encoded_str)

        # get data
        pattern = (r"\(ﾟДﾟ\)\[ﾟoﾟ\]\+ (.+?)\(ﾟДﾟ\)\[ﾟoﾟ\]\)")
        result = re.search(pattern, self.encoded_str, re.DOTALL)
        if result is None:
            common.logger.log_debug("AADecoder: data not found")
            return False

        data = result.group(1)

        # hex decode string
        begin_char = "(ﾟДﾟ)[ﾟεﾟ]+"
        alt_char = "(oﾟｰﾟo)+ "

        out = ''
        # print data
        while data != '':
            # Check new char
            if data.find(begin_char) != 0:
                common.logger.log_debug("AADecoder: data not found")
                return False

            data = data[len(begin_char):]

            # Find encoded char
            enc_char = ""
            if data.find(begin_char) == -1:
                enc_char = data
                data = ""
            else:
                enc_char = data[:data.find(begin_char)]
                data = data[len(enc_char):]

            radix = 8
            # Detect radix 16 for utf8 char
            if enc_char.find(alt_char) == 0:
                enc_char = enc_char[len(alt_char):]
                radix = 16

            # print repr(enc_char), radix
            # print enc_char.replace('(ﾟΘﾟ)', '1').replace('(ﾟｰﾟ)', '4').replace('(c^_^o)', '0').replace('(o^_^o)', '3')

            # print 'The CHAR', enc_char, radix
            str_char = self.decode_char(enc_char, radix)

            if str_char == "":
                common.logger.log_debug("no match :  ")
                common.logger.log_debug(data + "\nout = " + out + "\n")
                return False
            # print 'sofar', str_char, radix,out

            out += chr(int(str_char, radix))
            # print 'sfar', chr(int(str_char, radix)), out

        if out == "":
            common.logger.log_debug("no match : " + data)
            return False

        return out
