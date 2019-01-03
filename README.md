# domoticz-FritzBox
Adds Virtual Hardware for your Fritz!Box. Fritz!Box are quite famous router from [AVM](https://en.avm.de/)



<img src='https://github.com/belzetrigger/domoticz-FritzBox/raw/master/resources/switch_fb_on.PNG' width="200" alt="switch device - ON">

<img  src='https://github.com/belzetrigger/domoticz-FritzBox/raw/master/resources/alert_fb_ok.png' width="200" alt="alert device - ok">

<img  src='https://github.com/belzetrigger/domoticz-FritzBox/raw/master/resources/switch_fb_off.PNG' width="200" alt="switch device off">

<img  src='https://github.com/belzetrigger/domoticz-FritzBox/raw/master/resources/alert_fb_alarm.png' width="200" alt="alarm device Shwoing alarm">

## Summary
This is a virtual hardware plugin that adds information about your Fritz!Box. 
Therefore it generates two sensors. One alert sensor. Showing the status of the connection. One switch, showing if connection is established.
This plugin only works with Fritz Box. 

This plugin is open source.

This is more or less just a wrapper around python lib [fritzconnection](https://bitbucket.org/kbr/fritzconnection) from Klaus Bremer.
Icons used are from [DomoticzIcons](https://drive.google.com/folderview?id=0B-ZLFoCiqzMRSkFaaWdHV1Qxbm8&usp=sharing) see [Domoticz Wiki](https://www.domoticz.com/wiki/Custom_icons_for_webinterface)


## Prepare
- set up your Fritz!Box
  - for status, nothing needed
  - enable TR065
  - create a user
  - set password
  - assign rights to this user
  
## Installation and Setup
- a running Domoticz, tested with 4.10038
- Python 3
- install needed python moduls:
  - lxml
    - on Synology you might use Python 3 from the Community, it includes lxml, otherwise it's a bit tricky to build
  - fritzconnection
- clone project
    - go to `domoticz/plugins` directory 
    - clone the project
        ```bash
        cd domoticz/plugins
        git clone https://github.com/belzetrigger/domoticz-FritzBox.git
        ```
- or just download, unzip and copy to `domoticz/plugins` 
- make sure downloaded moduls are in path eg. sitepackes python paths or change in plugin.py the path
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
   - user
   - password - keep in mind, domoticz stores it plain in the database!!!!
     So really create a new user with restricted rights
   - Debug: if True, the log will be hold a lot more output.
  
## Bugs and ToDos
- On windows system changing icons for sensors did not work, so it's standard switch icon.
- On windows system "update" the hardware breaks imported python libs. Plugin can not get data from FritzBox. But after restart services it works fine.


## State
In development. Currently only this two sensor are integrated. They work without user/password.

## Developing
Based on https://github.com/ffes/domoticz-buienradar/ there are
 -  `fakeDomoticz.py` - used to run it outside of Domoticz
 -  `test.py` it's the entry point for tests




