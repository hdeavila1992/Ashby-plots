# -*- coding: utf-8 -*-
"""
Unit cell data plotting

This script plots scatter plot matrices of all engineering constants, 
color-coded with respect to unit cell type. 

This script reads in all of the OV and DV files and converts everything to 
a handful of pandas dataframes. Note that the files must be in the same 
directory as this script. 
"""
import pickle
import os
import pandas as pd
import numpy as np

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patches as patches

import seaborn as sns

def plotting_presets():
    '''
    Creates plotting presets for font size, marker size,
    and other quality of life presets.

    Returns
    -------
    None.

    '''
    #Graphs in a separate window
    get_ipython().run_line_magic('matplotlib', 'qt')
    #Graphs inline (ala Jupyter notebook)
    #get_ipython().run_line_magic('matplotlib', 'inline')
    plt.rc('font', family='serif') 
    plt.rc('font', serif='Times New Roman') 
    plt.rc('text', usetex='True') 
    plt.rcParams.update({'font.size': 12})
    plt.rcParams['svg.fonttype'] = 'none'
    
    plt.rcParams['lines.markersize'] = 10
    
    mpl.rcParams["scatter.edgecolors"] = 'face'
    
    return 


def orthonormal_rotation(data_frame):
    '''
    Apply an orthonormal rotation to the dataset. 
    E_1 = E_2, E_2 = E_1, nu_12 = nu_21*E_1/E_2
    
    This doubles the amount of data from a single dataset.
    '''
    rotated_data_frame = data_frame.copy()

    rotated_data_frame.rename(
        columns={
            'E1':'E2',
            'E2':'E1',
            },
        inplace=True
        )
    
    rotated_data_frame['Nu12'] = rotated_data_frame['Nu12']*rotated_data_frame['E1']/rotated_data_frame['E2']
    
    data_frame = pd.concat(
        [data_frame,rotated_data_frame],
        ignore_index=True,
        axis=0,
        )
    
    return data_frame 


def create_baseline_materials():
    '''
    Creates dictionarys with baseline material properties.
    This is nice to contextualize where the unit cell properties 
    lie in the space bounded by both constituent materials.

    Returns
    -------
    stiff : DICT
        3D printed PLA
    compliant_dense : DICT
        Dense elastomer infill (Mold Star 30)
    compliant_foam : DICT
        Foamed elastomer infill (Soma Foama 25)
    null_material : DICT
        No infill material
    '''
    stiff = {
        'E' : 2.009E3,
        'rho' : 1300E-6,
        'nu' : 0.3,
        }

    compliant_dense = {
        'E' : 1.07,
        'rho' : 970E-6,
        'nu' : 0.49,
        'name':'dense elastomer'
        }
    
    compliant_foam = {
        'E': 0.124,
        'rho': 400E-6, #fix this later. 
        'nu': 0.45,
        'name':'foamed elastomer'
        }
    
    null_material = {
        'E': 0,
        'rho': 0,
        'nu': 0,
        'G' : 0,
        'name':'none'}
    
    for material_dict in [stiff, compliant_dense, compliant_foam]:
        material_dict['G'] = material_dict['E']/(2*(1+material_dict['nu']))
    return stiff, compliant_dense, compliant_foam, null_material

