import os
import yt
import sys
import numpy as np

from yt.extensions.sam_mods.misc import *
from yt.extensions.sam_mods.profiles import my_profile
from yt.extensions.sam_mods.plots import *
from yt.extensions.sam_mods.graph_funcs import get_time_offset

from unyt import unyt_quantity, unyt_array
from unyt import G, Msun, kb, mh, pc
from grid_figure import GridFigure



MASS_FILE = "star_None_mass.h5"
SIMULATION_FILE = "simulation.h5"
OUTDIR = "Profiles/Timescale_graphs_mass"


try :
    star_mode = sys.argv[1]
except IndexError:
    star_mode = ""
    pass
time_offset = get_time_offset(star_mode)

fields = ["turbulent_sound_crossing_time", "sound_crossing_time", "total_dynamical_time", "cooling_time"]
labels = ["turbulent sound-crossing", "sound-crossing", "free-fall", "cooling"]
colors = ["orange", "red", "green", "blue"]
assert len(fields) == len(labels) == len(colors), "Error, field length do not match"

df_sim = yt.load(SIMULATION_FILE)
df_mass = yt.load(MASS_FILE)
idx_max = np.argmax(df_mass.data[('data', 'bonnor_ebert_ratio')][-1])
for index, time in enumerate(df_mass.data[('data', 'time')].to('Myr')):
    
    my_fig = GridFigure(1, 1, figsize=(6, 4.5),
                        top_buffer = 0.13, bottom_buffer = 0.12,
                        left_buffer = 0.14, right_buffer = 0.02,
                        horizontal_buffer = 0.05, vertical_buffer = 0)
    my_axes = my_fig[0]
    my_axes.set_xscale('log')
    my_axes.set_yscale('log')
    xlim = (1e-2, 1e5)
    tx = twin_unit_axes(my_axes, xlim, "mass", "Msun", top_units="kg")

    mass = df_mass.data[('data', 'gas_mass_enclosed')][index].to('Msun')
    mass_be = mass[idx_max].to('Msun')
    profile_dict = {}
    for field, label, color in zip(fields, labels, colors):        
        profile_dict[field] = df_mass.data[('data', field)][index].to('Myr')
        my_axes.plot(mass, df_mass.data[('data', field)][index].to('Myr'), color=color,
                     alpha=0.7, linewidth=1.5, label=label)

    ylim = (1e0, 1e5)
    ymajor = np.logspace(2, 10, 5)
    yminor = np.logspace(1, 9, 5)
    draw_major_grid(my_axes, 'y', ymajor, color='black', linestyle='-', linewidth=1, alpha=0.2)
    ty = mirror_yticks(my_axes, ylim, ymajor, yminor=yminor)

    bkgcolor = ['blue', 'green', 'yellow', 'red']
    for i in range (len(mass) - 1):
        if (profile_dict['cooling_time'][i] < profile_dict['total_dynamical_time'][i]):
            pyplot.axvspan(mass[i], mass[i+1], facecolor= bkgcolor[0], alpha=0.5)
        elif (profile_dict['total_dynamical_time'][i] < profile_dict['turbulent_sound_crossing_time'][i] and \
              profile_dict['total_dynamical_time'][i] < profile_dict['sound_crossing_time'][i]):
            pyplot.axvspan(mass[i], mass[i+1], facecolor= bkgcolor[1], alpha=0.5)
        elif (profile_dict['total_dynamical_time'][i] < profile_dict['sound_crossing_time'][i]):
            pyplot.axvspan(mass[i], mass[i+1], facecolor= bkgcolor[2], alpha=0.5)
        else :
            pyplot.axvspan(mass[i], mass[i+1], facecolor= bkgcolor[3], alpha=0.5)            
    my_axes.yaxis.set_label_text("t [Myr]")
    my_axes.axvline(x= mass_be, linewidth=2)
    my_axes.legend(loc= 'lower right')
    my_axes.annotate(f"time={(time - time_offset):.2f}", xy= (1e-1, 1e4), \
                     backgroundcolor= 'white', fontsize= 'medium')

    index_sim = np.argwhere(df_sim.data[('data', 'time')].to('Myr') == time).item()
    dsfn = df_sim.data[('data', 'filename')].astype(str)[index_sim].split('/')[-1]
    fpath = os.path.join(os.getcwd(), OUTDIR, f"{str(dsfn)}_timescale_profiles.png")
    pyplot.savefig(fpath)
    pyplot.close()
