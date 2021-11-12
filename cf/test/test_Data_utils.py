import datetime
import faulthandler
import unittest

import dask.array as da
import numpy as np

faulthandler.enable()  # to debug seg faults and timeouts

import cf


class DataUtilsTest(unittest.TestCase):
    def test_Data_Utils__da_ma_allclose(self):
        """TODO."""
        # Create a range of inputs to test against
        a = np.ma.array([1.0, 2.0, 3.0], mask=[1, 0, 0])
        b = np.ma.array([1.0, 2.0, 3.0], mask=[0, 1, 0])
        c = np.ma.array([1.0, 2.0, 100.0], mask=[1, 0, 0])
        d = np.array([1.0, 2.0, 3.0])
        e = a + 5e-04  # outside of default tolerances
        f = a + 5e-06  # within default tolerances

        # Test the function with these inputs as both numpy and dask arrays...
        allclose = cf.data.dask_utils._da_ma_allclose
        da_ = da.from_array(a)

        self.assertTrue(allclose(a, a).compute())
        self.assertTrue(allclose(da_, da_).compute())

        self.assertTrue(allclose(a, b).compute())
        self.assertTrue(allclose(da_, da.from_array(b)).compute())
        # ...including testing the 'masked_equal' parameter
        self.assertFalse(allclose(a, b, masked_equal=False).compute())
        self.assertFalse(
            allclose(da_, da.from_array(b), masked_equal=False).compute()
        )

        self.assertFalse(allclose(a, c).compute())
        self.assertFalse(allclose(da_, da.from_array(c)).compute())

        self.assertTrue(allclose(a, d).compute())
        self.assertTrue(allclose(da_, da.from_array(d)).compute())

        self.assertFalse(allclose(a, e).compute())
        self.assertFalse(allclose(da_, da.from_array(e)).compute())

        self.assertTrue(allclose(a, f).compute())
        self.assertTrue(allclose(da_, da.from_array(f)).compute())

        # Test when array inputs have different chunk sizes
        da_ = da.from_array(a, chunks=(1, 2))
        self.assertTrue(allclose(da_, da.from_array(b, chunks=(3,))).compute())
        self.assertFalse(
            allclose(
                da_, da.from_array(b, chunks=(3,)), masked_equal=False
            ).compute()
        )
        self.assertFalse(
            allclose(da_, da.from_array(c, chunks=(3,))).compute()
        )

        # Test the 'rtol' and 'atol' parameters:
        self.assertFalse(allclose(a, e, rtol=1e-06).compute())
        self.assertFalse(allclose(da_, da.from_array(e), rtol=1e-06).compute())
        b1 = a / 10000
        b2 = e / 10000
        self.assertTrue(allclose(b1, b2, atol=1e-05).compute())
        self.assertTrue(
            allclose(
                da.from_array(b1), da.from_array(b2), atol=1e-05
            ).compute()
        )


if __name__ == "__main__":
    print("Run date:", datetime.datetime.now())
    cf.environment()
    print()
    unittest.main(verbosity=2)
