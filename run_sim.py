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

# outer / inner edge length (length of one hex side) in cm
edge_outer = 1.0
edge_inner = 0.6

# create composite hexagonal prism surfaces
hex_outer = openmc.model.HexagonalPrism(edge_length=edge_outer, orientation='y',
                           origin=(0.0, 0.0), boundary_type='reflective')
hex_inner = openmc.model.HexagonalPrism(edge_length=edge_inner, orientation='y',
                           origin=(0.0, 0.0), boundary_type='reflective')

# get interior regions (unary - gives interior region)
region_outer = -hex_outer    # interior of outer hex
region_inner = -hex_inner    # interior of inner hex

# Z bounds for prism (height = 1.0)
z_min = openmc.ZPlane(z0=0.0, boundary_type='reflective')
z_max = openmc.ZPlane(z0=1.0, boundary_type='reflective')

# hollow hex region = outer interior MINUS inner interior, extruded in Z
hollow_hex_region = region_outer & ~region_inner & +z_min & -z_max

# create a cell (no material needed if only visualizing)
hollow_cell = openmc.Cell(name='hollow_hex', fill=moderator, region=hollow_hex_region)

geometry = openmc.Geometry([hollow_cell])
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
ww = 1
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
