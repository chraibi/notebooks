import os
import re

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

import matplotlib.cm as cm
import matplotlib.animation as animation
from matplotlib import rc
from matplotlib import colors

from matplotlib.patches import Polygon as ppolygon
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D

from xml.dom.minidom import parse

import mpl_toolkits.axes_grid1
import matplotlib.widgets

from IPython.display import HTML


class Player(FuncAnimation):
    def __init__(self, fig, func, frames=None, init_func=None, fargs=None,
                 save_count=None, mini=0, maxi=100, pos=(0.125, 0.92), **kwargs):
        self.i = 0
        self.min = mini
        self.max = maxi
        self.runs = True
        self.forwards = True
        self.fig = fig
        self.func = func
        self.setup(pos)
        FuncAnimation.__init__(self, self.fig, self.update, frames=self.play(),
                               init_func=init_func, fargs=fargs,
                               save_count=save_count, **kwargs)

    def play(self):
        while self.runs:
            self.i = self.i + self.forwards - (not self.forwards)
            if self.i > self.min and self.i < self.max:
                yield self.i
            else:
                self.stop()
                yield self.i

    def start(self):
        self.runs = True
        self.event_source.start()

    def stop(self, event=None):
        self.runs = False
        self.event_source.stop()

    def forward(self, event=None):
        self.forwards = True
        self.start()

    def backward(self, event=None):
        self.forwards = False
        self.start()

    def oneforward(self, event=None):
        self.forwards = True
        self.onestep()

    def onebackward(self, event=None):
        self.forwards = False
        self.onestep()

    def onestep(self):
        if self.i > self.min and self.i < self.max:
            self.i = self.i + self.forwards - (not self.forwards)
        elif self.i == self.min and self.forwards:
            self.i += 1
        elif self.i == self.max and not self.forwards:
            self.i -= 1
        self.func(self.i)
        self.slider.set_val(self.i)
        self.fig.canvas.draw_idle()

    def setup(self, pos):
        playerax = self.fig.add_axes([pos[0], pos[1], 0.64, 0.04])
        divider = mpl_toolkits.axes_grid1.make_axes_locatable(playerax)
        bax = divider.append_axes("right", size="80%", pad=0.05)
        sax = divider.append_axes("right", size="80%", pad=0.05)
        fax = divider.append_axes("right", size="80%", pad=0.05)
        ofax = divider.append_axes("right", size="100%", pad=0.05)
        sliderax = divider.append_axes("right", size="500%", pad=0.07)
        self.button_oneback = matplotlib.widgets.Button(playerax, label='$\u29CF$')
        self.button_back = matplotlib.widgets.Button(bax, label='$\u25C0$')
        self.button_stop = matplotlib.widgets.Button(sax, label='$\u25A0$')
        self.button_forward = matplotlib.widgets.Button(fax, label='$\u25B6$')
        self.button_oneforward = matplotlib.widgets.Button(ofax, label='$\u29D0$')
        self.button_oneback.on_clicked(self.onebackward)
        self.button_back.on_clicked(self.backward)
        self.button_stop.on_clicked(self.stop)
        self.button_forward.on_clicked(self.forward)
        self.button_oneforward.on_clicked(self.oneforward)
        self.slider = matplotlib.widgets.Slider(sliderax, '',
                                                self.min, self.max, valinit=self.i)
        self.slider.on_changed(self.set_pos)

    def set_pos(self, i):
        self.i = int(self.slider.val)
        self.func(self.i)

    def update(self, i):
        self.slider.set_val(i)


def read_obstacle(xml_doc):
    # Initialisierung eines dictionary mit obstacles
    return_dict = {}

    # obstacles einlesen und zu einem array fuer polygon-Darstellung zusammenfassen
    for o_num, o_elem in enumerate(xml_doc.getElementsByTagName('obstacle')):

        N_polygon = len(o_elem.getElementsByTagName('polygon'))
        # print('number of polygons: {0}'.format(N_polygon))

        if len(o_elem.getElementsByTagName('polygon')) == 1:
            pass
        else:
            array_temp = np.zeros((N_polygon, 2))

        for p_num, p_elem in enumerate(o_elem.getElementsByTagName('polygon')):

            N_vertex = len(p_elem.getElementsByTagName('vertex'))
            # print('polygon {0} - number of vertex: {1}'.format(p_num, N_vertex))

            if len(p_elem.getElementsByTagName('vertex')) == 2:

                array_temp[p_num, 0] = p_elem.getElementsByTagName('vertex')[0].attributes['px'].value
                array_temp[p_num, 1] = p_elem.getElementsByTagName('vertex')[0].attributes['py'].value
            else:
                # print('more than two vertex')
                array_temp = np.zeros((N_vertex, 2))

                for v_num, v_elem in enumerate(p_elem.getElementsByTagName('vertex')):
                    array_temp[v_num, 0] = p_elem.getElementsByTagName('vertex')[v_num].attributes['px'].value
                    array_temp[v_num, 1] = p_elem.getElementsByTagName('vertex')[v_num].attributes['py'].value

        # polygon-array von obstacle zu obstacles-dictionary hinzufuegen
        return_dict[o_num] = array_temp

    return return_dict


def read_subroom_walls(xml_doc):
    dict_polynom_wall = {}

    n_wall = 0

    for s_num, s_elem in enumerate(xml_doc.getElementsByTagName('subroom')):

        for p_num, p_elem in enumerate(s_elem.getElementsByTagName('polygon')):

            if p_elem.getAttribute('caption') == "wall":

                n_wall = n_wall + 1

                n_vertex = len(p_elem.getElementsByTagName('vertex'))

                vertex_array = np.zeros((n_vertex, 2))

                for v_num, v_elem in enumerate(p_elem.getElementsByTagName('vertex')):
                    vertex_array[v_num, 0] = p_elem.getElementsByTagName('vertex')[v_num].attributes['px'].value
                    vertex_array[v_num, 1] = p_elem.getElementsByTagName('vertex')[v_num].attributes['py'].value

                # polygon-array von obstacle zu obstacles-dictionary hinzufuegen
                dict_polynom_wall[n_wall] = vertex_array

    return dict_polynom_wall



