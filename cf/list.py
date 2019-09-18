import cfdm

from . import mixin


class List(mixin.PropertiesData,
           cfdm.List):
    '''A list variable required to uncompress a gathered array.

Compression by gathering combines axes of a multidimensional array
into a new, discrete axis whilst omitting the missing values and thus
reducing the number of values that need to be stored.

The information needed to uncompress the data is stored in a list
variable that gives the indices of the required points.

.. versionadded:: 3.0.0

    '''
#--- End: class