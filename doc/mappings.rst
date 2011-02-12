Wiican Mapping How-To
=====================

One of best wiican features it's to create your own mappings and share with 
friends. Wiican mappings are based on `wminput config files 
<http://abstrakraft.org/cwiid/wiki/wminput>`_. 

In this doc we'll try to expose the basic for editing wiican mappings, building
wminput config files, and show how to export this as wiican mapping package for
sharing.

.. _editing_mappings:

Editing Wiican Mappings
-----------------------

Actually wiican mappings are based on wminput config files with some
metadata and icon associated: 

* A file containing the wminput code

* A file containing name, description, author and version

* An optional icon file

Every mapping lives on home directory under .local/share/wiican/
so maybe you want to see if i'm telling the true now ;).

By the current mapping definition (wiican 0.3.2) there are names reserved for
the mapping file and the info file: mapping.wminput and info.desktop 
respectively.

.. _info_file:

Info file
~~~~~~~~~

The info file contains the name, description, author and version for a wiican
mapping. It follows the `XDG DesktopEntry specification <http://www.
freedesktop.org/wiki/Specifications/desktop-entry-spec>`_ in order to store 
translations and special fields easily. This is the basic structure::

    [Desktop Entry]
    Name=Wiimote IR Mouse
    Name[es_ES]=Ratón con wiimote IR
    Comment=Control mouse with IR and A+B buttons
    Comment[es_ES]=Controla el ratón con infrarojos y los botones A+B
    X-Authors=J. Félix Ontañón <felixonta `at` gmail `dot` com>
    X-Version=0.3.2
    Icon=wiimouse.svg

*Name* and *Comment* fields support translations via XDG DesktopEntry localized 
values for keys. Two fields has been added: *X-Authors* and *X-Version* extending the
XDG DesktopEntry spec. 

There are three possibilities for icon setting:

- An absolute path where the icon it's stored
- Icon filename if it's stored in the same dir as :attr:`Mapping.info_filename`
- Theme-icon-name for auto-getting the icon from the icon theme

.. note::

    Other XDG DesktopEntry fields could be added but not managed

.. _mapping_file:

Mapping file
~~~~~~~~~~~~

The mapping file contains the wminput configuration code. As wminput cwiid page 
says:

 wminput is an Linux event, mouse, and joystick driver for the wiimote using the 
 uinput system. It supports assigning key/button symbols to buttons on the wiimote, 
 nunchuk, and classic controller, and axes symbols to wiimote axes including direction 
 pads, "analog" sticks, and "analog" shoulder buttons. Furthermore, it provides a 
 plugin interface through which more advanced functionality can be implemented, 
 such as accelerometer and ir calculations. Plugins can provide button-type 
 events and axes.

Grammar
'''''''

The `official doc for wminput <http://abstrakraft.org/cwiid/wiki/wminput>`_ 
describes grammar for wminput we will reproduce it as is::

 Wiimote.<button> = <button_symbol>
 Nunchuk.<button> = <button_symbol>
 Classic.<button> = <button_symbol>
 Plugin.<plugin>.<button> = <button_symbol>

Map the button or key symbol specified on the right-hand side to the button 
event specified on the left-hand side. Button and key symbols are listed in 
/usr/include/linux/input.h (BTN_* and KEY_* macros), and in cwiid/wminput/action_enum.txt. 
All valid wiimote, nunchuk, and classic buttons are listed in cwiid/doc/wminput.list.::

 Wiimote.<axis> = [-][~]<abs_axis_symbol> | [-]<rel_axis_symbol>[[BR]]
 Nunchuk.<axis> = [-][~]<abs_axis_symbol> | [-]<rel_axis_symbl>[[BR]]
 Classic.<axis> = [-][~]<abs_axis_symbol> | [-]<rel_axis_symbol>[[BR]]
 Plugin.<plugin>.<axis> = [-][~]<abs_axis_symbol> | [-]<rel_axis_symbol>

Map the axis symbol specified on the right-hand side to the axis event specified 
on the left-hand side. Axis symbols are listed in /usr/include/linux/input.h 
(ABS_* and REL_* macros), and in cwiid/wminput/action_enum.txt. All valid wiimote, 
nunchuk, and classic axes are listed in cwiid/doc/wminput.list. A - before the 
axis symbol inverts the axis. A ~ is usually required before an absolute axis 
symbol in order to use it for cursor movement::

 Wiimote.Rumble = On | Off
 Activates or deactivates force feedback/rumble function.

