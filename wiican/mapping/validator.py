# -*- coding: utf-8 -*-
# vim: ts=4 
###
#
# Copyright (c) 2010 J. Félix Ontañón
#
# Ripped idea from lex/yacc definition of cwiid's wminput
# cwiid it's a great piece of software by L. Donnie Smith
# Copyright (C) 2007 L. Donnie Smith <wiimote@abstrakraft.org>
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

    def run(self, prompt='parser > '):
        while 1:
            try:
                s = raw_input(prompt)
            except EOFError:
                break
            if not s: continue
            yacc.parse(s)

from action_enum import BTN_ACTION_ENUM, ABS_ACTION_ENUM, REL_ACTION_ENUM
        
class WMInputValidator(Parser):
    """
    Lex and syntax validator for wminput config files.
    The wminput's "include" directive it's not allowed by now.
    """

    literals = ['-', '.', '=', '~']

    tokens = (
        'WM_BTN', 'NC_BTN', 'CC_BTN', 'PLUGIN', 'AXIS', 
        'WM_RUMBLE', 'ON_OFF',
        'BTN_ACTION', 'ABS_AXIS_ACTION', 'REL_AXIS_ACTION', 
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
    t_PLUGIN =      'Plugin\.[\w_][\w_-]*.[\w_][\w_-]*'
    t_ignore  = ' \t'
        
    def __init__(self, dbg_mode=False):
        Parser.__init__(self, debug=dbg_mode)
        self.validation_errors = []
        self.comments = []
        
    def validate(self, config, halt_on_errors=True, verbose=False):
        self.validation_errors = []
        self.comments = []        
        self.halt_on_errors = halt_on_errors
        self.verbose = verbose
                        
        yacc.parse(config)
                
    def validate_file(self, file_path, halt_on_errors=True, verbose=False):
        f = open(file_path, 'r')
        config = f.read()
        f.close()

        self.validate(config, halt_on_errors, verbose)

    # PLY makes function tokens resolved first, in this order:
    def t_NEWLINE(self, t):
        r'\n+'
        t.lexer.lineno += t.value.count("\n")
        #t.lexer.begin('INITIAL')

    def t_COMMENT(self, t):
        r'\#.*'
        self.comments.append(t)

    def t_INT(self, t):
        r'[0-9]+'
        return t

    def t_FLOAT(self, t):
        r'[0-9]+(\.[0-9]*)?([eE][+/-]?[0-9]+)?'
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
        mesg = "Illegal character at lineno %d: '%s'" % (t.lexer.lineno, t)
    
        if self.verbose:
            print mesg
            
        if self.halt_on_errors:
            raise RuntimeError, mesg

        self.validation_errors.append(t)
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
                    | PLUGIN '=' BTN_ACTION
                    | PLUGIN '=' sign pointer ABS_AXIS_ACTION
                    | PLUGIN '=' sign REL_AXIS_ACTION
                    | PLUGIN '=' INT
                    | PLUGIN '=' FLOAT """

        p[0] = p[1]
        p.set_lineno(0, p.lineno(1))

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
        if p: mesg = "Syntax error at lineno %d: '%s'" % (p.lineno, p)
        else: mesg = "Syntax error at EOF" 

        if self.verbose: print mesg
        if self.halt_on_errors: raise SyntaxError, mesg

        self.validation_errors.append(p)

if __name__ == '__main__':
    import sys
    
    wminput_validator = WMInputValidator()

    if len(sys.argv) >= 2:
        wminput_validator.validate_file(sys.argv[1], halt_on_errors=False)
    else:
        wminput_validator.run()
