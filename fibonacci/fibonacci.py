import json
import os
import time

from twisted.application import service, internet
from twisted.web import server, resource, http, error
from twisted.web.server import Site
from twisted.python import log
from twisted.internet import threads, reactor, defer

from txrestapi.resource import APIResource
from txrestapi.methods import GET


class FibonacciIterator(object):
    """
    Fibonacci sequence iterator
    """

    def __init__(self, initial_values=None):
        self.cursor = -1
        self.sequence = [0, 1]

    def next(self):
        p1, p2 = self.sequence[-2:]

        self.sequence.append(p1 + p2)
        self.cursor += 1
        return self.sequence[self.cursor]


class FibonacciGenerator(object):

    CACHE_INDEX = ".cache_index"
    CACHE_FILE = ".cache_file"

    def fetch(self, limit):
        """
        Fetch fibonacci sequence
        @param limit: Records number from the start
        @type limit: int
        @returns: List of fibonacci sequence numbers
        @rtype: str
        """
        start = time.time()
        log.msg("Started generation of fibonacci %s" % (limit))

        iterator = FibonacciIterator()
        sequence = []

        d = defer.Deferred()

        def process_batch(count):
            for i in xrange(count):
                next_number_string = str(iterator.next())
                sequence.append(next_number_string)

                if len(sequence) >= limit:
                    log.msg("Ended generation of fibonacci, elapsed time %s" % (time.time() - start))
                    d.callback(sequence)
                    return

            reactor.callLater(0, process_batch, count)

        process_batch(200)
        return d


class FibonacciServerResource(APIResource):
    """
    Fibonacci server rest API resource
    """

    def __init__(self, fibonacci_generator):
        """
        @param fibonacci_generator: Service which generates fibonacci sequence
        @type  fibonacci_generator: C{FibonacciGenerator}
        """
        APIResource.__init__(self)
        self.fibonacci_generator = fibonacci_generator

    @GET("^/sequence/?$")
    def get_fibonacci_sequence(self, request):
        """
        Get fibonacci sequence
        @param request: Request object
        @type  request: dict
        """

        try:
            limit = int(request.args.get("limit", [None])[0])
        except ValueError:
            request.setResponseCode(http.BAD_REQUEST)
            return "limit should be an integer"
        except TypeError:
            request.setResponseCode(http.BAD_REQUEST)
            return "limit param missing"

        if limit <= 0:
            request.setResponseCode(http.BAD_REQUEST)
            return "limit value must be a positive number"

        def write_response(result):
            request.setHeader("Content-Type", "application/json")
            request.write(''.join(["[", ",".join(result), "]"]))
            request.finish()

        self.fibonacci_generator.fetch(limit).addCallback(write_response)
        return server.NOT_DONE_YET


def makeService(config):
    """
    Create a fibonacci server

    @param config: Twisted plugin configuration dict
    @type  config: dict
    """
    fibonacci_generator = FibonacciGenerator()
    s = service.MultiService()
    h = internet.TCPServer(config["port"],
                           Site(FibonacciServerResource(fibonacci_generator), timeout=None),
                           interface=config["bind-address"])
    h.setServiceParent(s)
    return s
