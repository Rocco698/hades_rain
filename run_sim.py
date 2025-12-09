# cSpell: disable

import numpy as np
import os
import math
import openmc
import openmc.deplete
import matplotlib.pyplot as plt

# Set the environment variable for cross sections
os.environ["OPENMC_CROSS_SECTIONS"] = "/data/endfb-viii.0-hdf5/cross_sections.xml"


# ##############################################
#       MATERIALS
# ##############################################
fuel = openmc.Material(name='uo2', temperature=300)
fuel.set_density('g/cm3', 10.97)
fuel.add_element('U', 1.0, enrichment=2.5)
fuel.add_element('O', 2.0)
fuel.add_s_alpha_beta('c_O_in_UO2')

clad = openmc.Material(name='Zr', temperature=300)
clad.set_density('g/cm3', 3.2)
clad.add_element('Zr', 1.0)

moderator = openmc.Material(name='water', temperature=300)
moderator.set_density('g/cm3', 1)
moderator.add_element('H', 2)
moderator.add_element('O', 1)
moderator.add_s_alpha_beta('c_H_in_H2O')

gap = openmc.Material(name='Helium', temperature=300)
gap.set_density('sum')
gap.add_element('He', 1E-11)

absorber = openmc.Material(name='Boron Carbide', temperature=300)
absorber.set_density('g/cm3', 2.52)
absorber.add_element('B', 4)
absorber.add_nuclide('C12',0.989)

mat_list= openmc.Materials([fuel, clad, moderator, gap, absorber])
mat_list.cross_sections = "/data/endfb-viii.0-hdf5/cross_sections.xml"
mat_list.export_to_xml()

# print(fuel)
# print(moderator)
# print(clad)
print(mat_list)



# ################################################
#       GEOMETRY DEFINITION
# ################################################

# Bounding surfaces
xmin = openmc.XPlane(surface_id=700, x0=-300, boundary_type='vacuum')
xmax = openmc.XPlane(surface_id=701, x0=300,  boundary_type='vacuum')
ymin = openmc.YPlane(surface_id=702, y0=-300, boundary_type='vacuum')
ymax = openmc.YPlane(surface_id=703, y0=300,  boundary_type='vacuum')
zmin = openmc.ZPlane(surface_id=704, z0=-500, boundary_type='vacuum')
zmax = openmc.ZPlane(surface_id=705, z0=500,  boundary_type='vacuum')

bounding_region = +xmin & -xmax & +ymin & -ymax & +zmin & -zmax



# RPV 
RPV_floor = openmc.ZPlane(surface_id=1, z0=-500, boundary_type='vacuum')
RPV_ceiling = openmc.ZPlane(surface_id=2, z0=500, boundary_type='vacuum')
RPV_wall = openmc.ZCylinder(surface_id=3, r=300, boundary_type='vacuum')
#RPV_core_wall_hex = openmc.model.HexagonalPrism(edge_length=300, )

total_bound = openmc.ZCylinder(surface_id=90, r=500, boundary_type='vacuum')

RPV_region = -RPV_wall & +RPV_floor & -RPV_ceiling


# FUEL PIN
ceiling = openmc.ZPlane(surface_id=4, z0=250, boundary_type='transmission')
floor = openmc.ZPlane(surface_id=5, z0=-250, boundary_type='transmission')

fuel_out = openmc.ZCylinder(surface_id=6, r=1.932, boundary_type='transmission')
cladding_in = openmc.ZCylinder(surface_id=7, r=1.94, boundary_type='transmission')
cladding_out = openmc.ZCylinder(surface_id=8, r=2, boundary_type='transmission')
#fuel_unit_cell_out = openmc.model.HexagonalPrism(edge_length=2.598076211, orientation='y', boundary_type='reflective')

fuel_region = -fuel_out & -ceiling & +floor
gap_region = +fuel_out & -cladding_in & -ceiling & +floor
cladding_region = +cladding_in & -cladding_out & -ceiling & +floor
moderator_region = +cladding_out & -ceiling & +floor
top_moderator_region = +ceiling & -RPV_ceiling
bottom_moderator_region = -floor & +RPV_floor

fuel_cell = openmc.Cell(cell_id=1, name='Fuel', fill=fuel, region=fuel_region)
gap_cell = openmc.Cell(cell_id=2, name='Gap', fill=gap, region=gap_region)
cladding_cell = openmc.Cell(cell_id=3, name='Cladding', fill=clad, region=cladding_region)
moderator_cell = openmc.Cell(cell_id=4, name='Coolant', fill=moderator, region=moderator_region)
top_moderator_cell = openmc.Cell(cell_id=5, name='Coolant On Top', fill=moderator, region=top_moderator_region)
bottom_moderator_cell = openmc.Cell(cell_id=6, name='Coolant On Bottom', fill=moderator, region=bottom_moderator_region)


