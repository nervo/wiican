# -*- coding: utf-8 -*-
# vim: ts=4 
###
#
# Wiican is the legal property of J. Félix Ontañón <felixonta@gmail.com>
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
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
###

import gettext
import locale
import __builtin__
__builtin__._ = gettext.gettext

# i18n
gettext.install('wiican', '/usr/share/locale', unicode=1)

gettext.bindtextdomain('wiican', '/usr/share/locale')
if hasattr(gettext, 'bind_textdomain_codeset'):
    gettext.bind_textdomain_codeset('wiican','UTF-8')
gettext.textdomain('wiican')

locale.bindtextdomain('wiican', '/usr/share/locale')
if hasattr(locale, 'bind_textdomain_codeset'):
    locale.bind_textdomain_codeset('wiican','UTF-8')
locale.textdomain('wiican')
