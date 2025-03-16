'''
plot_ashby.py

Last updated: 6/19/2024

This script will plot various material properties in an 'Ashby-type' way (
i.e., convex hulls surrounding points of certain classes). 

Input file format: one excel file, with either material property ranges or 
single values defined. 

Dependencies:
    files: plot_convex_hull.py
           rotation_aware_annotation
    python modules:
        os (pre-installed)
        pandas
        numpy
        matplotlib
        scipy
        sklearn

'''
import os

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.colors as colors

from rotation_aware_annotation import RotationAwareAnnotation

from plot_convex_hull import (
    draw_ellipses,
    draw_hull,
    )

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
        # see: https://stackoverflow.com/questions/32538758/nameerror-name-get-ipython-is-not-defined
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

    return

def logarithmic_mean(x):
    '''
    Calculates the logarithmic mean of the array 'x'
    Holdover function from trying to manipulate the
    ellipses into log-log space; may not be needed.
    Kept here in case someone has an epiphany.

    Parameters
    ----------
    x : np.array
        n x 1 array to calculate the logarithmic mean

    Returns
    -------
    flt
        logathmic mean of array x.

    '''
    if np.mean(x) == np.array(x).all():
        return x
    else:
        return (x[1] - x[0])/(np.log(x[1]) - np.log(x[0]))


