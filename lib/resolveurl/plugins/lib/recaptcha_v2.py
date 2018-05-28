# -*- coding: utf-8 -*-
"""
    resolveurl XBMC Addon
    Copyright (C) 2016 tknorris
    Derived from Shani's LPro Code (https://github.com/Shani-08/ShaniXBMCWork2/blob/master/plugin.video.live.streamspro/unCaptcha.py)

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
import re
import os
import xbmcgui
from resolveurl import common

logger = common.log_utils.Logger.get_logger(__name__)
logger.disable()

class cInputWindow(xbmcgui.WindowDialog):

    def __init__(self, *args, **kwargs):
        bg_image = os.path.join(common.addon_path, 'resources', 'images', 'DialogBack2.png')
        check_image = os.path.join(common.addon_path, 'resources', 'images', 'checked.png')
        button_fo = os.path.join(common.kodi.get_path(), 'resources', 'skins', 'Default', 'media', 'button-fo.png')
        button_nofo = os.path.join(common.kodi.get_path(), 'resources', 'skins', 'Default', 'media', 'button-nofo.png')
        self.cancelled = False
        self.chk = [0] * 9
        self.chkbutton = [0] * 9
        self.chkstate = [False] * 9

        imgX, imgY, imgw, imgh = 436, 210, 408, 300
        ph, pw = imgh / 3, imgw / 3
        x_gap = 70
        y_gap = 70
        button_gap = 40
        button_h = 40
        button_y = imgY + imgh + button_gap
        middle = imgX + (imgw / 2)
        win_x = imgX - x_gap
        win_y = imgY - y_gap
        win_h = imgh + 2 * y_gap + button_h + button_gap
        win_w = imgw + 2 * x_gap

        ctrlBackgound = xbmcgui.ControlImage(win_x, win_y, win_w, win_h, bg_image)
        self.addControl(ctrlBackgound)
        self.msg = '[COLOR red]%s[/COLOR]' % (kwargs.get('msg'))
        self.strActionInfo = xbmcgui.ControlLabel(imgX, imgY - 30, imgw, 20, self.msg, 'font13')
        self.addControl(self.strActionInfo)
        img = xbmcgui.ControlImage(imgX, imgY, imgw, imgh, kwargs.get('captcha'))
        self.addControl(img)
        self.iteration = kwargs.get('iteration')
        self.strActionInfo = xbmcgui.ControlLabel(imgX, imgY + imgh, imgw, 20, common.i18n('captcha_round') % (str(self.iteration)), 'font40')
        self.addControl(self.strActionInfo)
        self.cancelbutton = xbmcgui.ControlButton(middle - 110, button_y, 100, button_h, common.i18n('cancel'), focusTexture=button_fo, noFocusTexture=button_nofo, alignment=2)
        self.okbutton = xbmcgui.ControlButton(middle + 10, button_y, 100, button_h, common.i18n('ok'), focusTexture=button_fo, noFocusTexture=button_nofo, alignment=2)
        self.addControl(self.okbutton)
        self.addControl(self.cancelbutton)

        for i in xrange(9):
            row = i / 3
            col = i % 3
            x_pos = imgX + (pw * col)
            y_pos = imgY + (ph * row)
            self.chk[i] = xbmcgui.ControlImage(x_pos, y_pos, pw, ph, check_image)
            self.addControl(self.chk[i])
            self.chk[i].setVisible(False)
            self.chkbutton[i] = xbmcgui.ControlButton(x_pos, y_pos, pw, ph, str(i + 1), font='font1', focusTexture=button_fo, noFocusTexture=button_nofo)
            self.addControl(self.chkbutton[i])

        for i in xrange(9):
            row_start = (i / 3) * 3
            right = row_start + (i + 1) % 3
            left = row_start + (i - 1) % 3
            up = (i - 3) % 9
            down = (i + 3) % 9
            self.chkbutton[i].controlRight(self.chkbutton[right])
            self.chkbutton[i].controlLeft(self.chkbutton[left])
            if i <= 2:
                self.chkbutton[i].controlUp(self.okbutton)
            else:
                self.chkbutton[i].controlUp(self.chkbutton[up])

            if i >= 6:
                self.chkbutton[i].controlDown(self.okbutton)
            else:
                self.chkbutton[i].controlDown(self.chkbutton[down])

        self.okbutton.controlLeft(self.cancelbutton)
        self.okbutton.controlRight(self.cancelbutton)
        self.cancelbutton.controlLeft(self.okbutton)
        self.cancelbutton.controlRight(self.okbutton)
        self.okbutton.controlDown(self.chkbutton[2])
        self.okbutton.controlUp(self.chkbutton[8])
        self.cancelbutton.controlDown(self.chkbutton[0])
        self.cancelbutton.controlUp(self.chkbutton[6])
        self.setFocus(self.okbutton)

    def get(self):
        self.doModal()
        self.close()
        if not self.cancelled:
            return [i for i in xrange(9) if self.chkstate[i]]

    def onControl(self, control):
        if control == self.okbutton and any(self.chkstate):
            self.close()

        elif control == self.cancelbutton:
            self.cancelled = True
            self.close()
        else:
            label = control.getLabel()
            if label.isnumeric():
                index = int(label) - 1
                self.chkstate[index] = not self.chkstate[index]
                self.chk[index].setVisible(self.chkstate[index])

    def onAction(self, action):
        if action == 10:
            self.cancelled = True
            self.close()

class UnCaptchaReCaptcha:
    net = common.Net()

    def processCaptcha(self, key, lang):
        headers = {'Referer': 'https://www.google.com/recaptcha/api2/demo', 'Accept-Language': lang}
        html = self.net.http_GET('http://www.google.com/recaptcha/api/fallback?k=%s' % (key), headers=headers).content
        token = ''
        iteration = 0
        while True:
            payload = re.findall('"(/recaptcha/api2/payload[^"]+)', html)
            iteration += 1
            message = re.findall('<label[^>]+class="fbc-imageselect-message-text"[^>]*>(.*?)</label>', html)
            if not message:
                message = re.findall('<div[^>]+class="fbc-imageselect-message-error">(.*?)</div>', html)
            if not message:
                token = re.findall('"this\.select\(\)">(.*?)</textarea>', html)[0]
                if token:
                    logger.log_debug('Captcha Success: %s' % (token))
                else:
                    logger.log_debug('Captcha Failed: %s')
                break
            else:
                message = message[0]
                payload = payload[0]

            cval = re.findall('name="c"\s+value="([^"]+)', html)[0]
            captcha_imgurl = 'https://www.google.com%s' % (payload.replace('&amp;', '&'))
            message = re.sub('</?(div|strong)[^>]*>', '', message)
            oSolver = cInputWindow(captcha=captcha_imgurl, msg=message, iteration=iteration)
            captcha_response = oSolver.get()
            if not captcha_response:
                break

            data = {'c': cval, 'response': captcha_response}
            html = self.net.http_POST("http://www.google.com/recaptcha/api/fallback?k=%s" % (key), form_data=data, headers=headers).content
        return token
