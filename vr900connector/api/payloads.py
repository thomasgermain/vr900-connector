class Payloads:
    """
    This is meant to be used with :mod: `vr900connector.api.urls` to allow user to easily obtain the payload for a
    request.
    Payload are always json formatted
    """

    @classmethod
    def hotwater_temperature_setpoint(cls, temperature: float):
        """
        Payload used to set target temperature for *hotwater*
        """
        return {"temperature_setpoint": temperature}

    @classmethod
    def room_temperature_setpoint(cls, temperature: float):
        """
        Payload used to set target temperature for *room*
        """
        return {
            "setpoint_temperature": temperature
        }

    @classmethod
    def zone_temperature_setpoint(cls, temperature: float):
        """
        Payload used to set target temperature for *zone*
        """
        return {
            "setpoint_temperature": temperature
        }

    @classmethod
    def zone_temperature_setback(cls, temperature: float):
        """
        Payload used to set setback temperature for *zone*
        """
        return {
            "setback_temperature": temperature
        }

    @classmethod
    def hot_water_operation_mode(cls, mode: str):
        """
        Payload to set operation mode for *hotwater*
        """
        return {"operation_mode": mode}

    @classmethod
    def room_operation_mode(cls, mode: str):
        """
        Payload to set operation mode for *room*
        """
        return {"operationMode": mode}

    @classmethod
    def zone_operation_mode(cls, mode: str):
        """
        Payload to set operation mode for *zone*
        """
        return {"mode": mode}

    @classmethod
    def quickmode(cls, quick_mode: str, duration: int = None):
        """
        Payload to set quick mode for the system.
        Duration is mandatory (Duration is in minutes, max 1440 =24 hours)
        """
        return {
            "quickmode":
                {
                    "quickmode": quick_mode,
                    "duration": duration if duration is not None else 0
                }
        }

    @classmethod
    def zone_quick_veto(cls, temperature: float):
        """
        Payload to set a quick veto for a *Zone*.
        The duration is not configurable by the API, it's 6 hours
        """
        return {
            "setpoint_temperature": temperature
        }

    @classmethod
    def room_quick_veto(cls, temperature: float, duration: int):
        """
        Payload to set a quick veto for a *Room*.
        Duration is mandatory (Duration is in minutes, max 1440 =24 hours)
        """
        return {
            "temperatureSetpoint": temperature,
            "duration": duration
        }
