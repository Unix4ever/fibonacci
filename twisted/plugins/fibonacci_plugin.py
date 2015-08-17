import sys

from zope.interface import implements

from twisted.python import usage
from twisted.application.service import IServiceMaker
from twisted.plugin import IPlugin

from fibonacci import fibonacci


class Options(usage.Options):
    synopsis = "[options]"
    longdesc = "Create a fibonacci server"

    optParameters = [
                ["port", None, 8080, "Listen on specified port number", int],
                ["bind-address", None, "10.1.0.6", "Bind on specified address", str]
            ]


class FibonacciServiceMaker(object):
    implements(IServiceMaker, IPlugin)

    tapname = "fibonacci"
    description = "Fibonacci server"
    options = Options

    def makeService(self, config):
        return fibonacci.makeService(config)

serviceMaker = FibonacciServiceMaker()
