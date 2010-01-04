# -*- coding: utf-8 -*-
# vim: ts=4 
###
#
# Copyright (c) 2009 J. Félix Ontañón
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Authors : J. Félix Ontañón <felixonta@gmail.com>
# 
###

import pynotify

class Notificator:
    __urgency = pynotify.URGENCY_LOW
    __status_icon = None

    def set_status_icon(self, status_icon):
        self.__status_icon = status_icon

    def show_notification(self, title, msg, timeout=6000, icon=None):
        notification = pynotify.Notification(title, msg, icon)
        notification.set_urgency(self.__urgency)
        notification.set_timeout(timeout)
        if self.__status_icon:
            notification.set_property("status-icon", self.__status_icon)
        notification.show()

    __instance = None
