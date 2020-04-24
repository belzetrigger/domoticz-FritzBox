# domoticz-FritzBox
[![PyPI pyversions](https://img.shields.io/badge/python-3.6%20|%203.7%20|%203.8-blue.svg)]() [![Plugin version](https://img.shields.io/badge/version-0.6.4-red.svg)](https://github.com/belzetrigger/domoticz-FritzPresence/branches/)

Adds Virtual Hardware for your [Fritz!Box](https://en.avm.de/, 'Fritz!Box are quite famous router from avm') within domoticz. That devices show connection information and enables you to control your WiFi.


| Device                | Images                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| --------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| guest WiFi            | <img  src='https://github.com/belzetrigger/domoticz-FritzBox/raw/master/resources/switch_wifi_on.PNG' width="200" alt="WiFi switch device on"> <img  src='https://github.com/belzetrigger/domoticz-FritzBox/raw/master/resources/switch_wifi_wps.PNG' width="200" alt="wps switch device on"> <br/> <img  src='https://github.com/belzetrigger/domoticz-FritzBox/raw/master/resources/switch_wifi_off.PNG' width="200" alt="WiFi switch device off"><img  src='https://github.com/belzetrigger/domoticz-FritzBox/raw/master/resources/switch_wifi_error.PNG' width="200" alt="WiFi switch device error"> |
| normal WiFi (2.4 GHz) | <img  src='https://github.com/belzetrigger/domoticz-FritzBox/raw/master/resources/switch_wifi_nrml_on.PNG' width="200" alt="switch device normal WiFi on">                                                                                                                                                                                                                                                                                                                                                                                                                                               |
|                       |
| counter               | <img src='https://github.com/belzetrigger/domoticz-FritzBox/raw/master/resources/counter_received_1.PNG' width="200" alt="counter - received"> <img src='https://github.com/belzetrigger/domoticz-FritzBox/raw/master/resources/counter_sent_1.PNG' width="200" alt="counter - sent"> <br> <img src='https://github.com/belzetrigger/domoticz-FritzBox/raw/master/resources/counter_received_2_data.PNG' width="200" alt="counter - details">                                                                                                                                                            |
|                       |
| alarm                 | <img  src='https://github.com/belzetrigger/domoticz-FritzBox/raw/master/resources/alert_fb_ok.png' width="200" alt="alert device - ok"> <img  src='https://github.com/belzetrigger/domoticz-FritzBox/raw/master/resources/alert_fb_alarm.png' width="200" alt="alarm device Showing alarm">                                                                                                                                                                                                                                                                                                              |
| switch                | <img src='https://github.com/belzetrigger/domoticz-FritzBox/raw/master/resources/switch_fb_on.PNG' width="200" alt="switch device - ON"> <img  src='https://github.com/belzetrigger/domoticz-FritzBox/raw/master/resources/switch_fb_off.PNG' width="200" alt="switch device off">                                                                                                                                                                                                                                                                                                                       |



## Summary
This is a plugin for Domoticz that works with your Fritz!Box. 
Therefore it generates three devices. 
* One alert sensor. Showing the status of the connection. 
* One switch, showing if connection is established.
* One selector switch for guest WiFi to turn on/off or also enable WPS
* another selector switch to turn on WPS for normal WiFi
* counter for sent and received bytes

This plugin only works with Fritz Box and is open source.

It is more or less just a wrapper around python lib [fritzconnection](https://github.com/kbr/fritzconnection) from Klaus Bremer.
Icons used are from [DomoticzIcons](https://drive.google.com/folderview?id=0B-ZLFoCiqzMRSkFaaWdHV1Qxbm8&usp=sharing) see [Domoticz Wiki](https://www.domoticz.com/wiki/Custom_icons_for_webinterface)


## Prepare
- set up your Fritz!Box
  - for plain status, nothing needed
  - enable TR064
  - for guest WiFi control
    - create user and assign TR064 right to this one
 
  
## Installation and Setup
- a running Domoticz, tested with version 2020.1 and Python 3.7
- Python >= 3.6 (mainly depending on requirements for fritzconnection)
- install needed python modules:
   - fritzconnection Version 1.2.1
   - you can use `sudo pip3 install -r requirements.txt` 
   - might be worth testing with fritzconnection works - just run `fritzconnection`
- clone project
    - go to `domoticz/plugins` directory 
    - clone the project
        ```bash
        cd domoticz/plugins
        git clone https://github.com/belzetrigger/domoticz-FritzBox.git
        ```
- or just download, unzip and copy to `domoticz/plugins` 
- no need on Raspbian for sys path adaption if using sudo for pip3
- some extra work for Windows or Synology, make sure downloaded modules are in path eg. site-packages python paths or change in plugin.py / fritzHelper.py path
  - example adaption:
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

| Parameter   | Information                                                                                      |
| ----------- | ------------------------------------------------------------------------------------------------ |
| host        | insert host name or Ip - default is fritz.box                                                    |
| Update time | polling time. <br> Something like 3 or 5 min should work and do not stress the router too much   |
| Debug       | if True, the log will hold a lot more output. Its good if something does not work like expected. |


|          | to control WiFi                                                                                               |
| -------- | ------------------------------------------------------------------------------------------------------------- |
| user     | name of the user set up in fritz box                                                                          |
| password | keep in mind, domoticz stores it plain in the database!!!! So really create a new user with restricted rights |
   
## Versions
| Version  | Note                                                                               |
| -------- | ---------------------------------------------------------------------------------- |
| 0.6.4    | <li>removed pw free mode</li> <li>adapt counter for sent/received megabytes </li>  |
| 0.6.3    | counter for sent/received megabytes <br>switch for standard WiFi                   |
| 0.6.2    | now allows you to control your guest WiFi                                          |
| 0.6.x    | works with new fritzconnection 1.2.1 and so without need of lxml but Python >= 3.6 |
| <= 0.5.x | worked with fritzconnection 0.6.x and 0.8.x, needs lxml                            |

## Bugs and ToDos
- counter needs still improvements
- rework standard WiFi / Wlan1 and add or integrate 5ghz WLAN in switch
- for WiFi-Selector Switch the BigText always shows Off, I did not found a way to change it.
- sometimes the Devices[idx].Used is incorrect, json shows correct value but on python it is still 0. So we do update even if not used!
- On windows system changing icons for sensors did not really work, so there will be the standard switch icons.
- On windows system "update" the hardware breaks imported python libs. Plugin can not get data from FritzBox. But after restart, service works fine.
- On Synology NAS, up to now, they official support python 3.5. So you might use a previous version of this plugin or use community python.

## State
In development. Guest WiFi is now more stable especially on refresh status for WPS.  Counters are new and behave a bit different than Fritz!Box Online Monitor. Means there is always a delta in the way FritzBox is showing the daily usage.

## Developing
For TR064 actions codes see [AVMs Documentation](https://avm.de/fileadmin/user_upload/Global/Service/Schnittstellen/wlanconfigSCPD.pdf)<br>
Based on https://github.com/ffes/domoticz-buienradar/ there are
 -  `fakeDomoticz.py` - used to run it outside of Domoticz
 -  `test.py` it's the entry point for tests




