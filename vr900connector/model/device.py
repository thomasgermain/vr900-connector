class Device:
    """
    This class represents a device in a room

    Args:
        name: Name of the device
        sgtin: Unique identifier of a device
        device_type: Device type (I only know 'VALVE' for now)
        battery_low: is battery device low
        radio_out_of_reach: is device out of reach
    """

    def __init__(self, name: str, sgtin: str, device_type: str, battery_low: bool, radio_out_of_reach: bool):
        self.name = name
        self.sgtin = sgtin
        self.device_type = device_type
        self.battery_low = battery_low
        self.radio_out_of_reach = radio_out_of_reach



