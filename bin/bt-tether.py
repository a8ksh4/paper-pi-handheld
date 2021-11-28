#!/usr/bin/env python3

import logging
import os
import subprocess
import time
from threading import Lock

import dbus

# import pwnagotchi.plugins as plugins
# import pwnagotchi.ui.fonts as fonts
# from pwnagotchi.ui.components import LabeledValue
# from pwnagotchi.ui.view import BLACK
# from pwnagotchi.utils import StatusFile


class BTError(Exception):
    """
    Custom bluetooth exception
    """
    pass


class BTNap:
    """
    This class creates a bluetooth connection to the specified bt-mac

    see https://github.com/bablokb/pi-btnap/blob/master/files/usr/local/sbin/btnap.service.py
    """

    IFACE_BASE = 'org.bluez'
    IFACE_DEV = 'org.bluez.Device1'
    IFACE_ADAPTER = 'org.bluez.Adapter1'
    IFACE_PROPS = 'org.freedesktop.DBus.Properties'

    def __init__(self, mac):
        self._mac = mac

    @staticmethod
    def get_bus():
        """
        Get systembus obj
        """
        bus = getattr(BTNap.get_bus, 'cached_obj', None)
        if not bus:
            bus = BTNap.get_bus.cached_obj = dbus.SystemBus()
        return bus

    @staticmethod
    def get_manager():
        """
        Get manager obj
        """
        manager = getattr(BTNap.get_manager, 'cached_obj', None)
        if not manager:
            manager = BTNap.get_manager.cached_obj = dbus.Interface(
                BTNap.get_bus().get_object(BTNap.IFACE_BASE, '/'),
                'org.freedesktop.DBus.ObjectManager')
        return manager

    @staticmethod
    def prop_get(obj, k, iface=None):
        """
        Get a property of the obj
        """
        if iface is None:
            iface = obj.dbus_interface
        return obj.Get(iface, k, dbus_interface=BTNap.IFACE_PROPS)

    @staticmethod
    def prop_set(obj, k, v, iface=None):
        """
        Set a property of the obj
        """
        if iface is None:
            iface = obj.dbus_interface
        return obj.Set(iface, k, v, dbus_interface=BTNap.IFACE_PROPS)

    @staticmethod
    def find_adapter(pattern=None):
        """
        Find the bt adapter
        """

        return BTNap.find_adapter_in_objects(BTNap.get_manager().GetManagedObjects(), pattern)

    @staticmethod
    def find_adapter_in_objects(objects, pattern=None):
        """
        Finds the obj with a pattern
        """
        bus, obj = BTNap.get_bus(), None
        for path, ifaces in objects.items():
            adapter = ifaces.get(BTNap.IFACE_ADAPTER)
            if adapter is None:
                continue
            if not pattern or pattern == adapter['Address'] or path.endswith(pattern):
                obj = bus.get_object(BTNap.IFACE_BASE, path)
                yield dbus.Interface(obj, BTNap.IFACE_ADAPTER)
        if obj is None:
            raise BTError('Bluetooth adapter not found')

    @staticmethod
    def find_device(device_address, adapter_pattern=None):
        """
        Finds the device
        """
        return BTNap.find_device_in_objects(BTNap.get_manager().GetManagedObjects(),
                                            device_address, adapter_pattern)

    @staticmethod
    def find_device_in_objects(objects, device_address, adapter_pattern=None):
        """
        Finds the device in objects
        """
        bus = BTNap.get_bus()
        path_prefix = ''
        if adapter_pattern:
            if not isinstance(adapter_pattern, str):
                adapter = adapter_pattern
            else:
                adapter = BTNap.find_adapter_in_objects(objects, adapter_pattern)
            path_prefix = adapter.object_path
        for path, ifaces in objects.items():
            device = ifaces.get(BTNap.IFACE_DEV)
            if device is None:
                continue
            if str(device['Address']).lower() == device_address.lower() and path.startswith(path_prefix):
                obj = bus.get_object(BTNap.IFACE_BASE, path)
                return dbus.Interface(obj, BTNap.IFACE_DEV)
        raise BTError('Bluetooth device not found')

    def power(self, on=True):
        """
        Set power of devices to on/off
        """
        logging.debug("BT-TETHER: Changing bluetooth device to %s", str(on))

        try:
            devs = list(BTNap.find_adapter())
            devs = dict((BTNap.prop_get(dev, 'Address'), dev) for dev in devs)
        except BTError as bt_err:
            logging.error(bt_err)
            return None

        for dev_addr, dev in devs.items():
            BTNap.prop_set(dev, 'Powered', on)
            logging.debug('Set power of %s (addr %s) to %s', dev.object_path, dev_addr, str(on))

        if devs:
            return list(devs.values())[0]

        return None


    def is_paired(self):
        """
        Check if already connected
        """
        logging.debug("BT-TETHER: Checking if device is paired")

        bt_dev = self.power(True)

        if not bt_dev:
            logging.debug("BT-TETHER: No bluetooth device found.")
            return False

        try:
            dev_remote = BTNap.find_device(self._mac, bt_dev)
            return bool(BTNap.prop_get(dev_remote, 'Paired'))
        except BTError:
            logging.debug("BT-TETHER: Device is not paired.")
        return False

    def wait_for_device(self, timeout=15):
        """
        Wait for device

        returns device if found None if not
        """
        logging.debug("BT-TETHER: Waiting for device")

        bt_dev = self.power(True)

        if not bt_dev:
            logging.debug("BT-TETHER: No bluetooth device found.")
            return None

        try:
            logging.debug("BT-TETHER: Starting discovery ...")
            bt_dev.StartDiscovery()
        except Exception as bt_ex:
            logging.error(bt_ex)
            raise bt_ex

        dev_remote = None

        # could be set to 0, so check if > -1
        while timeout > -1:
            try:
                dev_remote = BTNap.find_device(self._mac, bt_dev)
                logging.debug("BT-TETHER: Using remote device (addr: %s): %s",
                              BTNap.prop_get(dev_remote, 'Address'), dev_remote.object_path)
                break
            except BTError:
                logging.debug("BT-TETHER: Not found yet ...")

            time.sleep(1)
            timeout -= 1

        try:
            logging.debug("BT-TETHER: Stopping Discovery ...")
            bt_dev.StopDiscovery()
        except Exception as bt_ex:
            logging.error(bt_ex)
            raise bt_ex

        return dev_remote

    @staticmethod
    def pair(device):
        logging.debug('BT-TETHER: Trying to pair ...')
        try:
            device.Pair()
            logging.debug('BT-TETHER: Successful paired with device ;)')
            return True
        except dbus.exceptions.DBusException as err:
            if err.get_dbus_name() == 'org.bluez.Error.AlreadyExists':
                logging.debug('BT-TETHER: Already paired ...')
                return True
        except Exception:
            pass
        return False

    @staticmethod
    def nap(device):
        logging.debug('BT-TETHER: Trying to nap ...')

        try:
            logging.debug('BT-TETHER: Connecting to profile ...')
            device.ConnectProfile('nap')
        except Exception:  # raises exception, but still works
            pass

        net = dbus.Interface(device, 'org.bluez.Network1')

        try:
            logging.debug('BT-TETHER: Connecting to nap network ...')
            net.Connect('nap')
            return net, True
        except dbus.exceptions.DBusException as err:
            if err.get_dbus_name() == 'org.bluez.Error.AlreadyConnected':
                return net, True

            connected = BTNap.prop_get(net, 'Connected')
            if not connected:
                return None, False
            return net, True


