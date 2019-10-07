.. vr900-connector documentation master file, created by
   sphinx-quickstart on Wed Sep  4 15:44:56 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to vr900-connector's documentation!
===========================================

.. toctree::
   :maxdepth: 3
   :caption: Contents:


Low level Connector
===================
.. automodule:: vr900connector.api.connector
   :members:

.. automodule:: vr900connector.api.urls
   :members:


Mode
=====
.. automodule:: vr900connector.model.mode

.. autoclass:: Mode

.. autoclass:: QuickVeto
   :members:

.. autoclass:: OperatingMode
   :members:

.. autoclass:: OperatingModes
   :members:

.. autoclass:: SettingMode
   :members:

.. autoclass:: SettingModes
   :members:

.. autoclass:: QuickMode
   :members:

.. autoclass:: QuickModes
   :members:

.. autoclass:: ActiveMode
   :members:

.. autoclass:: HolidayMode
   :members:


Component
=========
.. automodule:: vr900connector.model.component

.. autoclass:: Component

.. autoclass:: Circulation

.. autoclass:: HotWater

.. autoclass:: Room

.. autoclass:: Zone

.. autoclass:: Device


Error
=====
.. automodule:: vr900connector.model.error

.. autoclass:: Error