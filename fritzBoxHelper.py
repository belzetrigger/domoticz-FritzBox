# this is our helper class to do the work with FritzConnection
#
# Attribute     Description
# is_linked     True if the FritzBox is physically linked to the provider
# is_connected  True if the FritzBox has established an internet-connection
# wan_access_type   Connection-type, can be DSL or Cable
# external_ip   External ip address
# uptime    Uptime in seconds
# bytes_sent    Bytes sent
# bytes_received    Bytes received
# transmission_rate_up  Current upstream speed in bytes/s
# transmission_rate_down    Current downstream speed in bytes/s
# max_byte_rate_up  Maximum upstream-rate in bytes/s
# max_byte_rate_down    Maximum downstream-rate in bytes/s

import sys
sys.path
# sys.path.append('/usr/lib/python3/dist-packages')
# sys.path.append('/volume1/@appstore/py3k/usr/local/lib/python3.5/site-packages')
sys.path.append('/volume1/@appstore/python3/lib/python3.5/site-packages')
sys.path.append('C:\\Program Files (x86)\\Python37-32\\Lib\\site-packages')
from datetime import datetime, timedelta
# from time import mktime
# import time as myTime
# import urllib

try:
    import Domoticz
except ImportError:
    import fakeDomoticz as Domoticz

from fritzconnection.lib.fritzstatus import FritzStatus
from fritzconnection import FritzConnection
from typing import Optional, Dict

# looks like this breaks some times conversion form string to int.
# import locale
# locale.setlocale(locale.LC_ALL, '')  # Use '' for auto, or force e.g. to 'en_US.UTF-8'


class Wlan:
    def __init__(self, nr: int = 3):
        Domoticz.Debug('Init Wlan #{}'.format(nr))
        self.isInit: bool = True
        self.previousError: Optional[Exception] = None
        self.hasError: bool = False
        self.errorMsg: Optional[Exception] = None
        self.fc: FritzConnection = None
        self.nr: int = nr
        self.ssid: Optional[str] = None
        self.isEnabled: bool = False
        self.isWpsEnabled: bool = False
        self.lastSsid: Optional[str] = None
        self.lastIsEnabled: bool = False
        self.lastIsWpsEnabled: bool = False
        self.needUpdate: bool = True  # init with true, so first time update..
        self.reset()

    def reset(self):
        self.isInit = True
        self.previousError = None
        self.hasError = False
        self.errorMsg = None
        self.fc = None
        self.ssid = None
        self.isEnabled = False
        self.isWpsEnabled = False
        self.lastSsid = None
        self.lastIsEnabled = False
        self.lastIsWpsEnabled = False
        self.needUpdate = False

    def getSummary(self):
        return "Wlan{} is on:{} and wps on: {}".format(self.nr, self.isEnabled, self.isWpsEnabled)

    def setMyError(self, error: Exception):
        self.hasError = True
        self.errorMsg = error

    def resetError(self):
        self.previousError = self.hasError
        self.hasError = False
        self.errorMsg = None

    def setFc(self, fc: FritzConnection):
        self.fc = fc

    def needsUpdate(self):
        return self.needUpdate

    def verifyUpdate(self):
        # TODO always update on init and error
        if(self.lastIsEnabled != self.isEnabled
           or self.lastIsWpsEnabled != self.isWpsEnabled
           or self.isInit
           ):
            self.needUpdate = True
        else:
            self.needUpdate = False
        # copy values to compare later
        self.lastIsEnabled = self.isEnabled
        self.lastIsWpsEnabled = self.isWpsEnabled
        Domoticz.Debug("Wlan {} updated needed?: {}".format(self.nr, self.needUpdate))

    def readStatus(self):
        Domoticz.Debug("Wlan {} read status".format(self.nr))
        # TODO should we read it here?
        try:
            self.resetError()
            if(self.fc is None):
                raise Exception("Wlan readStatus - missing fc")
            self.ssid = self.getFBSsid()
            self.isEnabled = self.isFBWlanEnabled()
            self.isWpsEnabled = self.isFBWpsEnabled()
            self.verifyUpdate()
            self.isInit = False
        except (Exception) as e:
            self.setMyError(e)
            Domoticz.Error("Error on Wlan readStatus:  msg '{}'; hasError:{}".format(e, str(self.hasError)))

    def getFBWlanInfo(self):
        Domoticz.Debug("getFBWlanInfo for Wlan:{} - fc: {}".format(self.nr, self.fc))
        result = self.fc.call_action('WLANConfiguration' + str(self.nr), 'GetInfo')
        return result

    def getFBSsid(self):
        result = self.getFBWlanInfo()
        return result["NewSSID"]

    def isFBWlanEnabled(self):
        result = self.getFBWlanInfo()
        return (result["NewEnable"] == 1)

    def fbWlanSwitch(self, enable: int = 1):
        # fc = self.fbGetFc()
        self.fc.call_action('WLANConfiguration' + str(self.nr), 'SetEnable', NewEnable=enable)
        result = self.getFBWlanInfo()
        r = result['NewEnable']
        Domoticz.Debug("WLan:{} enable:{} => isEnabled:{}".format(self.nr, enable, r))
        return r

    def getFBWlanWpsInfo(self):
        # fc = self.fbGetFc()
        result = self.fc.call_action('WLANConfiguration:' + str(self.nr), 'X_AVM-DE_GetWPSInfo')
        return result  # ["NewX_AVM-DE_WPSStatus"]

    def isFBWpsEnabled(self):
        result = self.getFBWlanWpsInfo()
        return result["NewX_AVM-DE_WPSStatus"] == "active"

    def fbWlanWpsSwitch(self, enable: int = 1):
        # fc = self.fbGetFc()
        result = dict()
        if(enable == 1):
            # https://avm.de/fileadmin/user_upload/Global/Service/Schnittstellen/wlanconfigSCPD.pdf
            # Actionname: X_AVM - DE_SetWPSConfig
            # ('NewX_AVM-DE_WPSAPPIN', 'out', 'string')
            # ('NewX_AVM-DE_WPSClientPIN', 'in', 'string')
            # ('NewX_AVM-DE_WPSMode', 'in', 'string')
            # ('NewX_AVM-DE_WPSStatus', 'out', 'string')
            # mode: pbc, pin_ap, pin_client (needs pin)
            arg = {'NewX_AVM-DE_WPSMode': 'pbc',
                   'NewX_AVM-DE_WPSClientPIN': ''}
            # arg = {'NewX_AVM-DE_PhoneNumber': number}
            # self.fc.call_action('X_VoIP1', 'X_AVM-DE_DialNumber', arguments=arg)
            # X_AVM-DE_SetWPSConfig
            result = self.fc.call_action('WLANConfiguration:' + str(self.nr), 'X_AVM-DE_SetWPSConfig',
                                         arguments=arg)
        else:
            arg = {'NewX_AVM-DE_WPSMode': 'stop',
                   'NewX_AVM-DE_WPSClientPIN': ''}
            result = self.fc.call_action('WLANConfiguration:' + str(self.nr), 'X_AVM-DE_SetWPSConfig',
                                         arguments=arg)
        r = result['NewX_AVM-DE_WPSStatus']
        Domoticz.Debug("WLan:{} WpsEnable:{} => isEnabled:{}".format(self.nr, enable, r))
        self.lastIsWpsEnabled = bool(r)
        return result
        # h = fc.call_action('WLANConfiguration3', 'X_AVM-DE_GetWPSInfo')
        # print(h["NewX_AVM-DE_WPSStatus"])


