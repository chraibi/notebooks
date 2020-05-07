import re
import os
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.patches import Polygon as ppolygon
from mpl_toolkits.axes_grid1 import make_axes_locatable

def read_IFD(IFD_filename):

    file_IFD = '{0}.dat'.format(IFD_filename)

    df = pd.read_csv('{0}'.format(file_IFD),
                     comment='#',sep='\t',
                     names=['Frame','PersID','x/m','y/m','z/m','rho','vel','Voronoi_Polygon'],
                     index_col=False)
    return df

def str_to_array(p):
    """
    convert jpsreport polygon into <np.array>
    --> can be converted to <Polygon.Polygon>
    """

    if not isinstance(p, str):
        raise TypeError('str_to_Array argument must be str')

    pat = re.compile(r'''(-*\d+\.?\d*, -*\d+\.?\d*),*''')
    matches = pat.findall(p)
    lst = []
    if matches:
        lst = [tuple(map(float, m.split(","))) for m in matches]
    else:
        print("WARNING: could not convert str to list")

    return np.array(lst)


def IFD_plot_polygon_rho(dataframe,frame_min, frame_max, xmin, xmax, ymin,ymax, fps, v_min, v_max):
    i = 0
    for f in range(frame_min, frame_max):

        fig = plt.figure()
        ax1 = fig.add_subplot(111, aspect='equal')

        ax1.set_title('frame {0:6d} - time {1:7.2f} s'.format(f, f/fps))

        ax1.set_xlim(xmin,xmax)
        ax1.set_xlabel(r'x / $m$')

        ax1.set_ylim(ymin,ymax)
        ax1.set_ylabel(r'y / $m$')

        divider = make_axes_locatable(ax1)
        cax1 = divider.append_axes("right", size="10%", pad="5%")

        sm = cm.ScalarMappable(cmap = cm.get_cmap('rainbow'))

        sm.set_clim(vmin=v_min, vmax=v_max)

        for i in dataframe[dataframe['Frame'] == f]['PersID'].iteritems():

                # workflow "agents voronoi polygon" in one line
                # 1. str_to_array
                # 2. adjusting the unit
                Polygon_Agent = str_to_array(dataframe['Voronoi_Polygon'][i[0]].strip())/10000

                # density value for display with colorbar
                rho = dataframe[dataframe['Frame'] == f]['rho'][i[0]]

                sm.set_array(rho)
                sm.autoscale_None()

                ax1.add_patch(ppolygon(Polygon_Agent,
                                       fc= sm.to_rgba(rho),
                                       ec='white',
                                       lw=1))

        label = r"$\rho$ /$P m^{-2}$"

        cbar = fig.colorbar(sm, cax = cax1, label = label)
        plt.show()
        plt.close()

        