# vr900-connector

For now, the connector is ony able to read data from the system

## Layers

The connector is separate in two main layers:

### 1. Vr900Connector
This is the low level connector using the vaillant API and returning raw data directly coming from the API

### 2. VaillantSystemManager
This layer allows you to interact in a more friendly way with the system

