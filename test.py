# just ot test FritzHelper a bit outside domoticz

from fritzBoxHelper import FritzBoxHelper


def format_bytes(size):
    # 2**10 = 1024
    power = 2**10
    n = 0
    power_labels = {0: '', 1: 'kilo', 2: 'mega', 3: 'giga', 4: 'tera'}
    while size > power:
        size /= power
        n += 1
    return size, power_labels[n] + 'bytes'


def humanbytes(B):
    'Return the given bytes as a human friendly KB, MB, GB, or TB string'
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


def bytesto(bytes: float, to: str = 'mb', bsize: int = 1024):
    """convert bytes to megabytes, etc.
       sample code:
           print('mb= ' + str(bytesto(314575262000000, 'm')))
       sample output: 
           mb= 300002347.946
    """

    a = {'k': 1, 'm': 2, 'g': 3, 't': 4, 'p': 5, 'e': 6}
    r = float(bytes)
    for i in range(a[to]):
        r = r / bsize

    return(r)


def runTest(fh: FritzBoxHelper):
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


tests = [1, 1024, 500000, 1048576, 50000000, 1073741824, 5000000000, 1099511627776, 5000000000000]
for t in tests:
    print('{0} == {1}'.format(t, format_bytes(t)))
    print('{0} == {1}'.format(t, humanbytes(t)))
    print('{} == {}'.format(t, bytesto(t, 'k')))


fh = FritzBoxHelper("fritz.box", "", "")
runTest(fh)
