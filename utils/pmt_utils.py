"""
PMT utility functions.
"""

__all__ = ["pmt_typ", "pmt_pos", "pmt_mfr", "pmt_tof"]

from collections.abc import Iterable

import numpy as np

from .constants import JUNOSW_DIR, IS_JUNOSW
from . import math_utils as mu


R_S = 17700    # Radius of the JUNO CD to the acrylics sphere [mm]
R_PMT = 19500  # Radius of the JUNO CD to the PMTs surface [mm]
N_LS = 1.5     # Refractive index of the JUNO LS
N_H2O = 1.33   # Refractive index of water (between acrylics sphere and PMTs surface)

GEOMETRY_DIR = f"{JUNOSW_DIR}/data/Detector/Geometry"
LPMT_POS_FPTH = f"{GEOMETRY_DIR}/PMTPos_CD_LPMT.csv"
SPMT_POS_FPTH = f"{GEOMETRY_DIR}/PMTPos_CD_SPMT.csv"
LPMT_MFR_FPTH = f"{GEOMETRY_DIR}/PMTType_CD_LPMT.csv"
SPMT_MFR_FPTH = f"{GEOMETRY_DIR}/PMTType_CD_SPMT.csv"


if IS_JUNOSW:
    ### Find maximum PMT id
    max_pmt_id = 0
    for file_pth in [LPMT_POS_FPTH, SPMT_POS_FPTH]:
        with open(file_pth, "r") as file:
            for line in file:
                pass
            last_line = line
            id = int(line.split()[0])
            max_pmt_id = max(max_pmt_id, id)
    ### Define PMT data arrays
    pmt_typ_arr = np.full(max_pmt_id + 1, None, dtype=object)
    pmt_mfr_arr = np.full(max_pmt_id + 1, None, dtype=object)
    pmt_pos_arr = np.full((max_pmt_id + 1, 3), np.nan, dtype=float)
    ### Load PMT types and positions from position files
    for file_pth, typ in zip([LPMT_POS_FPTH, SPMT_POS_FPTH], ["lpmt", "spmt"]):
        with open(file_pth, "r") as file:
            for line in file:
                if line.startswith(("#", "\"")):
                    continue
                line = line.split()
                id = int(line[0])
                theta = float(line[-2])
                phi = float(line[-1])
                pos = mu.sphe_to_cart((R_PMT, theta, phi))
                pmt_typ_arr[id] = typ
                pmt_pos_arr[id] = pos
    ### Load PMT manufacturers from manufacturer files
    for file_pth in [LPMT_MFR_FPTH, SPMT_MFR_FPTH]:
        with open(file_pth, "r") as file:
            for line in file:
                if line.startswith(("#", "\"")):
                    continue
                line = line.split()
                id = int(line[0])
                mfr = line[1]
                pmt_mfr_arr[id] = mfr


def pmt_typ(pmt_ids):
    """
    Returns PMT types for given PMT ids.
    ---
    Parameters:
    pmt_ids (int or array-like of int): The PMT ids
    ---
    Returns:
    pmt_typs (str or array-like of str): The PMT types (lpmt, spmt)
    """
    is_seq = isinstance(pmt_ids, Iterable)
    pmt_ids = np.atleast_1d(np.asarray(pmt_ids))
    if len(pmt_ids) == 0:
        return np.asarray([])
    result = np.full(pmt_ids.shape, None, dtype=object)
    result = pmt_typ_arr[pmt_ids]
    return result if is_seq else result[0]


def pmt_pos(pmt_ids):
    """
    Returns PMT positions for given PMT ids.
    ---
    Parameters:
    pmt_ids (int or array-like of int): The PMT ids
    ---
    Returns:
    pmt_pos (tuple[float] or array-like of tuple[float]): The PMT positions (x, y, z)
    """
    is_seq = isinstance(pmt_ids, Iterable)
    pmt_ids = np.atleast_1d(np.asarray(pmt_ids))
    if len(pmt_ids) == 0:
        return np.asarray([])
    result = np.full((pmt_ids.size, 3), np.nan, dtype=float)
    result = pmt_pos_arr[pmt_ids]
    return np.atleast_2d(result) if is_seq else result[0]


def pmt_mfr(pmt_ids):
    """
    Returns PMT manufacturers for given PMT ids.
    ---
    Parameters:
    pmt_ids (int or array-like of int): The PMT ids
    ---
    Returns:
    pmt_mfrs (str or array-like of str): The PMT manufacturers (Hamamatsu, HighQENNVT, HZC)
    """
    is_seq = isinstance(pmt_ids, Iterable)
    pmt_ids = np.atleast_1d(np.asarray(pmt_ids))
    if len(pmt_ids) == 0:
        return np.asarray([])
    result = np.full(pmt_ids.shape, None, dtype=object)
    result = pmt_mfr_arr[pmt_ids]
    return result if is_seq else result[0]


def pmt_tof(pmt_ids, evt_pos):
    """
    Returns PMT TOF values for given PMT ids and an event position.
    ---
    Parameters:
    pmt_ids (int or array-like of int): The PMT ids
    evt_pos (tuple[float]): The event position (x, y, z)
    ---
    Returns:
    pmt_tofs (float or array-like of float): The PMT TOF values [ns]
    """
    assert len(evt_pos) == 3
    is_seq = isinstance(pmt_ids, Iterable)
    pmt_ids = np.atleast_1d(np.asarray(pmt_ids))
    evt_pos = np.asarray(evt_pos)
    if len(pmt_ids) == 0:
        return np.asarray([])
    pos = np.atleast_2d(pmt_pos(pmt_ids))
    ### Calculate total distance between event and PMT
    d = np.sqrt(np.sum((pos - evt_pos)**2, axis=1))
    ### Calculate distance in water
    r = np.sqrt(np.sum(evt_pos**2))
    cos_theta = (R_PMT**2 + d**2 - r**2) / (2 * R_PMT * d)
    cos_theta = np.clip(cos_theta, -1, 1)
    theta = np.arccos(cos_theta)
    d_h2o = (R_PMT * np.cos(theta)) - np.sqrt(R_S**2 - (R_PMT**2 * np.sin(theta)**2))
    d_h2o = np.where(np.isnan(d_h2o), R_PMT * np.cos(theta), d_h2o)
    ### Calculate distance in liquid scintillator
    d_ls = d - d_h2o
    ### Calculate TOF
    tof = ((d_ls * N_LS) + (d_h2o * N_H2O)) / 300
    tof = np.where(np.isnan(tof), 0, tof)
    return tof if is_seq else tof[0]
