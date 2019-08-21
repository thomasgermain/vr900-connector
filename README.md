# vr900-connector
![PyPI - License](https://img.shields.io/pypi/l/vr900-connector.svg?color=44cc11)
[![Build Status](https://travis-ci.com/thomasgermain/vr900-connector.svg?branch=master)](https://travis-ci.com/thomasgermain/vr900-connector)
[![Coverage Status](https://coveralls.io/repos/github/thomasgermain/vr900-connector/badge.svg?branch=master)](https://coveralls.io/github/thomasgermain/vr900-connector?branch=master)
![PyPI](https://img.shields.io/pypi/v/vr900-connector.svg)
![PyPI - Status](https://img.shields.io/pypi/status/vr900-connector.svg)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/vr900-connector.svg)

<b>Please note that the project is still in beta state, it means  I may do some (un)intentional breaking changes</b>

## Legal Disclaimer
This software is not affiliated with Vaillant and the developers take no legal responsibility for the functionality or security of your vaillant devices

## Install
```bash
[sudo] pip install vr900-connector 
```

## Tests
You can run tests with
```bash
pytest
```

## Usages

### Module usage
 
The connector is separate in two layers:

#### 1. ApiConnector
This is the low level connector using the vaillant API and returning raw data directly coming from the API. The connector is handling the login and session.
The connector able to reuse an already existing session (cookies). Two files are saved (cookies and serial number of your installation) on the file system. Default location is:
```python
tempfile.gettempdir() + "/.vaillant_vr900_files"
```
but it can be overridden. Files are named .vr900-vaillant.cookies and .vr900-vaillant.serial.


Here is an example how to use it:
```python
from vr900connector.api import ApiConnector, Urls
   
connector = ApiConnector('user', 'pass')
connector.get(Urls.facilities_list()) 
```
to get some information about your installation, this returns the raw response, something like this:
```json
{
    "body": {
        "facilitiesList": [
            {
                "serialNumber": "1234567891234567891234567890",
                "name": "Name",
                "responsibleCountryCode": "BE",
                "supportedBrand": "GREEN_BRAND_COMPATIBLE",
                "capabilities": [
                    "ROOM_BY_ROOM",
                    "SYSTEMCONTROL_MULTIMATIC"
                ],
                "networkInformation": {
                    "macAddressEthernet": "12:34:56:78:9A:BC",
                    "macAddressWifiAccessPoint": "34:56:78:9A:BC:DE",
                    "macAddressWifiClient": "56:78:9A:BC:DE:F0"
                },
                "firmwareVersion": "1.1.1"
            }
        ]
    },
    "meta": {}
}
```

Basically, you can use 
```python
from vr900connector.api import ApiConnector
   
connector = ApiConnector('user', 'pass')
connector.get('') 
```
with urls from
```python
vr900connector.api.urls
``` 

I recommend using this layer if you only want to retrieve basic data (outdoor temperature, current temperature, etc.)

#### 2. SystemManager
This layer allows you to interact in a more friendly way with the system.
The underlying connector is hidden and raw responses are mapped to more useful object.

For now, the only function is:
```python
from vr900connector.systemmanager import SystemManager
   
manager = SystemManager('user', 'pass')
system = manager.get_system() 
```

The main object to manipulate is 
 ```python
 vr900connector.model.system
 ```
 
 Which is grouping all the information about the system.
 
 I recommend using this layer if you want to do more complex things, e.g: if you want to get the target temperature for 
 a room or a zone, it can become a bit complex since you have to deal with holiday mode, quick mode, quick veto, time program, etc.
 This layer is hiding you  this complexity
 

## Todo's
- add the possibility to remove quick mode
- Move ApiConnector to async
- Handling ventilation
- Add more documentation
- Handling missing information when VRC700 (and/or boiler) is shutdown 
(e.g. TimeProgram are not coming anymore from the API if boiler is down)
- Add some lint/pylint checks during the build (+ refactor some piece of code in a more pythonic way)