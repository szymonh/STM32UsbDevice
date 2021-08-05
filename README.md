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

## Vulnerability

The issues are caused by insufficient validation/handling of wLength
in certain usb device class control transfer handlers. Processing of
control transfer messages crafted to have wLength value
exceeding buffer size results in buffer overflows. In case of readout
this may lead to leage of various secrets including encryption keys or
credentials. Write of arbitrary content into memory might allow one to alter
critical data structures or execute arbitrary code.

For example one is capable of overflowing the hdfu->buffer by utilizing
a control trasnfer request with wLength set to a value larger then the
buffer size. The hdfu->wlength value supplied to USBD_CtlPrepareRx is
propagated directly from request wLength without assuring that buffer
boundaries are respected and overflow is prevented.

```
static void DFU_Download(USBD_HandleTypeDef *pdev, USBD_SetupReqTypedef *req)
{
  USBD_DFU_HandleTypeDef *hdfu = (USBD_DFU_HandleTypeDef *)pdev->pClassData;

  if (hdfu == NULL)
  {
    return;
  }

  /* Data setup request */
  if (req->wLength > 0U)
  {
    if ((hdfu->dev_state == DFU_STATE_IDLE) || (hdfu->dev_state == DFU_STATE_DNLOAD_IDLE))
    {
      /* Update the global length and block number */
      hdfu->wblock_num = req->wValue;
      hdfu->wlength = req->wLength;

      /* Update the state machine */
      hdfu->dev_state = DFU_STATE_DNLOAD_SYNC;
      hdfu->dev_status[4] = hdfu->dev_state;

      /* Prepare the reception of the buffer over EP0 */
      (void)USBD_CtlPrepareRx(pdev, (uint8_t *)hdfu->buffer.d8, hdfu->wlength);
```

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

> ./stm32usb.py -v 0x0483 -p 0xdf11 -m read -l 1000

## Notice

Please do not treat this utility as an oracle.
It is not certain that a particular implementation
is secure simply because this tool fails to exploit it.
