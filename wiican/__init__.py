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
