"""
Hit time utility functions.
"""

__all__ = ["select_pmts", "select_time", "correct_tof", "get_align_shift", "align", "shift", "remove_nan", "get_hits", "get_rec_hits"]

from collections.abc import Iterable
from warnings import warn

import numpy as np

#from .tools import Hist
from .ana_tools import Hist 
from . import pmt_utils as pu


def select_pmts(hit_times, hit_pmt_ids, *add_hit_arrs, pmt_typ=None, pmt_mfr=None):
    """
    Filters hit time data based on PMT type or manufacturer.
    ---
    Parameters:
    hit_times (array-like of int): The unfiltered hit times
    hit_pmt_ids (array-like of int): The unfiltered hit PMT ids
    add_hit_arrs (array-like of any): Additional unfiltered hit arrays (e.g. charges)
    pmt_typ (str, optional): The PMT type to be filtered (lpmt, spmt)
    pmt_mfr (str, optional): The PMT manufacturers to be filtered (Hamamatsu, HighQENNVT, HZC)
    ---
    Returns:
    hit_times (array-like of int): The filtered hit times
    hit_pmt_ids (array-like of int): The filtered hit PMT ids
    add_hit_arrs (array-like of any): Additional filtered hit arrays (e.g. charge)
    """
    hit_times, hit_pmt_ids, *add_hit_arrs = map(np.asarray, [hit_times, hit_pmt_ids, *add_hit_arrs])
    assert all(len(arr) == len(hit_times) for arr in [hit_pmt_ids, *add_hit_arrs])
    mask = hit_pmt_ids < 50000
    hit_times = hit_times[mask]
    hit_pmt_ids = hit_pmt_ids[mask]
    add_hit_arrs = [arr[mask] for arr in add_hit_arrs]
    if pmt_typ is not None:
        mask = pu.pmt_typ(hit_pmt_ids) == pmt_typ
        hit_times = hit_times[mask]
        hit_pmt_ids = hit_pmt_ids[mask]
        add_hit_arrs = [arr[mask] for arr in add_hit_arrs]
    if pmt_mfr is not None:
        mask = pu.pmt_mfr(hit_pmt_ids) == pmt_mfr
        hit_times = hit_times[mask]
        hit_pmt_ids = hit_pmt_ids[mask]
        add_hit_arrs = [arr[mask] for arr in add_hit_arrs]
    return hit_times, hit_pmt_ids, *add_hit_arrs


def select_time(hit_times, *add_hit_arrs, t_min=None, t_max=None):
    """
    Filters hit time data based on a time interval.
    ---
    Parameters:
    hit_times (array-like of int): The unfiltered hit times
    add_hit_arrs (array-like of any): Additional unfiltered hit arrays (e.g. PMT ids, charges)
    t_min (float, optional): The minimum time
    t_max (float, optional): The maximum time
    ---
    Returns:
    hit_times (array-like of int): The filtered hit times
    add_hit_arrs (array-like of any): Additional filtered hit arrays (e.g. PMT ids, charges)
    """
    hit_times, *add_hit_arrs = map(np.asarray, [hit_times, *add_hit_arrs])
    assert all(len(arr) == len(hit_times) for arr in [*add_hit_arrs])
    mask = np.where((hit_times >= (t_min if t_min is not None else -np.inf)) & (hit_times <= (t_max if t_max is not None else np.inf)))[0]
    hit_times = hit_times[mask]
    add_hit_arrs = [arr[mask] for arr in add_hit_arrs]
    return hit_times, *add_hit_arrs


def correct_tof(hit_times, hit_pmt_ids, evt_pos):
    """
    Applies TOF correction on hit times for a given event position.
    ---
    Parameters:
    hit_times (array-like of int): The uncorrected hit times
    hit_pmt_ids (array-like of int): The hit PMT ids
    evt_pos (tuple[float]): The event positionm (x, y, z)
    ---
    Returns:
    hit_times (array-like of int): The corrected hit times
    """
    hit_times, hit_pmt_ids = map(np.asarray, [hit_times, hit_pmt_ids])
    assert len(hit_times) == len(hit_pmt_ids)
    tof = pu.pmt_tof(hit_pmt_ids, evt_pos)
    hit_times -= tof
    return hit_times


def get_align_shift(hit_times, prominence, max_ratio=0.1, offset=2):
    """
    Calculates shift for alignement relative to the first peak with given prominence.
    ---
    Parameters:
    hit_times (array-like of int): The hit times
    prominence (float): The peak prominence
    max_ratio (float): The alignement maximum ratio
    offset (float): The alignement offset
    ---
    Returns:
    align_shift (float): The align shift
    """
    hit_times = np.asarray(hit_times)
    x_min, x_max = max(int(hit_times.min()), -100000), min(int(hit_times.max()), 100000)
    hist = Hist()
    hist.set_bins(x_max-x_min, x_min, x_max)
    hist.fill(hit_times)
    hist.smooth()
    peak_bin_idcs = hist.get_peak_bin_idcs(prominence)
    if len(peak_bin_idcs) > 0:
        bin_idx = peak_bin_idcs[0]
    else:
        warn("No peaks found. The maximum is used for alignment.")
        bin_idx = hist.get_max_bin_idx()
    max_val = hist.get_val(bin_idx)
    while bin_idx > 0:
        val = hist.get_val(bin_idx)
        if val < max_ratio*max_val or bin_idx == 0:
            break
        bin_idx -= 1
    x_val = hist.get_x_val(bin_idx)-0.5
    shift = - x_val + offset
    return shift


