# cSpell: disable

import numpy as np
import os
import openmc
import matplotlib.pyplot as plt


# ##############################################
#       MATERIALS
# ##############################################
fuel = openmc.Material(name='uo2', temperature=300)
fuel.set_density('g/cm3', 10.97)
fuel.add_element('U', 1.0, enrichment=3.5)
fuel.add_element('O', 2.0)
fuel.add_s_alpha_beta('c_O_in_UO2')

clad = openmc.Material(name='Zr', temperature=300)
clad.set_density('g/cm3', 3.2)
clad.add_element('Zr', 1.0)

moderator = openmc.Material(name='water', temperature=300)
moderator.set_density('g/cm3', 0.7)
moderator.add_element('H', 2)
moderator.add_element('O', 1)
moderator.add_s_alpha_beta('c_H_in_H2O')

mat_list= openmc.Materials([fuel, clad, moderator])
mat_list.export_to_xml()

# print(fuel)
# print(moderator)
# print(clad)
print(mat_list)
mat_list.cross_sections = "/Users/rocco698/Desktop/Undergrad/Fall Semester - 2025/NUCE 403/hades_rain_403/ENDF:B.VIII/endfb-viii.0-hdf5/cross_sections.xml"


# ################################################
#       GEOMETRY DEFINITION
# ################################################

# Plane Equation Calculator
def plane_from_points(p1, p2, p3, **kwargs):
    p1, p2, p3 = map(np.array, (p1, p2, p3))
    v1, v2 = p2 - p1, p3 - p1
    normal = np.cross(v1,v2)
    A, B, C = normal
    D = np.dot(normal, p1)
    return openmc.Plane(a=A, b=B, c=C, d=D, **kwargs)


fuel_out = openmc.ZCylinder(r=0.9)
annularclad_in = openmc.ZCylinder(r=0.15)
annularclad_out = openmc.ZCylinder(r=0.25)
clad1 = openmc.YPlane(1, boundary_type='reflective')
clad2 = openmc.YPlane(1.05, boundary_type='reflective')
clad3 = plane_from_points(
    [0.58,1,0],
    [1.15,0,0],
    [1.15,0,1],
    boundary_type='reflective'
)
clad4 = plane_from_points(
    [0.61,1.05,0],
    [1.21,0,0],
    [1.21,0,1],
    boundary_type='reflective'
)
clad5 = plane_from_points(
    [1.15,0,0],
    [0.58,-1,0],
    [0.58,-1,1],
    boundary_type='reflective'
)
clad6 = plane_from_points(
    [1.21,0,0],
    [0.61,-1.05,0],
    [0.61,-1.05,1],
    boundary_type='reflective'
)
clad7 = openmc.YPlane(-1, boundary_type='reflective')

clad8 = openmc.YPlane(-1.05, boundary_type='reflective')

clad9 = plane_from_points(
    [-0.58,-1,0],
    [-1.15,0,0],
    [-1.25,0,1],
    boundary_type='reflective'
)
clad10 = plane_from_points(
    [-0.61,1.05,0],
    [-1.21,0,0],
    [-1.21,0,1],
    boundary_type='reflective'
)
clad11 = plane_from_points(
    [-1.15,0,0],
    [-0.58,1,0],
    [-0.58,1,1],
    boundary_type='reflective'
)
clad12 = plane_from_points(
    [-1.21,0,0],
    [-0.61,1.05,0],
    [-0.61,1.05,1],
    boundary_type='reflective'
)



moderator_center = -annularclad_in
annular_cladding = +annularclad_in & -annularclad_out
region_fuel_in = +annularclad_out & -fuel_out
region_gap = +fuel_out & -clad1 & -clad3 & -clad5 & -clad7 & -clad9 & clad11
region_cladding = +clad1 & + clad3 & +clad5 & +clad7 & +clad9 & +clad11 & -clad2 & -clad4 & -clad6 & -clad8 & -clad10 & -clad12
region_moderator = +clad2 & +clad4 & +clad6 & +clad8 & +clad10 & +clad12

moderator_cell_1 = openmc.Cell(name='moderator', fill=moderator, region=moderator_center)
annular_cladding_cell = openmc.Cell(name='Cladding', fill=clad, region=annular_cladding)
fuel_cell = openmc.Cell(name='fuel', fill=fuel, region=region_fuel_in)
gap_cell = openmc.Cell(name='Gap', fill=moderator, region=region_gap)
cladding_outer_cell = openmc.Cell(name='Cladding Outer', fill=clad, region=region_cladding)
moderator_out_cell = openmc.Cell(name='Moderator Outer', fill=moderator, region=region_moderator)

geometry = openmc.Geometry([moderator_cell_1, annular_cladding_cell, fuel_cell, gap_cell, cladding_outer_cell, moderator_out_cell])
geometry.export_to_xml()

print(geometry)
print(mat_list)


###############################################################################
# Define problem settings
###############################################################################
settings = openmc.Settings()
settings.batches = 100
settings.inactive = 10
settings.particles = 1000
settings.export_to_xml()

print(settings)


# ################################
#  Plots Definition
# ################################
ww = 4
plot1 = openmc.Plot()
plot1.width = (ww,ww)
plot1.basis = 'xy'
plot1.color_by = 'material'
plot1.filename = 'RadialView'
plots = openmc.Plots([plot1])
plots.export_to_xml()

# Set the environment variable for cross sections
os.environ["OPENMC_CROSS_SECTIONS"] = "/Users/rocco698/Desktop/Undergrad/Fall Semester - 2025/NUCE 403/hades_rain_403/ENDF:B.VIII/endfb-viii.0-hdf5/cross_sections.xml"

openmc.plot_geometry()
openmc.run()
