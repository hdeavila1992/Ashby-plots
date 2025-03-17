# -*- coding: utf-8 -*-
"""
Math utilities to clean up organization.

@author: Walgren
"""
import numpy as np

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
    return (x[1] - x[0])/(np.log(x[1]) - np.log(x[0]))
