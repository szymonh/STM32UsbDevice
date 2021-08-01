from abc import abstractmethod

import importlib
import glob
import re


def relaxed_check(prop_or_none, prop):
    return (prop_or_none is None) or (prop_or_none == prop)


class DeviceExploit:

    _class = None
    _subclass = None
    _protocol = None

    def __init__(self, usbdev) -> None:
        self.device = usbdev

    @classmethod
    def __load_exploit(cls, device_class):
        imp = importlib.import_module('devices.' + device_class)
        for attribute in dir(imp):
            val = getattr(imp, attribute)
            if DeviceExploit.is_subclass(val):
                return val
        return None

    @classmethod
    def load_children(cls):
        pattern = r'devices/([\S]+).py'
        modules = [re.match(pattern, file_name).group(1) for file_name
                   in glob.glob('devices/*.py')]
        children = []
        for module in modules:
            child = cls.__load_exploit(module)
            if child:
                children.append(child)
        return children

    @classmethod
    def load_child(cls, usbclass, subclass, protocol):
        for child in cls.load_children():
            if child._class is not None and \
                    relaxed_check(child._class, usbclass) and \
                    relaxed_check(child._subclass, subclass) and \
                    relaxed_check(child._protocol, protocol):
                return child
        return None

    @classmethod
    def is_subclass(cls, child_class):
        try:
            return issubclass(child_class, cls) and child_class != cls
        except TypeError:
            return False

    @abstractmethod
    def read(self, length):
        raise NotImplementedError('Operation not supported')

    @abstractmethod
    def write(self, data):
        raise NotImplementedError('Operation not supported')

    @classmethod
    def build(cls, usbdev, device_type):
        return cls.__load_exploit(device_type)(usbdev)

    def exploit(self, mode, data_or_length):
        return getattr(self, mode)(data_or_length)
