from . import DeviceExploit

from const import REQ_DIR, REQ_DIR_TO_DEVICE, \
    REQ_TYPE, REQ_TYPE_CLASS, \
    REQ_RECIPIENT, REQ_RECIPIENT_DEVICE


class CdcRndis(DeviceExploit):

    _class = 0x0a
    _subclass = 0x00
    _protocol = 0x00

    def write(self, data):
        self.device.ctrl_transfer(
            bmRequest=(
                (REQ_DIR_TO_DEVICE << REQ_DIR) |
                (REQ_TYPE_CLASS << REQ_TYPE) |
                (REQ_RECIPIENT_DEVICE << REQ_RECIPIENT)
            ),
            bRequest=0x00,
            wValue=0x00,
            wIndex=0x00,
            data_or_wLenght=data
        )
