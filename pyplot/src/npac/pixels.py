#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Pixels module """
import math
import numpy as np

from typing import Tuple


class PixelsSet:
    """
    A Pixels set class
    Each pixel of an image is a tuple (struct) with 3 elements:
    (row index, column index, intensity value) = (int, int, int)
    """

    def __init__(self) -> None:
        """ Construct an empty set of pixels

        Examples
        ----------
        >>> ps = PixelsSet()
        >>> print(ps.pixels)
        []
        """
        self.pixels = []

    def __str__(self) -> str:
        """ Printable format for the set of pixels.

        Returns
        ----------
        out : str
            String containing the value of the flux (integral) and centroid
            of the pixel (or set of pixels) which has the max value.

        Examples
        ----------
        >>> ps = PixelsSet()
        >>> ps.add(0, 0, 10)
        >>> ps.add(1, 1, 10)
        >>> ps.__str__()
        '20 (integral) at 0.5|0.5 (peak)'

        >>> print(ps)
        20 (integral) at 0.5|0.5 (peak)
        """
        return "{} (integral) at {}|{} (peak)".format(
            self.get_integral(),
            *self.get_peak())

    def add(self, row: int, column: int, value: int) -> None:
        """ Add a given pixel to the set

        Parameters
        ----------
        row : int
            Index of the row
        column : int
            Index of the column
        value : int
            Flux value for the pixel

        Examples
        ----------
        >>> ps = PixelsSet()
        >>> print(ps.pixels)
        []

        >>> ps.add(0, 0, 10)
        >>> print(ps.pixels)
        [(0, 0, 10)]
        """
        self.pixels.append((row, column, value))

    def get_len(self) -> int:
        """ Get the number of pixels in the Set.

        Returns
        ----------
        out : int
            The number of pixels

        Examples
        ----------
        >>> ps = PixelsSet()
        >>> ps.pixels = [(2, 1, 10), (3, 1, 10), (1, 2, 10)]
        >>> nb = ps.get_len()
        >>> print(nb)
        3
        """
        return len(self.pixels)

    def get_integral(self) -> int:
        """ Get the sum of values for all pixels

        Returns
        ----------
        out : int
            The sum of values for all pixels.

        Examples
        ----------
        >>> ps = PixelsSet()
        >>> ps.pixels = [(2, 1, 10), (3, 1, 11), (1, 2, 12)]
        >>> sum_ps = ps.get_integral()
        >>> print(sum_ps)
        33
        """
        return sum([pixel[2] for pixel in self.pixels])

    def get_top(self) -> int:
        """ Get the max value of all pixels

        Returns
        ----------
        out : int
            The maximum flux value

        Examples
        ----------
        >>> ps = PixelsSet()
        >>> ps.pixels = [(2, 1, 50), (3, 1, 11), (1, 2, 12)]
        >>> top_ps = ps.get_top()
        >>> print(top_ps)
        50
        """
        return max([pixel[2] for pixel in self.pixels])

    def get_center(self) -> (float, float):
        """ Get the center coordinates of the bounding box enclosing pixels

        Returns
        ----------
        out : (float, float)
            The center coordinates

        Examples
        ----------
        >>> ps = PixelsSet()
        >>> ps.pixels = [(2, 1, 50), (3, 1, 11), (1, 4, 12)]
        >>> center_ps = ps.get_center()
        >>> print(center_ps)
        (2.0, 2.5)
        """
        rows, cols, values = zip(*self.pixels)
        row_center = (min(rows) + max(rows)) / 2.0
        col_center = (min(cols) + max(cols)) / 2.0
        return row_center, col_center

    def get_centroid(self) -> Tuple[float, float]:
        """ Get the coordinates of the barycenter of the pixel set.

        Returns
        ----------
        out : (float, float)
            Coordinates of the barycenter of the pixel set.

        Examples
        ----------
        >>> ps = PixelsSet()
        >>> centroid = ps.get_centroid()
        Traceback (most recent call last):
          ...
        AssertionError: The number of pixels must be at least one to compute the centroid!

        >>> ps.pixels = [(2, 1, 50), (3, 1, 11), (1, 4, 12)]
        >>> centroid = ps.get_centroid()
        >>> print(centroid)
        (2.0, 2.0)
        """
        nbpixels = len(self.pixels)
        if nbpixels == 0:
            raise AssertionError("The number of pixels must be at least one to compute the centroid!")

        rows, cols, _ = zip(*self.pixels)
        row_mean = sum(rows) / nbpixels
        col_mean = sum(cols) / nbpixels

        return row_mean, col_mean

    def get_weighted_centroid(self) -> Tuple[float, float]:
        """" Get the weighted centroid

        The weights correspond to the flux values of pixels.
        The more is the flux, the bigger is the weight (centroid will shift
        towards large flux values).

        Returns
        ----------
        out :

        Examples
        ----------
        >>> ps = PixelsSet()
        >>> ps.pixels = [(2, 1, 50), (3, 1, 11), (1, 4, 12)]
        >>> weight = ps.get_weighted_centroid()
        >>> print("{:.2f} {:.2f}".format(*weight))
        2.07 2.14
        """
        nbpixels = len(self.pixels)
        if nbpixels == 0:
            raise AssertionError("The number of pixels must be at least one to compute the centroid!")

        integral = self.get_integral()
        row_mean, col_mean = self.get_centroid()
        row_weighted = sum(
            [pixel[2] * ((pixel[0] - row_mean)**2) for pixel in self.pixels])
        col_weighted = sum(
            [pixel[2] * ((pixel[1] - col_mean)**2) for pixel in self.pixels])
        row_weighted = math.sqrt(row_weighted) / integral + row_mean
        col_weighted = math.sqrt(col_weighted) / integral + col_mean

        return row_weighted, col_weighted

    def get_peak(self) -> Tuple[float, float]:
        """
        Get the centroid of the pixel(s) which have the max value

        Returns
        ----------
        out : (float, float)
            The coordinates of the centroid.

        Examples
        ----------
        >>> ps = PixelsSet()
        >>> ps.pixels = [
        ...     (2, 1, 10), (3, 1, 10),
        ...     (1, 2, 10), (2, 2, 20),
        ...     (3, 2, 20), (1, 3, 10),
        ...     (2, 3, 20), (3, 3, 20)]
        >>> peak = ps.get_peak()
        >>> print(peak)
        (2.5, 2.5)
        """
        nbpixels = len(self.pixels)
        if nbpixels == 0:
            raise AssertionError("The number of pixels must be at least one to compute the centroid!")

        # Find the pixel(s) whose flux value is the biggest
        _, _, values = zip(*self.pixels)
        max_pixels_indices = np.where(values == np.max(values))[0]
        max_pixels = [self.pixels[i] for i in max_pixels_indices]

        rows, cols, _ = zip(*max_pixels)
        nbpixels = len(max_pixels)
        row_mean = sum(rows) / nbpixels
        col_mean = sum(cols) / nbpixels

        return row_mean, col_mean

    def get_extension(self) -> float:
        """
        Get the maximum extension of a pixel set relatively the peak pixel

        Returns
        ----------
        out : float
            The maximum extension.

        Examples
        ----------
        >>> ps = PixelsSet()
        >>> ps.pixels = [
        ...     (2, 1, 10), (3, 1, 10),
        ...     (1, 2, 10), (2, 2, 20),
        ...     (3, 2, 20), (1, 3, 10),
        ...     (2, 3, 20), (3, 3, 20)]
        >>> extension = ps.get_extension()
        >>> print(extension)
        2.5
        """
        nbpixels = len(self.pixels)
        if nbpixels == 0:
            raise AssertionError("The number of pixels must be at least one to compute the extension!")

        peak = self.get_peak()
        xs = [p[0] for p in self.pixels]
        ys = [p[1] for p in self.pixels]

        Xs = [x - peak[0] for x in xs]
        Ys = [y - peak[1] for y in ys]

        s = max([Xs[i]*Xs[i] + Ys[i]*Ys[i] for i in range(nbpixels)])

        return s

def _tests():
    """ Unit tests for pixels. To run the test, execute:

    python3 pixels.py

    It should exit gracefully if no error (exit code 0),
    otherwise it will print on the screen the failure.

    In PyCharm, just click on Run "Doctests in pixels" button (green button),
    or CTRL+click on the file, and choose Run "Doctests in pixels".
    """
    import doctest
    doctest.testmod()


if __name__ == '__main__':
    """ Execute the test suite """
    _tests()
