.. Wiican documentation master file, created by
   sphinx-quickstart on Sun Aug 29 12:10:52 2010.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Wiican's documentation!
==================================

WiiCan assists to setup your wiimote under GNU/Linux, create and share mappings. 
It also provide a d-bus api, so third apps could make use of wiimote easily. 
WiiCan acts as a sytem tray icon, programmed in python. It connects to bluez 
and hal via dbus for tracking the available bluetooth devices and wiimote connection status.

On backend it's wminput , the cwiid event driver for wiimote. WiiCan uses wminput and 
wminput configuration files for define and use mappings.

Features:

* Discover if everything it's ok for connecting wiimote.

* Notify the state of wiimote usaging.

* User-defined mappings creation, edition and share assistant.

* D-Bus API to manage the wiimote connections

Contents:

********************
Developers Reference
********************

.. toctree::
    :maxdepth: 2

    dbusapi.rst

    module_mapping.rst
    module_manager.rst

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`

