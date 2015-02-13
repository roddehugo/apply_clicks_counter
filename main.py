# -*- coding: utf-8 -*-
import logging
import os
import sys
from Queue import Queue

from request_thread import RequestThread
from display_thread import DisplayThread
from graceful_interrupt_handler import GracefulInterruptHandler

from settings import PIDFILE, PID, LOG_LEVEL, LOG_FORMAT


def exit_gracefuly():
    """
    We ensure every thread ends correctly.
    We remove the PIDFILE.
    Then Ciao!
    """

    logging.info('Waiting for threads to terminate...')
    request.stop()
    display.stop()
    request.join()
    request.join()
    os.unlink(PIDFILE)
    logging.info('Ciao...')
    sys.exit(1)

if __name__ == '__main__':
    """
    Main file for the application.
    Three threads involved :
        - MainThread
        - RequestThread
        - DisplayThread
    We ensure everything ends up gracefuly thanks to GracefulInterruptHandler
    as a context manager.
    """

    print '          _____________________________________________ '
    print '         //:::::::::::::::::::::::::::::::::::::::::::::\\\ '
    print '       //:::_______:::::::::________::::::::::_____:::::::\\\ '
    print '     //:::_/   _-"":::_--"""        """--_::::\_  ):::::::::\\\ '
    print '    //:::/    /:::::_"                    "-_:::\/:::::|^\:::\\\ '
    print '   //:::/   /~::::::I__                      \:::::::::|  \:::\\\ '
    print '   \\\:::\   (::::::::::""""---___________     "--------"  /:::// '
    print '    \\\:::\  |::::::::::::::::::::::::::::""""==____      /:::// '
    print '     \\\:::"\/::::::::::::::::::::::::::::::::::::::\   /~:::// '
    print '       \\\:::::::::::::::::::::::::::::::::::::::::::)/~:::// '
    print '         \\\::::\""""""------_____:::::::::::::::::::::::// '
    print '           \\\:::"\               """""-----_____::::::// '
    print '             \\\:::"\    __----__                ):::// '
    print '               \\\:::"\/~::::::::~\_         __/~::// '
    print '                 \\\::::::::::::::::""----"""::::// '
    print '                   \\\:::::::::::::::::::::::::// '
    print '                     \\\:::\^""--._.--""^/:::// '
    print '                       \\\::"\         /"::// '
    print '                         \\\::"\     /"::// '
    print '                           \\\::"\_/"::// '
    print '                             \\\:::::// '
    print '                               \\\_// '
    print '                                 " '

    logging.basicConfig(
        level=LOG_LEVEL,
        format=LOG_FORMAT,
    )

    if os.path.isfile(PIDFILE):
        logging.info('%s already exists, exiting...', PIDFILE)
        sys.exit(0)
    else:
        file(PIDFILE, 'w').write(PID)

    with GracefulInterruptHandler() as gih:
        logging.info('Starting...')
        queue = Queue()
        queue.put("Work4Labs")
        queue.put("AC Counter")

        try:
            request = RequestThread(queue)
            request.start()

            display = DisplayThread(queue, 5)
            display.start()
            display.join()

            display = DisplayThread(queue, 5)
            display.start()
            display.join()
        except KeyboardInterrupt:
            exit_gracefuly()

        while True:
            if gih.interrupted:
                exit_gracefuly()
            display = DisplayThread(queue)
            display.start()
            display.join()
