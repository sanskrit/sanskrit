import heapq


class PriorityQueue(object):

    """A priority queue. Higher values are popped first."""

    def __init__(self):
        self.heap = []

    def __copy__(self):
        p = PriorityQueue()
        p.heap = list(self.heap)

    def __str__(self):
        return str([(item, priority) for priority, item in self.heap])

    def __len__(self):
        return len(self.heap)

    def __iter__(self):
        for priority, item in self.heap:
            yield (item, -priority)

    def push(self, item, priority=0):
        """Add an item to the queue.

        :param item: the item to add
        :param priority: the priority to use
        """
        pair = (-priority, item)
        heapq.heappush(self.heap, pair)

    def pop(self):
        """Pop the highest-priority item from the queue."""
        return heapq.heappop(self.heap)[-1]

    def pop_with_priority(self):
        """Pop the highest-priority item and its priority from the queue::

            item, priority = q.pop_with_priority()

        ::
        """
        (priority, item) = heapq.heappop(self.heap)
        return (item, -priority)

    def peek(self):
        """Read the highest-priority item and its priority without removing
        them from the queue::

            item, priority = q.peek()
            assert (item, priority) == q.peek()

        If the queue is empty, throw an :exc:`IndexError`.
        """
        priority, item = self.heap[0]
        return (item, -priority)
