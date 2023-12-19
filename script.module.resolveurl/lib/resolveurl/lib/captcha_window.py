"""
    Copyright (C) 2023 MrDini123
    https://github.com/movieshark

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
import xbmcgui
from resolveurl import common


class CaptchaWindow(xbmcgui.WindowDialog):
    def __init__(self, image, width, height):
        bg_image = os.path.join(
            common.addon_path, 'resources', 'images', 'DialogBack1.png'
        )
        self.box_image = os.path.join(
            common.addon_path, 'resources', 'images', 'border90.png'
        )
        self.orig_image = image
        self.width = width
        self.height = height
        self.temp_file = self.create_temp_image()
        self.border_img = None
        self.frame_x = (self.getWidth() - self.width) // 2  # Centered horizontally
        self.frame_y = (self.getHeight() - self.height) // 2  # Centered vertically
        self.left_arrow = None
        self.right_arrow = None
        self.top_arrow = None
        self.bottom_arrow = None
        self.submit_button = None
        self.finished = False
        self.orig_x = self.frame_x
        self.orig_y = self.frame_y
        self.addControl(
            xbmcgui.ControlImage(
                x=(self.getWidth() - 650) // 2,
                y=(self.getHeight() - 650) // 2,
                height=650,
                width=650,
                filename=bg_image
            )
        )
        self.fadelabel = xbmcgui.ControlFadeLabel(
            x=(self.getWidth() - 500) // 2,
            y=(self.getHeight() - 550) // 2,
            width=500,
            height=50,
            textColor='0xFF9FFB05'
        )
        self.addControl(self.fadelabel)
        self.fadelabel.addLabel(common.i18n('waaw_captcha'))
        self.add_controls()

    def create_temp_image(self):
        temp_file = os.path.join(common.profile_path, 'captcha_img.jpg')
        with open(temp_file, 'wb') as binary_file:
            binary_file.write(self.orig_image)
        return temp_file

    @property
    def solution_x(self):
        return self.frame_x - self.orig_x + 45

    @property
    def solution_y(self):
        return self.frame_y - self.orig_y + 45

    def add_controls(self):
        # Define arrow directions, corresponding labels, and sizes
        arrow_info = {
            'top': (' ^', 150, 75),  # Increase width and height
            'bottom': (' v', 150, 75),  # Increase width and height
            'left': (' <', 75, 150),  # Increase width and height
            'right': (' >', 75, 150)  # Increase width and height
        }

        # Adjust this value to control the space between the button and arrows
        arrow_margin = 10

        # Calculate arrow positions and create arrow buttons
        for direction, (label, width, height) in arrow_info.items():
            if direction == 'top':
                x = self.frame_x + (self.width - width) // 2
                y = self.frame_y - height + arrow_margin
            elif direction == 'bottom':
                x = self.frame_x + (self.width - width) // 2
                y = self.frame_y + self.height - arrow_margin
            elif direction == 'left':
                x = self.frame_x - width - arrow_margin
                y = self.frame_y + (self.height - height) // 2
            elif direction == 'right':
                x = self.frame_x + self.width + arrow_margin
                y = self.frame_y + (self.height - height) // 2

            button = xbmcgui.ControlButton(
                x, y, width, height, label, textColor='0xFF9FFB05', alignment=6
            )

            # Add arrow button
            self.addControl(button)
            if direction == 'top':
                self.top_arrow = button
            elif direction == 'bottom':
                self.bottom_arrow = button
            elif direction == 'left':
                self.left_arrow = button
            elif direction == 'right':
                self.right_arrow = button

        captcha_image = xbmcgui.ControlImage(
            self.frame_x, self.frame_y, self.width, self.height, self.temp_file
        )
        self.addControl(captcha_image)

        # Calculate the position of the Submit button
        submit_button_width = 250
        submit_button_height = 100
        submit_button_x = self.frame_x + (self.width - submit_button_width) // 2
        # submit_button_y = self.frame_y + (self.height - submit_button_height) // 2
        submit_button_y = 450

        submit_button = xbmcgui.ControlButton(
            submit_button_x,
            submit_button_y,
            submit_button_width,
            submit_button_height,
            common.i18n('submit'),
            textColor='0xFF9FFB05',
            alignment=6
        )
        self.addControl(submit_button)
        self.submit_button = submit_button

        self.border_img = xbmcgui.ControlImage(
            self.frame_x, self.frame_y, 90, 90, self.box_image
        )
        self.addControl(self.border_img)

    def update_border_img(self):
        self.border_img.setPosition(self.frame_x, self.frame_y)

    def close(self):
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)
        return super(CaptchaWindow, self).close()

    def handle_action(self, action_or_control):
        # if left arrow/control is pressed, move left and jump to the right side if at the left edge
        if action_or_control in [self.left_arrow.getId(), xbmcgui.ACTION_MOVE_LEFT]:
            if self.frame_x - 10 >= self.orig_x:
                self.frame_x -= 10
            else:
                self.frame_x = self.orig_x + self.width - 90
            self.update_border_img()

        # if right arrow/control is pressed, move right and jump to the left side if at the right edge
        elif action_or_control in [self.right_arrow.getId(), xbmcgui.ACTION_MOVE_RIGHT]:
            if self.frame_x + 10 <= self.orig_x + self.width - 90:
                self.frame_x += 10
            else:
                self.frame_x = self.orig_x
            self.update_border_img()

        # if up arrow/control is pressed, move up and jump to the bottom if at the top edge
        elif action_or_control in [self.top_arrow.getId(), xbmcgui.ACTION_MOVE_UP]:
            if self.frame_y - 10 >= self.orig_y:
                self.frame_y -= 10
            else:
                self.frame_y = self.orig_y + self.height - 90
            self.update_border_img()

        # if down arrow/control is pressed, move down and jump to the top if at the bottom edge
        elif action_or_control in [self.bottom_arrow.getId(), xbmcgui.ACTION_MOVE_DOWN]:
            if self.frame_y + 10 <= self.orig_y + self.height - 90:
                self.frame_y += 10
            else:
                self.frame_y = self.orig_y
            self.update_border_img()

        # if enter is pressed, close
        elif action_or_control in [
            self.submit_button.getId(),
            xbmcgui.ACTION_SELECT_ITEM,
        ]:
            self.finished = True
            self.close()
        # if close button is pressed, close
        if action_or_control == xbmcgui.ACTION_NAV_BACK:
            self.close()
        elif not isinstance(action_or_control, int):
            super(CaptchaWindow, self).onAction(action_or_control)

    def onAction(self, action):
        self.handle_action(action)

    def onControl(self, control):
        self.handle_action(control.getId())
