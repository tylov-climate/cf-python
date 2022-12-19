import cfdm
from dask.utils import SerializableLock

from .mixin import FileArrayMixin


class NetCDFArray(FileArrayMixin, cfdm.NetCDFArray):
    """An array stored in a netCDF file."""

    def __repr__(self):
        """Called by the `repr` built-in function.

        x.__repr__() <==> repr(x)

        """
        return super().__repr__().replace("<", "<CF ", 1)

    @property
    def _dask_lock(self):
        """Set the lock for use in `dask.array.from_array`.

        Returns a lock object (unless no file name has been set, in
        which case `False` is returned) because concurrent reads are
        not currently supported by the netCDF-C library. The lock
        object will be the same for all `NetCDFArray` instances with
        this file name, which means that all file access coordinates
        around the same lock.

        .. versionadded:: TODODASKVER

        """
        filename = self.get_filename(None)
        if filename is None:
            return False

        return SerializableLock(filename)
