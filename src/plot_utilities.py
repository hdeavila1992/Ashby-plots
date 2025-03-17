# -*- coding: utf-8 -*-
"""
Plot utilities script.
Contains all the misc. functions to generate the ashby plot (not related to the actual ellipses).


@author: Walgren
"""
import os

import numpy as np

import matplotlib.pyplot as plt
from matplotlib import patches
from matplotlib import colors

from src.plot_convex_hull import (
    draw_ellipses,
    draw_hull,
    )

from src.rotation_aware_annotation import RotationAwareAnnotation


def plotting_presets(figure_type:str = 'publication'):
    '''
    Creates plotting presets for font size, marker size,
    and other quality of life presets.


    Parameters
    ----------
    figure_type : str
        Type of figure you would like to create.
        Options are 'publication' or 'presentation'
        Toggles different presets like font family, font size, etc.

    Returns
    -------
    None.
    '''
    #Graphs in a separate window (run in Spyder)
    if 'SPY_PYTHONPATH' in os.environ:
        # see https://stackoverflow.com/questions/32538758/nameerror-name-get-ipython-is-not-defined
        # running inside spyder!
        #Graphs in a separate window
        from IPython import get_ipython
        get_ipython().run_line_magic('matplotlib', 'qt')
        #Graphs inline (ala Jupyter notebook)
        #get_ipython().run_line_magic('matplotlib', 'inline')
    if figure_type.lower() == 'publication':
        # Plot with serif, Times New Roman Font
        plt.rc('font', family='serif')
        plt.rc('font', serif='Times New Roman')
        plt.rcParams.update({'font.size': 10})
        plt.rc('text', usetex='True')
    elif figure_type.lower() == 'presentation':
        #Plot with sans serif, Arial font
        plt.rc('font', family='sans-serif')
        plt.rcParams.update({'font.sans-serif':'Arial'})
        plt.rcParams.update({'font.size': 18})
        plt.rc('text',usetex='False')
    else:
        raise(ValueError,'Options for plotting_presets are publication or presentation')

    # Use Latex to render all fonts (this may interfere with the svg font encoding)
    # plt.rc('text', usetex='True')
    #Use no svg font encoding such that they can be imported as text into inkscape
    # FIXME grab the stack overflow link for this.
    plt.rcParams['svg.fonttype'] = 'none'
    #Modify marker size to make them readable
    plt.rcParams['lines.markersize'] = 10


def draw_plot(
        data,
        x_axis_quantity,
        y_axis_quantity,
        ax,
        material_colors,
        data_type = 'ranges'
        ):
    '''
    Plots both the data points (either ellipses if material upper and lower
    bounds are given, or a scatter plot if single points are given) and the
    convex hull around all data points of a given category.

    Parameters
    ----------
    data : pandas dataframe
        dataframe with all material data to be plotted.
        Note that this dataframe must include the column 'Category;'
        which is case sensitive!
    x_axis_quantity : str
        quantity you would like to plot on the x-axis.
    y_axis_quantity : str
        quantity you would like to plot on the y-axis.
    ax : matplotlib.pyplot.axis
        figure axis on which you would like to plot
    material_colors : dict
        key-value pairs of categories and the desired colors
    data_type : str, optional
        Flag for whether the data is defined as ranges (i.e., upper and lower
        bounds) or as values (i.e., single values). The default is 'ranges'.

    Returns
    -------
    None.

    '''
    for category, material_data in data.groupby('Category'):

        if data_type == 'ranges':
            X = np.zeros(shape=(2*len(material_data),2))
            X[:len(material_data),1] = material_data[y_axis_quantity + ' low']
            X[:len(material_data),0] = material_data[x_axis_quantity + ' low']

            X[len(material_data):,1] = material_data[y_axis_quantity + ' high']
            X[len(material_data):,0] = material_data[x_axis_quantity + ' high']

            for i in range(len(material_data)):
                draw_ellipses(
                        x = [material_data[x_axis_quantity + ' low'].iloc[i],
                             material_data[x_axis_quantity + ' high'].iloc[i]],
                        y = [material_data[y_axis_quantity + ' low'].iloc[i],
                             material_data[y_axis_quantity + ' high'].iloc[i]],
                        plot_kwargs = {
                            'facecolor':colors.to_rgba(
                                material_colors[category],
                                alpha=0.25
                                ),
                            'edgecolor':material_colors[category]
                            },
                        ax = ax,
                        )

        elif data_type == 'values':
            X = np.zeros(shape = (len(material_data),2))
            X[:,0] = material_data[x_axis_quantity]
            X[:,1] = material_data[y_axis_quantity]

            ax.scatter(
                X[:,0],
                X[:,1],
                c=material_colors[category])

        else:
            raise(ValueError, 'Only options for data_type in draw_plot are ranges or values')


        draw_hull(
            X,
            scale = 1.1,
            padding = 'scale',
            n_interpolate = 1000,
            interpolation = 'cubic',
            ax = ax,
            plot_kwargs = {
                'color':material_colors[category],
                'alpha':0.2
                }
            )


