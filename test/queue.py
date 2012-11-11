# -*- coding: utf-8 -*-
"""
test.queue
~~~~~~~~~~

Tests the :class:`~sanskrit.util.queue.PriorityQueue` class.

:license: MIT and BSD
"""

import os
from sanskrit.util import PriorityQueue
from . import TestCase

class QueueTestCase(TestCase):

    """Tests various queue functions."""

    def test_push_and_pop(self):
        """Test basic queue operations."""
        q = PriorityQueue()
        for i in range(5):
            q.push(i, -i)

        self.assertEqual(len(q), 5)
        self.assertEqual(4, q.pop())
        self.assertEqual(3, q.pop())
        self.assertEqual((2, -2), q.pop_with_priority())
        self.assertEqual(len(q), 2)

    def test_peek(self):
        """Test peeking at the top of the queue."""
        q = PriorityQueue()
        q.push('item', 0)
        q.push('item2', 1)
        item, priority = q.peek()
        self.assertEqual((item, priority), q.peek())
        q.pop()
        self.assertNotEqual((item, priority), q.peek())
        q.pop()
        self.assertRaises(IndexError, q.pop)
