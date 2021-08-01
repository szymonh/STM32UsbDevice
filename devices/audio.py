from . import DeviceExploit

from const import REQ_DIR, REQ_DIR_TO_DEVICE, REQ_DIR_TO_HOST, \
    REQ_TYPE, REQ_TYPE_CLASS, \
    REQ_RECIPIENT, REQ_RECIPIENT_DEVICE


class AudioExploit(DeviceExploit):

    _class = 0x01

    def read(self, length):
        return self.device.ctrl_transfer(
            bmRequestType=(
                (REQ_DIR_TO_HOST << REQ_DIR) |
                (REQ_TYPE_CLASS << REQ_TYPE) |
                (REQ_RECIPIENT_DEVICE << REQ_RECIPIENT)
            ),
            bRequest=0x81,
            wValue=0x01,
            wIndex=0x00,
            data_or_wLength=length
        )

    def write(self, data):
        self.device.ctrl_transfer(
            bmRequestType=(
                (REQ_DIR_TO_DEVICE << REQ_DIR) |
                (REQ_TYPE_CLASS << REQ_TYPE) |
                (REQ_RECIPIENT_DEVICE << REQ_RECIPIENT)
            ),
            bRequest=0x01,
            wValue=0x00,
            wIndex=0x00,
            data_or_wLength=data
        )
