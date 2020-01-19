# this is our helper class to do the work with FritzConnection
#
# Attribute 	Description
# is_linked 	True if the FritzBox is physically linked to the provider
# is_connected 	True if the FritzBox has established an internet-connection
# wan_access_type 	Connection-type, can be DSL or Cable
# external_ip 	External ip address
# uptime 	Uptime in seconds
# bytes_sent 	Bytes sent
# bytes_received 	Bytes received
# transmission_rate_up 	Current upstream speed in bytes/s
# transmission_rate_down 	Current downstream speed in bytes/s
# max_byte_rate_up 	Maximum upstream-rate in bytes/s
# max_byte_rate_down 	Maximum downstream-rate in bytes/s

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


class FritzBoxHelper:

    def __init__(self, host: str, user: str, password: str):
        self.host = host
        self.user = user
        self.password = password
        self.debug = False
        self.hasError = False
        self.previousError = False
        self.lastUpdate = datetime.now()
        self.nextpoll = datetime.now()
        self.reset()

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
        self.stopped = False
        self.fcStatus = None
        self.model = None
        self.is_linked = None
        self.is_connected = None
        self.external_ip = None
        self.uptime = None
        self.max_bit_rate = None
        self.last_external_ip = None
        self.last_is_connected = None
        self.last_max_bit_rate = None
        self.resetError()

    def connect(self):
        Domoticz.Debug("Try to get FritzStatus Connection")

        # import fritzconnection as fc
        self.fcStatus = FritzStatus(
            address=self.host
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
            self.verifyUpdate()

        except (Exception) as e:
            self.setMyError(e)
            Domoticz.Error("Error on readStatus: msg '{}'; hasError:{}".format(e, str(self.hasError)))

    def stop(self):
        self.stopped = True

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

    def getSummary(self):
        s = ("model = {}"
             "\tis_linked = {}"
             "\tis_connected = {}"
             "\texternal_ip = {}"
             "\tuptime = {}"
             "\tmax_bit_rate = {}".format(
                 self.model,
                 self.is_linked,
                 self.is_connected,
                 self.external_ip,
                 self.uptime,
                 self.max_bit_rate))
        return s

    def dumpStatus(self):
        '''just print status summary
        '''

        s = self.getSummary()
        Domoticz.Log(s)