def draw_guideline(
        guideline,
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
        if log_flag == True:
            y_values[i] = y_intercept*x_values[i]**power
        else:
            y_values[i] = power*x_values[i] + y_intercept

    line, = ax.plot(
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
    
    material_colors = {
        'Foams':'grey',
        'Elastomers':'grey',
        'Natural materials':'grey',
        'Polymers':'grey',
        'Nontechnical ceramics':'grey',
        'Composites':'grey',
        'Technical ceramics':'grey',
        'Metals':'grey',
        }

    return units, material_colors


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

            # for i in range(len(material_data)):
            #     draw_ellipses(
            #             x = [material_data[x_axis_quantity + ' low'].iloc[i], material_data[x_axis_quantity + ' high'].iloc[i]],
            #             y = [material_data[y_axis_quantity + ' low'].iloc[i], material_data[y_axis_quantity + ' high'].iloc[i]],
            #             plot_kwargs = {
            #                 'facecolor':colors.to_rgba(
            #                     material_colors[category],
            #                     alpha=0.25
            #                     ),
            #                 'edgecolor':material_colors[category]
            #                 },
            #             ax = ax,
            #             )

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
        print(material_class)
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


if __name__ == '__main__':
    #%% USER INPUTS (everything you will need to change *should* be here)
    # FIXME To-do:
    '''
        # Error handling/format checking for:
        #   file type
        # Create inputs for:
            # guideline power (figure out what to call that)
            # guideline x_limits and y_intercept
            # guideline string
    '''

    # file with all of your material data (must be xlsx)
    file_name = 'common_material_properties.xlsx'

    data_type = 'ranges' # type of material data ('ranges' or single 'values')

    figure_type = 'presentation' #options are 'publication' or 'presentation'
    figure_size = (9,7) #width, height, in inches

    # quantities you would like to plot
    x_axis_quantity = 'Density'
    # x_axis_quantity = 'Young Modulus'
    y_axis_quantity = "Poisson difference"
    # y_axis_quantity = 'Young Modulus'

    # x- and y-axes limits
    x_lim = [10, 30000] #min, max
    # x_lim = [1E-4,1E3]
    y_lim = [0.5,1.1] #min, max
    # y_lim = [0.5,1.5]
    # y_lim = [1E-4,1E3]

    #Flag to plot in log-log space
    log_flag = True

    # Guideline setup
    guideline_flag = False

    if guideline_flag == True:
        guideline = {
            'power':1, #power to plot the guideline on (e.g., 1/3, 1)
            # 'x_lim':[1E1, 1E5], #x-limits of the guideline (not necessarily the figure x limits)
            'x_lim':[1E1,1E5],
            # 'string':r"$\frac{E^{1/3}}{\rho} \equiv$ constant", #string to display
            'string':r"$\frac{1}{(1+\nu)\rho} \equiv k $",
            'y_intercept':0.005, #y-intercept of the guideline
            # 'y_intercept':1E-10,
            'string_position': (60,0.51), #(75,2E-4)
            }


    #%% General setup
    # Create dictionaries with common units bases etc.
    units, material_colors = common_definitions()

    # Set up baseline plot formatting
    plotting_presets(figure_type)

    #load data
    data = pd.read_excel(
        file_name
        )

    # Error handling about the colors dictionary
    if set(data.groupby('Category').groups) > set(material_colors):
        raise ValueError('You have material categories that have not been assigned \
a color. Please add a color to the material_colors dictionary (common_definitions function).')

    #%% Figure manipulation

    #Create figure
    fig, ax = plt.subplots(1,1, figsize=figure_size)

    # set x- and y-labels
    try:
        if y_axis_quantity == 'Poisson difference':
            y_label = r'Hyperbolic Poisson Ratio $\frac{1}{1+\nu}$, '+ units[y_axis_quantity]
        else:
            y_label = y_axis_quantity + ', ' + units[y_axis_quantity]


        ax.set_xlabel(x_axis_quantity + ', ' + units[x_axis_quantity])
        ax.set_ylabel(y_label)
    except:
        raise ValueError("Could not set correct x- and y-labels. \
Make sure your x_axis_quantity and y_axis_quantity \
have equivalent key-value pairs in the units dictionary (common_definitions function).")

    #set axes limits
    ax.set(xlim=x_lim, ylim= y_lim)

    #toggle log-log plot
    if log_flag == True:
        ax.loglog()

    # set x-scale to logarithmic
    # ax.set_xscale('log')

    #add grid lines
    # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.grid.htmls
    ax.grid(
        which = 'major',
        axis = 'both',
        linestyle = '-.',
        zorder = 0.5)

    #%% Data plotting
    if guideline_flag == True:
        #draw guideline
        draw_guideline(
                guideline,
                log_flag = log_flag,
                )

    if (x_axis_quantity == 'Poisson difference') or (y_axis_quantity == 'Poisson difference'):

        data['Poisson difference high'] = 1/(1+data['Poisson low'])
        data['Poisson difference low'] = 1/(1+data['Poisson high'])

    draw_plot(
            data,
            x_axis_quantity,
            y_axis_quantity,
            ax,
            material_colors,
            data_type = data_type,
            )

    # create_legend(
    #         material_classes = data.groupby('Category').groups.keys(),
    #         material_colors = material_colors,
    #         )
    
    
    # plot discrete materials 
    marker_size = 500
    
    foam = {
        'E':0.124E-3,
        'nu':0.45,
        'rho':400,
        }
    
    PLA = {
        'E':2.009,
        'nu':0.3,
        'rho':1300,
        }
    
    ax.scatter(
        foam['rho'],
        # foam['E'],
        1/(1+foam['nu']),
        c = 'b',
        edgecolors ='k',
        marker = '*',
        s = marker_size,
        )
    
    ax.scatter(
        PLA['rho'],
        # PLA['E'],
        1/(1+PLA['nu']),
        c = 'r',
        edgecolors ='k',
        marker = '*',
        s = marker_size,
        )
    
    
    from unit_cell_data.plot_data import create_baseline_materials
    stiff, compliant_dense, compliant_foam, null_material = create_baseline_materials()
    
    #Infill material in question 
    # Options are 'foamed elastomer', 'dense elastomer', or 'none'
    material = 'foamed elastomer'
    
    #Infill material in question 
    # Options are 'foamed elastomer', 'dense elastomer', or 'none'
    material = 'foamed elastomer'
    
    #File names 
    #DV_file_names = all input variables (i.e., geometric parameterization)
    #OV_file_names = all output variables (engineering constants)
    OV_file_names = ['Chiral_All_outputs.csv','Lattice_All_outputs.csv','Re-entrant_All_outputs.csv']
    DV_file_names = ['Chiral_All_inputs.csv','Lattice_All_inputs.csv','Re-entrant_All_inputs.csv'] 
    
    
    # Concatenate all of the OV files and DV files together in one Pandas dataframe.
    counter = 0
    
    for OV_file_name, DV_file_name in zip(OV_file_names,DV_file_names):
        OV_file = os.path.join(os.getcwd(),'unit_cell_data',OV_file_name)
        DV_file = os.path.join(os.getcwd(),'unit_cell_data',DV_file_name)
        if counter == 0:
            OV_data_frame = pd.read_csv(
                    OV_file
                    )
            DV_data_frame = pd.read_csv(
                DV_file
                )
        else:
            OV_data_frame = pd.concat(
                [
                OV_data_frame,
                pd.read_csv(
                    OV_file
                    )
                ]
                )
            DV_data_frame = pd.concat(
                [
                DV_data_frame,
                pd.read_csv(
                    DV_file
                    )
                ]
                )
        counter +=1
    
    # Merge all of the data into one master dataframe. 
    # This is definitely inefficient for a lot of the stuff that we will do with visualization, 
    # but it's nice to have it all in one place. 
    merged_data = OV_data_frame.merge(DV_data_frame,on=['ID','Unit Cell'])
        
    # Then, apply an orthonormal rotation to the data to double the amount of points. 
    from unit_cell_data.plot_data import orthonormal_rotation
    merged_data = orthonormal_rotation(merged_data)
    
    # Create a copy of this dataframe, and do some manipulation to clean up the fields.
    data_to_plot = merged_data.copy()
    data_to_plot = data_to_plot[data_to_plot['Infill material'] == material]
    
    data_to_plot = data_to_plot.reset_index(drop=True)
    
    # Organize the material data to plot the correct reference properties. 
    if material == 'foamed elastomer':
        compliant_material = compliant_foam 
    elif material == 'dense elastomer':
        compliant_material = compliant_dense
    elif material == 'none':
        compliant_material = null_material
        
    
    #Create density field 
    data_to_plot['Density'] = 1E6*(data_to_plot['Stiff volume']*stiff['rho'] + \
        (data_to_plot['Total volume']-data_to_plot['Stiff volume'])*compliant_material['rho'])/data_to_plot['Total volume']
        
    # Create poisson difference field
    data_to_plot['Poisson difference'] = 1/(1+data_to_plot['Nu12'])
    

    #Find outliers
    outlier_data = merged_data[(merged_data['E1'] < compliant_material['E']) | (merged_data['E2'] < compliant_material['E'])]
    outlier_data = outlier_data[outlier_data['Infill material'] == compliant_material['name']]
    
    #Delete outliers from data set
    data_to_plot = data_to_plot[(data_to_plot['E1'] > compliant_material['E']) & (data_to_plot['E2'] > compliant_material['E'])]
    
    

    
    colors = {'Chiral':'r',
              'Lattice':'b',
              'Re-entrant':'g'}
    
    if y_axis_quantity == 'Young Modulus':
        y_axis_quantity = 'E1'
    if x_axis_quantity == 'Young Modulus':
        x_axis_quantity = 'E1'
        
    X = np.zeros(shape = (len(data_to_plot),2))
    X[:,0] = data_to_plot[x_axis_quantity]
    X[:,1] = data_to_plot[y_axis_quantity] #*1E-3
    
    draw_hull(
        X,
        scale = 1.1,
        padding = 'scale',
        n_interpolate = 1000,
        interpolation = 'cubic',
        ax = ax,
        plot_kwargs = {
            'color':'b',#'#abefffff',#'#99999bff',
            'alpha':0.75,
            'hatch':'+'
            }) 
    
    # for (unit_cell_type, d) in data_to_plot.groupby('Unit Cell'):
        
    #     X = np.zeros(shape = (len(d),2))
    #     X[:,0] = d[x_axis_quantity]
    #     X[:,1] = d[y_axis_quantity]*1E-3
        
        
        
    #     draw_hull(
    #         X,
    #         scale = 1.1,
    #         padding = 'scale',
    #         n_interpolate = 1000,
    #         interpolation = 'cubic',
    #         ax = ax,
    #         plot_kwargs = {
    #             'color':colors[unit_cell_type],
    #             'alpha':0.2
    #             }
    #         )
    
        # ax.scatter(
            # d[x_axis_quantity],
            # d[y_axis_quantity],
            # c = colors[unit_cell_type]
            # )
    