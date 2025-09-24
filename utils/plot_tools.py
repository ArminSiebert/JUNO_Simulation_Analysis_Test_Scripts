"""
Basic plotting tools (based on matplotlib).
"""

__all__ = ["Ax", "Plot", "MultiPlot", "ColorIterator"]

import textwrap
from warnings import catch_warnings, simplefilter

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator,ScalarFormatter,MultipleLocator
from matplotlib.ticker import FormatStrFormatter

from .plot_constants import *


plt.rcParams["font.size"] = FONT_SIZE
plt.rcParams["figure.subplot.left"] = MARGIN
plt.rcParams["figure.subplot.right"] = 1 - MARGIN
plt.rcParams["figure.subplot.bottom"] = MARGIN
plt.rcParams["figure.subplot.top"] = 1 - MARGIN
mpl.rc('xtick', top=True)
mpl.rc('ytick', right=True)
mpl.rc('xtick', direction='in')
mpl.rc('ytick', direction='in')


def custom_log_formatter(val, _):
    return f"{val:g}" if 0.001 <= val <= 1000 else f"$10^{{{int(np.log10(val))}}}$"


class Ax:
    
    def __init__(self, ax):
        ax.ticklabel_format(axis="x", scilimits=[-3, 3])
        ax.ticklabel_format(axis="y", scilimits=[-3, 3])

        # Tickpositionen automatisch, „schöne“ Schritte
        ax.yaxis.set_major_locator(MaxNLocator(nbins='4'))

        # Ticklabels auf max. 1 Nachkommastelle
        #ax.yaxis.set_major_formatter(lambda x, _: f"{x:.1f}")
        
        self.ax = ax
    
    def add(self, obj, **kwargs):
        obj.plot(self.ax, **kwargs)
    
    def get_xlim(self):
        return self.ax.get_xlim()
    
    def get_ylim(self):
        return self.ax.get_ylim()
    
    def set_xlim(self, *args, **kwargs):
        self.ax.set_xlim(*args, **kwargs)
    
    def set_ylim(self, *args, **kwargs):
        self.ax.set_ylim(*args, **kwargs)
    
    def set_xscale(self, scale):
        if scale != "linear":
            self.ax.set_xscale(scale)
        if scale == "log" and self.ax.get_xlim()[1] is None:
            self.ax.xaxis.set_major_formatter(plt.FuncFormatter(custom_log_formatter))
    
    def set_yscale(self, scale, *args, **kwargs):
        if scale != "linear":
            self.ax.set_yscale(scale, *args, **kwargs)
        if scale == "log" and self.ax.get_ylim()[1] is None:
            self.ax.yaxis.set_major_formatter(plt.FuncFormatter(custom_log_formatter))
    
    def set_grid(self, *args, linestyle="solid", linewidth=0.5, color="gray", alpha=0.25, **kwargs):
        self.ax.grid(*args, linestyle=linestyle, linewidth=linewidth, color=color, alpha=alpha, **kwargs)
    
    def set_xlabel(self, *args, loc="right", **kwargs):
        self.ax.set_xlabel(*args, loc=loc, **kwargs)
    
    def set_ylabel(self, *args, loc="top", **kwargs):
        self.ax.set_ylabel(*args, loc=loc, **kwargs)
    
    def set_xint(self, int, *args, **kwargs):
        if int == True:
            self.ax.xaxis.set_major_locator(MaxNLocator(integer=int))
    
    def set_yint(self, int, *args, **kwargs):
        if int == True:
            self.ax.yaxis.set_major_locator(MaxNLocator(integer=int))
    
    def set_legend(self, title=None, *args, **kwargs):
        leg = self.ax.legend(*args, **kwargs)
        if title != None:
            title = textwrap.fill(title, width=20)
            title_fontproperties={"weight": "bold"}
            leg.set_title(title, title_fontproperties)
            leg.get_title().set_multialignment("center")

    def set_title(self, *args, **kwargs): #hab ich gemacht 
        self.ax.set_title(*args, **kwargs)
    
    def remove(self):
        self.ax.remove()

    


class Plot(Ax):
    
    def __init__(self, figsize=(7.4, 5)):
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(1, 1, 1)
        super().__init__(ax)
        self.fig = fig
    
    def savefig(self, *args, **kwargs):
        with catch_warnings():
            simplefilter("ignore", UserWarning)
            self.fig.savefig(*args, dpi=600, **kwargs)
        plt.close(self.fig)


class MultiPlot:
    
    def __init__(self, row_num, col_num, figsize=None, **kwargs):
        figsize = figsize or (col_num*5, row_num*5)
        fig, axs_ = plt.subplots(figsize=figsize, nrows=row_num, ncols=col_num, **kwargs)
        axs = np.vectorize(lambda ax: Ax(ax))(axs_)
        self.fig = fig
        self.axs = axs
    
    def __getitem__(self, index):
        return self.axs[index]
    
    def savefig(self, *args, **kwargs):
        with catch_warnings():
            simplefilter("ignore", UserWarning)
            self.fig.savefig(*args, dpi=600, **kwargs)
        plt.close(self.fig)


class ColorIterator:
    
    def __init__(self, cmap_nm, color_num, min=0, max=1):
        self.cmap = plt.get_cmap(cmap_nm)
        self.color_num = color_num
        self.min = min
        self.max = max
        self.idx = 0
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.idx >= self.color_num:
            raise StopIteration
        if self.color_num == 1:
            value = (self.min + self.max) / 2
        else:
            value = self.min + (self.idx / (self.color_num - 1)) * (self.max - self.min)
        self.idx += 1
        return self.cmap(value)
