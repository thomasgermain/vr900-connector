from datetime import date


class Payloads:

    _DATE_FORMAT = "%Y-%m-%d"

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
            "temperatureSetpoint": temperature
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
        payload = {
            "quickmode":
                {
                    "quickmode": quick_mode,
                }
        }

        if duration:
            payload["quickmode"]["duration"] = duration

        return payload

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

    @classmethod
    def holiday_mode(cls, active: bool, start_date: date, end_date: date, temperature: float):
        """
        Payload to set holiday mode
        """
        return {
            "active": active,
            "start_date": start_date.strftime(cls._DATE_FORMAT),
            "end_date": end_date.strftime(cls._DATE_FORMAT),
            "temperature_setpoint": temperature
        }