fuel_u = openmc.Universe(universe_id=100, name='Fuel Pin', cells=(fuel_cell, gap_cell, cladding_cell, moderator_cell, top_moderator_cell, bottom_moderator_cell))

# CONTROL ROD

absorber_out = openmc.ZCylinder(surface_id=9, r=1.94, boundary_type='transmission')
absorber_clad = openmc.ZCylinder(surface_id=10, r=2, boundary_type='transmission')
#absorber_unit_cell_out = openmc.model.HexagonalPrism(edge_length=2.598076211, orientation='y', boundary_type='reflective')


absorber_region = -absorber_out & -ceiling & +floor
absorber_clad_region = +absorber_out & -absorber_clad & -ceiling & +floor
absorber_moderator_region = +absorber_clad & -ceiling & +floor
absorber_top_moderator_region = +ceiling & -RPV_ceiling
absorber_bottom_moderator_region = -floor & +RPV_floor

absorber_cell = openmc.Cell(cell_id=7, name='CR Absorber', fill=absorber, region=absorber_region)
absorber_clad_cell = openmc.Cell(cell_id=8, name='CR Clad', fill=clad, region=absorber_clad_region)
absorber_moderator_cell = openmc.Cell(cell_id=9, name='CR Moderator', fill=moderator, region=absorber_moderator_region)
absorber_top_moderator_cell = openmc.Cell(cell_id=10, name='CR Moderator Top', fill=moderator, region=absorber_top_moderator_region)
absorber_bottom_moderator_cell = openmc.Cell(cell_id=11, name='CR Moderator Bottom', fill=moderator, region=absorber_bottom_moderator_region)

control_rod_u = openmc.Universe(universe_id=200, name='Control Rod', cells=(absorber_cell, absorber_clad_cell, absorber_moderator_cell, absorber_top_moderator_cell, absorber_bottom_moderator_cell))

# WATER ROD (for all rods out)

water_rod_out = openmc.ZCylinder(surface_id=12, r=2, boundary_type='transmission')

region_water_rod = -water_rod_out & -ceiling & +floor
region_water_moderator = +water_rod_out & -ceiling & +floor
region_water_moderator_top = +ceiling & +ceiling & -RPV_ceiling
region_water_moderator_bottom = -floor & +RPV_floor

water_cell = openmc.Cell(cell_id=22, name='Water Filled Rod', fill=moderator, region=region_water_rod)
water_moderator_cell = openmc.Cell(cell_id=23, name='Water Filled Rod', fill=moderator, region=region_water_moderator)
water_top_cell = openmc.Cell(cell_id=24, name='Water Filled Rod', fill=moderator, region=region_water_moderator_top)
water_bottom_cell = openmc.Cell(cell_id=25, name='Water Filled Rod', fill=moderator, region=region_water_moderator_bottom)

water_rod_u = openmc.Universe(universe_id=59, name='water filled rod', cells=(water_cell, water_moderator_cell, water_top_cell, water_bottom_cell))

# HEXAGONAL LATTICE

########
# Water to surround everything
########

all_moderator_cell=openmc.Cell(fill=moderator)
outer_u = openmc.Universe(cells=(all_moderator_cell,))

########
# Assembly Formation (Hexagonal Lattice)
########

fuel_assembly_lattice = openmc.HexLattice(name='Assembly Fuel Lattice')
fuel_assembly_lattice.center = (0., 0.)
fuel_assembly_lattice.pitch = (4.4,)
fuel_assembly_lattice.orientation = 'y'
fuel_assembly_lattice.outer = outer_u

print(fuel_assembly_lattice.show_indices(num_rings=4))

ring_4 = [fuel_u]*18
#ring_3 = [control_rod_u] + [fuel_u]*2 + [control_rod_u] + [fuel_u]*2 + [control_rod_u] + [fuel_u]*2 + [control_rod_u] + [fuel_u]*2
ring_3 = [water_rod_u] + [fuel_u]*2 + [water_rod_u] + [fuel_u]*2 + [water_rod_u] + [fuel_u]*2 + [water_rod_u] + [fuel_u]*2
#ring_3 = [fuel_u]*12
ring_2 = [fuel_u]*6
#ring_1 = [control_rod_u]
ring_1 = [water_rod_u]
#ring_1 = [fuel_u]

fuel_assembly_lattice.universes = [ring_4, ring_3, ring_2, ring_1]
print(fuel_assembly_lattice)

hex_outer_in_surface = -openmc.model.HexagonalPrism(edge_length=18, orientation='y')

assembly_cell = openmc.Cell(fill=fuel_assembly_lattice, region=hex_outer_in_surface)

hex_outer_in_fill = openmc.Cell(fill=moderator, region=~hex_outer_in_surface)

assembly_u = openmc.Universe(universe_id=300, cells=(assembly_cell, hex_outer_in_fill))

# FILL ENTIRE CORE WITH ASSEMBLIES

core_lattice = openmc.HexLattice (name='Reactor Core')
core_lattice.center = (0., 0.)
core_lattice.pitch = (29,)
core_lattice.orientation='x'
core_lattice.outer = outer_u

