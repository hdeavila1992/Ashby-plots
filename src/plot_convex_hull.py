# -*- coding: utf-8 -*-
"""
Created on Fri Apr 12 16:49:38 2024

@author: Walgren
"""
import sklearn.preprocessing
import sklearn.pipeline
import scipy.spatial
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import patches
import matplotlib.colors as colors



def log_transform(x):
    return np.log(x)


def inv_log_transform(x):
    return np.exp(x)


def draw_ellipses(
        x,
        y,
        ax,
        data_type = 'ranges',
        scale = 1.0,
        plot_kwargs = None,
        ):

    # x = np.log(x)
    # y = np.log(y)

    # FIXME add log flag
    center_x = (x[0] + x[1])/2.0
    center_y = (y[0] + y[1])/2.0

    # log_center_x = logarithmic_mean(x)
    # log_center_y = logarithmic_mean(y)

    r_x = (x[1] - x[0])
    r_y = (y[1] - y[0])
    
    if data_type == 'values':
        
        #scale the ellipse somewhat larger (padding)
        r_x = scale*r_x
        r_y = scale*r_y
        
        plot_kwargs['facecolor'] = colors.to_rgba(
            plot_kwargs['color'],
            alpha=0.25
            )
        plot_kwargs['edgecolor'] = plot_kwargs['color']
        
        del plot_kwargs['color']
        del plot_kwargs['alpha']
        

        if r_y == 0:
            angle = 0
        elif r_x == 0:
            angle = 180
        elif r_x > r_y:
            angle = np.rad2deg(np.arctan((r_y)/(r_x)))
        else:
            angle = np.rad2deg(np.arctan((r_x)/(r_y)))
    else: 
        angle = 0

    #FIXME add log flag
    # ell_offset = ScaledTranslation(log_center_x, log_center_y,ax.transScale)
    # ell_offset = ScaledTranslation(center_x, center_y,ax.transScale)
    # ell_tform = ell_offset + ax.transLimits + ax.transAxes

    # ell_scaling = ax.transScale.transform((r_x, r_y))



    ellipse = patches.Ellipse(
        # xy = (0, 0),
        xy = (center_x,center_y),
        width = r_x,
        height = r_y,
        angle = angle,
        **plot_kwargs,
        # width = r_x,
        # height = r_y,
        # facecolor = colors.to_rgba(color,alpha=0.25),
        # edgecolor = color,
        # transform=ell_tform,
        )


# # Create the ellipse centred on the origin, apply the composite tform
# ax.add_patch(Ellipse(xy=(0, 0), width=0.2, height=0.5, color="grey", fill=False, lw=1, zorder=5, )
    ax.add_patch(ellipse)


