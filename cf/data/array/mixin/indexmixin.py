from numbers import Integral

import numpy as np
from dask.base import is_dask_collection

from ....functions import indices_shape, parse_indices


class IndexMixin:
    """Mixin class for lazy indexing of a data array.

    A data for a subspace it retrieved by casting the `{{class}}` as a
    `numpy` array:

    >>> a = cf.{{class}}(....)
    >>> a.shape
    (6, 5)
    >>> print(np.asanyarray(a)
    [[ 0  1  2  3  4])
     [ 5  6  7  8  9]
     [10 11 12 13 14]
     [15 16 17 18 19]
     [20 21 22 23 24]
     [25 26 27 28 29]]
    >>> a = a[::2, [1, 3, 4]]
    >>> a = a[[False, True, True], 1:]
    >>> a.shape
    (2, 2)
    >>> print(np.asanyarray(a))
    [[13 14]
     [23 24]]

    .. versionadded:: NEXTVERSION

    """

    def __array__(self, *dtype):
        """Convert the ``{{class}}` into a `numpy` array.

        .. versionadded:: (cfdm) NEXTVERSION

        :Parameters:

            dtype: optional
                Typecode or data-type to which the array is cast.

        :Returns:

            `numpy.ndarray`
                An independent `numpy` array of the subspace of the
                data defined by the `indices` attribute.

        """
        array = self._get_array()
        if dtype:
            return array.astype(dtype[0], copy=False)

        return array

    def __getitem__(self, index):
        """Returns a subspace of the array as a new `{{class}}`.

        x.__getitem__(indices) <==> x[indices]

        The new `{{class}}` may be converted to a `numpy` array with
        its `__array__` method.

        Consecutive subspaces are lazy, with only the final data
        elements retrieved from the data when `__array__` is called.

        For example, if the original data has shape ``(12, 145, 192)``
        and consecutive subspaces of ``[8:9, 10:20:3, [15, 1, 4, 12]``
        and ``[[0], [True, False, True], ::-2]`` are applied, then
        only the elements defined by subspace ``[[8], [10, 16], [12,
        1]]`` will be retrieved from the data when `__array__` is
        called.

        .. versionadded:: NEXTVERSION

        .. seealso:: `index`, `original_shape`, `__array__`,
                     `__getitem__`

        :Returns:

            `{{class}}`
                The subspaced array.

        """
        shape0 = self.shape
        index0 = self.index
        original_shape = self.original_shape

        index = parse_indices(shape0, index, keepdims=False)

        new = self.copy()
        new_indices = []
        new_shape = []

        i = 0
        for ind0, original_size in zip(index0, original_shape):
            if isinstance(ind0, Integral):
                # This dimension has been previously removed by the
                # integer index 'ind0'
                new_indices.append(ind0)
                continue

            # 'index' might have fewer elements than 'index0'
            ind1 = index[i]
            size0 = shape0[i]
            i += 1

            if isinstance(ind1, slice) and ind1 == slice(None):
                # This dimension is not subspaced
                new_indices.append(ind0)
                continue

            # Still here? Then we have to work out the the subspace of
            # the full array implied by applying both 'ind0' and
            # 'ind1'.
            if is_dask_collection(ind1):
                # Note: This will never occur when __getitem__ is
                #       being called from within a Dask graph, because
                #       any lazy indices will have already been
                #       computed as part of the whole graph execution;
                #       i.e. we don't have to worry about a
                #       compute-within-a-compute situation. (If this
                #       were not the case then we could get round it
                #       by wrapping the compute inside a `with
                #       dask.config.set({"scheduler":
                #       "synchronous"}):` clause.)
                ind1 = ind1.compute()

            if isinstance(ind0, slice):
                if isinstance(ind1, slice):
                    # ind0: slice
                    # ind1: slice
                    start, stop, step = ind0.indices(original_size)
                    start1, stop1, step1 = ind1.indices(size0)
                    size1, mod1 = divmod(stop1 - start1, step1)

                    if mod1 != 0:
                        size1 += 1

                    start += start1 * step
                    step *= step1
                    stop = start + (size1 - 1) * step

                    if step > 0:
                        stop += 1
                    else:
                        stop -= 1

                    if stop < 0:
                        stop = None

                    new_index = slice(start, stop, step)
                else:
                    # ind0: slice
                    # ind1: int, or array of int/bool
                    new_index = np.arange(*ind0.indices(original_size))[ind1]
            else:
                # ind0: array of int
                new_index = np.asanyarray(ind0)[ind1]

            new_indices.append(new_index)

        new_shape = indices_shape(new_indices, original_shape, keepdims=False)
        new._set_component("shape", tuple(new_shape), copy=False)
        new._custom["index"] = tuple(new_indices)

        return new

    def __repr__(self):
        """Called by the `repr` built-in function.

        x.__repr__() <==> repr(x)

        """
        return (
            f"<CF {self.__class__.__name__}{self.shape}: "
            f"{self}{self.original_shape}>"
        )

    @property
    def __asanyarray__(self):
        """Whether the array is accessed by conversion to a `numpy` array.

        .. versionadded:: NEXTVERSION

        :Returns:

            `True`

        """
        return True

    def _get_array(self, index=None):
        """Returns a subspace of the data as a `numpy` array.

        .. versionadded:: NEXTVERSION

        .. seealso:: `__array__`, `index`

        :Parameters:

            index: `tuple` or `None`, optional
                Provide the indices that define the subspace. If
                `None` then the `index` attribute is used.

        :Returns:

            `numpy.ndarray`
                The subspace.

        """
        return NotImplementedError(
            f"Must implement {self.__class__.__name__}._get_array"
        )

    @property
    def index(self):
        """The index to be applied when converting to a `numpy` array.

        The `shape` is defined by the `index` applied to the
        `original_shape`.

        .. versionadded:: NEXTVERSION

        .. seealso:: `shape`, `original_shape`

        **Examples**

        >>> x.index
        (slice(None), slice(None), slice(None))
        >>> x.shape
        (12, 145, 192)
        >>> x = x[8:9, 10:20:3, [15, 1,  4, 12]]
        >>> x.index
        (slice(8, 9), slice(10, 20, 3), [15, 1,  4, 12])
        >>> x.shape
        (1, 3, 4)
        >>> x = x[[0], [True, False, True], ::-2]
        >>> x.index
        ([8], [10, 16], [12, 1])
        >>> x.shape
        (1, 2, 2)

        """
        ind = self._custom.get("index")
        if ind is None:
            ind = (slice(None),) * self.ndim
            self._custom["index"] = ind
            self._custom["original_shape"] = self.shape

        return ind

    @property
    def original_shape(self):
        """The original shape of the data.

        The `shape` is defined by the `index` applied to the
        `original_shape`.

        .. versionadded:: NEXTVERSION

        .. seealso:: `index`, `shape`

        """
        out = self._custom.get("original_shape")
        if out is None:
            # If shape is None then no subspace has been defined
            out = self.shape
            self._custom["original_shape"] = out

        return out
