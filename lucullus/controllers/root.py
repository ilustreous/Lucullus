import logging

from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect_to

from lucullus.lib.base import BaseController, template

log = logging.getLogger(__name__)

class RootController(BaseController):
    def index(self):
        return template('index.mako')

