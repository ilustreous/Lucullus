import bottle
import lucullus.server

# Python Issue #5853
import mimetypes
mimetypes.init()

bottle.run(server=bottle.PasteServer, host='0.0.0.0', port=8080, reloader=True)