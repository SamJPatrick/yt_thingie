import re
import yt
import numpy as np
from unyt import unyt_quantity



SIMULATION = "simulation.h5"

T0_CCSNe = unyt_quantity(211.81, 'Myr')
T0_PISNe = unyt_quantity(211.31, 'Myr')

TLIFE_CCSNe = unyt_quantity(3.68, 'Myr')
TLIFE_PISNe = unyt_quantity(2.20, 'Myr')

E_CCSNe = unyt_quantity(1e51, 'erg')
E_PISNe = unyt_quantity(1e53, 'erg')

LIMS_DENSITY = (1e-27, 1e-18)
LIMS_TEMPERATURE = (1e1, 1e8)
LIMS_BE_RATIO = (1e-4, 1e2)
LIMS_VELOCITY = (0, 1e6)
#LIMS_VELOCITY = (-1e6, 1e6)
LIMS_CS = (0, 1e6)
LIMS_MDOT = (1e-5, 1e-2)
LIMS_MDOT_Z = (1e-8, 1e-5)
LIMS_Z = (1e-7, 1e0)
LIMS_H2 = (1e-4, 5e-3)

FIELD_DICTS = []
FIELD_DICTS.append({'name': 'density', 'units': 'g/cm**3', 'limits': LIMS_DENSITY, 'colormap': 'viridis', 'log': True})
FIELD_DICTS.append({'name': 'temperature', 'units': 'K', 'limits': LIMS_TEMPERATURE, 'colormap': 'plasma', 'log': True})
FIELD_DICTS.append({'name': 'bonnor_ebert_ratio', 'units': '', 'limits': LIMS_BE_RATIO, 'colormap': 'cividis', 'log': True})
#FIELD_DICTS.append({'name': 'velocity', 'units': 'km/s', 'limits': LIMS_VELOCITY, 'colormap': 'spring', 'log': False})
FIELD_DICTS.append({'name': 'velocity_magnitude', 'units': 'km/s', 'limits': LIMS_VELOCITY, 'colormap': 'spring', 'log': False})
FIELD_DICTS.append({'name': 'sound_speed', 'units': 'km/s', 'limits': LIMS_CS, 'colormap': 'spring', 'log': False})
FIELD_DICTS.append({'name': 'accretion_rate', 'units': 'Msun/yr', 'limits': LIMS_MDOT, 'colormap': 'magma', 'log': True})
FIELD_DICTS.append({'name': 'accretion_rate_z', 'units': 'Msun/yr', 'limits': LIMS_MDOT_Z, 'colormap': 'magma', 'log': True})
FIELD_DICTS.append({'name': 'metallicity3', 'units': 'Zsun', 'limits': LIMS_Z, 'colormap': 'cool', 'log': True})
FIELD_DICTS.append({'name': 'H2_p0_fraction', 'units': '', 'limits': LIMS_H2, 'colormap': 'cool', 'log': False})


def get_field_dict(field):
    if (isinstance(field, str)):
        entry_num = np.argwhere(np.array([field['name'] for field in FIELD_DICTS]) == field)
    elif (isinstance(field, tuple)):
        entry_num = np.argwhere(np.array([field['name'] for field in FIELD_DICTS]) == field[1])
    else :
        raise TypeError(f"Error, expecting either tuple or string for field, instead got {field}")
    if (len(entry_num) != 1):
        print(f"Error, field {field} was not found within field list")
        quit()
    return FIELD_DICTS[entry_num.item()]


def get_time_offset(star_mode):
    time_offset = unyt_quantity(0.0, 'Myr')
    if (("PI" in star_mode) or ("pi" in star_mode)):
        time_offset = T0_PISNe
    elif (("CC" in star_mode) or ("cc" in star_mode)):
        time_offset = T0_CCSNe
    else:
        print("No offset provided, setting to zero...")
        pass
    return time_offset


def get_lifetime_offset(star_mode):
    time_offset = unyt_quantity(0.0, 'Myr')
    if (("PI" in star_mode) or ("pi" in star_mode)):
        time_offset = TLIFE_PISNe
    elif (("CC" in star_mode) or ("cc" in star_mode)):
        time_offset = TLIFE_CCSNe
    else:
        print("No offset provided, setting to zero...")
        pass
    return time_offset


def get_sn_energy(star_mode):
    if (("PI" in star_mode) or ("pi" in star_mode)):
        sn_energy = E_PISNe
    elif (("CC" in star_mode) or ("cc" in star_mode)):
        sn_energy = E_CCSNe
    else:
        sn_energy = E_CCSNe
        print("None provided, setting to values for core collapse...")
        pass
    #print(f"Energy set to: {sn_energy}") 
    return sn_energy


def get_dump_num(filename):
    dump_num = re.search(r'^DD([0-9]{4})(_[-_a-zA-Z0-9]+\.h5)?$', filename).group(1)
    return dump_num


def get_time_z(filename, star_mode):
    time_offset = get_time_offset(star_mode)
    dump = f"DD{get_dump_num(filename)}"
    fname = '/'.join([dump, dump]).encode()
    sim = yt.load(SIMULATION)
    time = sim.data['time'][np.argwhere(sim.data['filename'] == fname).item()].in_units('Myr') - time_offset
    z = sim.data['redshift'][np.where(sim.data['filename'] == fname)][0].value
    return (time, z)


def get_title(filename, star_mode):
    time, z = get_time_z(filename, star_mode)
    dump = f"DD{get_dump_num(filename)}"
    #title = f"{dump}, z={z:.2f}, t = {time:.2f}"
    title = f"z={z:.2f}, t = {time:.2f}"
    return title
