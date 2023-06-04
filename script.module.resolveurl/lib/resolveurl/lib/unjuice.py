# -*- coding: utf-8 -*-

import re
import sys
from resolveurl.lib import jsunpack


Juice = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="


def test(e):
    return True if re.search(r'JuicyCodes.Run\(', e, re.IGNORECASE) else False


def run(e):
    try:
        e = re.findall(r'JuicyCodes.Run\(([^\)]+)', e, re.IGNORECASE)[0]
        e = re.sub(r'\"\s*\+\s*\"', '', e)
        e = re.sub(r'[^A-Za-z0-9+\\/=]', '', e)
    except BaseException:
        return None

    t = ""
    n = r = i = s = o = u = a = f = 0

    while f < len(e):
        s = Juice.index(e[f])
        f += 1
        o = Juice.index(e[f])
        f += 1
        u = Juice.index(e[f])
        f += 1
        a = Juice.index(e[f])
        f += 1
        n = s << 2 | o >> 4
        r = (15 & o) << 4 | u >> 2
        i = (3 & u) << 6 | a
        t += chr(n)
        if 64 != u:
            t += chr(r)
        if 64 != a:
            t += chr(i)

    if jsunpack.detect(t):
        t = jsunpack.unpack(t)

    return t


def main():
    # for testing
    code = 'JuicyCodes.Run("ZXZhbChmdW5jdGlvbihwLGEsYyxrLGUsZCl7ZT1mdW5jdGlvbihj"+"KXtyZXR1cm4oYzxhPycnOmUocGFyc2VJbnQoYy9hKSkpKygoYz1j"+"JWEpPjM1P1N0cmluZy5mcm9tQ2hhckNvZGUoYysyOSk6Yy50b1N0"+"cmluZygzNikpfTtpZighJycucmVwbGFjZSgvXi8sU3RyaW5nKSl7"+"d2hpbGUoYy0tKXtkW2UoYyldPWtbY118fGUoYyl9az1bZnVuY3Rp"+"b24oZSl7cmV0dXJuIGRbZV19XTtlPWZ1bmN0aW9uKCl7cmV0dXJu"+"J1xcdysnfTtjPTF9O3doaWxlKGMtLSl7aWYoa1tjXSl7cD1wLnJl"+"cGxhY2UobmV3IFJlZ0V4cCgnXFxiJytlKGMpKydcXGInLCdnJyks"+"a1tjXSl9fXJldHVybiBwfSgnMyBqPXsiSCI6IlgiLCJKIjoiUC1G"+"IiwiSyI6bH07eS5NPVwnVj09XCc7MyAxPXkoXCd2LTFcJyk7MyBk"+"OzMgNzszIEksbT1sOzMgajskKHgpLncoMigpe2ouRT14LlI7JC5R"+"KHtOOlwnTzovL1Mudi5ZLzdcJyxXOlwnVVwnLDY6aixaOlwnTFwn"+"LEM6MihlKXtkPWUuZDs3PWUuNzt0KCl9LH0pOyQoXCcjQi04XCcp"+"LnMoMigpeyQoXCcjZi04XCcpLmMoXCd1XCcpOzEuQShhLmkoNi5i"+"KSl9KTskKFwnI0QtOFwnKS5zKDIoKXskKFwnI2YtOFwnKS5jKFwn"+"dVwnKTsxLnEoKX0pfSk7MiB0KCl7MyBwPXs3OjcsZDpkLEc6IlQl"+"IiwxaTpcJzE2OjlcJywxbzpsLDFuOnt9LDFtOnsxazpcJyMxbFwn"+"LDFxOjF3LDExOjAsMXY6XCcxdFwnLDFyOlwnMXVcJ30sfTsxLjFz"+"KHApOzEuNChcJ3FcJywyKCl7fSk7MS40KFwnd1wnLDIoKXt9KTsx"+"LjQoXCcxcFwnLDIoKXt9KTsxLjQoXCcxalwnLDIoKXsxOChtJiZh"+"LmkoNi5iKSYmYS5pKDYuYik+MTkpezEuMTcoKTttPTE1OyQoXCcj"+"NS04XCcpLjEyKHooYS5pKDYuYikpKTskKFwnI2YtOFwnKS5jKFwn"+"b1wnKX19KTsxLjQoXCc1XCcsMigpe2EuMTMoNi5iLDEuMTQoKSl9"+"KTsxLjQoXCduXCcsMigpeyQoXCcjZi1uXCcpLmMoXCdvXCcpfSk7"+"MS40KFwnMWFcJywyKCl7JChcJyNmLW5cJykuYyhcJ29cJyl9KX0y"+"IHoocil7MyA1PTFiIDFnKDAsMCwwKTs1LjFoKHIpOzMgZz01LjFm"+"KCk7MyBoPTUuMWUoKTszIGs9NS4xYygpOzFkKGc8MTA/KFwnMFwn"+"K2cpOmcpK1wnOlwnKyhoPDEwPyhcJzBcJytoKTpoKStcJzpcJyso"+"azwxMD8oXCcwXCcrayk6ayl9Jyw2Miw5NSwnfHBsYXllcnxmdW5j"+"dGlvbnx2YXJ8b258dGltZXxkYXRhfHNvdXJjZXN8cmVzdW1lfHxs"+"b2NhbFN0b3JhZ2V8aWR8bW9kYWx8dHJhY2tzfHxwb3B8dGltZV9o"+"fHRpbWVfbXxnZXRJdGVtfGRhdGFQT1NUfHRpbWVfc3x0cnVlfGZp"+"cnN0X2xvYWR8ZXJyb3J8c2hvd3xqd2NvbmZpZ3xwbGF5fF90aW1l"+"fGNsaWNrfGxvYWRQbGF5ZXJ8aGlkZXxzdHJlYW1kb3J8cmVhZHl8"+"ZG9jdW1lbnR8andwbGF5ZXJ8Y29udmVydF90aW1lfHNlZWt8eWVz"+"fHN1Y2Nlc3N8bm98cmVmZXJlcnxjOXZJek5CanVPRmRqcEtYcV9f"+"WlF8d2lkdGh8ZXBpc29kZUlEfHBsYXlsaXN0fGZpbGV8c3VidGl0"+"bGV8anNvbnxrZXl8dXJsfGh0dHBzfFY0SUdfVGRxOFlPU2ZzWmlG"+"ZDFFc2xjeU9lSkIyUENZQ2hrXzRxcmkwX2lsTkE2TVpPX1BGcldX"+"REc1aHZkSGh8YWpheHxyZWZlcnJlcnxhcGl8MTAwfFBPU1R8SE92"+"OVlLNmVncFpnazVjY0JpWnBZZklBUXgzUTVib0dWN3RpR3d8bWV0"+"aG9kfDM2MDg0NXxjb3xkYXRhVHlwZXx8YmFja2dyb3VuZE9wYWNp"+"dHl8dGV4dHxzZXRJdGVtfGdldFBvc2l0aW9ufGZhbHNlfHxwYXVz"+"ZXxpZnwzMHxzZXR1cEVycm9yfG5ld3xnZXRTZWNvbmRzfHJldHVy"+"bnxnZXRNaW51dGVzfGdldEhvdXJzfERhdGV8c2V0U2Vjb25kc3xh"+"c3BlY3RyYXRpb3xmaXJzdEZyYW1lfGNvbG9yfGYzZjM3OHxjYXB0"+"aW9uc3xjYXN0fGF1dG9zdGFydHxjb21wbGV0ZXxmb250U2l6ZXxl"+"ZGdlU3R5bGV8c2V0dXB8SGVsdmV0aWNhfHJhaXNlZHxmb250ZmFt"+"aWx5fDIwJy5zcGxpdCgnfCcpLDAse30pKQo=")'
    print(test(code))
    print(run(code))
    pass


if __name__ == "__main__":
    sys.exit(int(main() or 0))