An event device is always created. A mouse device is created if REL_X, REL_Y, 
and BTN_LEFT symbols are mapped (~ABS_X and ~ABS_Y effectively map REL_X and REL_Y, 
respectively). A joystick device is created if ABS_X is mapped.

Examples
''''''''

Mouse pointer controlled by wiimote accelerometer with A+B wiimote buttons as 
left and right mouse buttons::

 # Wiimote accelerometer as mouse XY axis
 Plugin.acc.X    = REL_X
 Plugin.acc.Y    = REL_Y

 # Left and right mouse buttons
 Wiimote.A       = BTN_LEFT
 Wiimote.B       = BTN_RIGHT

 # Other wiimote buttons mapped to keys
 Wiimote.Up      = KEY_UP
 Wiimote.Down    = KEY_DOWN
 Wiimote.Left    = KEY_LEFT
 Wiimote.Right   = KEY_RIGHT
 Wiimote.Minus   = KEY_BACK
 Wiimote.Plus    = KEY_FORWARD
 Wiimote.Home    = KEY_HOME
 Wiimote.1       = KEY_PROG1
 Wiimote.2       = KEY_PROG2

Same example as above but using wiimote IR sensors for moving mouse pointer.
Note that a sensor bar it's needed::

 # Wiimote IR as mouse XY axis (sensor bar needed)
 Plugin.ir_ptr.X = ABS_X
 Plugin.ir_ptr.Y = ABS_Y

 # Left and right mouse buttons
 Wiimote.A       = BTN_LEFT
 Wiimote.B       = BTN_RIGHT

 # Other wiimote buttons mapped to keys
 Wiimote.Up      = KEY_UP
 Wiimote.Down    = KEY_DOWN
 Wiimote.Left    = KEY_LEFT
 Wiimote.Right   = KEY_RIGHT
 Wiimote.Minus   = KEY_BACK
 Wiimote.Plus    = KEY_FORWARD
 Wiimote.Home    = KEY_HOME
 Wiimote.1       = KEY_PROG1
 Wiimote.2       = KEY_PROG2

Wiimote and nunchuk emulating a gamepad device::

 # Gamepad axis 0 (analog)
 Nunchuk.Stick.X = ABS_X
 Nunchuk.Stick.Y = ABS_Y

 # Gamepad axis 1 (absolute)
 Wiimote.Dpad.X = ABS_HAT0X
 Wiimote.Dpad.Y = ABS_HAT1X

 # Main gamepad buttons
 Wiimote.A = BTN_A
 Wiimote.B = BTN_B
 Nunchuk.C = BTN_C
 Nunchuk.Z = BTN_X

 # Other gamepad buttons
 Wiimote.Home = BTN_START
 Wiimote.Minus = BTN_SELECT
 Wiimote.Plus = BTN_MODE
 Wiimote.1 = BTN_Y
 Wiimote.2 = BTN_Z

Wii classic controller emulating a gamepad device::

 Classic.Dpad.X = ABS_X
 Classic.Dpad.Y = ABS_Y

 Classic.LStick.X = ABS_HAT0X
 Classic.LStick.Y = ABS_HAT0Y
 Classic.RStick.X = ABS_HAT1X
 Classic.RStick.Y = ABS_HAT1Y

 Classic.A = BTN_A
 Classic.B = BTN_B
 Classic.X = BTN_X
 Classic.Y = BTN_Y

 Classic.Minus = BTN_SELECT
 Classic.Plus  = BTN_START
 Classic.Home  = BTN_MODE

 Classic.L  = BTN_TL
 Classic.R  = BTN_TR
 Classic.ZL = BTN_TL2
 Classic.ZR = BTN_TR2


Sharing Mappings
----------------

One of best features of Wiican it's you can easily export your mappings and
import other people mappings. 

As you can see at :ref:`editing_mappings` a wiican mapping it's formed by 
a :ref:`info_file`, a :ref:`mapping_file` and an optional icon file. The
wiican GUI provides a comfortable environment to create and edit mappings with
synxtax validation and on-the-fly testing. Once you're happy with your mapping
you can export it as a :mimetype:`wii` file.

In this section we will explain the basis of the :mimetype:`wii` and some tips
and tricks for sharing mappings in the right way.

Wiican mapping package
~~~~~~~~~~~~~~~~~~~~~~

A :mimetype:`wii` file, known as wiican mapping package, it's a POSIX tar 
archive which contains the the :ref:`info_file`, :ref:`mapping_file` and 
optional icon.

There are reserved names for the 

Tips&Tricks
~~~~~~~~~~~


