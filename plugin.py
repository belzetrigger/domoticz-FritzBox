# plugin for fritz box
#
# Author: belze
#
"""
<plugin key="FritzBox" name="Fritz!Box Plugin"
    author="belze" version="0.6.3" >
    <!--
    wikilink="https://github.com/belzetrigger/domoticz-FritzBox"
    externallink=""
    //-->
    <description>
        <h2>Fritz!Box</h2><br/>
        Add your FritzBox to Domoticz Interface
        <h3>Features</h3>
        <ul style="list-style-type:square">
            <li>checks connection state of FritzBox</li>
            <li>shows details of connections</li>
            <li>uses fritz box model as name for devices</li>
            <li>easily turn guest WiFi on or off</li>
            <li>activate WPS mode for guest WiFi</li>
            <li>activate WPS mode for standard WiFi</li>
            <li>leave user/password empty and remove WiFi from used to "unused" devices - and you can run FB Plugin in password free mode FB Status</li>
            <li>counter for sent/received mega bytes</li>
        </ul>
        <h3>Devices</h3>
        <ul style="list-style-type:square">
            <li>switch - shows if Box is connected or not</li>
            <li>alarm - shows details of your box and if not connected is red</li>
            <li>selector switch - turn guest WiFi on/off or activate WPS</li>
            <li>selector switch - activate WPS for normal WiFi</li>
            <li>counter items for sent and received mega bytes</li>
        </ul>
        <h3>Configuration</h3>
        Configuration options...
    </description>
    <params>
        <param field="Mode1" label="Hostname or IP" width="200px" required="true"
        default="fritz.box"/>
        <param field="Mode2" label="User" width="200px" required="false"
        />
        <param field="Mode3" label="Password" width="200px" required="false"
        password="true"
        />
        <param field="Mode4" label="Update every x minutes" width="200px"
        required="true" default="5"/>
        <param field="Mode5" label="Debug" width="75px">
            <options>
                <option label="True" value="Debug"/>
                <option label="False" value="Normal"  default="False" />
            </options>
        </param>
    </params>
</plugin>
"""
# import datetime as dt
from datetime import datetime, timedelta
from os import path
import sys
try:
    import Domoticz
except ImportError:
    import fakeDomoticz as Domoticz
sys.path
sys.path.append('/usr/lib/python3/dist-packages')
# sys.path.append('/volume1/@appstore/python3/lib/python3.5/site-packages')
# sys.path.append('/volume1/@appstore/py3k/usr/local/lib/python3.5/site-packages')
# sys.path.append('C:\\Program Files (x86)\\Python37-32\\Lib\\site-packages')
from fritzBoxHelper import FritzBoxHelper

# config
WLAN1_NAME = "WiFi"        # Name of the device shown in domoticz, standard 'WiFi'


WLAN3_NAME = "GuestWiFi"        # Name of the device shown in domoticz, standard 'GuestWiFi'
WLAN_ENABLE_WPS = 23            # number we use internal to mark a switch, to turn on wps as well

ERROR_THRESHOLD = 2             # how many times an error fb error can happen, before we show Error also in domoticz, standard: 2
ICON_FritzBox = "FritzBoxWan"   # icon used for fritz box switch and alert
ICON_WIFI = "FritzBoxWifi"      # normal WiFi icon
ICON_WIFI_WPS = "FritzBoxWPS"   # icon set if wps is used

# WiFi
UNIT_WIFI_GUEST_IDX = 3
UNIT_WIFI_GUEST_IMG = ICON_WIFI
UNIT_WIFI_GUEST_NAME = WLAN3_NAME

UNIT_WIFI_NRML_IDX = 4
UNIT_WIFI_NRML_IMG = ICON_WIFI
UNIT_WIFI_NRML_NAME = WLAN1_NAME

# counter
UNIT_SENT_IDX = 5
UNIT_SENT_IMG = ICON_FritzBox
UNIT_SENT_NAME = "Sent MB"

UNIT_RECEIVED_IDX = 6
UNIT_RECEIVED_NAME = "Received MB"
UNIT_RECEIVED_IMG = ICON_FritzBox

"""
as there is bug sometime in Used == 1
we can turn it off here and always update
"""
IGNORE_USED_STATE = True


