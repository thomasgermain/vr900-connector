class BoostMode:
    name = None
    forZone = False
    forRoom = False
    forWaterHeater = False
    forCirculation = False

    def __init__(self, name, for_zone, for_room, for_water_heater, for_circulation):
        self.name = name
        self.forZone = for_zone
        self.forRoom = for_room
        self.forWaterHeater = for_water_heater
        self.forCirculation = for_circulation

    @staticmethod
    def from_name(name):
        return _VALUES[name]


QM_HOTWATER_BOOST = BoostMode('QM_HOTWATER_BOOST', False, False, True, False)
QM_VENTILATION_BOOST = BoostMode('QM_VENTILATION_BOOST', True, True, False, False)
QM_ONE_DAY_AWAY = BoostMode('QM_ONE_DAY_AWAY', True, True, True, False)
QM_SYSTEM_OFF = BoostMode('QM_SYSTEM_OFF', True, True, True, True)
QM_ONE_DAY_AT_HOME = BoostMode('QM_ONE_DAY_AT_HOME', True, False, False, False)
QM_PARTY = BoostMode('QM_PARTY', True, False, False, False)

_VALUES = {
        QM_HOTWATER_BOOST.name: QM_HOTWATER_BOOST,
        QM_VENTILATION_BOOST.name: QM_VENTILATION_BOOST,
        QM_ONE_DAY_AWAY.name: QM_ONE_DAY_AWAY,
        QM_SYSTEM_OFF.name: QM_SYSTEM_OFF,
        QM_ONE_DAY_AT_HOME.name: QM_ONE_DAY_AT_HOME,
        QM_PARTY.name: QM_PARTY
    }



