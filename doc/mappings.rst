Mapping edition how-to
======================

One of best wiican features it's to create your own mappings and share with 
friends. Wiican mappings are based on `wminput config files 
<http://abstrakraft.org/cwiid/wiki/wminput>`_. 

In this doc we'll try to expose the basic for editing wiican mappings, building
wminput config files, and show how to export this as wiican mapping package for
sharing.

Wiican Mappings
---------------

Actually wiican mappings are based on wminput config files with some
metadata and icon associated: 

* A file containing the wminput code

* A file containing name, description, author and version

* An optional icon file

Every mapping lives on home directory under .local/share/wiican/
so maybe you want to see if i'm telling the true now ;).

By the current mapping definition (wiican 0.3.0) there are names reserved for
the mapping file and the info file: mapping.wminput and info.desktop 
respectively.

Info file
~~~~~~~~~

The info file contains the name, description, author and version for a wiican
mapping file. It follows the `XDG DesktopEntry specification <http://www.freedesktop.org/wiki/Specifications/desktop-entry-spec>`_ in order to store translations and special fields easily.


