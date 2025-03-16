# -*- coding: utf-8 -*-
"""
Created on Tue Jun  4 11:16:50 2024

@author: 1545585665157005
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.text as mtext
import matplotlib.transforms as mtransforms

class RotationAwareAnnotation(mtext.Annotation):
    '''
    Creates an annotation to automatically map to 
    a predefined line and rotate with it. 
    
    Shamelessly ripped from:
        https://stackoverflow.com/questions/19907140/keeps-text-rotated-in-data-coordinate-system-after-resizing/53111799#53111799
    '''
    def __init__(self, s, xy, p, pa=None, ax=None, **kwargs):
        '''
        

        Parameters
        ----------
        s : STR
            Text to display.
        xy : tuple (2)
            text coordinates
        p : tuple
            ending location of the reference line.
        pa : tuple, optional
            starting location of the reference line.
            The default is None, and if None, the starting location 
            is assuming to be the text coordinates.
        ax : matplotlib axes object, optional
            The default is None.
        **kwargs 
            text.Annotation keyword arguments.

        Returns
        -------
        None.

        '''
        self.ax = ax or plt.gca()
        self.p = p
        if not pa:
            self.pa = xy
        else:
            self.pa = pa
        kwargs.update(rotation_mode=kwargs.get("rotation_mode", "anchor"))
        mtext.Annotation.__init__(self, s, xy, **kwargs)
        self.set_transform(mtransforms.IdentityTransform())
        if 'clip_on' in kwargs:
            self.set_clip_path(self.ax.patch)
        self.ax._add_text(self)

    def calc_angle(self):
        p = self.ax.transData.transform_point(self.p)
        pa = self.ax.transData.transform_point(self.pa)
        ang = np.arctan2(p[1]-pa[1], p[0]-pa[0])
        return np.rad2deg(ang)

    def _get_rotation(self):
        return self.calc_angle()

    def _set_rotation(self, rotation):
        pass

    _rotation = property(_get_rotation, _set_rotation)