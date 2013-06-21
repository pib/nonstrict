import sys

class LazyList(object):
    """ List which wraps an iterable object, lazily evaluates it, and
    caches the result for subsequent use.

    Implements all the standard list functionality like iterating,
    indexing, slicing, length checking, boolean conversion,
    containment checking. For each of these operations, the minimum
    amount of the original iteratable is evaluated.
    
    Length checking will force the entire iterable to be evaluated,
    boolean conversion will only evaluate the first item. All the
    others will evaluate just as much as needed.

    >>> il = LazyList(range(100))
    >>> il._expanded_len == len(il._expanded) == 0
    True
    >>> il[42]
    42
    >>> il._expanded_len
    43
    >>> 55 in il
    True
    >>> il._expanded_len
    56
    """
    def __init__(self, iterable):
        self._expanded = []
        self._iterator = iter(iterable)
        self._expanded_len = 0

    def __iter__(self):
        """
        >>> il = LazyList(range(10))
        >>> list(il)
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        >>> len(il._expanded)
        10
        >>> i1 = iter(il)
        >>> next(i1)
        0
        >>> i2 = iter(il)
        >>> next(i1)
        1
        >>> next(i2)
        0
        >>> next(i1)
        2
        """
        def iterate():
            index = 0
            while True:
                try:
                    yield self._get(index)
                except IndexError:
                    raise StopIteration
                index += 1
        return iterate()

    def __getitem__(self, desired_index):
        """
        >>> il = LazyList(range(10))
        >>> il[5]
        5
        >>> il._expanded
        [0, 1, 2, 3, 4, 5]
        >>> il[5:8]
        [5, 6, 7]
        >>> il._expanded
        [0, 1, 2, 3, 4, 5, 6, 7, 8]
        """
        try:
            return self._get(desired_index)
        except StopIteration:
            raise IndexError

    def _get(self, desired_index):
        if self._iterator is not None:
            if isinstance(desired_index, slice):
                self.expand_to_slice(desired_index)
            else:
                self.expand_to_index(desired_index)

        return self._expanded[desired_index]

    def expand_to_index(self, desired_index):
        while self._expanded_len <= desired_index:
            try:
                next_val = next(self._iterator)
            except StopIteration:
                self._iterator = None
                raise

            self._expanded.append(next_val)
            self._expanded_len += 1

    def expand_to_slice(self, desired_slice):
        max = desired_slice.stop or sys.maxsize

        try:
            self.expand_to_index(max)
        except (IndexError, StopIteration):
            self._iterator = None

    def __bool__(self):
        """
        >>> il = LazyList(range(0))
        >>> bool(il)
        False
        >>> il = LazyList(range(10))
        >>> bool(il)
        True
        >>> il._expanded
        [0]
        """
        for _ in self:
            return True
        return False

    __nonzero__ = __bool__

    def __len__(self):
        try:
            self.expand_to_index(sys.maxsize)
        except StopIteration:
            pass
        return len(self._expanded)
