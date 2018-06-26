# author: Daniel Burkhardt <daniel.burkhardt@yale.edu>
# (C) 2017 Krishnaswamy Lab GPLv2

# Plotting convenience functions
from __future__ import print_function, division
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D  # NOQA: F401
import pandas as pd
import numbers
from .phate import PHATE

try:
    import anndata
except ImportError:
    # anndata not installed
    pass


def _get_plot_data(data):
    """Get plot data out of an input object

    Parameters
    ----------
    data : array-like, `phate.PHATE` or `scanpy.AnnData`
    """
    if isinstance(data, PHATE):
        data = data.transform()
    else:
        try:
            if isinstance(data, anndata.AnnData):
                try:
                    data = data.obsm['X_phate']
                except KeyError:
                    raise RuntimeError(
                        "data.obsm['X_phate'] not found. "
                        "Please run `sc.tl.phate(adata)` before plotting.")
        except NameError:
            # anndata not installed
            pass
    return data


def _auto_params(data, c, discrete, cmap, legend):
    """Automatically select nice parameters for a scatter plot
    """
    if c is not None:
        if discrete is None:
            # guess
            if not np.all([isinstance(x, numbers.Number) for x in c]):
                discrete = True
            else:
                discrete = len(np.unique(c)) <= 20
            if discrete:
                print("Assuming discrete data.")
            else:
                print("Assuming continuous data.")
        if discrete:
            c, labels = pd.factorize(c)
            if cmap is None and len(np.unique(c)) <= 10:
                cmap = mpl.colors.ListedColormap(
                    mpl.cm.tab10.colors[:len(np.unique(c))])
            elif cmap is None:
                cmap = 'tab20'
        else:
            labels = None
            if cmap is None:
                cmap = 'inferno'
    else:
        labels = None
        legend = False
    if len(data) == 3:
        subplot_kw = {'projection': '3d'}
    elif len(data) == 2:
        subplot_kw = {}
    else:
        raise ValueError("Expected either 2 or 3 dimensional data. "
                         "Got {}".format(len(data)))
    return c, labels, discrete, cmap, subplot_kw, legend


