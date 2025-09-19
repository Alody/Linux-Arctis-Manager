from arctis_manager.device_manager.device_manager import device_manager_factory
from arctis_manager.devices.device_arctis_nova_7x import ArctisNova7XWirelessDevice


@device_manager_factory(0x2258, 'Arctis Nova 7X Wireless Alt')
class ArctisNova7XDeviceAlt(ArctisNova7XWirelessDevice):
    pass
