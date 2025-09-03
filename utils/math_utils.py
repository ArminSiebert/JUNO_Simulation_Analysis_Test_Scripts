"""
Math utility functions.
"""

__all__ = ["norm", "sphe_to_cart"]

import numpy as np


def norm(pt_1, pt_2=None):
    """
    Calculates the Euclidean distance between two points.
    ---
    Parameters:
    pt_1 (array-like of float): The first point
    pt_2 (array-like of float, optional): The second point (defaults to the origin if not provided)
    ---
    Returns:
    d (float): The Euclidean distance
    """
    pt_1 = np.asarray(pt_1)
    pt_2 = np.asarray(pt_2) if pt_2 is not None else np.full_like(pt_1, fill_value=0)
    assert pt_1.shape == pt_2.shape
    d = np.linalg.norm(pt_2 - pt_1)
    return d


def sphe_to_cart(pt):
    """
    Converts a point in spherical to cartesian coordinates.
    ---
    Parameters:
    pt (array-like of float): The point in spherical coordinates
    ---
    Returns:
    pt (array-like of float): The point in cartesian coordinates
    """
    pt = np.asarray(pt)
    assert pt.shape == (3,)
    theta = np.radians(pt[1])
    phi = np.radians(pt[2])
    x = pt[0] * np.sin(theta) * np.cos(phi)
    y = pt[0] * np.sin(theta) * np.sin(phi)
    z = pt[0] * np.cos(theta)
    pt = np.asarray([x, y, z])
    return pt