class BasePlugin:
    enabled = False

    def __init__(self):
        self.fritz = None
        self.debug = False
        self.error = False
        self.nextpoll = datetime.now()
        self.host = None
        self.user = None
        self.password = None
        self.pollinterval = 60 * 5
        self.errorCounter = 0
        self.wlanGuestOptions = {}

    def onStart(self):
        self.errorCounter = 0
        if Parameters["Mode5"] == 'Debug':
            self.debug = True
            Domoticz.Debugging(1)
            DumpConfigToLog()
        else:
            Domoticz.Debugging(0)

        Domoticz.Log("onStart called")

        # check polling interval parameter
        try:
            temp = int(Parameters["Mode4"])
        except:
            Domoticz.Error("Invalid polling interval parameter")
        else:
            if temp < 5:
                temp = 5  # minimum polling interval
                Domoticz.Error("Specified polling interval too short: changed to 5 minutes")
            elif temp > (60):
                temp = (60)  # maximum polling interval is 1 hour
                Domoticz.Error("Specified polling interval too long: changed to 1 hour")
            self.pollinterval = temp * 60
        Domoticz.Log("Using polling interval of {} seconds".format(str(self.pollinterval)))

        self.host = Parameters["Mode1"]
        self.user = Parameters["Mode2"]
        self.password = Parameters["Mode3"]

        self.wlanOptionNames = "Off|On|WPS"
        self.wpsLevel = 20
        self.onLevel = 10
        LevelActions = self.wlanOptionNames.count('|')
        Domoticz.Debug('LevelActions {}'.format(LevelActions))
        self.wlanGuestOptions = {'LevelActions': '|asas|asas',
                                 'LevelNames': self.wlanOptionNames,
                                 'LevelOffHidden': 'false',
                                 'SelectorStyle': '0'}

        self.wlanNrmlOptions = {'LevelActions': '|On1|WPS2',
                                'LevelNames': '|On|WPS',
                                'LevelOffHidden': 'true',
                                'SelectorStyle': '0'}

        self.fritz = FritzBoxHelper(self.host, self.user, self.password)
        if self.debug is True:
            self.fritz.dumpConfig()

        # check images
        checkImages("FritzBox", "FritzBox.zip")
        checkImages(ICON_WIFI, ICON_WIFI + ".zip")
        checkImages(ICON_WIFI_WPS, ICON_WIFI_WPS + ".zip")

        # Check if devices need to be created
        createDevices(self.wlanGuestOptions, self.wlanNrmlOptions)

        # init with empty data
        updateDevice(1, 0, "Init - No Data")
        updateDevice(2, 0, "Init - No Data")
        updateDevice(UNIT_WIFI_GUEST_IDX, 0, "Init - No Data", UNIT_WIFI_GUEST_NAME)
        updateDevice(UNIT_WIFI_NRML_IDX, 0, "Init - No Data", UNIT_WIFI_NRML_NAME)
        updateImage(1, ICON_FritzBox)
        updateImage(2, ICON_FritzBox)
        # WIFI
        updateImage(UNIT_WIFI_GUEST_IDX, UNIT_WIFI_GUEST_IMG)
        updateImage(UNIT_WIFI_NRML_IDX, UNIT_WIFI_NRML_IMG)
        # Counter
        updateImage(UNIT_SENT_IDX, UNIT_SENT_IMG)
        updateImage(UNIT_RECEIVED_IDX, UNIT_RECEIVED_IMG)

    def onStop(self):
        self.fritz.stop()
        Domoticz.Log("onStop called")

    def onConnect(self, Connection, Status, Description):
        Domoticz.Log("onConnect called")

    def onMessage(self, Connection, Data):
        Domoticz.Log("onMessage called")

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Debug("onCommand called for Unit: {} Parameter: {} Level: {} ".format(
            str(Unit), str(Command), str(Level)))
        Command = Command.strip()
        action, sep, params = Command.partition(' ')
        action = action.capitalize()
        params = params.capitalize()

        try:
            if (Unit == UNIT_WIFI_GUEST_IDX):     # guest wlan
                if (action == "On"):
                    Domoticz.Debug("On")
                    self.switchWlan(unit=Unit, enable=1)
                elif (action == "Set"):
                    Domoticz.Debug("Set")
                    if(Level == self.onLevel):
                        Domoticz.Debug("Set On")
                        self.switchWlan(unit=Unit, enable=1)

                    elif(Level == self.wpsLevel):
                        Domoticz.Debug("Set WPS")
                        self.switchWlan(unit=Unit, enable=WLAN_ENABLE_WPS)
                        updateImage(Unit, ICON_WIFI_WPS)

                elif (action == "Off"):
                    Domoticz.Debug("Off")
                    self.switchWlan(unit=Unit, enable=0)
            elif (Unit == UNIT_WIFI_NRML_IDX):  # normal wlan
                if (action == "Set"):
                    if(Level == self.wpsLevel):
                        Domoticz.Debug("Set WPS")
                        self.switchWlan(unit=Unit, nr=1, enable=WLAN_ENABLE_WPS, baseName=UNIT_WIFI_NRML_NAME)
                        updateImage(Unit, ICON_WIFI_WPS)
                    else:
                        Domoticz.Error("For normal WiFi only wps works at the moment")

        except (Exception) as e:
            Domoticz.Error("Error on deal with WiFi unit {}: msg '{}';".format(Unit, e))

    def switchWlan(self, unit: int = 3, nr: int = 3, enable: int = 1, baseName: str = WLAN3_NAME):
        Domoticz.Debug("switchWlan no:{} to {}".format(nr, enable))
        state = "On"
        ssid = ""
        r = ""
        # force init of wlan
        self.fritz.readWlanStatus()
        if(enable >= 1):
            r = self.fritz.getWlan(nr).fbWlanSwitch(enable=1)
            ssid = self.fritz.getWlan(nr).getFBSsid()
            state = "On"
            # TODO we can cover wps here as well
            if(enable == WLAN_ENABLE_WPS):
                r = self.fritz.getWlan(nr).fbWlanWpsSwitch(enable=1)
                state = "WPS"
                ssid += ":WPS"
                enable = 1
            #            Devices[3].Update(1, "WPS", Name=WLAN3_NAME+':'+s+':WPS')
            #            updateImage(3, ICON_WIFI_WPS)

        else:
            r = self.fritz.getWlan(nr).fbWlanSwitch(enable=enable)
            state = "Off"

        Domoticz.Log("turn wlan no:{} {}".format(nr, state))
        self.updateWlanDevice(unit=unit, enable=enable, state=state, ssid=ssid, baseName=baseName)

    def updateWlanDevice(self, unit: int = 3, image: str = ICON_WIFI,
                         enable: int = 1, state: str = "On", ssid: str = "", baseName: str = ""):
        Domoticz.Debug("updateWlanDevice( unit: {} , "
                       " image: {} , enable: {}, "
                       " state: {} , ssid {} , "
                       " baseName {} )".format(unit, image, enable, state, ssid, baseName))
        updateImage(unit, image)
        Devices[unit].Update(enable, state, Name=baseName + ':' + state + ' ' + ssid)

    def onHeartbeatWlan(self, unit: int = 3, wlanNr: int = 3, baseName: str = WLAN3_NAME):
        Domoticz.Debug("onHeartbeatWlan - Unit: {}  WiFi: {}".format(unit, wlanNr))
        wlan = self.fritz.getWlan(wlanNr)
        if(wlan and wlan.hasError is False):
            Domoticz.Debug("Wlan status {} ".format(wlan.getSummary()))
            if(wlan.needsUpdate()):
                Domoticz.Debug("Wlan needs to be updated. {} ".format(wlan.getSummary()))
                ssid = wlan.getFBSsid()
                state = "Off"
                enable = 0
                img = ICON_WIFI
                if(wlan.isFBWpsEnabled()):
                    state = "WPS"
                    enable = 1
                    img = ICON_WIFI_WPS
                elif(wlan.isFBWlanEnabled()):
                    state = "On"
                    enable = 1
                self.updateWlanDevice(unit=unit, enable=enable,
                                      state=state, ssid=ssid, image=img, baseName=baseName)

        else:
            e = "Error - check log"
            if(wlan):
                e = "Error {} ".format(wlan.errorMsg)
            self.updateWlanDevice(unit=3, enable=0, state=e)

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Log("Notification: " + Name + "," + Subject + "," + Text + "," +
                     Status + "," + str(Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self, Connection):
        Domoticz.Log("onDisconnect called")

    def onHeartbeat(self):
        Domoticz.Log("onHeartbeat called")
        myNow = datetime.now()
        if myNow >= self.nextpoll:
            Domoticz.Debug("----------------------------------------------------")
            self.nextpoll = myNow + timedelta(seconds=self.pollinterval)

            # read info it it is time
            self.fritz.readStatus()

            # check for error
            if(self.fritz is None or self.fritz.hasError is True):
                Domoticz.Error("Uuups (Fritz!Box). Something went wrong ... Shouldn't be here.")
                self.errorCounter += 1
                self.nextpoll = myNow  # just try again with next heart beat

                # only show error after 2 error
                t = "Error"
                if self.debug is True and self.fritz is not None:
                    Domoticz.Debug(self.fritz.getSummary())
                if(self.fritz is not None and self.fritz.hasError is True):
                    t = "{}:{}".format(t, self.fritz.errorMsg)

                if(self.errorCounter >= ERROR_THRESHOLD):
                    Domoticz.Debug("Error and threshold reached -> so show error on devices")
                    updateDevice(1, 0, t, 'Fritz!Box - Error')
                    updateDevice(2, 3, t)
                    # TODO switch to off?
                    # updateImage(1, 'FritzBoxWan48_Off')
                else:
                    Domoticz.Debug("Error happend but under threshold, so we wait next heartbeat")
            else:
                self.errorCounter = 0
                # always update counter
                r = self.fritz.getMegabytesReceived()
                s = self.fritz.getMegabytesSent()
                updateDevice(UNIT_SENT_IDX, 0, "{}" .format(s), alwaysUpdate=True)
                updateDevice(UNIT_RECEIVED_IDX, 0, "{}".format(r), alwaysUpdate=True)

                # check if we need update for basic fb items
                if self.fritz.needUpdate is True:
                    alarm = 1
                    connected = 1
                    if(self.fritz.is_connected is False):
                        alarm = 4
                        connected = 0
                    # device 1 == switch
                    updateDevice(1, connected, "", self.fritz.getDeviceNameWithMB())
                    updateDevice(2, alarm, self.fritz.getShortSummary("; "), self.fritz.getDeviceNameWithMB())

                # force init wlan status
                self.fritz.readWlanStatus()
                Domoticz.Debug("{} is used: {}".format(UNIT_WIFI_GUEST_NAME, Devices[UNIT_WIFI_GUEST_IDX].Used))
                if((Devices[UNIT_WIFI_GUEST_IDX].Used == 0
                        or Devices[UNIT_WIFI_GUEST_IDX].Used == "0") and IGNORE_USED_STATE is False):
                    Domoticz.Log("{} is marked as unused. So we skip reading status".format(UNIT_WIFI_GUEST_NAME))
                else:
                    self.onHeartbeatWlan(unit=UNIT_WIFI_GUEST_IDX, wlanNr=3, baseName=UNIT_WIFI_GUEST_NAME)

                if((Devices[UNIT_WIFI_NRML_IDX].Used == 0
                        or Devices[UNIT_WIFI_NRML_IDX].Used == "0") and IGNORE_USED_STATE is False):
                    Domoticz.Log("{} is marked as unused. So we skip reading status".format(UNIT_WIFI_NRML_NAME))
                else:
                    self.onHeartbeatWlan(unit=UNIT_WIFI_NRML_IDX, wlanNr=1, baseName=UNIT_WIFI_NRML_NAME)

            Domoticz.Debug("----------------------------------------------------")


global _plugin
_plugin = BasePlugin()


def onStart():
    global _plugin
    _plugin.onStart()


def onStop():
    global _plugin
    _plugin.onStop()


def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)


