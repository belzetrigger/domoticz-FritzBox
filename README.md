# domoticz-FritzBox
[![PyPI pyversions](https://img.shields.io/badge/python-3.6%20|%203.7%20|%203.8-blue.svg)]() [![Plugin version](https://img.shields.io/badge/version-0.6.0-red.svg)](https://github.com/belzetrigger/domoticz-FritzPresence/branches/)

Adds Virtual Hardware for your Fritz!Box within domoticz. That devices shows connection information.
Fritz!Box are quite famous router from [AVM](https://en.avm.de/)



<img src='https://github.com/belzetrigger/domoticz-FritzBox/raw/master/resources/switch_fb_on.PNG' width="200" alt="switch device - ON">

<img  src='https://github.com/belzetrigger/domoticz-FritzBox/raw/master/resources/alert_fb_ok.png' width="200" alt="alert device - ok">

<img  src='https://github.com/belzetrigger/domoticz-FritzBox/raw/master/resources/switch_fb_off.PNG' width="200" alt="switch device off">

<img  src='https://github.com/belzetrigger/domoticz-FritzBox/raw/master/resources/alert_fb_alarm.png' width="200" alt="alarm device Showing alarm">

## Summary
This is a virtual hardware plugin that adds information about your Fritz!Box. 
Therefore it generates two sensors. 
* One alert sensor. Showing the status of the connection. 
* One switch, showing if connection is established.

This plugin only works with Fritz Box and is open source.

It is more or less just a wrapper around python lib [fritzconnection](https://github.com/kbr/fritzconnection) from Klaus Bremer.
Icons used are from [DomoticzIcons](https://drive.google.com/folderview?id=0B-ZLFoCiqzMRSkFaaWdHV1Qxbm8&usp=sharing) see [Domoticz Wiki](https://www.domoticz.com/wiki/Custom_icons_for_webinterface)


## Prepare
- set up your Fritz!Box
  - for status, nothing needed
  - enable TR064
  - for future use
    - create user and assign TR064 right to this one
 
  
## Installation and Setup
- a running Domoticz, tested with 4.10038
- Python 3
- install needed python modules:
   - fritzconnection Version 1.2.1
- clone project
    - go to `domoticz/plugins` directory 
    - clone the project
        ```bash
        cd domoticz/plugins
        git clone https://github.com/belzetrigger/domoticz-FritzBox.git
        ```
- or just download, unzip and copy to `domoticz/plugins` 
- make sure downloaded modules are in path eg. sitepackages python paths or change in plugin.py the path
```bash
import sys
sys.path
sys.path.append('/usr/lib/python3/dist-packages')
# for synology python3 from community
# sys.path.append('/volume1/@appstore/python3/lib/python3.5/site-packages')
# for synology sys.path.append('/volume1/@appstore/py3k/usr/local/lib/python3.5/site-packages')
# for windows check if installed packages as admin or user...
# sys.path.append('C:\\Program Files (x86)\\Python37-32\\Lib\\site-packages')
```
- restart Domoticz service
- Now go to **Setup**, **Hardware** in your Domoticz interface. There add
**Fritz!Box Plugin**.
### Settings
   - host: insert host name or Ip
   - Debug: if True, the log will be hold a lot more output.
   - for later use:
     - user
     - password - keep in mind, domoticz stores it plain in the database!!!!
       So really create a new user with restricted rights
   
## Versions
| Version | Note                                                                               |
| ------- | ---------------------------------------------------------------------------------- |
| <= 0.5  | worked with fritzconnection 0.6.x and 0.8.x, needs lxml                            |
| \>= 0.6 | works with new fritzconnection 1.2.1 and so without need of lxml but Python >= 3.6 |

## Bugs and ToDos
- On windows system changing icons for sensors did not work, so it's standard switch icon.
- On windows system "update" the hardware breaks imported python libs. Plugin can not get data from FritzBox. But after restart services it works fine.
- On Synology NAS, up to now, they official support python 3.5. So you might use a previous version of this plugin or use community python.

## State
In development. Currently only this two sensor are integrated. They work without user/password. For future there might be something like reconnect, de-/activate Wifi or Guest Wifi.

## Developing
Based on https://github.com/ffes/domoticz-buienradar/ there are
 -  `fakeDomoticz.py` - used to run it outside of Domoticz
 -  `test.py` it's the entry point for tests