if __name__ == "__main__":
    plotting_presets()
    
    stiff, compliant_dense, compliant_foam, null_material = create_baseline_materials()
    
    #Infill material in question 
    # Options are 'foamed elastomer', 'dense elastomer', or 'none'
    material = 'foamed elastomer'
    
    manufacturing_constraints = {
        'flag': True, #flag to plot manufacturing constraints as gray.
        'field':'Strut thickness [mm]', #field to apply manufacturing constraints to
        'value':0.5,
        }
    
    #File names 
    #DV_file_names = all input variables (i.e., geometric parameterization)
    #OV_file_names = all output variables (engineering constants)
    OV_file_names = ['Chiral_All_outputs.csv','Lattice_All_outputs.csv','Re-entrant_All_outputs.csv']
    DV_file_names = ['Chiral_All_inputs.csv','Lattice_All_inputs.csv','Re-entrant_All_inputs.csv'] 
    
    
    # Concatenate all of the OV files and DV files together in one Pandas dataframe.
    counter = 0
    
    for OV_file_name, DV_file_name in zip(OV_file_names,DV_file_names):
        OV_file = os.path.join(os.getcwd(),OV_file_name)
        DV_file = os.path.join(os.getcwd(),DV_file_name)
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
    merged_data = orthonormal_rotation(merged_data)
    
    # Create a copy of this dataframe, and do some manipulation to clean up the fields.
    data_to_plot = merged_data.copy()
    data_to_plot = data_to_plot[data_to_plot['Infill material'] == material]
    
    data_to_plot = data_to_plot.reset_index(drop=True)
    
    
    #Create density field 
    data_to_plot['Density'] = (data_to_plot['Stiff volume']*stiff['rho'] + \
        (data_to_plot['Total volume']-data_to_plot['Stiff volume'])*compliant_dense['rho'])/data_to_plot['Total volume']
    
        
    #Drop unneccessary columns
    plotting_data_frame = data_to_plot.drop(['ID','Error','E3','Nu13','Nu23','G13','G23',
                                           'Stiff volume','Total volume','Infill material'],
                                          axis=1)
    
    # Apply manufacturing constraints
    # df.loc[df['Time'].str[:2] == '02', 'Value'] = 30
    plotting_data_frame.loc[plotting_data_frame['Strut thickness [mm]'] < 0.5, 'Unit Cell'] = 'Violated'
    
    
    # Only plot the 2D properties. If you'd like to plot more (i.e., for 3D), add the keys here
    plotting_data_frame = plotting_data_frame[['Unit Cell','E1','E2','G12',"Nu12"]]
    
    colors = {'Chiral':'r',
              'Lattice':'b',
              'Re-entrant':'g',
              'Violated':'grey'
              }
    
    
    
    
    
    
    
    # Organize the material data to plot the correct reference properties. 
    if material == 'foamed elastomer':
        compliant_material = compliant_foam 
    elif material == 'dense elastomer':
        compliant_material = compliant_dense
    elif material == 'none':
        compliant_material = null_material
        
    #Find outliers
    outlier_data = merged_data[(merged_data['E1'] < compliant_material['E']) | (merged_data['E2'] < compliant_material['E'])]
    outlier_data = outlier_data[outlier_data['Infill material'] == compliant_material['name']]
    
    #Delete outliers from data set
    plotting_data_frame = plotting_data_frame[(plotting_data_frame['E1'] > compliant_material['E']) & (plotting_data_frame['E2'] > compliant_material['E'])]
    
    

    
    # Create scatterplot matrix figure
    fig, axes = plt.subplots(4,4,sharex='col')
    
    for i, axs in enumerate(axes):
        for j, ax in enumerate(axs):
            if i == j:
                if plotting_data_frame.columns[i+1] == 'Nu12':
                    log_flag = False
                else:
                    log_flag = True
                
                sns.kdeplot(
                    data=plotting_data_frame,
                    x=plotting_data_frame.columns[i+1],
                    hue='Unit Cell',
                    fill=True,
                    legend=False,
                    palette=colors,
                    cut=0,
                    ax=ax,
                    log_scale = log_flag)
                
                ax.set_ylabel('')
                if i < 3:
                    ax.set_xlabel("")
                    
                ax.yaxis.set_visible(False)
                
                # lower_x_bound = np.nanmin(plotting_data_frame[plotting_data_frame.columns[i+1]])
                # upper_x_bound = np.nanmax(plotting_data_frame[plotting_data_frame.columns[i+1]])
                
                # ax.set_xlim(left=lower_x_bound,right=upper_x_bound)
                
                
            elif i < j:
                ax.set_visible(False)
                
            else:
                if plotting_data_frame.columns[i+1] == 'Nu12': #y
                    y_log_flag = False
                else:
                    y_log_flag = True
                    
                if plotting_data_frame.columns[j+1] == 'Nu12': #x
                    x_log_flag = False
                else:
                    x_log_flag = True
                
                
                
                sns.scatterplot(
                    data=plotting_data_frame,
                    x=plotting_data_frame.columns[j+1],
                    y=plotting_data_frame.columns[i+1],
                    hue='Unit Cell',
                    legend=False,
                    palette=colors,
                    ax=ax,
                    s = 7.5
                    )
                

                
                if x_log_flag == True:
                    ax.set_xscale('log')
                if y_log_flag == True:
                    ax.set_yscale('log')
                
                if j > 0:
                    ax.set_ylabel("")
                    
                if i < 3:
                    ax.set_xlabel("")
                    
                    
                # lower_x_bound = np.nanmin(plotting_data_frame[plotting_data_frame.columns[j+1]])
                # upper_x_bound = np.nanmax(plotting_data_frame[plotting_data_frame.columns[j+1]])
                # lower_y_bound = np.nanmin(plotting_data_frame[plotting_data_frame.columns[i+1]])
                # upper_y_bound = np.nanmax(plotting_data_frame[plotting_data_frame.columns[i+1]])
                
                # ax.set_xlim(left=lower_x_bound,right=upper_x_bound)
                # ax.set_ylim(bottom=lower_y_bound,top=upper_y_bound)
                    
    axes_labels = ["$E_1$ [MPa]","$E_2$ [MPa]","$G_{12}$ [MPa]","$\\nu_{12}$ [-]"]
    
    
    columns = ['E1','E2','G12',"Nu12"]
    
    for i, axs in enumerate(axes):
        for j, ax in enumerate(axs):
            if j == 0:
                ax.yaxis.label.set_rotation(90)
                ax.set_ylabel(axes_labels[i])
            if i == 3:
                ax.set_xlabel(axes_labels[j])
                
            if i < 3:
                ax.xaxis.set_visible(False)
                
            if j > 0:
                ax.yaxis.set_visible(False)
                
            if i != j:
                ax.scatter(
                    data_to_plot[(data_to_plot['Unit Cell'] == 'Re-entrant') & (data_to_plot['ID'] == 152)][columns[j]].iloc[0],
                    data_to_plot[(data_to_plot['Unit Cell'] == 'Re-entrant') & (data_to_plot['ID'] == 152)][columns[i]].iloc[0],
                    c = 'y',
                    marker = '*',
                    edgecolors = 'k',
                    s = 200
                    )
                    
                
    axes[1,0].plot(stiff['E'],stiff['E'],'*',color='gray')
    axes[1,0].plot(compliant_material['E'],compliant_material['E'],'*',color='cyan')
    
    
    axes[2,0].plot(stiff['E'],stiff['G'],'*',color='gray')
    axes[2,0].plot(compliant_material['E'],compliant_material['G'],'*',color='cyan')
    
    
    
    axes[3,0].plot(stiff['E'],stiff['nu'],'*',color='gray')
    axes[3,0].plot(compliant_material['E'],compliant_material['nu'],'*',color='cyan')
    
    axes[2,1].plot(stiff['E'],stiff['G'],'*',color='gray')
    axes[2,1].plot(compliant_material['E'],compliant_material['G'],'*',color='cyan')
    
    axes[3,1].plot(stiff['E'],stiff['nu'],'*',color='gray')
    axes[3,1].plot(compliant_material['E'],compliant_material['nu'],'*',color='cyan')
    
    axes[3,2].plot(stiff['G'],stiff['nu'],'*',color='gray')
    axes[3,2].plot(compliant_material['G'],compliant_material['nu'],'*',color='cyan')
    
    
    
                
    
    
    fig.set_size_inches(10,6)
    fig.tight_layout(pad=0.0)
    
    plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0.0, hspace=0.0)
    
    
    
        
    plt.show()    

    
    plt.savefig(
        os.path.join(
            os.getcwd(),
            "output_images",
            material+"unit_cell.svg"
            )
            )
    BREAK
    fig.set_size_inches(6,6)
    plt.savefig(
        os.path.join(
            os.getcwd(),
            "output_images",
            material+"unit_cell.png"
            )
        )
    
    
    # Find median of the dataset 
    for unit_cell_type in ['Lattice','Re-entrant']:
        data = plotting_data_frame[plotting_data_frame['Unit Cell'] == unit_cell_type]
        
        print('Unit cell = ',unit_cell_type)
        print('E_1 = ', np.median(data['E1']))
        print('E_2 = ',np.median(data['E2']))
        print('G_12 = ',np.median(data['G12']))
        print('nu_12 = ',np.median(data['Nu12']))
    
    
    # for material_dict in [compliant_foam]:
    
        
    #     outlier_data = merged_data[(merged_data['E1'] < material_dict['E']) | (merged_data['E2'] < material_dict['E'])]
    
    #     outlier_data = outlier_data[outlier_data['Infill material'] == material_dict['name']]
    
    
    # plt.show()    
    # # import matplotlib.rcParams
    # # lower_bound = np.nanmin(plotting_data_frame.iloc[:,:-1])
    # # upper_bound = np.nanmax(plotting_data_frame.iloc[:,:-1])
    
    # fig, ax = plt.subplots(1,1,figsize=(6,6))
    
    # data_to_plot['E1'] = data_to_plot['E1']/1E3
    # data_to_plot['Density'] = data_to_plot['Density']*1E6
    
    # sns.scatterplot(
    #     x = 'Density',
    #     y = 'E1',
    #     data = data_to_plot,
    #     hue = 'Unit Cell',
    #     ax = ax,
    #     palette = colors,
    #     )
    
    # ax.loglog()
    # ax.set(xlim=[10,100000], ylim= [0.0001,1000])
    
    
    #         if i!=j:
                
    #             ax.xaxis.label.set_rotation(0)
    #             ax.yaxis.label.set_rotation(0)
                
    #             if 'nu' not in ax.get_xlabel() or 'nu' not in ax.get_ylabel():
                    
    #                 ax.set_yscale('log')
    #                 ax.set_xscale('log')
                
                
            
                # ax.yaxis.label.set_ha('right')
                #     ax.set_xlim(left=1E5)
                #     ax.set_ylim(bottom=1E5)
                #     ax.set_xlim(left=lower_bound,right=upper_bound)
                #     ax.set_ylim(bottom=lower_bound,top=upper_bound)
                    
                #     for c in ax.get_children():
                #         # set the facecolor to none
                #         if type(c) == mpl.collections.PathCollection:  
                #             c.set_edgecolor(c.get_facecolor())
                #             c.set_facecolor('none')
        
    
                
    # for ax in pair_plot.axes.flat:
    #     if ax.get_xlabel() not in ['Nu12']:
    #         ax.set(xscale="log")
                    
    
            # except:
            #     pass
    
    
    #     # ax.set_xlabel('Stiffness')
    #     # ax.set_ylabel('Stiffness')
        
    # figure = plt.gcf()
    
    
    #         ax.scatter(
    #             x = d_2[load_cases[load_case]+' Safety factor: '+strain_levels[strain_level]],
    #             y = d_2[load_cases[load_case]+' Stiffness: '+strain_levels[strain_level]],
    #             label=cat,
    #             facecolor = face_color,
    #             edgecolor = colors[cat])
    
    
        
    # for strain_level in [0,1]:
    #     if strain_level == 0:
    #         alpha = 1.0
    #     else:
    #         alpha = 0.25
    # #single plot
    #     for cat,d in data_frame.groupby('unit_cell_type'):
    #         for infill,d_2 in d.groupby('Infill flag'):
    #             # if cat == 'Re-entrant':
    #             if infill == True:
    #                 face_color = colors[cat]
    #             if infill == False:
    #                 face_color = "None" 
                    
    #             upper_bound = (1,)*len(d_2[load_cases[load_case]+' Stress: '+strain_levels[strain_level]])
    #             lower_bound = (0.5,)*len(d_2[load_cases[load_case]+' Stress: '+strain_levels[strain_level]])
                
    #             alpha_array=np.linspace(upper_bound,lower_bound,2).T
        
                    
    #             ax.scatter(
    #                 # x = d_2[load_cases[load_case]+' Safety factor: '+strain_levels[strain_level]],
    #                 x = d_2[load_cases[load_case]+' Stress: '+strain_levels[strain_level]],
    #                 y = d_2[load_cases[load_case]+' Stiffness: '+strain_levels[strain_level]],
    #                 label=cat,
    #                 facecolor = face_color,
    #                 edgecolor = colors[cat],
    #                 alpha = alpha)
                
                
    #             max_y = data_frame[load_cases[load_case]+' Stiffness: '+strain_levels[-1]].max()
        
    #             ax.set_yscale('log')
    #             ax.set_xscale('log')
        
    #             rect = patches.Rectangle((0,0),1,1.2*max_y,alpha=0.1,facecolor='r')    
    #             ax.add_patch(rect)
        
        
        
                # ax.set_xlim(.1,100.0)
    
    
    
    # for cat,d in data_frame.groupby('unit_cell_type'):
        
    #     # d = d.loc[data_frame['Infill flag'] == True]
    #     for infill,d_2 in d.groupby('Infill flag'):
    #     # if cat == 'Re-entrant':
    #         if infill == True:
    #             face_color = colors[cat]
    #         if infill == False:
    #             face_color = "None" 
            
    #         upper_bound = (1,)*len(d_2[load_cases[load_case]+' Stress: '+strain_levels[strain_level]])
    #         lower_bound = (0.5,)*len(d_2[load_cases[load_case]+' Stress: '+strain_levels[strain_level]])
            
    #         alpha_array=np.linspace(upper_bound,lower_bound,2).T
    
                
    #         ax.scatter(
    #             # x = d_2[load_cases[load_case]+' Safety factor: '+strain_levels[strain_level]],
    #             x = d_2[load_cases[load_case]+' Stress: '+strain_levels[strain_level]],
    #             y = d_2[load_cases[load_case]+' Stiffness: '+strain_levels[strain_level]],
    #             label=cat,
    #             facecolor = face_color,
    #             edgecolor = colors[cat],
    #             alpha = alpha)
            
            
    #         max_y = data_frame[load_cases[load_case]+' Stiffness: '+strain_levels[-1]].max()
    
    #         ax.set_yscale('log')
    #         ax.set_xscale('log')
    
        # rect = patches.Rectangle((0,0),1,1.2*max_y,alpha=0.1,facecolor='r')    
        # ax.add_patch(rect)
    
    
    
        # ax.set_xlim(.1,100.0)
    
    
    
    # ax.set_xlim(1E6,1E10)
    # ax.set_ylim(1E4,1.2*max_y)
    
    # ax.set_ylabel(load_case_labels[load_cases[load_case]+' Stiffness: '+strain_levels[0]])
    
    # ax.set_xlabel('Stress, Pa')
    
    # rect = patches.Rectangle((yield_stress/1.5,0),1E10,1.2*max_y,alpha=0.1,facecolor='r')    
    # ax.add_patch(rect)
    
    # BREAK
    
                
    
    # ax = data_frame.plot.scatter(
    #     x = load_case+' Safety factor: '+strain_levels[strain_level],
    #     y = load_case+' Stiffness: '+strain_levels[strain_level],
    #     c = data_frame['unit_cell_type'],
    #     )
    
    
    
    ## scatter matrix 
    # axes = pd.plotting.scatter_matrix(
    #     data_frame[
    #         [load_cases[0]+' Stiffness: '+strain_levels[strain_level],
    #          load_cases[1]+' Stiffness: '+strain_levels[strain_level],
    #          load_cases[2]+' Stiffness: '+strain_levels[strain_level],
    #          load_cases[3]+' Stiffness: '+strain_levels[strain_level],
    #          # load_cases[4]+' Stiffness: '+strain_levels[strain_level],
    #          # load_cases[5]+' Stiffness: '+strain_levels[strain_level],
    #          # load_cases[6]+' Stiffness: '+strain_levels[strain_level],
    #          # load_cases[7]+' Stiffness: '+strain_levels[strain_level],
    #          load_cases[8]+' Stiffness: '+strain_levels[strain_level]
    #          ]
    #         ],
    #     alpha=0.4,
    #     )
    
                  
                  
    
    
    
    
    
    
    
    
    # import matplotlib.rcParams
    # lower_bound = np.nanmin(plotting_data_frame.iloc[:,:-1])
    # upper_bound = np.nanmax(plotting_data_frame.iloc[:,:-1])
    
    # for i, axs in enumerate(pair_plot.axes):
    #     for j, ax in enumerate(axs):
                
    #         # try:
    #             ax.xaxis.label.set_rotation(0)
    #             ax.yaxis.label.set_rotation(0)
            
    #             ax.yaxis.label.set_ha('right')
    #             if ax.get_ylabel() != '':
    #                 ax.set_ylabel(
    #                     load_case_labels[ax.get_ylabel()]
    #                     )
    #             if ax.get_xlabel() != '':
    #                 ax.set_xlabel(
    #                     load_case_labels[ax.get_xlabel()]
    #                     )
    #             if i!=j:
        
    #                     ax.set_yscale('log')
    #                     ax.set_xscale('log')
    #                     # ax.set_xlim(left=1E5)
    #                     # ax.set_ylim(bottom=1E5)
    #                     ax.set_xlim(left=lower_bound,right=upper_bound)
    #                     ax.set_ylim(bottom=lower_bound,top=upper_bound)
                        
    #                     # for c in ax.get_children():
    #                     #     # set the facecolor to none
    #                     #     if type(c) == mpl.collections.PathCollection:  
    #                     #         c.set_edgecolor(c.get_facecolor())
    #                     #         c.set_facecolor('none')
        
                
    #             if i == j:
    #                 # ax.set_xlim(left=1E5)
    #                 # ax.set_xscale('log')
    #                 # ax.set_yscale('log')
                    
    #                 # ax.set_ylim(bottom=1E-11)
    #                 ax.set_yscale('log')
    #                 ax.set_xlim(left=lower_bound,right=upper_bound)
    #                 ax.set_ylim(bottom=lower_bound,top=upper_bound)
                
                    
    #             if i < j:
    #                 ax.set_visible(False)
    #         # except:
    #         #     pass
    
    
    #     # ax.set_xlabel('Stiffness')
    #     # ax.set_ylabel('Stiffness')
        
    # figure = plt.gcf()
    
        
        
    # # count number of unit cells in each 
    # for cat,d in data_frame.groupby('unit_cell_type'):
    #     for infill,d_2 in d.groupby('Infill flag'):
    #         print(cat,', ',infill, ':' ,d_2.shape[0])