print(core_lattice.show_indices(num_rings=5))

core_ring_0 = [assembly_u]*24
core_ring_1 = [assembly_u]*18
core_ring_2 = [assembly_u]*12
core_ring_3 = [assembly_u]*6
core_ring_4 = [assembly_u]

core_lattice.universes = [core_ring_0, core_ring_1, core_ring_2, core_ring_3, core_ring_4]
print(core_lattice)

core_in_surface = -openmc.model.HexagonalPrism(edge_length=300, orientation='y')

core_cell = openmc.Cell(fill=core_lattice, region=core_in_surface)

core_outer_fill = openmc.Cell(fill=moderator, region=(~core_in_surface) & bounding_region)

core_u = openmc.Universe(cells=(core_cell, core_outer_fill))

root_cell = openmc.Cell(name='absolute boundary', fill=core_u, region=bounding_region)
root_u = openmc.Universe(name='absolute', cells=(root_cell,))




fuel.volume = (500 * math.pi * fuel_out.r**2) * (32) * (61)

geometry = openmc.Geometry(root_u)
geometry.export_to_xml()

print(geometry)
print(mat_list)

###############################################################################
# Define problem settings
###############################################################################

settings = openmc.Settings()
settings.batches = 100
settings.inactive = 20
settings.particles = 10000
settings.temperature = {'method' : 'interpolation'}

settings.export_to_xml()

print(settings)


##############################################
#               MODEL
##############################################
model = openmc.Model(geometry=geometry, materials=mat_list, settings=settings)

chain_file = 'chain_simple.xml'

operator = openmc.deplete.CoupledOperator(
    model,
    chain_file,
)

time_to_seconds_factor = 24 * 60 * 60


time_steps = [0.1*time_to_seconds_factor, 0.2*time_to_seconds_factor, 0.4*time_to_seconds_factor, 0.8*time_to_seconds_factor, 1.6*time_to_seconds_factor, 3.2*time_to_seconds_factor] 

#[0.1*time_to_seconds_factor, 0.2*time_to_seconds_factor, 0.4*time_to_seconds_factor, 0.8*time_to_seconds_factor, 1.6*time_to_seconds_factor, 3.2*time_to_seconds_factor, 3.2*time_to_seconds_factor, 3.2*time_to_seconds_factor, 3.2*time_to_seconds_factor, 3.2*time_to_seconds_factor, 6.4*time_to_seconds_factor, 6.4*time_to_seconds_factor, 6.4*time_to_seconds_factor, 6.4*time_to_seconds_factor, 6.4*time_to_seconds_factor, 6.4*time_to_seconds_factor, 6.4*time_to_seconds_factor, 20*time_to_seconds_factor, 50*time_to_seconds_factor, 50*time_to_seconds_factor, 50*time_to_seconds_factor, 50*time_to_seconds_factor, 50*time_to_seconds_factor, 50*time_to_seconds_factor, 50*time_to_seconds_factor, 50*time_to_seconds_factor, 50*time_to_seconds_factor, 50*time_to_seconds_factor, 100*time_to_seconds_factor, 100*time_to_seconds_factor, 100*time_to_seconds_factor, 100*time_to_seconds_factor, 100*time_to_seconds_factor, 100*time_to_seconds_factor, 100*time_to_seconds_factor, 100*time_to_seconds_factor, 100*time_to_seconds_factor, 200*time_to_seconds_factor, 200*time_to_seconds_factor, 200*time_to_seconds_factor, 200*time_to_seconds_factor, 200*time_to_seconds_factor, 200*time_to_seconds_factor, 200*time_to_seconds_factor, 200*time_to_seconds_factor, 200*time_to_seconds_factor, 200*time_to_seconds_factor] 
power = 25e6

integrator = openmc.deplete.CECMIntegrator(
    operator,
    time_steps,
    power,
)
integrator.integrate()

##############################################
#          DEPLETION RESULTS
##############################################

results = openmc.deplete.Results("depletion_results.h5")
time, keff = results.get_keff(time_units='d')

plt.errorbar(time, keff[:,0], keff[:,1])
plt.xlabel("Days")
plt.ylabel("keff")
plt.title("Reactor Depletion (Whole-Core Fuel Material)")
plt.savefig('letdown.png')
plt.show()



# ################################
#  Plots Definition
# ################################

ww = 500
plot1 = openmc.Plot()
plot1.width = (ww,ww)
plot1.basis = 'xy'
plot1.origin =(0.0, 0.0, 0.0)
plot1.color_by = 'material'
plot1.colors = {
    fuel: 'purple',
    clad: 'tan',
    moderator: 'blue',
    gap: 'red',
    absorber: 'deeppink'
}

plot1.filename = 'RadialView'
plots = openmc.Plots([plot1])
plots.export_to_xml()

openmc.plot_geometry()
openmc.run()
