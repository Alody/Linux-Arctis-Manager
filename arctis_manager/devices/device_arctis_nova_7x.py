from typing import Optional
from arctis_manager.config_manager import ConfigManager
from arctis_manager.device_manager import DeviceState, DeviceManager, DeviceStatus, InterfaceEndpoint
from arctis_manager.device_manager.device_settings import DeviceSetting, SliderSetting, ToggleSetting
from arctis_manager.device_manager.device_status import DeviceStatusValue

INACTIVE_TIME_MINUTES = {
    0: 0, 1: 1, 2: 5, 3: 10, 4: 15, 5: 30, 6: 60
}

STATUS_REQUEST_MESSAGE = [0x06, 0xb0]


class ArctisNova7XDevice(DeviceManager):
    game_mix: int = None
    chat_mix: int = None

    def get_device_name(self):
        return "Arctis Nova 7X Wireless"

    def get_device_product_id(self):
        return 0x2258  # Replace if different

    def get_local_settings(self) -> dict[str, int]:
        self._local_config = ConfigManager.get_instance().get_config(
            self.get_device_vendor_id(), self.get_device_product_id()
        ) or {
            'wireless_mode': 0x00,
            'mic_volume': 0x0a,
            'mic_side_tone': 0x00,
            'mic_gain': 0x02,
            'mic_led_brightness': 0x0a,
            'pm_shutdown': 0x05,
        }
        return self._local_config

    def save_local_settings(self) -> None:
        ConfigManager.get_instance().save_config(
            self.get_device_vendor_id(),
            self.get_device_product_id(),
            self._local_config
        )

    def get_endpoint_addresses_to_listen(self) -> list[InterfaceEndpoint]:
        # Replace (ADD_NUMBER) with the correct interface/endpoint
        return [InterfaceEndpoint(interface=(ADD_NUMBER), endpoint=(ADD_NUMBER))]

    def get_request_device_status(self):
        # Replace (ADD_NUMBER) with the correct interface/endpoint
        return InterfaceEndpoint(interface=(ADD_NUMBER), endpoint=(ADD_NUMBER)), STATUS_REQUEST_MESSAGE

    def init_device(self):
        """
        Sends initialization commands to the headset.
        Replace endpoints and command bytes after reverse engineering.
        """
        local_settings = self.get_local_settings()
        commands = [
            ([0x06, 0x20], True),
            ([0x06, 0x37, local_settings['mic_volume']], False),
            (STATUS_REQUEST_MESSAGE, True),
        ]
        endpoint, _ = self.get_request_device_status()
        self.kernel_detach(endpoint)
        for command in commands:
            self.send_06_command(command[0], False)

    def manage_input_data(self, data: list[int], endpoint: InterfaceEndpoint) -> DeviceState:
        """
        Map incoming USB data to DeviceState and DeviceStatus.
        """
        volume = 1
        device_status = None
        # Replace (ADD_NUMBER) with the actual interface number
        if endpoint == InterfaceEndpoint((ADD_NUMBER), (ADD_NUMBER)):
            # Parse data here
            pass

        return DeviceState(
            game_volume=volume,
            chat_volume=volume,
            game_mix=self.game_mix if self.game_mix is not None else 1,
            chat_mix=self.chat_mix if self.chat_mix is not None else 1,
            device_status=device_status,
        )

    def send_06_command(self, command: list[int], kernel_detach: bool = False) -> None:
        endpoint, _ = self.get_request_device_status()
        commands_endpoint_address = self.device[0].interfaces()[endpoint.interface].endpoints()[endpoint.endpoint].bEndpointAddress
        if kernel_detach:
            self.kernel_detach(endpoint)
        self.device.write(commands_endpoint_address, self.packet_0_filler(command, 64))

    @staticmethod
    def packet_0_filler(packet: list[int], size: int):
        return [*packet, *[0 for _ in range(size - len(packet))]]

    # Settings callbacks to be implemented
    def on_mic_volume_change(self, value: int): ...
    def on_mic_side_tone_change(self, value: int): ...
    def on_mic_led_brightness_change(self, value: int): ...
    def on_mic_gain_change(self, value: bool): ...
    def on_pm_shutdown_change(self, value: int): ...
    def on_wireless_mode_change(self, value: bool): ...
