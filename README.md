# STM32UsbDevice

## Overview

This simple utility attempts to verify if a STM32-based USB
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

## Affected devices

- STM32 or "compatible" MCUs with USB device support
- STM32Cube usb device middleware prior to 2.8.0

## Requirements

This tool requires python3 and the pyusb package.

> python3 -m pip install pyusb
or
> python3 -m pip install -r requirements.txt

For better results it is recommended to use a libusb build with
MAX_CTRL_BUFFER_LENGTH size increased from default 4096 bytes to
0xFFFF (libusb/os/linux_usbfs.h).

## Use example

Sample invocation to read 1000 bytes:

./stm32usb.py -v 0x0483 -p 0xdf11 -m read -l 1000

## Notice

Please do not treat this utility as an oracle.
It is not certain that a particular implementation
is secure simply because this tool fails to exploit it.
