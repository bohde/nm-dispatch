Overview 
---------
This program is similar to Network Manager's dispatcher, with the exception that it runs at the user level.

Requirements
____________
 - Network Manager
 - Python 2.6
 - Python DBus Bindings 

Usage
-----
I recommend putting the following in your .xsession

::

  ./nm-dispatch.py &

This may be different depending on how you start your window manager. 

Once running, this will call all executables in ~/.nmdispatch/, passing in three arguments: the interface name (i.e. eth0), "up" or "down" depending on the state of the interface, and the current access point SSID if the interface is wireless.

Contact Info
____________
:Author: 
    `Josh Bohde <josh.bohde@gmail.com>`_
