# Python Issue #5853
import mimetypes
mimetypes.init()

import logging, sys
COLOR_SEQ = "\033[1;%dm"
format="%(asctime)s $BOLD%(levelname)s$RESET [%(name)s] %(filename)s (%(lineno)d)\n$WHITE%(message)s$RESET\n"
format = format.replace('$RESET', "\033[0m")
format = format.replace('$BOLD', "\033[1m")
format = format.replace('$WHITE', "\033[1;37m")

logging.basicConfig(level=logging.DEBUG, stream=sys.stderr, format=format)

import bottle
bottle.debug(True)
import lucullus.server
bottle.run(server=bottle.PasteServer, host='0.0.0.0', port=8080, reloader=True)