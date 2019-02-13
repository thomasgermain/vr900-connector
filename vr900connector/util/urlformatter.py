from string import Template


class UrlFormatter:

    @classmethod
    def format(cls, url: str, serial=None, zone=None, room=None, dhw=None, device=None, safe=True):
        template = Template(url)
        params = dict()

        cls.__add_if_not_none(params, 'serialNumber', serial)
        cls.__add_if_not_none(params, 'zoneIdentifier', zone)
        cls.__add_if_not_none(params, 'roomIndex', room)
        cls.__add_if_not_none(params, 'dhwIdentifier', dhw)
        cls.__add_if_not_none(params, 'deviceId', device)

        return template.safe_substitute(params) if safe else template.substitute(params)

    @classmethod
    def __add_if_not_none(cls, params, key, value):
        if value:
            params[key] = value

