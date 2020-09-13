# this is the configuration file with input values, which will be executed as python commands

# BASIC INPUTS:

path = "."  # path to the working directory (without whitespaces) where the initial file is located
#path = "."  # example - in the current working directory
#path = "~/tmp/beso/"  # Linux example
#path = "D:\\tmp\\"  # Windows example

file_name = "2DBeam.inp"  # file with prepared linear static analysis

elset_name = "SolidMaterialElementGeometry2D"  # string with name of the element set in .inp file (CASE sensitive!)
# TODO: Instead of sets of tuples, and we have domain configuration dictionaries?
domain_optimized[elset_name] = True  # True - optimized domain, False - elements will not be removed
domain_density[elset_name] = [1e-6, 1]  # equivalent density of the domain material for states of switch_elm
# TODO: Can we just parse this from *SHELL SECTION in the INP file instead?
domain_thickness[elset_name] = [1.0, 1.0]  # thickness of shell elements for states of switch_elm
# TODO: Can we just parse OFFSET from *SHELL SECTION?
#       It's only used for re-writing INP file.
domain_offset[elset_name] = 0.0  # offset of shell elements
                                     # ISOTROPIC - identical values in all directions - glass and metal
                                     # ANISOTROPIC - different values in all directions - wood and composites
domain_orientation[elset_name] = []  # orientations for each state referring to inp file,
                                     # e.g. for 2 states ["or1", "or1"], for isotropic material use empty list []
# TODO: Can we just parse this from *MATERIAL section in the INP file instead?
domain_material[elset_name] = ["*ELASTIC \n210000e-6,  0.3",  # material definition after CalculiX *MATERIAL card, use \n for line break
                               "*ELASTIC \n210000,  0.3"]  # next string for the next state of switch_elm
# copy this block for defining properties of the next domain

mass_goal_ratio = 0.40  # the goal mass as a fragment of the full mass of optimized domains,
                        # i.e. fragment of mass evaluated from effective density and volumes of optimized elements in the highest state

# TODO: Can we automatically determine the filter radius from mesh element size?
#       Heuristic is element size * 2 or * 3.
filter_radius = 2
# averages sensitivity number with surroundings (suffer from boundary sticking?),
# works on sensitivities

# ADVANCED INPUTS:
                             # TODO: If we know we want COMPOSITE for S8R and S6 shell elements, then why make it a config option?
shells_as_composite = False  # True - use more integration points to catch bending stresses (ccx 2.12 WILL FAIL for other than S8R and S6 shell elements)
                             # False - use ordinary shell section
sensitivity_averaging = False  # True - averaging sensitivity numbers with previous iteration, False - do not average

mass_addition_ratio = 0.01  # mass to be added in each iteration
mass_removal_ratio = 0.03  # mass to be removed in each iteration
save_iteration_results = 10  # every i-th iteration save temporary results, 0 - save only final results
save_solver_files = ""  # not removed outputs from the solver, e.g. "inp frd dat cvg sta" will preserve all outputs in iterations defined by save_iteration_results
save_resulting_format = "inp vtk" # "frd" or "inp" format of resulting meshes (each state separately in own mesh file)
                                  # "vtk" output for viewing in Paraview (renumbered mesh, states, sensitivity numbers, failure indices)
                                  # "csv" simple tabelized data - also possible to import into Paraview (element centres of gravity, states, sensitivity numbers, failure indices)
