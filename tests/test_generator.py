import time
import unittest

from hamcrest import *
from flexmock import flexmock
from functools import partial

from twisted.internet import reactor, defer, task

from fibonacci.fibonacci import FibonacciGenerator


class TestGenerator(unittest.TestCase):
    """
    Unit tests for fibonacci generator
    """

    # Testcases:
    # 1. Invalid cache
    # 2. Calling self.generator several times in parallel

    def setUp(self):
        self.generator = FibonacciGenerator()
        self.sequence = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987, 1597, 2584, 4181, 6765, 10946, 17711, 28657, 46368, 75025, 121393, 196418, 317811, 514229]

    def fetch(self, count):
        return self.generator.fetch(count).addCallback(lambda res: map(int, res))

    @defer.inlineCallbacks
    def test_basic(self):
        """
        Basic test
        1. fetch sequence several times with different ranges
        2. self.generator should reuse data from cache
        """
        self.generator = FibonacciGenerator()
        res = yield self.fetch(10)
        assert_that(res, equal_to(self.sequence[:10]))
        res = yield self.fetch(10)
        assert_that(res, equal_to(self.sequence[:10]))
        res = yield self.fetch(11)
        assert_that(res, equal_to(self.sequence[:11]))

        res = yield self.fetch(200)
        assert_that(len(res), equal_to(200))

    def test_parallel_requests(self):
        """
        Check how generator handles several parallel requests
        And when one request is slow, other should be still processed
        E.g. check if GIL occurs or not
        """

        def validate(res, count):
            if count < 21:
                assert_that(res, equal_to(self.sequence[:count]))
            else:
                assert_that(len(res), equal_to(count))

        values = [4, 1000, 12, 15, 1, 20, 10, 3, 5, 11, 9, 8, 7, 19]

        flexmock(self.generator) \
            .should_call("fetch") \
            .times(len(values))

        return defer.DeferredList([self.fetch(i).addCallback(validate, i) for i in values])