def calculate_hull(
        X, 
        scale=1.1, 
        padding="scale", 
        n_interpolate=100, 
        interpolation="quadratic", 
        return_hull_points=False):
    """
    Calculates a "smooth" hull around given points in `X`.
    The different settings have different drawbacks but the given defaults work reasonably well.
    Parameters
    ----------
    X : np.ndarray
        2d-array with 2 columns and `n` rows
    scale : float, optional
        padding strength, by default 1.1
    padding : str, optional
        padding mode, by default "scale"
    n_interpolate : int, optional
        number of interpolation points, by default 100
    interpolation : str or callable(ix,iy,x), optional
        interpolation mode, by default "quadratic_periodic"

    Inspired by: https://stackoverflow.com/a/17557853/991496
    """
    
    if padding == "scale":

        # scaling based padding
        scaler = sklearn.pipeline.make_pipeline(
            # sklearn.preprocessing.MaxAbsScaler()
            # sklearn.preprocessing.RobustScaler(quantile_range = (25,75))
            # sklearn.preprocessing.PowerTransformer(method='box-cox'),
            # TODO: make a flag based on log-log scaling?
            sklearn.preprocessing.FunctionTransformer(log_transform),
            sklearn.preprocessing.MinMaxScaler(feature_range = (0,1)),
            sklearn.preprocessing.StandardScaler(with_std=False),
            )
        points_scaled = scaler.fit_transform(X) * scale
        
        points_scaled = points_scaled[~np.isnan(points_scaled[:, 0])]
        points_scaled = points_scaled[~np.isnan(points_scaled[:, 1])]

        hull_scaled = scipy.spatial.ConvexHull(points_scaled, incremental=True)
        hull_points_scaled = points_scaled[hull_scaled.vertices]
        
        #old code (modified for log scaling)
        hull_points= np.concatenate([hull_points_scaled,hull_points_scaled[:1]])
        
        #stackoverflow code
        # hull_points = scaler.inverse_transform(hull_points_scaled)
        # hull_points = np.concatenate([hull_points, hull_points[:1]])
    
    elif padding == "extend" or isinstance(padding, (float, int)):
        # extension based padding
        # TODO: remove?
        if padding == "extend":
            add = (scale - 1) * np.max([
                X[:,0].max() - X[:,0].min(), 
                X[:,1].max() - X[:,1].min()])
        else:
            add = padding
        points_added = np.concatenate([
            X + [0,add], 
            X - [0,add], 
            X + [add, 0], 
            X - [add, 0]])
        hull = scipy.spatial.ConvexHull(points_added)
        hull_points = points_added[hull.vertices]
        hull_points = np.concatenate([hull_points, hull_points[:1]])
    else:
        raise ValueError(f"Unknown padding mode: {padding}")
    
    # number of interpolated points
    nt = np.linspace(0, 1, n_interpolate)
    
    x, y = hull_points[:,0], hull_points[:,1]
    
    # ensures the same spacing of points between all hull points
    t = np.zeros(x.shape)
    t[1:] = np.sqrt((x[1:] - x[:-1])**2 + (y[1:] - y[:-1])**2)
    t = np.cumsum(t)
    t /= t[-1]

    # interpolation types
    if interpolation is None or interpolation == "linear":
        x2 = scipy.interpolate.interp1d(t, x, kind="linear")(nt)
        y2 = scipy.interpolate.interp1d(t, y, kind="linear")(nt)
    elif interpolation == "quadratic":
        x2 = scipy.interpolate.interp1d(t, x, kind="quadratic")(nt)
        y2 = scipy.interpolate.interp1d(t, y, kind="quadratic")(nt)

    elif interpolation == "quadratic_periodic":
        x2 = scipy.interpolate.splev(nt, scipy.interpolate.splrep(t, x, per=True, k=4))
        y2 = scipy.interpolate.splev(nt, scipy.interpolate.splrep(t, y, per=True, k=4))
    
    elif interpolation == "cubic":
        x2 = scipy.interpolate.CubicSpline(t, x, bc_type="periodic")(nt)
        y2 = scipy.interpolate.CubicSpline(t, y, bc_type="periodic")(nt)
    else:
        x2 = interpolation(t, x, nt)
        y2 = interpolation(t, y, nt)
    
    X_hull = np.concatenate([x2.reshape(-1,1), y2.reshape(-1,1)], axis=1)
    
    
    if padding == 'scale':
        X_hull = scaler.inverse_transform(X_hull)
        
        X_hull = inv_log_transform(X_hull)
        
        X_hull = X_hull[~np.isnan(X_hull).any(axis=1)]
        
    if return_hull_points:
        return X_hull, hull_points
    else:
        return X_hull


def draw_hull(
        X, 
        scale=1.1, 
        padding="scale", 
        n_interpolate=1000, 
        interpolation="quadratic_periodic",
        plot_kwargs=None, 
        ax=None):
    """Uses `calculate_hull` to draw a hull around given points.

    Parameters
    ----------
    X : np.ndarray
        2d-array with 2 columns and `n` rows
    scale : float, optional
        padding strength, by default 1.1
    padding : str, optional
        padding mode, by default "scale"
    n_interpolate : int, optional
        number of interpolation points, by default 100
    interpolation : str or callable(ix,iy,x), optional
        interpolation mode, by default "quadratic_periodic"
    plot_kwargs : dict, optional
        `matplotlib.pyplot.plot` kwargs, by default None
    ax : `matplotlib.axes.Axes`, optional
        [description], by default None
    """

    if plot_kwargs is None:
        plot_kwargs = {}
        
    if len(X) < 3: #if you have fewer than three data points, you cannot form a convex hull
    
        draw_ellipses(
            x = X[:,0],
            y = X[:,1],
            ax = ax,
            data_type = 'values',
            scale = scale,
            plot_kwargs = plot_kwargs
            )
    else:
        X_hull = calculate_hull(
            X,
            scale=scale,
            padding=padding,
            n_interpolate=n_interpolate,
            interpolation=interpolation
            )
        # ell_tform = ax.transScale + ax.transLimits + ax.transAxes
        
        # new_hull = ell_tform.transform(X_hull)
        
        if ax is None:
            ax= plt.gca()
            
        plt.fill(
            X_hull[:,0],
            X_hull[:,1],
            **plot_kwargs,
            )
        
        try: 
            del plot_kwargs['hatch']
        except:
            pass
        
        plt.plot(
            X_hull[:,0],
            X_hull[:,1],
            **plot_kwargs
            )



