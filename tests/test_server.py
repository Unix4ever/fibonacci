import json

from hamcrest import *

from flexmock import flexmock

from twisted.python import log, failure
from twisted.trial import unittest
from twisted.internet import defer, reactor
from twisted.web.server import Site
from twisted.web.client import getPage

from fibonacci.fibonacci import FibonacciServerResource, FibonacciGenerator


class TestAPI(unittest.TestCase):

    """
    Tests for server API functional
    """

    def setUp(self):
        self.web_root = FibonacciServerResource(FibonacciGenerator())
        self.site = Site(self.web_root)
        self.server = reactor.listenTCP(8000, self.site)

    def tearDown(self):
        return self.server.stopListening()

    def test_sequence_api(self):
        """
        Check how limit value is handled
        1. Pass negative limit
        2. Pass limit as string
        3. Do not pass the limit at all
        """
        def check_params(method, uri, params, content, code):
            def check_response(res):
                if isinstance(res, failure.Failure):
                    assert_that(res.value.status, equal_to(str(code)))
                    assert_that(res.value.response, contains_string(content))
                else:
                    assert_that(res, contains_string(content))

            d = getPage("http://localhost:8000%s?%s" % (uri, "&".join(["%s=%s" % (key, value) for key, value in params.iteritems()])))
            return d.addBoth(check_response)

        cases = (
            ("GET", "/sequence", {}, "limit param missing", 400),
            ("GET", "/sequence", dict(limit="nope"), "limit should be an integer", 400),
            ("GET", "/sequence", dict(limit=-1), "limit value must be a positive number", 400),
            ("GET", "/sequence", dict(limit=5), "[0,1,1,2,3]", 200),
        )
        return defer.DeferredList([check_params(*args) for args in cases], fireOnOneErrback=True)
