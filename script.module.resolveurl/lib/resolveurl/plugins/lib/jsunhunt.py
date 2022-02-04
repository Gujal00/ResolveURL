"""
    Javascript (h,u,n,t,e,r) Deobfuscator
    Copyright (C) 2019 jairoxyz, gujal

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.


    usage:

    if detect(some_string):
        unhunted = unhunt(some_string)

"""

from functools import reduce
import re


class UnpackingError(Exception):
    """Badly packed source or general error. Argument is a
    meaningful description."""
    pass


def detect(source):
    """Detects whether `source` is H.U.N.T.E.R. coded."""
    source = source.replace(' ', '')
    if re.search(r'eval\(function\(h,u,n,t,e,r', source):
        return True
    else:
        return False


def _dehunt(d, e, f):
    g = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ+/"
    h = g[0:e]
    i = g[0:f]
    d = d[::-1]
    j = reduce(lambda a, b: a + int(h[int(b[1])]) * (e ** int(b[0])) if int(h[int(b[1])]) != -1 else None, enumerate(d), 0)
    k = ""
    while j > 0:
        k = i[int(j % f)] + k
        j = (j - (j % f)) / f

    return k or "0"


def _jsunhunter(h, n, t, e):
    r = ""
    i = 0
    while i < len(h):
        s = ""
        while h[i] != n[e]:
            s += h[i]
            i += 1

        for j in enumerate(n):
            s = s.replace(j[1], str(j[0]))

        r += chr(int(_dehunt(s, e, 10)) - t)
        i += 1

    return r


def _filterargs(source):
    """Juice from a source file the four args needed by decoder."""
    argsregex = r'\(h,\s*u,\s*n,\s*t,\s*e,\s*r\).+}\("([^"]+)",[^,]+,\s*"([^"]+)",\s*(\d+),\s*(\d+)'
    try:
        payload, n, t, e = re.search(argsregex, source, re.DOTALL).groups()
        return payload, n, int(t), int(e)
    except AttributeError:
        raise UnpackingError('Corrupted h.u.n.t.e.r. data.')


def unhunt(source):
    payload, n, t, e = _filterargs(source)
    return _jsunhunter(payload, n, t, e)