def align(hit_times, prominence, max_ratio=0.1, offset=2, **kwargs):
    """
    Aligns hit times relative to the first peak with given prominence.
    ---
    Parameters:
    hit_times (array-like of int): The hit times
    prominence (float): The peak prominence
    max_ratio (float): The alignement maximum ratio
    offset (float): The alignement offset
    ---
    Returns:
    hit_times (array-like of int): The aligned hit times
    """
    hit_times = np.asarray(hit_times)
    shift = get_align_shift(hit_times, prominence, max_ratio, offset)
    hit_times += shift
    if kwargs.get('rtn_align_shift', False):
        return hit_times, shift
    return hit_times


def shift(hit_times, shift):
    """
    Shifts hit times.
    ---
    Parameters:
    hit_times (array-like of int): The hit times
    shift (float): The shift
    ---
    Returns:
    hit_times (array-like of int): The shifted hit times
    """
    hit_times = np.asarray(hit_times)
    hit_times += shift
    return hit_times


def remove_nan(*hit_arrs):
    """
    Removes nan values in hit arrays.
    ---
    Parameters:
    hit_arrs (array-like of any): The hit arrays (e.g. times, PMT ids, charges)
    ---
    Returns:
    hit_arrs (array-like of any): The hit arrays without nan values
    """
    assert all(len(arr) == len(hit_arrs[0]) for arr in hit_arrs)
    mask = ~np.any(np.isnan(hit_arrs), axis=0)
    hit_arrs = [arr[mask] for arr in hit_arrs]
    return (*hit_arrs,)


def get_hits(phys_evt, pmt_typ=None, pmt_mfr=None, rtn_track_ids=False):
    """
    Returns hit time data from a physcial event, filtered based on PMT type or manufacturer.
    ---
    Parameters:
    phys_evt (PhysEvt): The physical event
    pmt_typ (str, optional): The PMT type to be filtered (lpmt, spmt)
    pmt_mfr (str, optional): The PMT manufacturers to be filtered (Hamamatsu, HighQENNVT, HZC)
    rtn_track_ids (bool, optional): Allows to return track ids
    ---
    Returns:
    hit_times (array-like of int): The filtered hit times
    hit_pmt_ids (array-like of int): The filtered hit PMT ids
    hit_track_ids (array-like of int, optional): The filtered hit track ids
    """
    hit_times, hit_pmt_ids = phys_evt.hit_times, phys_evt.hit_pmt_ids
    if rtn_track_ids:
        hit_track_ids = phys_evt.hit_track_ids
        hit_times, hit_pmt_ids, hit_track_ids = select_pmts(hit_times, hit_pmt_ids, hit_track_ids, pmt_typ=pmt_typ, pmt_mfr=pmt_mfr)
        mask = ~np.isnan(hit_times) & ~np.isnan(hit_pmt_ids) & ~np.isnan(hit_track_ids)
        hit_times = hit_times[mask]
        hit_pmt_ids = hit_pmt_ids[mask]
        hit_track_ids = hit_track_ids[mask]
        return hit_times, hit_pmt_ids, hit_track_ids
    else:
        hit_times, hit_pmt_ids = select_pmts(hit_times, hit_pmt_ids, pmt_typ=pmt_typ, pmt_mfr=pmt_mfr)
        mask = ~np.isnan(hit_times) & ~np.isnan(hit_pmt_ids)
        hit_times = hit_times[mask]
        hit_pmt_ids = hit_pmt_ids[mask]
        return hit_times, hit_pmt_ids


def get_rec_hits(trig_evts, pmt_typ=None, pmt_mfr=None, rtn_charges=False):
    """
    Returns reconstructed hit time data from trigger events, filtered based on PMT type or manufacturer.
    ---
    Parameters:
    trig_evts (list[TrigEvt]): The trigger events
    pmt_typ (str, optional): The PMT type to be filtered (lpmt, spmt)
    pmt_mfr (str, optional): The PMT manufacturers to be filtered (Hamamatsu, HighQENNVT, HZC)
    rtn_charges (bool, optional): Allows to return charges
    ---
    Returns:
    rec_hit_times (array-like of int): The filtered reconstructed hit times
    rec_hit_pmt_ids (array-like of int): The filtered reconstructed hit PMT ids
    rec_hit_charges (array-like of int, optional): The filtered reconstructed hit charges
    """
    trig_evts = trig_evts if isinstance(trig_evts, Iterable) else [trig_evts]
    rec_hit_times, rec_hit_pmt_ids, rec_hit_charges = [], [], []
    for trig_evt in trig_evts:
        trig_time = trig_evt.trig_time - trig_evts[0].trig_time
        rec_hit_times_, rec_hit_pmt_ids_ = trig_evt.rec_hit_times, trig_evt.rec_hit_pmt_ids
        if rtn_charges:
            rec_hit_charges_ = trig_evt.rec_hit_charges
            rec_hit_times_, rec_hit_pmt_ids_, rec_hit_charges_ = select_pmts(rec_hit_times_, rec_hit_pmt_ids_, rec_hit_charges_, pmt_typ=pmt_typ, pmt_mfr=pmt_mfr)
        else:
            rec_hit_times_, rec_hit_pmt_ids_ = select_pmts(rec_hit_times_, rec_hit_pmt_ids_, pmt_typ=pmt_typ, pmt_mfr=pmt_mfr)
        rec_hit_times_ += trig_time
        rec_hit_times.extend(rec_hit_times_)
        rec_hit_pmt_ids.extend(rec_hit_pmt_ids_)
        if rtn_charges:
            rec_hit_charges.extend(rec_hit_charges_)
    rec_hit_times = np.asarray(rec_hit_times)
    rec_hit_pmt_ids = np.asarray(rec_hit_pmt_ids)
    rec_hit_charges = np.asarray(rec_hit_charges)
    if rtn_charges:
        return rec_hit_times, rec_hit_pmt_ids, rec_hit_charges
    else:
        return rec_hit_times, rec_hit_pmt_ids
