# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 15:18:49 2020

@author: Testa4
"""
import importlib

from .mockers import MockLaser


class FullDigitalLaser:
    def __new__(cls, iName, ports):
        try:
            if len(ports) < 1:
                raise ValueError('FullDigitalLaser requires at least one port, none passed')

            driver = getDriver(iName)

            lasers = []
            for port in ports:
                laser = driver(port)
                laser.initialize()
                lasers.append(laser)

            return lasers[0] if len(ports) == 1 else LinkedFullDigitalLaser(lasers)
        except:
            return MockLaser()


class LinkedFullDigitalLaser:
    def __init__(self, lasers):
        if len(lasers) < 1:
            raise ValueError('LinkedFullDigitalLaser requires at least one laser, none passed')

        self.lasers = lasers

    @property
    def idn(self):
        return 'Linked Lasers ' + ' '.join([str(laser.idn) for laser in self.lasers])

    @property
    def autostart(self):
        value = self.lasers[0].autostart
        for laser in self.lasers:
            if laser.autostart != value:
                raise ValueError('Laser {laser.idn} autostart state is {laser.autostart} while laser'
                                 ' {self.lasers[0]} autostart state is {value}')

        return value

    @autostart.setter
    def autostart(self, value):
        for laser in self.lasers:
            laser.autostart = value

    @property
    def enabled(self):
        value = self.lasers[0].enabled
        for laser in self.lasers:
            if laser.enabled != value:
                raise ValueError('Laser {laser.idn} enabled state is {laser.enabled} while laser'
                                 ' {self.lasers[0]} enabled state is {value}')

        return value

    @enabled.setter
    def enabled(self, value):
        for laser in self.lasers:
            laser.enabled = value

    @property
    def power(self):
        return sum([laser.power for laser in self.lasers])

    @property
    def power_sp(self):
        return sum([laser.power_sp for laser in self.lasers])

    @power_sp.setter
    def power_sp(self, value):
        for laser in self.lasers:
            laser.power_sp = value / len(self.lasers)

    @property
    def digital_mod(self):
        value = self.lasers[0].digital_mod
        for laser in self.lasers:
            if laser.digital_mod != value:
                raise ValueError('Laser {laser.idn} digital_mod state is {laser.digital_mod} while'
                                 ' laser {self.lasers[0]} digital_mod state is {value}')

        return value

    @digital_mod.setter
    def digital_mod(self, value):
        for laser in self.lasers:
            laser.digital_mod = value

    @property
    def mod_mode(self):
        return [laser.mod_mode for laser in self.lasers]

    def enter_mod_mode(self):
        for laser in self.lasers:
            laser.enter_mod_mode()

    def changeEdit(self):
        for laser in self.lasers:
            laser.changeEdit()

    def query(self, value):
        for laser in self.lasers:
            laser.query(value)

    @property
    def power_mod(self):
        """Laser modulated power (mW).
        """
        return sum([laser.power_mod for laser in self.lasers])

    @power_mod.setter
    def power_mod(self, value):
        for laser in self.lasers:
            laser.power_mod = value / len(self.lasers)

    def finalize(self):
        for laser in self.lasers:
            laser.finalize()


def getDriver(iName):
    pName, driverName = iName.rsplit('.', 1)

    try:
        # Try our included drivers first
        package = importlib.import_module('model.drivers.' + pName)
        driver = getattr(package, driverName)
    except ModuleNotFoundError or AttributeError:
        # If that fails, try to load the driver from lantz
        package = importlib.import_module('lantz.drivers.' + pName)
        driver = getattr(package, driverName)

    return driver


