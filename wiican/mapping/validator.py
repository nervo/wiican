# -*- coding: utf-8 -*-
# vim: ts=4 
###
#
# Copyright (c) 2010 J. Félix Ontañón
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

import ply.lex as lex
import ply.yacc as yacc
import os

#FIXME: This prevents ply's deprecated use of md5 instead of hashlib warning
import warnings
warnings.filterwarnings('ignore')

class Parser():
    """
    Base class for a lexer/parser that has the rules defined as methods
    """
    tokens = ()
    precedence = ()

    def __init__(self, **kw):
        self.debug = kw.get('debug', 0)
        self.names = { }
        try:
            modname = os.path.split(os.path.splitext(__file__)[0])[1] + "_" \
            + self.__class__.__name__
        except:
            modname = "parser"+"_"+self.__class__.__name__
        self.debugfile = modname + ".dbg"
        self.tabmodule = modname + "_" + "parsetab"

        # Build the lexer and parser
        lex.lex(module=self, debug=self.debug)
        yacc.yacc(module=self,
                  debug=self.debug,
                  debugfile=self.debugfile,
                  write_tables=0) #FIXME: Smarter parsetab managing it's needed
                  #tabmodule="parsetab.py")

    def run(self):
        while 1:
            try:
                s = raw_input('parser > ')
            except EOFError:
                break
            if not s: continue
            yacc.parse(s)

from action_enum import BTN_ACTION_ENUM, ABS_ACTION_ENUM, REL_ACTION_ENUM
        
class WMInputValidator(Parser):
    literals = ['-', '.', '=', '~']

    tokens = (
        'WM_BTN', 'NC_BTN', 'CC_BTN', 'PLUGIN', 'AXIS', 
        'WM_RUMBLE', 'ON_OFF',
        'ID', 'BTN_ACTION', 'ABS_AXIS_ACTION', 'REL_AXIS_ACTION', 
        'INT', 'FLOAT',
    )

    # String tokens in order of ply-resolution (re length)
    t_AXIS =        r'Wiimote\.Dpad\.(X|Y)|Nunchuk\.Stick\.(X|Y)|'\
                    +'Classic\.(Dpad\.(X|Y)|LStick\.(X|Y)|RStick\.(X|Y)|LAnalog'\
                    +'RAnalog)'
    t_CC_BTN =      r'Classic\.(Up|Down|Left|Right|Minus|Plus|Home|A|B|X|Y|ZL|ZR|L|R)'
    t_WM_BTN =      r'Wiimote\.(Up|Down|Left|Right|A|B|Minus|Plus|Home|1|2)'    
    t_WM_RUMBLE =   r'Wiimote\.Rumble'
    t_NC_BTN =      r'Nunchuk\.(C|Z)'
    t_ID =          r'[\w_][\w_-]*'
    t_ignore  = ' \t'
        
    def __init__(self):
        Parser.__init__(self)
        self.lineno = 0
        
    def validate(self, path):
        self.lineno = 1
        
        f = open(path, 'r')
        yacc.parse(f.read())
        f.close()

    # PLY makes function tokens resolved first, in this order:
    def t_NEWLINE(self, t):
        r'\n+'
        self.lineno += t.value.count("\n")

    def t_COMMENT(self, t):
        r'\#.*'
        pass

    def t_FLOAT(self, t):
        r'[0-9]+(\.[0-9]*)?([eE][+/-]?[0-9]+)?'
        t.value = float(t.value)    
        return t

    def t_INT(self, t):
        r'[0-9]+'
        t.value = int(t.value)
        return t

    def t_PLUGIN(self, t):
        r'Plugin\.'
        return t

    def t_ON_OFF(self, t):
        r'On|Off'
        return t

    def t_BTN_ACTION(self, t):
        r'(BTN|KEY)_[\w_]+'
        if not t.value in BTN_ACTION_ENUM:
            self.t_error(t)

        return t
        
    def t_ABS_AXIS_ACTION(self, t):
        r'ABS_[\w_]+'
        if not t.value in ABS_ACTION_ENUM:
            self.t_error(t)

        return t

    def t_REL_AXIS_ACTION(self, t):
        r'REL_[\w_]+'
        if not t.value in REL_ACTION_ENUM:
            self.t_error(t)

        return t

    def t_error(self, t):
        print "[lineno: %d] Illegal character '%s'" % (self.lineno, t.value[0]) 
        t.lexer.skip(1)

    def p_conf_list(self, p):
        """ conf_list : conf_list conf_item 
                    | conf_item"""

        p[0] = None

    def p_conf_item(self, p):
        """ conf_item : WM_RUMBLE '=' ON_OFF
                    | WM_BTN '=' BTN_ACTION
                    | NC_BTN '=' BTN_ACTION 
                    | CC_BTN '=' BTN_ACTION
                    | AXIS '=' sign pointer ABS_AXIS_ACTION 
                    | AXIS '=' sign REL_AXIS_ACTION
                    | PLUGIN ID '.' ID '=' BTN_ACTION
                    | PLUGIN ID '.' ID '=' sign pointer ABS_AXIS_ACTION
                    | PLUGIN ID '.' ID '=' sign REL_AXIS_ACTION
                    | PLUGIN ID '.' ID '=' INT
                    | PLUGIN ID '.' ID '=' FLOAT """

        p[0] = p[1]

    def p_sign_item(self, p):
        """ sign : empty
                    | '-' """
        pass
        
    def p_pointer_item(self, p):
        """ pointer : empty
                    | '~' """
        pass

    def p_empty_item(self, p):
        """ empty : """
        
    def p_error(self, p):
        if p:
            print "[lineno: %d] Syntax error at '%s'" % (self.lineno, p.value)
        else:
            print "Syntax error at EOF"

if __name__ == '__main__':
    import sys
    
    wminput_validator = WMInputValidator()
    wminput_validator.validate(sys.argv[1])
