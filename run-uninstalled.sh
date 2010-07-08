#!/bin/sh

# Maybe this only works on debian/ubuntu
DBUS_LOCAL=/usr/local/share/dbus-1/services
CURDIR=$(pwd)

# Gen .in files with @PREFIX@ replaced
for file in org.gnome.wiican.service wiican/defs.py; do
    cp $file.in $file
    sed -i "s|@PREFIX@|$CURDIR|g" $file
done

if [ ! -f $DBUS_LOCAL/org.gnome.wiican.service ]; then
    echo "I need to copy org.gnome.wiican.service file to dbus service directory"
    echo "Do you want me to do it for you? [y/n]: "
    read response
    case "$response" in
    y|Y)    
        if [ ! -d  ] $DBUS_LOCAL; then mkdir -p $DBUS_LOCAL; fi
        sudo cp org.gnome.wiican.service $DBUS_LOCAL;;
    *) 
        echo "Wiican will not run";;
    esac
fi

export PYTHONPATH=$CURDIR
./bin/wiican
