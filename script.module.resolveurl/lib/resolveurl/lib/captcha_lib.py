"""
    resolveurl XBMC Addon
    Copyright (C) 2014 tknorris

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

    reusable captcha methods
"""
from resolveurl import common
import re
import xbmcgui
import os
from resolveurl.lib import recaptcha_v2
from resolveurl.lib import helpers
import base64
import json

net = common.Net()
IMG_FILE = 'captcha_img.gif'
TWOCAPTCHA_API = 'https://api.2captcha.com'


def get_response(img, x=450, y=225, w=400, h=130):
    try:
        img = xbmcgui.ControlImage(x, y, w, h, img)
        wdlg = xbmcgui.WindowDialog()
        wdlg.addControl(img)
        wdlg.show()
        common.kodi.sleep(5000)
        solution = common.kodi.get_keyboard(common.i18n('letters_image'))
        if not solution:
            raise Exception('captcha_error')
    finally:
        wdlg.close()
        return solution


def write_img(url=None, bin=None):
    img = os.path.join(common.profile_path, IMG_FILE)
    if url:
        bin = net.http_GET(url).nodecode(True).content
    with open(img, 'wb') as file:
        _ = file.write(bin)
    return img


def do_captcha(html, base_url=None):
    solvemedia = re.search(r'<iframe[^>]+src="((?:https?:)?//api\.solvemedia\.com[^"]+)', html)
    recaptcha = re.search(r'<script\s+type="text/javascript"\s+src="(http://www\.google\.com[^"]+)', html)
    recaptcha_v2 = re.search(r'data-sitekey="([^"]+)', html)
    xfilecaptcha = re.search(r'<img\s+src="([^"]+/captchas/[^"]+)', html)
    ccapimg = re.search(r'key=([^"]+)"', html)

    if solvemedia:
        return do_solvemedia_captcha(solvemedia.group(1))
    elif recaptcha:
        return do_recaptcha(recaptcha.group(1))
    elif recaptcha_v2:
        return do_recaptcha_v2(recaptcha_v2.group(1))
    elif xfilecaptcha:
        return do_xfilecaptcha(xfilecaptcha.group(1))
    elif ccapimg and base_url:
        return {'secimgkey': ccapimg.group(1), 'secimginp': do_ccapimg_captcha(base_url + 'ccapimg?key=' + ccapimg.group(1))}
    else:
        captcha = re.compile(r'''left:(\d+)px;padding-top:\d+px;['"]>&#(.+?);<''').findall(html)
        result = sorted(captcha, key=lambda ltr: int(ltr[0]))
        solution = ''.join(str(int(num[1]) - 48) for num in result)
        if solution:
            return {'code': solution}
        else:
            return {}


def do_solvemedia_captcha(captcha_url):
    common.logger.log_debug('SolveMedia Captcha: %s' % captcha_url)
    if captcha_url.startswith('//'):
        captcha_url = 'http:' + captcha_url
    html = net.http_GET(captcha_url).content
    data = {
        'adcopy_challenge': ''  # set to blank just in case not found; avoids exception on return
    }
    data.update(helpers.get_hidden(html), include_submit=False)

    # Check for alternate puzzle type - stored in a div
    alt_frame = re.search('<div><iframe src="(/papi/media[^"]+)', html)
    if alt_frame:
        html = net.http_GET("http://api.solvemedia.com%s" % alt_frame.group(1)).content
        alt_puzzle = re.search(r'<div\s+id="typein">\s*<img\s+src="data:image/png;base64,([^"]+)', html, re.DOTALL)
        if alt_puzzle:
            captcha_img = write_img(bin=base64.b64decode(alt_puzzle.group(1)))
        else:
            raise Exception('captcha_error')
    else:
        captcha_img = write_img("http://api.solvemedia.com%s" % re.search('<img src="(/papi/media[^"]+)"', html).group(1))

    solution = get_response(captcha_img)
    data['adcopy_response'] = solution
    html = net.http_POST('http://api.solvemedia.com/papi/verify.noscript', data)
    return {'adcopy_challenge': data['adcopy_challenge'], 'adcopy_response': 'manual_challenge'}


def do_recaptcha(captcha_url):
    common.logger.log_debug('Google ReCaptcha: %s' % captcha_url)
    if captcha_url.startswith('//'):
        captcha_url = 'http:' + captcha_url
    personal_nid = common.get_setting('personal_nid')
    if personal_nid:
        headers = {'Cookie': 'NID=' + personal_nid}
    else:
        headers = {}
    html = net.http_GET(captcha_url, headers=headers).content
    part = re.search(r"challenge \: \\'(.+?)\\'", html)
    captcha_img = 'http://www.google.com/recaptcha/api/image?c=' + part.group(1)
    solution = get_response(captcha_img)
    return {'recaptcha_challenge_field': part.group(1), 'recaptcha_response_field': solution}


def do_recaptcha_v2(sitekey):
    token = recaptcha_v2.UnCaptchaReCaptcha().processCaptcha(sitekey, lang='en')
    if token:
        return {'g-recaptcha-response': token}

    return {}


def do_turnstile(sitekey, page_url, timeout=120):
    """
    Solve a standalone Cloudflare Turnstile widget through the 2Captcha API
    (createTask / getTaskResult). Turnstile cannot be solved in pure python,
    so the token is bought from the service using the API key from the
    addon settings. Returns the form fields to POST back to the site
    (Turnstile fills both names in reCAPTCHA compatibility mode) or an
    empty dict if no API key is configured.
    """
    api_key = common.get_setting('twocaptcha_key')
    if not api_key:
        return {}

    common.logger.log_debug('Cloudflare Turnstile via 2Captcha: %s' % sitekey)
    common.kodi.notify(msg=common.i18n('solving_captcha'), duration=8000)
    headers = {'User-Agent': common.SMR_USER_AGENT}
    task = {
        'clientKey': api_key,
        'task': {
            'type': 'TurnstileTaskProxyless',
            'websiteURL': page_url,
            'websiteKey': sitekey
        }
    }
    resp = json.loads(net.http_POST(TWOCAPTCHA_API + '/createTask', form_data=task, headers=headers, jdata=True).content)
    if resp.get('errorId'):
        raise Exception('2Captcha: %s' % resp.get('errorCode', 'createTask failed'))

    result = {'clientKey': api_key, 'taskId': resp.get('taskId')}
    waited = 0
    # the service asks for the first poll after 5 seconds and 5 seconds between polls
    while waited < timeout:
        common.kodi.sleep(5000)
        waited += 5
        resp = json.loads(net.http_POST(TWOCAPTCHA_API + '/getTaskResult', form_data=result, headers=headers, jdata=True).content)
        if resp.get('errorId'):
            raise Exception('2Captcha: %s' % resp.get('errorCode', 'getTaskResult failed'))
        if resp.get('status') == 'ready':
            token = resp.get('solution', {}).get('token')
            if token:
                return {'cf-turnstile-response': token, 'g-recaptcha-response': token}
            break

    raise Exception('2Captcha: no Turnstile token received')


def do_xfilecaptcha(captcha_url):
    common.logger.log_debug('XFileLoad ReCaptcha: %s' % captcha_url)
    if captcha_url.startswith('//'):
        captcha_url = 'http:' + captcha_url
    captcha_img = write_img(captcha_url)
    solution = get_response(captcha_img)
    return {'code': solution}


def do_ccapimg_captcha(captcha_url):
    common.logger.log_debug('CCapImg Captcha: %s' % captcha_url)
    captcha_img = write_img(captcha_url)
    return get_response(captcha_img)