if __name__ == "__main__":
    test = '''eval(function(h, u, n, t, e, r) {r = "";for (var i = 0, len = h.length; i < len; i++) {var s = "";while (h[i] !== n[e]) {s += h[i];i++}for (var j = 0; j < n.length; j++) s = s.replace(new RegExp(n[j], "g"), j);console.log(_0xe41c(s, e, 10) - t);r += String.fromCharCode(_0xe41c(s, e, 10) - t)}}("jjMErrQEryyEriQErrrEryiErimEriOEriQEjjMErrQEriOEryjEriyErrmEryyEryiErrMEryyEryjEriiEjrMErriErrmEryiErrmEjimEjjMErQrEjjMEryjErryEryiEryyEryjEriQEjjMEryOErimEriQErriEriOEryOEjiQErrmEryiEriOErrjEjrMErirErryErQmErmyEryjEriiEjimEjjMEjirEjjMEjrOEjQOEryrEryiEryjErryErrmEriyEjQyEjrOEjjMEjirEjjMEryrEryiEryjEjMQErrmEriyErryEjjMEjirEjjMEjrOEjrQEryrErrrEriOErriErryEjQyEjrOEjjMEjirEjjMErriErrmEryiErrmEjiQEryrErrrEriOErriErryEjjMEjirEjjMEjrOEjrQErryEryMEriMErimEryjErryEryrEjQyEjrOEjjMEjirEjjMErriErrmEryiErrmEjiQEryiEryrEjQrEjjMErQyEjjMErrQEryyEriQErrrEryiErimEriOEriQEjjMErrmEryyEryiErrMErrrErrMErryErrrErirEjrMEjimEjjMErQrEjjMErimErrQEjjMEjrMEryOErimEriQErriEriOEryOEjiQEriMErryErryEryjEjyyEjimEjjMErQrEjjMEjriEjiQErrmErijErrmEryMEjrMErQrEjjMEryyEryjEriiEjQjEjjMErrmEryyEryiErrMErmyEryjEriiEjiiEjjMEryMErrMEryjEjOQErimErryEriiErriEryrEjQjEjjMErQrEjjMEryOErimEryiErrMEjOrEryjErryErriErryEriQEryiErimErrmEriiEryrEjQjEjjMEryiEryjEryyErryEjjMErQyEjiiEjjMEryrEryyErrrErrrErryEryrEryrEjQjEjjMErrQEryyEriQErrrEryiErimEriOEriQEjjMEjrMEryjErryEryrEriMEriOEriQEryrErryEjimEjjMErQrEjjMErrmEryyEryiErrMErmyEryjEriiEjjMEjQyEjjMErrQEriOEryjEriyErrmEryyEryiErrMEryyEryjEriiEjrMEryjErryEryrEriMEriOEriQEryrErryEjimEjQrEjjMEryrErryEryiErmiErimEriyErryEriOEryyEryiEjrMErrmEryyEryiErrMErrrErrMErryErrrErirEjiiEjjMEjyyEjjMEjijEjjMEjyQEjiMEjjMEjijEjjMEjymEjiMEjiMEjiMEjimEjQrEjjMErQyEjiiEjjMErryEryjEryjEriOEryjEjQjEjjMErrQEryyEriQErrrEryiErimEriOEriQEjjMEjrMEjimEjjMErQrEjjMErimErrQEjjMEjrMErrQErrmErimEriiEjOrEriOEryyEriQEryiEjjMEjQiEjjMEjyrEjimEjjMErQrEjjMEryrErryEryiErmiErimEriyErryEriOEryyEryiEjrMErrmEryyEryiErrMErrrErrMErryErrrErirEjiiEjjMEjyyEjiMEjiMEjiMEjimEjQrEjjMErrQErrmErimEriiEjOrEriOEryyEriQEryiEjirEjirEjQrEjjMErQyEjjMErryEriiEryrErryEjjMErQrEjjMEryrEryiEriOEriMEriMEriiErrmErQmErryEryjEjrMEjimEjQrEjjMErQyEjjMErQyEjjMErQyEjimEjQrEjjMErQyEjjMErQyEjjMErrQEryyEriQErrrEryiErimEriOEriQEjjMEriMErryErryEryjErrrErrMErryErrrErirEjrMEjimEjjMErQrEjjMEryQErrmEryjEjjMEriMErmrEryiEryrEjjMEjQyEjjMEriMErryErryEryjEjyyEjiQErrOErryEryiErmrEryiErrmEryiEryrEjrMEjimEjQrEjjMErimErrQEjjMEjrMEriMErmrEryiEryrEjiQEryiEriOEryiErrmEriiEjOMEryiEryiEriMEjOiEriOEryOEriQEriiEriOErrmErriErryErriEjjMEjQyEjQyEjQyEjjMEjiMEjjMEjrQEjrQEjjMEriMErmrEryiEryrEjiQEryiEriOEryiErrmEriiEjMMEjyjEjMMEjOiEriOEryOEriQEriiEriOErrmErriErryErriEjjMEjQyEjQyEjQyEjjMEjiMEjimEjjMErQrEjjMEryrEryiEriOEriMEriMEriiErrmErQmErryEryjEjrMEjimEjQrEjjMErQyEjjMErQyEjjMErrQEryyEriQErrrEryiErimEriOEriQEjjMEryrEryiEriOEriMEriMEriiErrmErQmErryEryjEjrMEjimEjjMErQrEjjMEriMEriiErrmErQmErryEryjEjMOErrjErijEjiQEryrEryiEriOEriMEjrMEjimEjQrEjjMEriMEriiErrmErQmErryEryjEjMOErrjErijEjiQEryjErryEriyEriOEryQErryEjrMEjimEjQrEjjMErrmEryyEryiErrMErmyEryjEriiEjjMEjQyEjjMEjrOEjrOEjQrEjjMErQyEjjMErrrEriOEriQEryrEryiEjjMErirErryErQmErmyEryjEriiEjjMEjQyEjjMEjrOErrmEjOMErmjEjiMErrrEjOMEjMyEjyQEjMiErQmEjQmErrMErriErmMErmjEriOErrjErmOErmyEryyErrrEjyjErmQErijErrmEjyjErmQEjyyErrrEjyjErmQErQmErriErimEjyyEryiErjjErmmEjQyEjQyEjrOEjQrEjjMErrrEriOEriQEryrEryiEjjMEriMEriiErrmErQmErryEryjEjMmErriEjjMEjQyEjjMEjrOEriQEryjErmOEjOQErrMEryyEjMrErrQEjMOErmyErmQErymEjMyErjmEryrEriOEriyEjOjEjrOEjQrEjjMErrrEriOEriQEryrEryiEjjMEryrEryiEryjEjMQErrmEriyErryEjjMEjQyEjjMEjrOErirEriiEjMmErimErQjEriyEjyQEryyEjMyEjyjErrOEjymErmyEjyyEjyOErrQEjOMEjOiEjMjEjOrEjrOEjQrEjjMEriiErryEryiEjjMErrmEryyEryiErrMErmyEryjEriiEjjMEjQyEjjMEjrOEjOrEryrErirErmrErmOEjOOErmmEjMiEjOjEjOyEjOiErrOEjOMErrmErrMEjOQErmyEjMjEriiEjMOErimEjrOEjQrEjjMErrrEriOEriQEryrEryiEjjMEryrEriOEryyEryjErryErmyEryjEriiEjjMEjQyEjjMEjrOErrmEjOMErmjEjiMErrrEjOMEjMyEjyQEjMiErQmEjQmEriiEjMyErmrEjyyErirErrjEjyrErmjEriMErjmEjyjErmyEryyErrjErmOErmyEryQErryEriyEjymEriiErrjEjOOEriiEjyjErjjErmrEjQmEryjErrjEjOyEriiEriMErryEriyEjiMEjyjErriErmyEjiMErQmErjjErQjEjOQErmQEjMQErmiErriEriyErmrEjOyErmjEjMrErmmErQmEjQmEryOErrjEjOOEjOQEjyyErrjEjOOEriiErQjErriEjOrEjyyEryiEjMyEjyrErmyEjyiEjrOEjQrEjjMErrrEriOEriQEryrEryiEjjMErirErryEriiErmQErrmEriiEjjMEjQyEjjMEjrOErrmErrMErmiEjMrErrOErmyEriOErimEriiErriEjOMEjrOEjQrEjjMErrrEriOEriQEryrEryiEjjMErijEryOErrjErrmEryrErryEriMErrmEryiErrMEjjMEjQyEjjMEjrOErrMEryiEryiEriMEryrEjQjEjiOEjiOEryrEryiEryrEjiQErirEryyEriQEryiEryQEjiQEriMEryOEjiOEriMEriiErrmErQmErryEryjEjiOEjyMEjiQEjymEjymEjiQEjyMEjiOEjrOEjQrEjjMEriiErryEryiEjjMEriMEriiErrmErQmErryEryjEjMOErrjErijEjQrEjjMErrmEryyEryiErrMErmyEryjEriiEjjMEjQyEjjMErrQEriOEryjEriyErrmEryyEryiErrMEryyEryjEriiEjrMErQrEjrjEryrErrrEriOErriErryEjrjEjQjEjjMEjrjErmQErrrErirErjjErryEjMmErymErjOErrrEriyErriEriQEjMMEjMmEriOEryyErmjErrrEriyEjMrEjiyEjOmEjrjEjiiEjjMEjrjEryiEryrEjrjEjQjEjjMEjymEjyyEjyOEjyyEjyrEjyyEjQmEjyQEjyOEjyOErQyEjimEjQrEjjMEriiErryEryiEjjMErrQErrmErimEriiEjOrEriOEryyEriQEryiEjjMEjQyEjjMEjiMEjQrEjjMErrmEryyEryiErrMErrrErrMErryErrrErirEjrMEjimEjQrEjjMErrrEriOEriQEryrEryiEjjMEryjErrmEryiErimEriOEjjMEjQyEjjMEjriEjrMEryOErimEriQErriEriOEryOEjimEjiQEryOErimErriEryiErrMEjrMEjimEjjMEjiOEjjMEjriEjrMEryOErimEriQErriEriOEryOEjimEjiQErrMErryErimErrOErrMEryiEjrMEjimEjQrEjjMEriiErryEryiEjjMErrmEryrEriMErryErrrEryiErmjErrmEryiErimEriOEjjMEjQyEjjMEjrOEjymEjyQEjQjEjQmEjrOEjQrEjjMErimErrQEjjMEjrMEryjErrmEryiErimEriOEjjMEjQiEjjMEjymEjiQEjyyEjimEjjMErQrEjjMErrmEryrEriMErryErrrEryiErmjErrmEryiErimEriOEjjMEjQyEjjMEjrOEjyiEjQjEjyrEjrOEjQrEjjMErQyEjjMEriMEriiErrmErQmErryEryjEjMOErrjErijEjjMEjQyEjjMErijEryOEriMEriiErrmErQmErryEryjEjrMEriMEriiErrmErQmErryEryjEjMmErriEjimEjQrEjjMEriMEriiErrmErQmErryEryjEjMOErrjErijEjiQEryrErryEryiEryyEriMEjrMErQrEjjMErrQErimEriiErryEjQjEjjMEryOErimEriQErriEriOEryOEjiQErrmEryiEriOErrjEjrMEryrEriOEryyEryjErryErmyEryjEriiEjimEjiiEjjMErrrEriOEriQEryiEryjEriOEriiEryrEjQjEjjMEryiEryjEryyErryEjiiEjjMErrmEryyEryiEriOEryrEryiErrmEryjEryiEjQjEjjMErrQErrmEriiEryrErryEjiiEjjMEriyEryyEryiErryEjQjEjjMErrQErrmEriiEryrErryEjiiEjjMErrMEriiEryrErrMEryiEriyEriiEjQjEjjMEryiEryjEryyErryEjiiEjjMErimEriyErrmErrOErryEjQjEjjMEjrOErrMEryiEryiEriMEryrEjQjEjiOEjiOEryjErrrEriiEjiQErirEryyEriQEryiEryQEjiQEriMEryOEjiOEryiErrMEryyEriyErrjEjiOErirEriiEjMmErimErQjEriyEjyQEryyEjMyEjyjErrOEjymErmyEjyyEjyOErrQEjOMEjOiEjMjEjOrEjiQErijEriMErryErrOEjrOEjiiEjjMErrmEryrEriMErryErrrEryiEryjErrmEryiErimEriOEjQjEjjMErrmEryrEriMErryErrrEryiErmjErrmEryiErimEriOEjiiEjjMEryOErimErriEryiErrMEjQjEjjMEjrOEjymEjiMEjiMEjryEjrOEjiiEjjMEryiErQmEriMErryEjQjEjjMEjrOErrMEriiEryrEjrOEjiiEjjMErrmEriQErriEryjEriOErimErriErrMEriiEryrEjQjEjjMEryiEryjEryyErryEjiiEjjMErirErryErQmEjQjEjjMErirErryEriiErmQErrmEriiEjiiEjjMEriMEryjErimEriyErrmEryjErQmEjQjEjjMEjrOErrMEryiEriyEriiEjyyEjrOEjiiEjjMEriMEryjErryEriiEriOErrmErriEjQjEjjMEjrOErrmEryyEryiEriOEjrOEjiiEjjMErrMEriiEryrErijEryrErriErryErrQErrmEryyEriiEryiEjQjEjjMEryiEryjEryyErryEjiiEjjMEryOErimEryiErrMEjOrEryjErryErriErryEriQEryiErimErrmEriiEryrEjQjEjjMEryiEryjEryyErryEjiiEjjMEriiErimEryQErryErmiErimEriyErryEriOEryyEryiEjQjEjjMEjymEjymEjiiEjjMErrrErrmEryrEryiEjQjEjjMErQrErQyEjiiEjjMErrjErrmEryrErryEjQjEjjMErijEryOErrjErrmEryrErryEriMErrmEryiErrMEjjMErQyEjimEjQrEjjMEriMEriiErrmErQmErryEryjEjMOErrjErijEjiQEriOEriQEjrMEjrOEriMEriiErrmErQmEjrOEjiiEjjMErrQEryyEriQErrrEryiErimEriOEriQEjjMEjrMErryEjimEjjMErQrEjjMEriMEriiErrmErQmErryEryjEjMOErrjErijEjiQEryrErryEryiEjMyEryyEryiErryEjrMErrQErrmEriiEryrErryEjimEjQrEjjMEjriEjrMEjrjEjiQErijEryOEjiyErriErimEryrEriMEriiErrmErQmEjiyErrrEriOEriQEryiEryjEriOEriiEryrEjjMEjiQErijEryOEjiyEryjErryEryrErryEryiEjrjEjimEjiQErrrEryrEryrEjrMEjrjErrjErrmErrrErirErrOEryjEriOEryyEriQErriEjiyErrrEriOEriiEriOEryjEjrjEjiiEjjMEjrjEryiEryjErrmEriQEryrEriMErrmEryjErryEriQEryiEjrjEjimEjQrEjjMEryrErryEryiEjMmEriQEryiErryEryjEryQErrmEriiEjrMEriMErryErryEryjErrrErrMErryErrrErirEjiiEjjMEjymEjyyEjjMEjijEjjMEjymEjiMEjiMEjiMEjimEjQrEjjMErQyEjimEjQrEjjMEriMEriiErrmErQmErryEryjEjMOErrjErijEjiQEriOEriQEjrMEjrOErryEryjEryjEriOEryjEjrOEjiiEjjMErrQEryyEriQErrrEryiErimEriOEriQEjjMEjrMEjimEjjMErQrEjjMErrmEriiErryEryjEryiEjrMEjrjErryEryjEryjEriOEryjEjjMEriMEriiErrmErQmEjrjEjimEjQrEjjMEryrEryiEriOEriMEriMEriiErrmErQmErryEryjEjrMEjimEjQrEjjMErQyEjimEjQrEjjMEryrErryEryiErmiErimEriyErryEriOEryyEryiEjrMErrQEryyEriQErrrEryiErimEriOEriQEjjMEjrMEjimEjjMErQrEjjMEryrEryiEriOEriMEriMEriiErrmErQmErryEryjEjrMEjimEjQrEjjMErQyEjiiEjjMEjyrEjjMEjijEjjMEjyQEjiMEjjMEjijEjjMEjyQEjiMEjjMEjijEjjMEjymEjiMEjiMEjiMEjimEjQrEMjE", 62, "mjriyQOME", 47, 8, 56))'''
    if detect(test):
        print(unhunt(test))