def draw_rounded_hull(X, padding=0.1, line_kwargs=None, ax=None):
    """Plots a convex hull around points with rounded corners and a given padding.

    Parameters
    ----------
    X : np.array
        2d array with two columns and n rows
    padding : float, optional
        padding between hull and points, by default 0.1
    line_kwargs : dict, optional
        line kwargs (used for `matplotlib.pyplot.plot` and `matplotlib.patches.Arc`), by default None
    ax : matplotlib.axes.Axes, optional
        axes to plat on, by default None
    """

    default_line_kwargs = dict(
        color="black",
        linewidth=1
    )
    if line_kwargs is None:
        line_kwargs = default_line_kwargs
    else:
        line_kwargs = {**default_line_kwargs, **line_kwargs}

    if ax is None:
        ax = plt.gca()

    hull = scipy.spatial.ConvexHull(X)
    hull_points = X[hull.vertices]

    hull_points = np.concatenate([hull_points[[-1]], hull_points, hull_points[[0]]])

    diameter = padding * 2
    for i in range(1, hull_points.shape[0] - 1):

        # line
        
        # source: https://stackoverflow.com/a/1243676/991496
        
        norm_next = np.flip(hull_points[i] - hull_points[i + 1]) * [-1, 1]
        norm_next /= np.linalg.norm(norm_next)

        norm_prev = np.flip(hull_points[i - 1] - hull_points[i]) * [-1, 1]
        norm_prev /= np.linalg.norm(norm_prev)

        # plot line
        line = hull_points[i:i+2] + norm_next * diameter / 2
        ax.plot(line[:,0], line[:,1], **line_kwargs) 

        # arc

        angle_next = np.rad2deg(np.arccos(np.dot(norm_next, [1,0])))
        if norm_next[1] < 0:
            angle_next = 360 - angle_next

        angle_prev = np.rad2deg(np.arccos(np.dot(norm_prev, [1,0])))
        if norm_prev[1] < 0:
            angle_prev = 360 - angle_prev
            
            
        ell_tform = ax.transScale + ax.transLimits + ax.transAxes

        arc = patches.Arc(
            hull_points[i], 
            diameter, diameter,
            angle=0,
            fill=False,
            theta1=angle_prev,
            theta2=angle_next,
            transform = ell_tform,
            **line_kwargs)

        ax.add_patch(arc)


if __name__ == '__main__':

    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib import patches

    np.random.seed(42)
    
    
    
    # sample data for technical ceramics
    # X = np.zeros(shape = (10,2))
    # X[:,1] = np.array([400, 280, 300, 215, 600, 472, 310, 460, 413,720]).transpose()
    # X[:,0] = np.array([2350, 3000, 3000, 3500, 15300, 2550, 3290, 3210, 3980, 15900]).transpose()
    
    # sample data for foams 
    X = np.zeros(shape = (12,2))
    X[:,1] = np.array([0.0003,0.023,0.001,0.004,0.08,0.2,0.001,0.08,0.003,0.012,0.2,0.48]).transpose()
    X[:,0] = np.array([16,36,38,75,78,170,35,70,70,115,165,470]).transpose()
    
    
    
    fig, ax = plt.subplots(1,1, figsize=(5,5))
    ax.scatter(X[:,0], X[:,1])
    # draw_rounded_hull(X, padding=0.1, ax = ax)
    draw_hull(
        X,
        ax = ax,
        scale = 1.1,
        padding = 'scale',
        interpolation = 'cubic'
        )
    ax.loglog()
    # ax.set(xlim=[-1,2], ylim= [-1,2])
    # fig.savefig("_out/test.png")