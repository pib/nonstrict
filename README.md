Non-strict versions of Python data structures.

So far, there is a LazyList implementation which takes an iterable and
only consumes it as needed, while still allowing regular list usage
such as subscripting, slicing, and iterating over the list.