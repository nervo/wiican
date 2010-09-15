:mod:`manager` --- mapping collection manager
=============================================

.. class:: MappingManager()

    The :class:`MappingManager` allows scan mappings from the 
    :attr:`MappingManager.system_paths` and :attr:`MappingManager.home_path` 
    directories and builds a :class:`Mapping` object for each, with 
    mapping dirname as key id. It also provides some methods for doing the 
    import and export mappings as Wiican Mapping Packages.
    
    The :class:`MappingManager` offers some python :class:`dict` methods 
    allowing to: get/set attributes, iteration, deletion and check size 
    (number of mappings managed).

    Despite of the metadata that every mapping has associated: name, version, 
    author ... (see :class:`Mapping` for details) there are some extra options
    in the context of managing a collection of mappings: order and visibility.
    The :class:`MappingManager` provides some methods for tracking with this
    options.

.. attribute:: MappingManager.home_path

    Directory where scan the user managed mappings.
    User managed mappings are only available for the running user which has 
    the perms for edit and remove them.

.. attribute:: MappingManager.system_paths

    List of directories where scan the system installed mappings.
    A system installed mapping will be available for all users but could not be
    removed or edited.

    .. important::

        The dirname it's used as key id for every loaded mapping.

        The last one with same :class:`Mapping` dirname between distinct 
        directories in :attr:`MappingManager.system_paths` to scan will prevail.

.. method:: MappingManager.scan_mappings()

    Scan mappings from default :attr:`MappingManager.system_paths` and 
    :attr:`MappingManager.home_path` directories and restores the order 
    and visibility options, if any.
    
    It also auto-import the initial wiican mapping packages into user data dir 
    if it does not exists.

    .. note::
        The system_paths mappings are loaded first and  mappings are distinguished 
        by dirname. If a system_paths mapping has the same dirname as one in the 
        home_paths, the system mapping it's ignored.

Manage mapping collections
--------------------------

.. method:: MappingManager.import_mapping(package_path)

    Import a wiican mapping package into :attr:`MappingManager.home_path`.
    Returns the assigned mapping_id key on the :class:`MappingManager`

    :param package_path: Path for the wiican mapping package to import
    :type package_path: string

    :rtype: string

    :raises: :exc:`MappingManagerError` if the file it's not recognised as
        a wiican mapping package

.. method:: MappingManager.export_mapping(mapping_id, dest_filepath)

    Export a mapping as a wiican mapping package.

    :param mapping_id: The :class:`MappingManager` key that refers a 
        :class:`Mapping` object to export.
    :type mapping_id: string

    :param dest_filepath: An absolute path for filename in which the 
        :class:`Mapping` object will be exported as wiican mapping package.
    :type dest_filepath: string

    :raises: :exc:`MappingManagerError` if no mapping found by the given 
        mapping_id

.. method:: MappingManager.add_new_mapping(mapping)

    Add a mapping to be controlled by mapping manager.
    Returns the assigned mapping_id key on the :class:`MappingManager`

    :param mapping: The mapping for be controlled by mapping manager
    :type mapping: :class:`Mapping`

    :rtype: string

.. method:: MappingManager.write_mapping(mapping)

    Write a mapping to disk. It's a proxy for :meth:`Mapping.write` that copies
    to the given mapping in :attr:`MappingManager.home_path` if the mapping
    belongs to any directory at :attr:`MappingManager.system_paths`.

    Returns the assigned mapping_id key on the :class:`MappingManager` as result
    of copying a system mapping to home_path or None.

    :param mapping: The mapping for be controlled by mapping manager
    :type mapping: :class:`Mapping`

    :rtype: string or :const:`None`


Mapping options in a collection
-------------------------------

.. method:: MappingManager.swap_mapping_order(mapping_id1, mapping_id2)

    Swap the order in the mapping collection between two mappings

    :param mapping_id1: The :class:`MappingManager` key that refers a 
        :class:`Mapping` object to swap order.
    :type mapping_id1: string
    
    :param mapping_id2: The other :class:`MappingManager` key that refers a
        :class:`Mapping` object to swap order.
    :type mapping_id2: string

    :raises: :exc:`MappingManagerError` if no mapping found by the given 
        mapping_id

.. method:: MappingManager.is_system_mapping(mapping_id)

    Check if the mapping it's a system mapping in the collection.

    :param mapping_id: The :class:`MappingManager` key that refers a
        :class:`Mapping` object to check.
    :type mapping_id: string

    :rtype: bool

    :raises: :exc:`MappingManagerError` if no mapping found by the given 
        mapping_id

.. method:: MappingManager.is_visible(mapping_id)

    Check if the mapping it's marked as visible in the collection.

    :param mapping_id: The :class:`MappingManager` key that refers a
        :class:`Mapping` object to check.
    :type mapping_id: string

    :rtype: bool

    :raises: :exc:`MappingManagerError` if no mapping found by the given 
        mapping_id

.. method:: MappingManager.set_visible(mapping_id, visible)

    Mark a mapping as visible or invisible.

    :param mapping_id: The :class:`MappingManager` key that refers a
        :class:`Mapping` object to set visibility.
    :type mapping_id: string

    :param visible: Visibility option
    :type visible: bool

    :raises: :exc:`MappingManagerError` if no mapping found by the given 
        mapping_id

.. method:: MappingManager.loadconf()

    Loads the stored order and visibility options for the user mappings 
    collection. The options are auto-loaded at 
    :meth:`MappingManager.scan_mappings`.

.. method:: MappingManager.saveconf()

    Saves the order and visibility options for the user mapping collection.

.. exception:: MappingManagerError

    Base class for all :mod:`manager` exceptions.

Examples
--------

List the mappings contained in a collection::

    >>> from wiican.mapping import MappingManager
    >>> mm = MappingManager()
    >>> print mm.home_path
    '/home/user/.local/share/wiican'
    >>> print mm.system_paths
    ['/usr/local/share/wiican/mappings_base']
    >>> mm.scan_mappings()
    >>> print mm
    {'222082': Mapping <Wiimote IR Mouse 0.0>, 
    '370583': Mapping <Classic Gamepad 0.0>, 
    '556216': Mapping <Wii Gamepad 0.0>}

Export and import mappings::

    >>> mm.export_mapping('222082', '/tmp/wiimote_ir.wii')
    >>> del(mm['222082'])
    >>> print mm
    {'370583': Mapping <Classic Gamepad 0.0>, 
    '556216': Mapping <Wii Gamepad 0.0>}
    >>> mm.import_mapping('/tmp/wiimote_ir.wii')
    '7872'
    >>> print mm
    {'370583': Mapping <Classic Gamepad 0.0>, 
    '556216': Mapping <Wii Gamepad 0.0>,
    '7872': Mapping <Wiimote IR Mouse 0.0>}

Collection mapping Options::

    >>> mm.options
    {'mapping_sort': ['556216', '370583', '7872'],
     'mapping_visible': set(['370583', '556216', '7872'])}
    >>> for mapping_id, mapping in mm.items():
    ...     print mapping.get_name(), mm.is_visible(mapping_id)
    Classic Gamepad True
    Wii Gamepad True
    Wiimote IR Mouse True
    >>> mm.set_visible['556216'].set_visible(False)
    >>> mm.swap_mapping_order('7872', '556216')
    >>> mm.options
    {'mapping_sort': ['7872', '556216', '370583'],
     'mapping_visible': set(['370583', '7872'])}
