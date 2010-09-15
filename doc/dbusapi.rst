DBus API Reference
==================

Interfaces 

* :ref:`org.gnome.Wiican`

.. _org.gnome.Wiican:

org.gnome.Wiican
----------------

A D-Bus service which allows to manage wiimote connections and track the 
wiimote connection states.

Methods
^^^^^^^

.. method:: ConnectWiimote(self, config_file, daemon):

    Request a wiimote connection using the config_file as mapping.

    In order to allow connections a bluetooth adaptor must be available, 
    the uinput module must be loaded and no other connection could be in 
    use (:attr:`WC_AVAILABLE` status)

    The bluetooth adaptor connection changes are auto-discovered.
    By now, the uinput module load/unload it's only discovered at service 
    start and at bluetooth adaptor connection changes too. So the best
    it's to ensure that module it's loaded before launching the service.

    The daemon mode sets the connection for waiting indefinitely for 
    pressing 1+2 (not daemon mode only wait for 3 seconds) and trying to 
    reconnect if wiimote it's disconnected.

    :param config_file: Absolute path to mapping config file
    :type config_file: string

    :param daemon: Set the daemon mode
    :type daemon: bool

    **Possible Errors**:

    * Not uinput module present

    * Not bluetooth adapter present

    * A wiimote connection still in use (disconnect first)

    * Mapping validation error

.. method:: DisconnectWiimote()

    Close the wiimote connection or do nothing if no connection in use.

.. method:: GetStatus()

    Get the current status as defined in the StatusChanged signal.

    :rtype: an integer representing the current status

.. method:: Quit()

    Exit wiican dbus service.

Signals
^^^^^^^ 

.. method:: StatusChanged(status)

    Emitted when the status of the connection changes.

    :param status: an integer indicating the new status
    :type status: int

Types
^^^^^

.. attribute:: WC_DISABLED

    Status indicating No bluetooth adaptor available and uinput module it's 
    not loaded. 
    
    Wiimote connection could not be performed.

    Integer value: 0

.. attribute:: WC_BLUEZ_PRESENT    

    Status indicating Bluetooth adaptor available, nor uinput module. 
    
    Wiimote connection could not be performed.

    Integer value: 1

.. attribute:: WC_UINPUT_PRESENT

    Status indicating the uinput module it's loaded, no bluetooth device 
    available. 
    
    Wiimote connection could not be performed.

    Integer value: 2 

.. attribute:: WC_AVAILABLE

    Status indicating bluetooth adaptor available, uinput module loaded.
    
    Wiimote connection could be performed.

    Integer value: 3

.. attribute:: WC_CONNECTED

    Status indicating wiimote connection in use. 
    
    Disconnect first to make a new connection.

    Integer value: 7
