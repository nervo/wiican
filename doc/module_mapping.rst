:mod:`mapping` --- representation of a wiican mapping
===============================================================

An object representation of a wiican mapping.

.. note::
    A wiican mapping must be located in a single directory containing a file 
    with the wminput code, a file containing the metadata (name, description, 
    author, version) and an optional icon file.

.. class:: Mapping([path=None])
      
    Builds a mapping object.

    The :attr:`Mapping.info_filename` and :attr:`Mapping.mapping_filename` class attributes
    marks the requiered filenames for the metadata file and wminput config 
    file respectively. The :attr:`Mapping.mapping_filename` file must contain 
    wminput config file code The :attr:`Mapping.info_filename` follows XDG 
    DesktopEntry syntax.
    
    The :attr:`Mapping.info_filename` contains the source of the optional associated
    icon. If no icon found or no icon directive it falls back to default 
    icon.

    .. important::
        There are three possibilities for icon setting:

        - An absolute path where the icon it's stored
        - Icon filename if it's stored in the same dir as :attr:`Mapping.info_filename`
        - Theme-icon-name for auto-getting the icon from the icon theme

    :param path: dirname which contains the needed files for building the 
                 mapping object or :const:`None` for a new empty mapping.
    :type path: string


.. attribute:: Mapping.info_filename

    Mandatory filename for the metadata file.

    Default value: ``info.desktop``

.. attribute:: Mapping.mapping_filename

    Mandatory filename for the wminput config file.

    Default value: ``mapping.wminput``

.. method:: Mapping.get_path()

    Gets the absolute path where the wiican mapping it's saved.

    :rtype: string if the mapping it's not saved yet.

.. method:: Mapping.write([dest_path=None])

    Saves the mapping object by writing the files in the mapping directory.

    The metadata it's saved in :attr:`Mapping.info_filename` file.
    The wminput config code it's saved in :attr:`Mapping.mapping_filename` file.
    The associated icon it's copied to the mapping directory.

    :raises: :exc:`MappingError` if no path provided for a new mapping

Mapping info metadata
---------------------

.. method:: Mapping.get_name()

    Gets the name of the mapping contained in the metadata file

    :rtype: string

.. method:: Mapping.set_name(name)

    Sets the name for the mapping

    :param name: the mapping name
    :type name: string

.. method:: Mapping.get_comment()

    Gets the descriptive comment

    :rtype: string

.. method:: Mapping.set_comment(comment)

    Sets the descriptive comment for the mapping

    :param comment: a comment about the mapping
    :type comment: string

.. method:: Mapping.get_icon()

    Gets the associated icon contained in the metadata file.
    If no icon found or no icon directive it falls back to default icon.

    :rtype: string

.. method:: Mapping.set_icon(icon_path)

    Sets the icon for the mapping. 

    .. important::
        There are three possibilities for icon setting:

        - An absolute path where the icon it's stored
        - Icon filename if it's stored in the same dir as :attr:`Mapping.info_filename`
        - Theme-icon-name for auto-getting the icon from the icon theme

    :param icon_path: the icon absolute path or filename for being associated
                      with the mapping
    :type icon_path: string

.. method:: Mapping.get_authors()

    Gets the mapping authors

    :rtype: string

.. method:: Mapping.set_authors(authors)

    Sets the author for the mapping.

    .. tip::
        It's better to set the author/s as:
            
            Name <email@address.too> [, Name2 <second@email.address> ...]

        In order to contact the author/s for enhancements or bug reporting
        about the mapping.

    :param authors: author/s for the mapping
    :type authors: string

.. method:: Mapping.get_version()

    Gets the version of the mapping contained

    :rtype: string

.. method:: Mapping.set_version(version)

    Sets the version of the mapping

    :param version: version for the mapping
    :type version: string

Wminput mapping code
--------------------

.. method:: Mapping.get_mapping()

    Gets the wminput config code

    :rtype: string

.. method:: Mapping.set_mapping(mapping)

    Sets the wminput config code

    :param mapping: wminput config code
    :type mapping: string

.. exception:: MappingError

    Base class for all :mod:`mapping` exceptions.

Examples
--------

Create and write a new mapping::

    >>> from wiican.mapping import Mapping
    >>> x = Mapping()
    >>> x.set_name('Test Mapping')
    >>> x.set_comment('A test mapping for doing doc examples')
    >>> print x
    <Test Mapping 0.0>
    >>> x.set_mapping('Wiimote.A = KEY_ENTER')
    >>> x.write('/tmp/test_mapping')

Load a mapping, set a theme icon and save::

    >>> y = Mapping('/tmp/test_mapping/')
    >>> print y.get_name(), y.get_comment()
    A test mapping for doing doc examples
    >>> y.set_icon('gnome-mouse')
    >>> y.get_icon()
    u'/usr/share/pixmaps/gnome-mouse.png'
    >>> y.write()
    >>> y.get_icon()
    u'/tmp/test_mapping/gnome-mouse.png'
