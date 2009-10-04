#!/usr/bin/env python
"""
nm-dispatch.py: A user level network manager dispatcher.
Copyright (c) 2009, Josh Bohde

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>
"""

import os.path
import pwd
import xml.etree.ElementTree as et
from subprocess import call

import dbus.mainloop.glib
import gobject


def runFiles(call_args):
    for f in filter(lambda x: os.access(x, os.X_OK), os.listdir('.')):
        c = ' '.join(['./' + f] + ["'%s'" % s for s in call_args])
        call(c,shell=True)
        

def wrap_dbus(dbus_object):
    do = dbus_object
    def wrapper(*args,**kwargs):
        if kwargs['member'] == 'StateChanged':
            check = int(args[0])
            if check in [3,8]:
                call_args = [str(do.get("Interface"))] + \
                            (["up",do.getSsid()] if check==8 else ["down"])
                runFiles(call_args)
    return wrapper


class NetworkManager(object):
    def __init__(self):
        self.nm = dbus.SystemBus().get_object('org.freedesktop.NetworkManager',
                                              '/org/freedesktop/NetworkManager')
        
    def getDevices(self):
        return [str(x) for x in list(self.nm.GetDevices(
            dbus_interface='org.freedesktop.NetworkManager'))]


class NetworkDevice(object):
    def __init__(self, object_path):
        self.path = object_path
        self.obj = dbus.SystemBus().get_object('org.freedesktop.NetworkManager', object_path)
        self.ifaces = self.parseIfaces()
        
    def parseIfaces(self):
        tree = et.fromstring(self.obj.Introspect(dbus_interface='org.freedesktop.DBus.Introspectable'))
        return filter(lambda x: "NetworkManager" in x,
                      [n.get("name") for n in tree.findall("interface")])

    def get(self, prop):
        for iface in  self.ifaces:
            try:
                return self.obj.Get(iface, prop, dbus_interface='org.freedesktop.DBus.Properties')
            except Exception as e:
                pass
            raise AttributeError(prop)

    def getSsid(self):
        ap = NetworkDevice(self.get("ActiveAccessPoint"))
        return ''.join((chr(x) for x in list(ap.get("Ssid"))))

        
def main():
    nmdispatch = pwd.getpwuid(os.getuid())[5]+"/.nmdispatch/"

    if not(os.access(nmdispatch, os.R_OK)):
           os.mkdir(nmdispatch)
    os.chdir(nmdispatch)
           
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()
    nm = NetworkManager()

    for dev in nm.getDevices():
        nd = NetworkDevice(dev)
        
        bus.add_signal_receiver(
            wrap_dbus(nd), 
            interface_keyword='dbus_interface', 
            member_keyword='member',
            dbus_interface="org.freedesktop.NetworkManager.Device",
            path=dev)
                            
    gobject.MainLoop().run()

if __name__ == '__main__':
    main()
    