class SystemdUnitWrapper:
    """
    systemd wrapper
    """

    def __init__(self, unit):
        self.unit = unit

    @staticmethod
    def _action_on_unit(action, unit):
        process = subprocess.Popen(f"systemctl {action} {unit}", shell=True, stdin=None,
                                   stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
        process.wait()
        if process.returncode > 0:
            return False
        return True

    @staticmethod
    def daemon_reload():
        """
        Calls systemctl daemon-reload
        """
        process = subprocess.Popen("systemctl daemon-reload", shell=True, stdin=None,
                                   stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
        process.wait()
        if process.returncode > 0:
            return False
        return True

    def is_active(self):
        """
        Checks if unit is active
        """
        return SystemdUnitWrapper._action_on_unit('is-active', self.unit)

    def is_enabled(self):
        """
        Checks if unit is enabled
        """
        return SystemdUnitWrapper._action_on_unit('is-enabled', self.unit)

    def is_failed(self):
        """
        Checks if unit is failed
        """
        return SystemdUnitWrapper._action_on_unit('is-failed', self.unit)

    def enable(self):
        """
        Enables the unit
        """
        return SystemdUnitWrapper._action_on_unit('enable', self.unit)

    def disable(self):
        """
        Disables the unit
        """
        return SystemdUnitWrapper._action_on_unit('disable', self.unit)

    def start(self):
        """
        Starts the unit
        """
        return SystemdUnitWrapper._action_on_unit('start', self.unit)

    def stop(self):
        """
        Stops the unit
        """
        return SystemdUnitWrapper._action_on_unit('stop', self.unit)

    def restart(self):
        """
        Restarts the unit
        """
        return SystemdUnitWrapper._action_on_unit('restart', self.unit)


class IfaceWrapper:
    """
    Small wrapper to check and manage ifaces

    see: https://github.com/rlisagor/pynetlinux/blob/master/pynetlinux/ifconfig.py
    """

    def __init__(self, iface):
        self.iface = iface
        self.path = f"/sys/class/net/{iface}"

    def exists(self):
        """
        Checks if iface exists
        """
        return os.path.exists(self.path)

    def is_up(self):
        """
        Checks if iface is ip
        """
        return open(f"{self.path}/operstate", 'r').read().rsplit('\n') == 'up'

    def set_addr(self, addr):
        """
        Set the netmask
        """
        process = subprocess.Popen(f"ip addr add {addr} dev {self.iface}", shell=True, stdin=None,
                                   stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
        process.wait()

        if process.returncode == 2 or process.returncode == 0:  # 2 = already set
            return True

        return False

    @staticmethod
    def set_route(gateway, device):
        process = subprocess.Popen(f"ip route replace default via {gateway} dev {device}", shell=True, stdin=None,
                                   stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
        process.wait()

        if process.returncode > 0:
            return False

        return True


class Device:
    def __init__(self, name, share_internet, mac, ip, netmask, interval, gateway=None, priority=10, scantime=15, search_order=0, max_tries=0, **kwargs):
        self.name = name
        sf = f'/root/.bt-tether-{name}'
        # if not os.path.exists(sf):
        #     print('Creating status file', sf)
        #     with open(sf, 'w') as f:
        #         pass
        # self.status = StatusFile(sf)
        # self.status.update()
        self.tries = 0
        self.network = None

        self.max_tries = max_tries
        self.search_order = search_order
        self.share_internet = share_internet
        self.ip = ip
        self.netmask = netmask
        self.gateway = gateway
        self.interval = interval
        self.mac = mac
        self.scantime = scantime
        self.priority = priority

    def connected(self):
        """
        Checks if device is connected
        """
        return self.network and BTNap.prop_get(self.network, 'Connected')

    def interface(self):
        """
        Returns the interface name or None
        """
        if not self.connected():
            return None
        return BTNap.prop_get(self.network, 'Interface')

    # def on_unload(self, ui):
    #     self.running = False
    #     with ui._lock:
    #         ui.remove_element('bluetooth')


    # def on_ui_setup(self, ui):
    #     with ui._lock:
    #         ui.add_element('bluetooth', LabeledValue(color=BLACK, label='BT', value='-', position=(ui.width() / 2 - 15, 0),
    #                        label_font=fonts.Bold, text_font=fonts.Medium))


    # def on_ui_update(self, ui):
    #     ui.set('bluetooth', self.status)


if __name__ == '__main__':
    print('foo')
    
    options = { 'enabled': True, 'priority': 99, 
                'scantime': 15, 'search_order': 1,
                'max_tries': 0, 'share_internet': True, 
                'mac': 'F0:5C:77:C1:9C:B5', 'ip': '192.168.44.45',
                'netmask': 24, 'interval': 1}

    device = Device(name='P4XL', **options)
    bt_unit = SystemdUnitWrapper('bluetooth.service')
    if not bt_unit.is_active():
        bt_unit.start()

    status = '5'
    route_applied = False
    while True:
       time.sleep(10)
       connected = False

       if device.connected():
           continue

       if not device.max_tries:
           device.tries += 1

       bt = BTNap(device.mac)

       try:
           print('BT-TETHER: Search %d secs for %s ...', device.scantime, device.name)
           dev_remote = bt.wait_for_device(timeout=device.scantime)
           if dev_remote is None:
               logging.debug('BT-TETHER: Could not find %s, try again in %d minutes.', device.name, device.interval)
               status = 'NF'
               continue
       except Exception as bt_ex:
           print(bt_ex)
           status = 'NF'
           continue

       paired = bt.is_paired()
       if not paired:
           if BTNap.pair(dev_remote):
               print('BT-TETHER: Paired with %s.', device.name)
           else:
               print('BT-TETHER: Pairing with %s failed ...', device.name)
               status = 'PE'
               continue
       else:
           print('BT-TETHER: Already paired.')


       print('BT-TETHER: Try to create nap connection with %s ...', device.name)
       device.network, success = BTNap.nap(dev_remote)
       interface = None

       if success:
           try:
               interface = device.interface()
           except Exception:
               print('BT-TETHER: Could not establish nap connection with %s', device.name)
               continue

           if interface is None:
               status = 'BE'
               print('BT-TETHER: Could not establish nap connection with %s', device.name)
               continue

           print('BT-TETHER: Created interface (%s)', interface)
           status = 'C'
           any_device_connected = True
           device.tries = 0 # reset tries
       else:
           print('BT-TETHER: Could not establish nap connection with %s', device.name)
           status = 'NF'
           continue

       addr = f"{device.ip}/{device.netmask}"
       if device.gateway:
           gateway = device.gateway
       else:
           gateway = ".".join(device.ip.split('.')[:-1] + ['1'])

       wrapped_interface = IfaceWrapper(interface)
       print('BT-TETHER: Add ip to %s', interface)
       if not wrapped_interface.set_addr(addr):
           status = 'AE'
           print("BT-TETHER: Could not add ip to %s", interface)
           continue

       if device.share_internet:
           if not route_applied:
               print('BT-TETHER: Set default route to %s via %s', gateway, interface)
               IfaceWrapper.set_route(gateway, interface)
               route_applied = True

               print('BT-TETHER: Change resolv.conf if necessary ...')
               with open('/etc/resolv.conf', 'r+') as resolv:
                   nameserver = resolv.read()
                   if 'nameserver 9.9.9.9' not in nameserver:
                       print('BT-TETHER: Added nameserver')
                       resolv.seek(0)
                       resolv.write(nameserver + 'nameserver 9.9.9.9\n')

       if device.connected:
           status = 'C'
    print('Status:', status)
