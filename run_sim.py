# cSpell: disable

import numpy as np
import os
import openmc
import matplotlib.pyplot as plt


# ##############################################
#       MATERIALS
# ##############################################
fuel = openmc.Material(name='puo2', temperature=300)
fuel.set_density('g/cm3', 11.46)
fuel.add_element('Pu', 1.0, enrichment=19.5)
fuel.add_element('O', 2.0)
fuel.add_s_alpha_beta('c_O_in_PUO2')

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
edge_outer_cladding = 1.21
edge_inner_cladding = 1.15
edge_fuel_pellet = 1.1


# create composite hexagonal prism surfaces
hex_outer_clad = openmc.model.hexagonal_prism(edge_length=edge_outer_cladding, orientation='x', origin=(0.0, 0.0), boundary_type='reflective', corner_radius=0.0)

hex_inner_clad = openmc.model.hexagonal_prism(edge_length=edge_inner_cladding, orientation='x', origin=(0.0, 0.0), boundary_type='reflective', corner_radius=0.0)

fuel_pellet = openmc.model.hexagonal_prism(edge_length=edge_inner_cladding, orientation='x', origin=(0.0, 0.0), boundary_type='reflective', corner_radius=0.0)

annular_clad_out = openmc.ZCylinder(r=0.25, boundary_type='reflective')

annular_clad_in = openmc.ZCylinder(r=0.225, boundary_type='reflective')

region_annular_coolant = -annular_clad_in

region_annular_cladding = +annular_clad_in & -annular_clad_out

region_fuel = +annular_clad_out & fuel_pellet

region_gap = ~fuel_pellet & hex_inner_clad

region_clad = hex_outer_clad & ~hex_inner_clad

annular_coolant_cell = openmc.Cell(name='Annular Coolant Channel', fill=moderator, region=region_annular_coolant)

annular_clad_cell = openmc.Cell(name='Annular Cladding', fill=clad, region=region_annular_cladding)

fuel_cell = openmc.Cell(name='Fuel', fill=fuel, region=region_fuel)

gap_cell = openmc.Cell(name='gap', fill=moderator, region=region_gap)

clad_cell = openmc.Cell(name='cladding', fill=clad, region=region_clad)



geometry = openmc.Geometry([annular_coolant_cell, annular_clad_cell, fuel_cell, gap_cell, clad_cell])
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
ww = 3
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