def scatter(*data, c=None, cmap=None, s=1, discrete=None,
            ax=None, legend=True, figsize=None,
            xticks=False,
            yticks=False,
            zticks=False,
            xticklabels=False,
            yticklabels=False,
            zticklabels=False,
            xlabel="PHATE1",
            ylabel="PHATE2",
            zlabel="PHATE3",
            **plot_kwargs):
    """Create a scatter plot

    Builds upon `matplotlib.pyplot.scatter` with nice defaults
    and handles categorical colors / legends better. For easy access, use
    `scatter2d` or `scatter3d`.

    Parameters
    ----------
    *data : array-like
        positional arguments containing data, one argument for each axis
        (min: 2, max: 3)
    c : list-like or None, optional (default: None)
        Color vector. Can be an array of RGBA values, or a list of discrete or
        continuous values of any data type. The values in `c` will be used to
        populate the legend / colorbar
    cmap : `matplotlib` colormap, str or None, optional (default: None)
        matplotlib colormap. If None, uses `tab20` for discrete data and
        `inferno` for continuous data
    s : float, optional (default: 1)
        Point size.
    discrete : bool or None, optional (default: None)
        States whether the data is discrete. If None, discreteness is
        detected automatically. Data containing non-numeric `c` is always
        discrete, and numeric data with 20 or less unique values is discrete.
    ax : `matplotlib.Axes` or None, optional (default: None)
        axis on which to plot. If None, an axis is created
    legend : bool, optional (default: True)
        States whether or not to create a legend. If data is continuous,
        the legend is a colorbar.
    figsize : tuple, optional (default: None)
        Tuple of floats for creation of new `matplotlib` figure. Only used if
        `ax` is None.
    xticks : True, False, or list-like (default: False)
        If True, keeps default x ticks. If False, removes x ticks.
        If a list, sets custom x ticks
    yticks : True, False, or list-like (default: False)
        If True, keeps default y ticks. If False, removes y ticks.
        If a list, sets custom y ticks
    zticks : True, False, or list-like (default: False)
        If True, keeps default z ticks. If False, removes z ticks.
        If a list, sets custom z ticks.  Only used for 3D plots
    xticklabels : True, False, or list-like (default: False)
        If True, keeps default x tick labels. If False, removes x tick labels.
        If a list, sets custom x tick labels
    yticklabels : True, False, or list-like (default: False)
        If True, keeps default y tick labels. If False, removes y tick labels.
        If a list, sets custom y tick labels
    zticklabels : True, False, or list-like (default: False)
        If True, keeps default z tick labels. If False, removes z tick labels.
        If a list, sets custom z tick labels. Only used for 3D plots
    xlabel : str or None (default : "PHATE1")
        Label for the x axis. If None, no label is set.
    ylabel : str or None (default : "PHATE2")
        Label for the y axis. If None, no label is set.
    zlabel : str or None (default : "PHATE3")
        Label for the z axis. If None, no label is set. Only used for 3D plots
    **plot_kwargs : keyword arguments
        Extra arguments passed to `matplotlib.pyplot.scatter`.
    """
    c, labels, discrete, cmap, subplot_kw, legend = _auto_params(
        data, c, discrete,
        cmap, legend)
    plot_idx = np.random.permutation(data[0].shape[0])
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize, subplot_kw=subplot_kw)
        show = True
    else:
        show = False
    if legend and not discrete:
        im = ax.imshow(np.arange(10).reshape(-1, 1),
                       vmin=np.min(c), vmax=np.max(c), cmap=cmap)
        ax.clear()
    sc = ax.scatter(*[d[plot_idx] for d in data],
                    c=c[plot_idx] if c is not None else c,
                    cmap=cmap, s=s, **plot_kwargs)

    if not xticks:
        ax.set_xticks([])
    elif xticks is True:
        pass
    else:
        ax.set_xticks(xticks)
    if not xticklabels:
        ax.set_xticklabels([])
    elif xticklabels is True:
        pass
    else:
        ax.set_xticklabels(xticklabels)
    if xlabel is not None:
        ax.set_xlabel(xlabel)

    if not yticks:
        ax.set_yticks([])
    elif yticks is True:
        pass
    else:
        ax.set_yticks(yticks)
    if not yticklabels:
        ax.set_yticklabels([])
    elif yticklabels is True:
        pass
    else:
        ax.set_yticklabels(yticklabels)
    if ylabel is not None:
        ax.set_ylabel(ylabel)

    if len(data) == 3:
        if not zticks:
            ax.set_zticks([])
        elif zticks is True:
            pass
        else:
            ax.set_zticks(zticks)
        if not zticklabels:
            ax.set_zticklabels([])
        elif zticklabels is True:
            pass
        else:
            ax.set_zticklabels(zticklabels)
        if zlabel is not None:
            ax.set_zlabel(zlabel)

    if legend:
        if discrete:
            def handle(c):
                return plt.Line2D([], [], color=c, ls="", marker="o")
            plt.legend(
                handles=[handle(sc.cmap(sc.norm(i)))
                         for i in range(len(labels))],
                labels=list(labels),
                ncol=max(1, len(labels) // 10))
        else:
            plt.colorbar(im)
    if show:
        plt.tight_layout()
        plt.show(block=False)


def scatter2d(data, **kwargs):
    """Create a 2D scatter plot

    Builds upon `matplotlib.pyplot.scatter` with nice defaults
    and handles categorical colors / legends better.

    Parameters
    ----------
    data : array-like, `phate.PHATE` or `scanpy.AnnData`
        Input data. Only the first two dimensions are used.
    **kwargs : keyword arguments
        See `phate.plot.scatter`.
    """
    data = _get_plot_data(data)
    scatter(data[:, 0], data[:, 1], **kwargs)


def scatter3d(data, **kwargs):
    """Create a 3D scatter plot

    Builds upon `matplotlib.pyplot.scatter` with nice defaults
    and handles categorical colors / legends better.

    Parameters
    ----------
    data : array-like, `phate.PHATE` or `scanpy.AnnData`
        Input data. Only the first three dimensions are used.
    **kwargs : keyword arguments
        See `phate.plot.scatter`.
    """
    data = _get_plot_data(data)
    scatter(data[:, 0], data[:, 1], data[:, 2],
            **kwargs)


def rotate_scatter3d(data,
                     filename=None,
                     azim=10,
                     interval=50,
                     frames=90,
                     ax=None,
                     figsize=None,
                     **kwargs):
    """Create a rotating 3D scatter plot

    Builds upon `matplotlib.pyplot.scatter` with nice defaults
    and handles categorical colors / legends better.

    Parameters
    ----------
    data : array-like, `phate.PHATE` or `scanpy.AnnData`
        Input data. Only the first three dimensions are used.
    filename : str, optional (default: None)
        If not None, saves a .gif or .mp4 with the output
    azim : float, optional (default: 10)
        Elevation of viewpoint from horizontal, in degrees
    interval : float, optional (default: 50)
        Number of milliseconds between frames
    frames : int, optional (default: 90)
        Total number of frames.
    ax : `matplotlib.Axes` or None, optional (default: None)
        axis on which to plot. If None, an axis is created
    figsize : tuple, optional (default: None)
        Tuple of floats for creation of new `matplotlib` figure. Only used if
        `ax` is None.
    **kwargs : keyword arguments
        See `phate.plot.scatter`.
    """
    if filename is not None:
        if not (filename.endswith(".mp4") or filename.endswith(".gif")):
            raise ValueError(
                "filename must end in .gif or .mp4. Got {}".format(filename))

    if ax is not None:
        fig, ax = plt.subplots(figsize=figsize,
                               subplot_kw={'projection': '3d'})
    else:
        fig = ax.get_figure()

    degrees_per_frame = 360.0 / frames

    def init():
        # Plot the surface.
        scatter3d(data, ax=ax, **kwargs)
        return fig

    def animate(i):
        # elevation angle : -180 deg to 180 deg
        ax.view_init(elev=-180 + i * degrees_per_frame, azim=azim)
        return fig,

    ani = mpl.animation.FuncAnimation(
        fig, animate, init_func=init,
        frames=frames, interval=interval, blit=True)

    if filename is not None:
        ani.save(filename)
    return ani