def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)


def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)


def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)


def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)


def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

    # Generic helper functions


def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug("'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return


def checkImages(sName: str, sZip: str):
    Domoticz.Debug("Make sure images {} {}".format(sName, sZip))
    # Check if images are in database
    if sName not in Images:
        Domoticz.Image(sZip).Create()
    # image = Images[sName].ID
    # Domoticz.Debug("Image created. ID: " + str(image))
        # Domoticz.Error("pic:{} -> {}".format(sName ))


def createDevices(wifiGuestOpts, wifiNrmlOpt):
    '''
    this creates the alarm device for fritz box
    '''
    # create the mandatory child devices if not yet exist
    if 1 not in Devices:
        Domoticz.Device(Name="Fritz!Box", Unit=1, TypeName="Switch",
                        Options={"Custom": ("1;Foo")}, Image=102, Used=1).Create()
        updateImage(1, 'FritzBoxWan')
        Domoticz.Log("Devices[1] created.")

    if 2 not in Devices:
        Domoticz.Device(Name="Fritz!Box", Unit=2, TypeName="Alert",
                        Used=1).Create()
        Domoticz.Log("Devices[2] created.")

    # WiFi
    if UNIT_WIFI_GUEST_IDX not in Devices:
        Domoticz.Device(Name=UNIT_WIFI_GUEST_NAME, Unit=UNIT_WIFI_GUEST_IDX, TypeName="Selector Switch",
                        Used=1,
                        Switchtype=18, Options=wifiGuestOpts).Create()
        Domoticz.Log("Devices[UNIT_WIFI_GUEST_IDX] created.")

    if UNIT_WIFI_NRML_IDX not in Devices:
        Domoticz.Device(Name=UNIT_WIFI_NRML_NAME, Unit=UNIT_WIFI_NRML_IDX, TypeName="Selector Switch",
                        Used=1,
                        Switchtype=18, Options=wifiNrmlOpt).Create()
        Domoticz.Log("Devices[UNIT_WIFI_NRML_IDX] created.")

    # counter
    # TODO: using counter or managed counter=
    # managed: Type=243, Subtype=33, Switchtype=3, Used=1,
    if UNIT_SENT_IDX not in Devices:
        Domoticz.Device(Name=UNIT_SENT_NAME, Unit=UNIT_SENT_IDX, Type=113, Subtype=0,
                        Switchtype=3, Used=1,
                        Options={"ValueUnits": "MB",
                                 "ValueQuantity": UNIT_SENT_NAME}
                        ).Create()
        Domoticz.Log("Devices[5] created.")

    if UNIT_RECEIVED_IDX not in Devices:
        Domoticz.Device(Name=UNIT_RECEIVED_NAME, Unit=UNIT_RECEIVED_IDX, Type=113, Subtype=0,
                        Switchtype=3, Used=1,
                        Options={"ValueUnits": "MB",
                                 "ValueQuantity": UNIT_RECEIVED_NAME}
                        ).Create()
        # Domoticz.Device(Name="MB Sent", Unit=4,  TypeName="RFXMeter",
        Domoticz.Log("Devices[UNIT_RECEIVED_IDX] created.")


# Update Device into database


def updateDevice2(Unit, nValue, sValue, sName='', AlwaysUpdate=False):
    # Make sure that the Domoticz device still exists (they could already be deleted) before updating it
    if Unit in Devices:
        if Devices[Unit].nValue != nValue or Devices[Unit].sValue != sValue or AlwaysUpdate is True:
            if(len(sName) <= 0):
                Devices[Unit].Update(nValue, str(sValue))
            else:
                # Devices[Unit].Update(int(alarmLevel), alarmData, Name=name)
                Devices[Unit].Update(nValue, str(sValue), Name=sName)
            Domoticz.Log("Update " + Devices[Unit].Name + ": " + str(nValue) + " - '" + str(sValue) + "'")
    return


def updateDevice(Unit, alarmLevel, alarmData, name='', alwaysUpdate=False):
    '''update a device - with given data.
    If there are changes and the device exists.
    Arguments:
        Unit {int} -- index of device, 1 = today, 2 = tomorrow
        highestLevel {[type]} -- the maximum warning level for that day, it is used to set the domoticz alarm level
        alarmData {[str]} -- data to show in that device, aka text

    Optional Arguments:
        name {str} -- optional: to set the name of that device, eg. mor info about  (default: {''})
        alwaysUpdate {bool} -- optional: to ignore current status/needs update (default: {False})
    '''

    # Make sure that the Domoticz device still exists (they could already be deleted) before updating it
    if Unit in Devices:
        if (alarmData != Devices[Unit].sValue) or (int(alarmLevel) != Devices[Unit].nValue or alwaysUpdate is True):
            if(len(name) <= 0):
                Devices[Unit].Update(int(alarmLevel), alarmData)
            else:
                Devices[Unit].Update(int(alarmLevel), alarmData, Name=name)
            Domoticz.Log("BLZ: Updated to: {} value: {}".format(alarmData, alarmLevel))
        else:
            Domoticz.Log("BLZ: Remains Unchanged")
    else:
        Domoticz.Error("Devices[{}] is unknown. So we cannot update it.".format(Unit))


# Synchronize images to match parameter in hardware page
def updateImage(Unit, picture):
    Domoticz.Debug("Image: Update Unit: {} Image: {}".format(Unit, picture))
    if Unit in Devices and picture in Images:
        Domoticz.Debug("Image: Name:{}\tId:{}".format(picture, Images[picture].ID))
        if Devices[Unit].Image != Images[picture].ID:
            Domoticz.Log("Image: Device update: 'Fritz!Box', Currently " +
                         str(Devices[Unit].Image) + ", should be " + str(Images[picture].ID))
            Devices[Unit].Update(nValue=Devices[Unit].nValue, sValue=str(Devices[Unit].sValue),
                                 Image=Images[picture].ID)
            # Devices[Unit].Update(int(alarmLevel), alarmData, Name=name)
    else:
        Domoticz.Error("Image: Unit {} or Picture {} unknown".format(Unit, picture))
        for picture in Images:
            Domoticz.Error("pic:{} id:{} base: {} descr: {}".format(picture, Images[picture].ID, Images[picture].Base,
                                                                    Images[picture].Description))
    return
