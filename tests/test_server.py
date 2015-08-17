import json
import unittest

from hamcrest import *

from twisted.web.resource import Resource
from twisted.web.server import Request, Site
from twisted.web.http import StringTransport
from twisted.protocols.basic import LineReceiver

from fibonacci.fibonacci import FibonacciServerResource, FibonacciGenerator


class TestAPI(unittest.TestCase):

    """
    Tests for server API functional
    """

    def setUp(self):
        self.web_root = FibonacciServerResource(FibonacciGenerator())
        self.site = Site(self.web_root)

    def request(self, method, uri, **kwargs):
        req = Request(LineReceiver(), True)
        req.transport = StringTransport()
        req.method = method
        req.uri = uri
        req.path = uri
        req.args = kwargs
        req.clientproto = 'HTTP/1.1'
        req.prepath = []
        req.postpath = uri.split('/')[1:]
        return req

    def render(self, req):
        resource = self.site.getResourceFor(req)
        req.render(resource)
        resp = req.transport.getvalue().split('\r\n\r\n')
        return {
            "headers": resp[0],
            "content": resp[1],
        }

    def test_sequence_api(self):
        """
        Check how limit value is handled
        1. Pass negative limit
        2. Pass limit as string
        3. Do not pass the limit at all
        """
        def check_responce(res, content, code):
            assert_that(res["headers"], contains_string(str(code)))
            if content:
                assert_that(res["content"], equal_to(content))
            return res

        check_responce(self.render(self.request("GET", "/sequence")),
                       "limit param missing",
                       400)

        check_responce(self.render(self.request("GET", "/sequence", limit=["nope"])),
                       "limit should be an integer",
                       400)

        check_responce(self.render(self.request("GET", "/sequence", limit=[-1])),
                       "limit value must be a positive number",
                       400)

        check_responce(self.render(self.request("GET", "/sequence", limit=[0])),
                       "limit value must be a positive number",
                       400)

        res = check_responce(self.render(self.request("GET", "/sequence", limit=[5])), None, 200)

        assert_that(res['content'].strip(), contains_string("[0,1,1,2,3]"))