class FritzBoxHelper:

    def __init__(self, host: str, user: str, password: str):
        Domoticz.Debug('Init fritz box helper')
        self.fc = None
        self.host: str = host
        self.user: str = user
        self.password: str = password
        self.debug: bool = False
        self.hasError: bool = False
        self.previousError: bool = False
        self.lastUpdate: datetime = datetime.now()
        self.nextpoll: datetime = datetime.now()
        self.reset()
        # guest wif
        self.wlan3 = Wlan(nr=3)
        # standard wifi
        self.wlan1 = Wlan(nr=1)

    def dumpConfig(self):
        Domoticz.Debug(
            "host:\t{}".format(self.host)
        )

    def needsUpdate(self):
        '''does some of the devices need an update

        Returns:
            boolean -- if True -> please update the device in domoticz
        '''
        return self.needUpdate

    def reset(self):
        self.needUpdate: bool = True
        self.stopped: bool = False
        self.fc = None
        self.fcStatus = None
        self.model = None
        self.is_linked = None
        self.is_connected = None
        self.external_ip = None
        self.uptime = None
        self.max_bit_rate = None

        self.last_bytes_received: int = 0
        self.bytes_received: int = 0
        self.delta_bytes_received: int = 0

        self.last_bytes_sent: int = 0
        self.bytes_sent: int = 0
        self.delta_bytes_sent: int = 0

        self.last_external_ip = None
        self.last_is_connected = None
        self.last_max_bit_rate = None
        self.resetError()

    def connect(self):
        Domoticz.Debug("Try to get FritzStatus Connection")

        # all params ae optional an can handle it, if they are empty
        # so for pw free status mode, this works as well
        self.fcStatus = FritzStatus(
            address=self.host,
            user=self.user, password=self.password
        )
        Domoticz.Debug("status: {}".format(self.fcStatus))
        return self.fcStatus

    def setMyError(self, error):
        self.hasError = True
        self.errorMsg = error

    def resetError(self):
        self.previousError = self.hasError
        self.hasError = False
        self.errorMsg = None

    def verifyUpdate(self):
        if(self.last_external_ip != self.external_ip or
           self.last_is_connected != self.is_connected or
           self.last_max_bit_rate != self.max_bit_rate or
           self.previousError is True
           ):
            self.needUpdate = True
        else:
            self.needUpdate = False
        # copy values to compare later
        self.last_external_ip = self.external_ip
        self.last_is_connected = self.is_connected
        self.last_max_bit_rate = self.max_bit_rate
        Domoticz.Debug("updated needed?: {}".format(self.needUpdate))

    def readWlanStatus(self):
        """
        init fc and reads current statuts from fritz boxs.
        Reads WLan3 aka Guest Wifi and
        Wlan1 normal Wifi
        """
        Domoticz.Debug("read Wlan status")
        try:
            self.wlan3.setFc(self.fbGetFc())
            self.wlan3.readStatus()
        except (Exception) as e:
            # no prob, wlan should handle error it self
            self.wlan3.setMyError(e)
            Domoticz.Error("Error on readStatus: wlan3 msg '{}'; hasError:{}".format(e, str(self.hasError)))

        try:
            self.wlan1.setFc(self.fbGetFc())
            self.wlan1.readStatus()
        except (Exception) as e:
            # no prob, wlan should handle error it self
            self.wlan1.setMyError(e)
            Domoticz.Error("Error on readStatus: wlan1 msg '{}'; hasError:{}".format(e, str(self.hasError)))

    def readStatus(self):
        Domoticz.Debug("read status for {}".format(self.host))
        try:
            self.resetError()
            if(self.fcStatus is None):
                self.connect()
            fs = self.fcStatus
            self.model = fs.modelname
            self.is_linked = fs.is_linked
            self.is_connected = fs.is_connected
            self.external_ip = fs.external_ip
            self.uptime = fs.str_uptime
            # bytes send:', fs.bytes_sent),
            # ('bytes received:', fs.bytes_received),
            self.max_bit_rate = fs.str_max_bit_rate

            # workaround to get 64bit value
            # self.bytes_received = fs.bytes_received
            # self.bytes_sent = fs.bytes_sent
            self.getBytesFromAddOn()

            # md = fs.get_monitor_data()

            # do init bytes and delta
            self.initAndCalcDelta()
            self.verifyUpdate()
            # self.wlan3.setFc(self.fbGetFc())
            # self.wlan3.readStatus()
        except (Exception) as e:
            self.setMyError(e)
            Domoticz.Error("Error on readStatus: msg '{}'; hasError:{}".format(e, str(self.hasError)))

    def getBytesFromAddOn(self):
        s = self.fcStatus.fc.call_action('WANCommonIFC', 'GetAddonInfos')
        # Domoticz.Debug("BLZ: new data {}".format(s))
        self.bytes_sent = int(s['NewX_AVM_DE_TotalBytesSent64'])
        # Domoticz.Debug("BLZ: new data tx {}".format(self.bytes_sent))
        self.bytes_received = int(s['NewX_AVM_DE_TotalBytesReceived64'])
        # Domoticz.Debug("BLZ: new data rx {}".format(self.bytes_received))

    def stop(self):
        self.stopped = True

    def initAndCalcDelta(self):
        # received
        if(self.last_bytes_received is None):
            self.last_bytes_received = self.bytes_received
        self.delta_bytes_received = self.calcDelta(self.last_bytes_received, self.bytes_received, "received")
        self.last_bytes_received = self.bytes_received

        # sent
        if(self.last_bytes_sent is None):
            self.last_bytes_sent = self.bytes_sent
        self.delta_bytes_sent = self.calcDelta(self.last_bytes_sent, self.bytes_sent, "sent")
        self.last_bytes_sent = self.bytes_sent

    def calcDelta(self, last: int, current: int, sType: str):
        delta: int = 0
        if(last is None or last == 0):
            last = current
            Domoticz.Error("restart cnx: ? last None or 0")
        elif(last > current):
            # looks like new connection with new calculated counter
            # this did not really work, looks like AVM does an new calc, so value is not really starts wiht null, feels more like
            # restore from another 1000 vs 1024 calc
            # so using just new value is not working delta = current
            # delta = abs(current - last)
            # try with just ignoring the last bytes ...
            # but better use GetAddonInfos
            delta = 0
            Domoticz.Error("new cnx: {} lst-crnt: {} - {} = {}".format(sType,
                                                                       convertHumanbytes(last),
                                                                       convertHumanbytes(current),
                                                                       convertHumanbytes(delta)))
            Domoticz.Error("new cnx: {} lst-crnt: {:n} - {:n} = {:n}".format(sType, last, current, delta))

        else:
            delta = current - last

        Domoticz.Debug("calcDelta cnx: {} lst-crnt: {:n} - {:n} = {:n} || {}".format(sType,
                                                                                     last, current,
                                                                                     delta,
                                                                                     convertHumanbytes(delta)))
        return delta

    def getDeviceName(self):
        return self.model

    def getDeviceNameWithMB(self):
        s = self.model
        if(self.is_connected is True):
            s = "{} ({})".format(s, self.max_bit_rate[1])
        return s

    def getDeviceNameWithEIP(self):
        s = self.model
        if(self.is_connected is True):
            s = "{} ({})".format(s, self.external_ip)
        return s

    def getShortSummary(self, seperator: str = "\t"):
        s = ("connected = {}{}"
             "EIP = {}{}"
             "max_bit_rate = {}".format(
                 self.is_connected, seperator,
                 self.external_ip, seperator,
                 self.max_bit_rate))
        return s

    def getMegabytesReceivedTotal(self):
        return int(bytesTo(self.bytes_received))

    def getMegabytesReceived(self):
        return int(bytesTo(self.delta_bytes_received))

    def getMegabytesSent(self):
        return int(bytesTo(self.delta_bytes_sent))

    def getSummary(self):
        s = ("model = {}"
             "\tis_linked = {}"
             "\tis_connected = {}"
             "\texternal_ip = {}"
             "\tuptime = {}"
             "\tmax_bit_rate = {}"
             "\treceived = {}"
             "\tsent = {}"
             "\tdelta received = {}"
             "\tdelta sent = {}"
             .format(
                 self.model,
                 self.is_linked,
                 self.is_connected,
                 self.external_ip,
                 self.uptime,
                 self.max_bit_rate,
                 convertHumanbytes(self.bytes_received),
                 convertHumanbytes(self.bytes_sent),
                 convertHumanbytes(self.delta_bytes_received),
                 convertHumanbytes(self.delta_bytes_sent),


             ))
        return s

    def dumpStatus(self):
        '''just print status summary
        '''

        s = self.getSummary()
        Domoticz.Log(s)

    def fbGetFc(self):
        if(isNotBlank(self.user) and isNotBlank(self.password)):
            #  first try with fritz status
            if(self.fcStatus):
                self.fc = self.fcStatus.fc
            if(self.fc is None):
                self.fc = FritzConnection(address=self.host,
                                          user=self.user, password=self.password)
            return self.fc
        else:
            raise Exception("ConfigError - Password and User required")

    def getWlan(self, nr: int = 3):
        """returns matching wlan object

        Keyword Arguments:
            nr {int} -- AVM Wlan Number (default: {3})

        Returns:
            [Wlan] -- related Wlan object
        """
        if(nr == 3):
            return self.getWlan3()
        elif(nr == 1):
            return self.getWlan1()

    def getWlan3(self):
        return self.wlan3

    def getWlan1(self):
        return self.wlan1


