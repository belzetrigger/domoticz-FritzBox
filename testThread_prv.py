import logging
import threading
import time

logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-10s) %(message)s',
                    )


def worker():
    logging.debug('Starting')
    #from fritzBoxHelper import FritzBoxHelper
    #fh = FritzBoxHelper("192.168.176.43", "", "")
    # fh.readStatus()
    # fh.dumpStatus()
    time.sleep(2)
    logging.debug('Exiting')


def my_service():
    logging.debug('Starting')
    #from fritzBoxHelper import FritzBoxHelper
    from fritzconnection.lib.fritzstatus import FritzStatus
    fc = FritzStatus(address='192.168.176.1')
    logging.debug(fc.is_connected)
   # fh = FritzBoxHelper("fritz.box", "", "")
   # fh.readStatus()
   # fh.dumpStatus()
    time.sleep(3)
    logging.debug('Exiting')


t = threading.Thread(name='2my_service', target=my_service)
w = threading.Thread(name='worker', target=worker)
w2 = threading.Thread(target=worker)  # use default name

w.start()
w2.start()
t.start()
