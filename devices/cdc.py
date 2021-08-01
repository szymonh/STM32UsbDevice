from . import DeviceExploit

from const import REQ_DIR, REQ_DIR_TO_DEVICE, REQ_DIR_TO_HOST, \
    REQ_TYPE, REQ_TYPE_CLASS, \
    REQ_RECIPIENT, REQ_RECIPIENT_DEVICE


class CdcExploit(DeviceExploit):

    _class = 0x02
    _subclass = 0x02

    def read(self, length):
        return self.device.ctrl_transfer(
            bmRequestType=(
                (REQ_DIR_TO_HOST << REQ_DIR) |
                (REQ_TYPE_CLASS << REQ_TYPE) |
                (REQ_RECIPIENT_DEVICE << REQ_RECIPIENT)
            ),
            bRequest=0x09,
            wValue=0x01,
            wIndex=0x00,
            data_or_wLength=length
        )

    def write(self, data):
        self.device.ctrl_transfer(
            bmRequest=(
                (REQ_DIR_TO_DEVICE << REQ_DIR) |
                (REQ_TYPE_CLASS << REQ_TYPE) |
                (REQ_RECIPIENT_DEVICE << REQ_RECIPIENT)
            ),
            bRequest=0x09,
            wValue=0x01,
            wIndex=0x00,
            data_or_wLenght=data
        )
