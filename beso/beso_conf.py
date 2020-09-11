# this is the configuration file with input values, which will be executed as python commands

# BASIC INPUTS:

path = "."  # path to the working directory (without whitespaces) where the initial file is located
#path = "."  # example - in the current working directory
#path = "~/tmp/beso/"  # Linux example
#path = "D:\\tmp\\"  # Windows example

file_name = "2DBeam.inp"  # file with prepared linear static analysis

elset_name = "SolidMaterialElementGeometry2D"  # string with name of the element set in .inp file (CASE sensitive!)
domain_optimized[elset_name] = True  # True - optimized domain, False - elements will not be removed
domain_density[elset_name] = [1e-6, 1]  # equivalent density of the domain material for states of switch_elm
domain_thickness[elset_name] = [1.0, 1.0]  # thickness of shell elements for states of switch_elm
domain_offset[elset_name] = 0.0  # offset of shell elements
domain_orientation[elset_name] = []  # orientations for each state referring to inp file,
                                     # e.g. for 2 states ["or1", "or1"], for isotropic material use empty list []
domain_FI[elset_name] = [[("stress_von_Mises", 450.0e6)],  # inner tuples () for separate Failure indices
                         [("stress_von_Mises", 450.0)]]  # new inner list [] for the next state of switch_elm
                        # Failure Indices definition in python tuples (separate FI for each element state if there are more lists)
                        # Failure Indice FI = element stress / allowable value
                        # Failure Indices are not evaluated if they are not defined here, i.e. domain_FI[elset_name] = [],
                        # and then optimization_base must not be "failure_index"
                        # examples:
                        # [("stress_von_Mises", 450.0)]  # for von Mises stress give only allowable stress
domain_material[elset_name] = ["*ELASTIC \n210000e-6,  0.3",  # material definition after CalculiX *MATERIAL card, use \n for line break
                               "*ELASTIC \n210000,  0.3"]  # next string for the next state of switch_elm
domain_same_state[elset_name] = False  # False - element states can differ,
                                       # "max" - domain elements have common state given by maximum sensitivity
                                       # "average" - domain elements have common state given by average sensitivity
# copy this block for defining properties of the next domain

mass_goal_ratio = 0.4  # the goal mass as a fragment of the full mass of optimized domains,
                       # i.e. fragment of mass evaluated from effective density and volumes of optimized elements in the highest state

filter_list = [["simple", 2]]  # [[filter type, range], [next filter type, range]]
                            # filter types:
                            # "simple" - averages sensitivity number with surroundings (suffer from boundary sticking?),
                            # works on sensitivities
# ADVANCED INPUTS:

optimization_base = "failure_index"  # "stiffness" - maximization of stiffness (minimization of compliance)
                                     # "failure_index" sensitivity number is given by FI/density

cpu_cores = 0  # 0 - use all processor cores, N - will use N number of processor cores

FI_violated_tolerance = 1  # N - freeze mass if, compared to initial state, there is N more elements with FI >= 1
decay_coefficient = -0.2  # k - exponential decay coefficient to dump mass_additive_ratio and mass_removal_ratio after freezing mass
                          # fits to equation: exp(k * i), where i is iteration number from triggering by exceeding FI_violated_tolerance
                          # k = -0.2 ~ after 10 iterations slows down approximately 10 times
                          # k = 0 ~ no decaying

                             # TODO: If we know we want COMPOSITE for S8R and S6 shell elements, then why make it a config option?
shells_as_composite = False  # True - use more integration points to catch bending stresses (ccx 2.12 WILL FAIL for other than S8R and S6 shell elements)
                             # False - use ordinary shell section
reference_points = "integration points"  # "integration points" - read int. pt values (stresses) from .dat file,
reference_value = "max"  # "max" - maximal value on element,
sensitivity_averaging = False  # True - averaging sensitivity numbers with previous iteration, False - do not average

mass_addition_ratio = 0.01  # mass to be added in each iteration
mass_removal_ratio = 0.03  # mass to be removed in each iteration
ratio_type = "relative"  # "relative" - ratios of actual mass
compensate_state_filter = True  # True - if state filter changes iteration mass, next iteration will compensate it
                                 # False - do nothing

iterations_limit = "auto"  # "auto" - automatic estimate, <integer> - the maximum allowable number of iterations
tolerance = 1e-3  # the maximum relative difference in mean stress in optimization domains between the last 5 iterations needed to finish

displacement_graph = []  # plot maximal displacement of the given node set, e.g.
                         # [] - do not plot it
                         # [["nset1", "ux"], ["nset2", "uy"]] - plot maximal x displacement of node set nset1 and maximal y displacement of node set nset2
                         # [["nset1", "total"]] - plot maximal total displacement of node set nset1, same as [["nset", "sqrt(ux**2 + uy**2 + uz**2)"]]
save_iteration_results = 10  # every i-th iteration save temporary results, 0 - save only final results
save_solver_files = ""  # not removed outputs from the solver, e.g. "inp frd dat cvg sta" will preserve all outputs in iterations defined by save_iteration_results
save_resulting_format = "inp vtk" # "frd" or "inp" format of resulting meshes (each state separately in own mesh file)
                                  # "vtk" output for viewing in Paraview (renumbered mesh, states, sensitivity numbers, failure indices)
                                  # "csv" simple tabelized data - also possible to import into Paraview (element centres of gravity, states, sensitivity numbers, failure indices)