def create_legend(
        material_classes,
        material_colors
        ):
    '''
    Creates a legend located outside the plot bounding box. Currently
    set to the top of the plot.

    Important references:
        Extracting an iterable from a pandas groupby:
            https://stackoverflow.com/questions/28844535/python-pandas-groupby-get-list-of-groups
        Manual legend creation:
            https://stackoverflow.com/questions/39500265/how-to-manually-create-a-legend
        Plotting legends outside the bounding box:
            https://stackoverflow.com/questions/4700614/how-to-put-the-legend-outside-the-plot

    Parameters
    ----------
    material_classes : Iterable list or dict_keys object
        The list of different material classes you wish to display in the
        legend. Commonly found via data.groupby("Category").groups.keys()
    material_colors : DICT
        Dictionary that references the material class to the color you
        wish to display it as.
    Returns
    -------
    None.
    '''
    handles = []
    # make a manual legend
    for material_class in material_classes:
        patch = patches.Patch(
            color = material_colors[material_class],
            label = material_class
            )
        handles.append(patch)

    # place legend outside the plot
    plt.legend(
        handles=handles,
        bbox_to_anchor = (0, 1.02, 1, 0.2),
        loc = 'lower left',
        mode = 'expand',
        borderaxespad = 0,
        ncol = 4)

def draw_guideline(
        guideline,
        ax,
        log_flag = True,
        ):
    '''
    Draws guideline for material index.

    Parameters
    ----------
    guideline : dict
        power : float
            power of the material index (and thus the guideline)
            e.g., 1 for E/rho, 3 for E^(1/3)/rho.
        x_lim : list
            x-axis limits ([low, high])
        y_intercept : float optional
            y_intercept of the guideline.
            This gets tricky if your x- and y-axis limits do not include 1.0.
            The default is 1.0.
        string : string to display and label the guideline
        string_position : location to start the string
    ax : matplotlib axis object
        The current plotting axis.
    log_flag : bool
        Flag to determine whether the logarithmic equation for a line
        will be used or a standard equation.
        The default is True.

    Returns
    -------
    None.
    '''
    power = guideline['power']
    x_lim = guideline['x_lim']
    y_intercept = guideline['y_intercept']
    string = guideline['string']
    string_position = guideline['string_position']


    # Create linspace to span x-limits
    num_points = 5
    x_values = np.linspace(x_lim[0],x_lim[1],num_points)
    y_values = np.zeros(shape = num_points)

    #Create the line
    for i in range(len(x_values)):
        if log_flag:
            y_values[i] = y_intercept*x_values[i]**power
        else:
            y_values[i] = power*x_values[i] + y_intercept

    ax.plot(
        x_values,
        y_values,
        'k--',
        )

    #Create an annotation on the line to denote the equation
    # The spacing of this line takes a bit (xytext variable),
    # because the units are 1/72 in
    # FIXME generalize the xytext placement?
    RotationAwareAnnotation(
        string,
        xy=string_position,
        p=(x_values[3], y_values[3]),
        pa = (x_values[0], y_values[0]),
        ax=ax,
        xytext=(0,0),
        textcoords="offset points",
        va="top"
        )


def common_definitions():
    '''
    Creates two dictionaries for colors and units (labeling).
    Add the units that you wish to see in the world (Ghandhi, 1913)

    Returns
    -------
    units : dict
        Dictionary with key-value pairs for each quantity and its
        respective SI unit. Keys are case sensitive.
        Could maybe be a way to just grab this
        from a preexisting python package.

    material_colors : dict
        key-value pairs for each category of material and the respective
        color in which you wish to see it plotted. Keys are case sensitive.
    '''
    # common units for labeling the axes. These are case sensitive.
    units = {
        'Density': 'kg/m$^3$',
        'Tensile Strength': 'MPa',
        "Young Modulus": 'GPa',
        "Fracture Toughness": r"MPa$\sqrt{\text{m}}$",
        "Thermal Conductivity": r"W/m$\cdot$K",
        "Thermal expansion": "1$^-6$/m",
        "Resistivity": r"$\Omega \cdot$m",
        "Poisson": "-",
        "Poisson difference": "-",
        }

    material_colors = {
        'Foams':'blue',
        'Elastomers':'orange',
        'Natural materials':'green',
        'Polymers':'red',
        'Nontechnical ceramics':'purple',
        'Composites':'Brown',
        'Technical ceramics':'pink',
        'Metals':'grey',
        }

    return units, material_colors
