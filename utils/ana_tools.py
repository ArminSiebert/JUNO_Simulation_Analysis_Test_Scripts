"""
Basic analysis tools.
"""

__all__ = ["Hist", "Graph", "Scatter", "Func", "Fit"]

from inspect import signature
from warnings import warn

import numpy as np
from scipy.signal import savgol_filter, find_peaks
from scipy.optimize import curve_fit, minimize_scalar
from scipy.integrate import quad
import matplotlib.pyplot as plt


class Hist:

    def __init__(self):
        pass

    def set_bins(self, bin_num, min, max):
        self.bin_num = bin_num
        self.min = min
        self.max = max
    
    def fill(self, vals):
        self.vals, self.bin_edges = np.histogram(vals, bins=self.bin_num, range=(self.min, self.max))
    
    def normalize(self, factor=1):
        integ = self.get_integ()
        self.vals = factor * (self.vals / integ) if integ != 0 else np.zeros_like(self.vals)
    
    def smooth(self, window_length=5, polyorder=3):
        self.vals = savgol_filter(self.vals, window_length=window_length, polyorder=polyorder)
        self.vals = np.ceil(self.vals)
        self.vals[self.vals < 0] = 0
    
    def fit(self, fit, max_iter_num=10000, use_init_on_fail=True):
        x_vals = (self.bin_edges[:-1] + self.bin_edges[1:]) / 2
        y_vals = self.vals
        fit_x_vals = x_vals[(x_vals >= fit.min) & (x_vals <= fit.max)]
        fit_y_vals = y_vals[(x_vals >= fit.min) & (x_vals <= fit.max)]
        try:
            popt, _ = curve_fit(fit.func, fit_x_vals, fit_y_vals, p0=fit.init_vals, bounds=(fit.lower_bounds, fit.upper_bounds), maxfev=max_iter_num)
        except Exception as e:
            if not use_init_on_fail:
                raise e
            warn("Fit did not converge. Using initial values.")
            popt = fit.init_vals
        setattr(fit, 'fit_x_vals', fit_x_vals)
        setattr(fit, 'fit_y_vals', fit_y_vals)
        setattr(fit, 'vals', popt)
    
    def get_integ(self):
        integ = np.sum(self.vals * np.diff(self.bin_edges))
        return integ
    
    def get_max_bin_idx(self):
        max_bin_idx = np.argmax(self.vals)
        return max_bin_idx
    
    def get_peak_bin_idcs(self, prominence):
        peak_bin_idcs, _ = find_peaks(self.vals, prominence=prominence)
        return peak_bin_idcs
    
    def get_bin_idx(self, x_val):
        bin_idx = np.digitize([x_val], self.bin_edges)[0] - 1
        return bin_idx
    
    def get_x_val(self, bin_idx):
        x_val = (self.bin_edges[bin_idx] + self.bin_edges[bin_idx+1]) / 2
        return x_val
    
    def get_val(self, bin_idx):
        val = self.vals[bin_idx]
        return val
    
    def plot(self, ax=plt, **kwargs):
        kwargs.setdefault("align", "edge")
        kwargs.setdefault("rasterized", True)
        width = kwargs.get("width", 0.9) if kwargs["align"] == "center" else np.diff(self.bin_edges)
        ax.bar(self.bin_edges[:-1], self.vals, width, **kwargs)


class Graph:
    
    def __init__(self):
        pass
    
    def fill(self, x_vals, y_vals):
        self.x_vals, self.y_vals = x_vals, y_vals
    
    def plot(self, ax=plt, **kwargs):
        kwargs.setdefault("rasterized", True)
        ax.plot(self.x_vals, self.y_vals, **kwargs)


class Scatter:
    
    def __init__(self):
        pass
    
    def fill(self, x_vals, y_vals):
        self.x_vals, self.y_vals = x_vals, y_vals
    
    def plot(self, ax=plt, **kwargs):
        kwargs.setdefault("rasterized", True)
        ax.scatter(self.x_vals, self.y_vals, **kwargs)


class Func:
    
    def __init__(self, min, max, func, vals):
        self.min = min
        self.max = max
        self.func = func
        self.vals = vals
    
    def get_max(self, min=None, max=None):
        min = min or self.min
        max = max or self.max
        max = minimize_scalar(lambda x: -self.func(x, *self.vals), bounds=(min, max)).x
        return max
    
    def get_integ(self, min=None, max=None):
        min = min or self.min
        max = max or self.max
        integ, _ = quad(lambda x: self.func(x, *self.vals), min, max)
        return integ
    
    def plot(self, ax=plt, pt_num=1e6, **kwargs):
        x_vals = np.linspace(self.min, self.max, num=int(pt_num))
        kwargs.setdefault("rasterized", True)
        ax.plot(x_vals, self.func(x_vals, *self.vals), **kwargs)


class Fit(Func):
    
    def __init__(self, min, max, func, init_vals=None, lower_bounds=None, upper_bounds=None):
        super().__init__(min, max, func, vals=None)
        self.init_vals = init_vals
        self.lower_bounds = lower_bounds
        self.upper_bounds = upper_bounds
    
    def get_chisq(self, min=None, max=None):
        x_vals = self.fit_x_vals
        y_vals = self.fit_y_vals
        if min != None:
            x_vals = x_vals[x_vals >= min]
            y_vals = y_vals[len(y_vals) - len(x_vals):]
        if max != None:
            x_vals = x_vals[x_vals <= max]
            y_vals = y_vals[:len(x_vals)]
        non_zero_idcs = (y_vals != 0)
        chisq = np.sum(((self.func(x_vals[non_zero_idcs], *self.vals) - y_vals[non_zero_idcs]) ** 2) / np.abs(y_vals[non_zero_idcs]))
        return chisq
    
    def get_ndf(self, min=None, max=None):
        x_vals = self.fit_x_vals
        if min != None:
            x_vals = x_vals[x_vals >= min]
        if max != None:
            x_vals = x_vals[x_vals <= max]
        bin_num = len(x_vals)
        par_num = len(signature(self.func).parameters) - 1
        ndf = bin_num - par_num
        return ndf
    
    def get_chisq_ndf(self, min=None, max=None):
        chisq = self.get_chisq(min, max)
        ndf = self.get_ndf(min, max)
        chisq_ndf = chisq / ndf
        return chisq_ndf