def isBlank(myString):
    if myString and myString.strip():
        # myString is not None AND myString is not empty or blank
        return False
    # myString is None OR myString is empty or blank
    return True


def isNotBlank(myString):
    if myString and myString.strip():
        # myString is not None AND myString is not empty or blank
        return True
    # myString is None OR myString is empty or blank
    return False


def bytesTo(bytes: float, to: str = 'm', bsize: int = 1024):
    """convert bytes to megabytes, etc.
       sample code:
           print('mb= ' + str(bytesTo(314575262000000, 'm')))
       sample output:
           mb= 300002347.946
           https://gist.github.com/shawnbutts/3906915

    """

    a = {'k': 1, 'm': 2, 'g': 3, 't': 4, 'p': 5, 'e': 6}
    r = float(bytes)
    for i in range(a[to]):
        r = r / bsize

    return(r)


def convertHumanbytes(B):
    '''Return the given bytes as a human friendly KB, MB, GB, or TB string
    https://stackoverflow.com/questions/12523586/python-format-size-application-converting-b-to-kb-mb-gb-tb
    '''
    if(B is None):
        B = 0
    B = float(B)
    KB = float(1024)
    MB = float(KB ** 2)  # 1,048,576
    GB = float(KB ** 3)  # 1,073,741,824
    TB = float(KB ** 4)  # 1,099,511,627,776
    if B < KB:
        return '{0} {1}'.format(B, 'Bytes' if 0 == B > 1 else 'Byte')
    elif KB <= B < MB:
        return '{0:.2f} KB'.format(B / KB)
    elif MB <= B < GB:
        return '{0:.2f} MB'.format(B / MB)
    elif GB <= B < TB:
        return '{0:.2f} GB'.format(B / GB)
    elif TB <= B:
        return '{0:.2f} TB'.format(B / TB)
