# vr900-connector

For now, the connector is ony able to read data from the system, it only handles only one heating system (one serial number). I cannot test more than that since I only have heating system at home

## Layers

The connector is separate in two main layers:

### 1. Vr900Connector
This is the low level connector using the vaillant API and returning raw data directly coming from the API. The connector is handling the login and session.
The connector able to reuse an already existing session (cookies). Two files are saved (cookies and serial number of your installation) on the file system. Default location is:
```python
tempfile.gettempdir() + "/vaillant_vr900_files"
```
but it can be overridden. File are named .vr900-vaillant.cookies and .vr900-vaillant.serial.


Here is an example how to use it:
```python
from vr900connector import Vr900Connector
   
connector = Vr900Connector('user', 'pass')
connector.get_facilities() 
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

### 2. VaillantSystemManager
This layer allows you to interact in a more friendly way with the system.
The underlying connector is hidden and raw responses are mapped to more useful object.

For now, the only function is:
```python
from vaillantsystemmanager import VaillantSystemManager
   
manager = VaillantSystemManager('user', 'pass')
manager.get_system() 
```
Basically, the connector is returning quite the same information as the android mobile app can display (and maybe a bit more)

