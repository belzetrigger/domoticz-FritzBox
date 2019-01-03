# just ot test FritzHelper a bit outside domoticz

# play with imports, because on windows lxml works on start but not after update
try:
    from lxml import etree
    print("running with lxml.etree")
except ImportError:
    try:
        # Python 2.5
        import xml.etree.cElementTree as etree
        print("running with cElementTree on Python 2.5+")
    except ImportError:
        try:
            # Python 2.5
            import xml.etree.ElementTree as etree
            print("running with ElementTree on Python 2.5+")
        except ImportError:
            try:
                # normal cElementTree install
                import cElementTree as etree
                print("running with cElementTree")
            except ImportError:
                try:
                    # normal ElementTree install
                    import elementtree.ElementTree as etree
                    print("running with ElementTree")
                except ImportError:
                    print("Failed to import ElementTree from any known place")

from fritzHelper import FritzHelper


def runTest(fh: FritzHelper):
    fh.dumpConfig()
    fh.readStatus()
    fh.dumpStatus()
    print("need Update: {}".format(fh.needUpdate))
    fh.readStatus()
    print("need Update: {}".format(fh.needUpdate))
    print("summary: {}".format(fh.getSummary()))
    print("summary short: {}".format(fh.getShortSummary()))
    print("summary short: {}".format(fh.getShortSummary("; ")))

    print("name:\t{}".format(fh.getDeviceName()))
    print("nameMB:\t{}".format(fh.getDeviceNameWithMB()))
    print("nameEIP:\t{}".format(fh.getDeviceNameWithEIP()))

    # print("date: {} level:{} txt: {} name: {}".format(y.getNearestDate(),
    #
    #                  y.getAlarmLevel(), y.getAlarmText(),
    #              y.getDeviceName()))
    #
fh = FritzHelper("fritz.box", "", "")
runTest(fh)
