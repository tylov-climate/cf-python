from urllib.parse import urlparse

import cfdm

from ..array.abstract import Array
from ..array.mixin import FileArrayMixin
from .h5netcdffragmentarray import H5netcdfFragmentArray
from .mixin import FragmentArrayMixin
from .netcdf4fragmentarray import NetCDF4FragmentArray


class NetCDFFragmentArray(
    FragmentArrayMixin,
    cfdm.data.mixin.NetCDFFileMixin,
    FileArrayMixin,
    cfdm.data.mixin.FileArrayMixin,
    Array,
):
    """A netCDF fragment array.

    Access will either with `netCDF4` (for local and OPenDAP files) or
    `h5netcdf` (for S3 files).

    .. versionadded:: 3.15.0


    """

    def __init__(
        self,
        filename=None,
        address=None,
        dtype=None,
        shape=None,
        aggregated_units=False,
        aggregated_calendar=False,
        units=False,
        calendar=None,
        storage_options=None,
        source=None,
        copy=True,
    ):
        """**Initialisation**

        :Parameters:

            filename: (sequence of `str`), optional
                The names of the netCDF fragment files containing the
                array.

            address: (sequence of `str`), optional
                The name of the netCDF variable containing the
                fragment array. Required unless *varid* is set.

            dtype: `numpy.dtype`, optional
                The data type of the aggregated array. May be `None`
                if the numpy data-type is not known (which can be the
                case for netCDF string types, for example). This may
                differ from the data type of the netCDF fragment
                variable.

            shape: `tuple`, optional
                The shape of the fragment within the aggregated
                array. This may differ from the shape of the netCDF
                fragment variable in that the latter may have fewer
                size 1 dimensions.

            units: `str` or `None`, optional
                The units of the fragment data. Set to `None` to
                indicate that there are no units. If unset then the
                units will be set during the first `__getitem__` call.

            calendar: `str` or `None`, optional
                The calendar of the fragment data. Set to `None` to
                indicate the CF default calendar, if applicable. If
                unset then the calendar will be set during the first
                `__getitem__` call.

            {{aggregated_units: `str` or `None`, optional}}

            {{aggregated_calendar: `str` or `None`, optional}}

            {{init storage_options: `dict` or `None`, optional}}

                .. versionadded:: 3.17.0

            {{init source: optional}}

            {{init copy: `bool`, optional}}

        """
        super().__init__(
            source=source,
            copy=copy,
        )

        if source is not None:
            try:
                shape = source._get_component("shape", None)
            except AttributeError:
                shape = None

            try:
                filename = source._get_component("filename", None)
            except AttributeError:
                filename = None

            try:
                address = source._get_component("address", None)
            except AttributeError:
                address = None

            try:
                dtype = source._get_component("dtype", None)
            except AttributeError:
                dtype = None

            try:
                units = source._get_component("units", False)
            except AttributeError:
                units = False

            try:
                calendar = source._get_component("calendar", False)
            except AttributeError:
                calendar = False

            try:
                aggregated_units = source._get_component(
                    "aggregated_units", False
                )
            except AttributeError:
                aggregated_units = False

            try:
                aggregated_calendar = source._get_component(
                    "aggregated_calendar", False
                )
            except AttributeError:
                aggregated_calendar = False

            try:
                storage_options = source._get_component(
                    "storage_options", None
                )
            except AttributeError:
                storage_options = None

        if filename is not None:
            if isinstance(filename, str):
                filename = (filename,)
            else:
                filename = tuple(filename)

            self._set_component("filename", filename, copy=False)

        if address is not None:
            if isinstance(address, int):
                address = (address,)
            else:
                address = tuple(address)

            self._set_component("address", address, copy=False)

        if storage_options is not None:
            self._set_component("storage_options", storage_options, copy=False)

        self._set_component("shape", shape, copy=False)
        self._set_component("dtype", dtype, copy=False)
        self._set_component("units", units, copy=False)
        self._set_component("calendar", calendar, copy=False)
        self._set_component("mask", True, copy=False)

        self._set_component("aggregated_units", aggregated_units, copy=False)
        self._set_component(
            "aggregated_calendar", aggregated_calendar, copy=False
        )

        # By default, close the file after data array access
        self._set_component("close", True, copy=False)

    def __getitem__(self, indices):
        """Returns a subspace of the fragment as a numpy array.

        x.__getitem__(indices) <==> x[indices]

        .. versionadded:: 3.15.0

        """

        kwargs = {
            "dtype": self.dtype,
            "shape": self.shape,
            "aggregated_units": self.get_aggregated_units(None),
            "aggregated_calendar": self.get_aggregated_calendar(None),
            "units": self.get_units(None),
            "calendar": self.get_units(None),
            "copy": False,
        }

        # Loop round the files, returning as soon as we find one that
        # is accessible.
        filenames = self.get_filenames()
        for filename, address in zip(filenames, self.get_addresses()):
            kwargs["filename"] = filename
            kwargs["address"] = address

            scheme = urlparse(filename).scheme
            if scheme == "s3":
                kwargs["storage_options"] = self.get_storage_options(
                    endpoint_url=False
                )
                fragment = H5netcdfFragmentArray(**kwargs)
            else:
                fragment = NetCDF4FragmentArray(**kwargs)

            try:
                return fragment[indices]
            except FileNotFoundError:
                pass
            except RuntimeError as error:
                raise RuntimeError(f"{error}: {filename}")

        # Still here?
        if len(filenames) == 1:
            raise FileNotFoundError(f"No such fragment file: {filenames[0]}")

        raise FileNotFoundError(f"No such fragment files: {filenames}")
