# optimization program using CalculiX solver
# BESO (Bi-directional Evolutionary Structural Optimization Method)

import numpy as np
import matplotlib.pyplot as plt
import multiprocessing
import os
import subprocess
import sys
import time
import logging
import shutil
import beso.beso_lib as beso_lib
import beso.beso_filters as beso_filters
from .import_inp import import_inp


start_time = time.time()

# initialization of variables - default values
domain_optimized = {}
domain_density = {}
domain_thickness = {}
domain_offset = {}
domain_orientation = {}
domain_material = {}
path = "."
file_name = "Plane_Mesh.inp"
mass_goal_ratio = 0.4
filter_list = [["simple", 0]]
optimization_base = "stiffness"
decay_coefficient = -0.2
shells_as_composite = False
sensitivity_averaging = False
mass_addition_ratio = 0.01
mass_removal_ratio = 0.03
save_iteration_results = 1
save_solver_files = ""
save_resulting_format = "inp vtk"

# read configuration file to fill variables listed above
beso_dir = os.path.dirname(__file__)
exec(open(os.path.join(beso_dir, "beso_conf.py")).read())

log_filename = file_name[:-4] + ".log"
logging.basicConfig(filename=log_filename, filemode='a', level=logging.INFO)

domains_from_config = domain_optimized.keys()

# default values if not defined by user
for dn in domain_optimized:
    try:
        domain_thickness[dn]
    except KeyError:
        domain_thickness[dn] = []
    try:
        domain_offset[dn]
    except KeyError:
        domain_offset[dn] = 0.0
    try:
        domain_orientation[dn]
    except KeyError:
        domain_orientation[dn] = []

number_of_states = 0  # find number of states possible in elm_states
for dn in domains_from_config:
    number_of_states = max(number_of_states, len(domain_density[dn]))

# writing log file with settings
msg = "\n"
msg += "---------------------------------------------------\n"
msg += ("file_name = %s\n" % file_name)
msg += ("Start at    " + time.ctime() + "\n\n")
for dn in domain_optimized:
    msg += ("elset_name              = %s\n" % dn)
    msg += ("domain_optimized        = %s\n" % domain_optimized[dn])
    msg += ("domain_density          = %s\n" % domain_density[dn])
    msg += ("domain_thickness        = %s\n" % domain_thickness[dn])
    msg += ("domain_offset           = %s\n" % domain_offset[dn])
    msg += ("domain_orientation      = %s\n" % domain_orientation[dn])
    msg += ("domain_material         = %s\n" % domain_material[dn])
    msg += "\n"
msg += ("mass_goal_ratio         = %s\n" % mass_goal_ratio)
msg += ("filter_list             = %s\n" % filter_list)
msg += ("optimization_base       = %s\n" % optimization_base)
msg += ("decay_coefficient       = %s\n" % decay_coefficient)
msg += ("shells_as_composite     = %s\n" % shells_as_composite)
msg += ("mass_addition_ratio     = %s\n" % mass_addition_ratio)
msg += ("mass_removal_ratio      = %s\n" % mass_removal_ratio)
msg += ("sensitivity_averaging   = %s\n" % sensitivity_averaging)
msg += ("save_iteration_results  = %s\n" % save_iteration_results)
msg += ("save_solver_files       = %s\n" % save_solver_files)
msg += ("save_resulting_format   = %s\n" % save_resulting_format)
msg += "\n"
file_name = os.path.join(path, file_name)
logging.info(msg)

# mesh and domains importing
# plane_strain, plane_stress, axisymmetry "special type" sets are only used when writing the inp in each iteration
# opt_domains is short for "optimized domains"; Just a list of element numbers.
[nodes, Elements, domains, opt_domains, plane_strain, plane_stress, axisymmetry] = import_inp(
    file_name, domains_from_config, domain_optimized)
domain_shells = {}
domain_volumes = {}
for dn in domains_from_config:  # distinguishing shell elements and volume elements
    # Shell elements are surface elements, they have no thickness
    domain_shells[dn] = set(domains[dn]).intersection(list(Elements.tria3.keys()) + list(Elements.tria6.keys()) +
                                                      list(Elements.quad4.keys()) + list(Elements.quad8.keys()))
    # Volume elements are three-dimensional and have a volume.
    # Volume elements are also called solids, bricks or tets. The last is short for tetrahedrons.
    domain_volumes[dn] = set(domains[dn]).intersection(list(Elements.tetra4.keys()) + list(Elements.tetra10.keys()) +
                                                       list(Elements.hexa8.keys()) + list(Elements.hexa20.keys()) +
                                                       list(Elements.penta6.keys()) + list(Elements.penta15.keys()))

# initialize element states
elm_states = {}
for dn in domains_from_config:
    for en in domains[dn]:
        elm_states[en] = len(domain_density[dn]) - \
            1  # set to highest state

# computing volume or area, and centre of gravity of each element
[cg, cg_min, cg_max, volume_elm, area_elm] = beso_lib.elm_volume_cg(
    file_name, nodes, Elements)
mass = [0.0]
mass_full = 0  # sum from initial states TODO make it independent on starting elm_states?

for dn in domains_from_config:
    if domain_optimized[dn] is True:
        for en in domain_shells[dn]:
            mass[0] += domain_density[dn][elm_states[en]] * \
                area_elm[en] * domain_thickness[dn][elm_states[en]]
            mass_full += domain_density[dn][len(domain_density[dn]) - 1] * area_elm[en] * domain_thickness[dn][
                len(domain_density[dn]) - 1]
        for en in domain_volumes[dn]:
            mass[0] += domain_density[dn][elm_states[en]] * volume_elm[en]
            mass_full += domain_density[dn][len(
                domain_density[dn]) - 1] * volume_elm[en]
print("initial optimization domains mass {}" .format(mass[0]))

# iterations limit - default "auto"matic setting
iterations_limit = 0
m = mass[0] / mass_full
it = 0
if mass_removal_ratio - mass_addition_ratio > 0:
    while m > mass_goal_ratio:
        m -= m * (mass_removal_ratio - mass_addition_ratio)
        it += 1
else:
    while m < mass_goal_ratio:
        m += m * (mass_addition_ratio - mass_removal_ratio)
        it += 1
iterations_limit = it + 25
print("\niterations_limit set automatically to %s" % iterations_limit)
msg = ("\niterations_limit        = %s\n" % iterations_limit)
logging.info(msg)

# PREPARING PARAMETERS FOR FILTERING SENSITIVITY NUMBERS
# ======================================================
"""
weight_factor2 is a dictionary where the key is a tuple of two element numbers, and value is some kind of weight.
               first element in key is min, second element is max
{
    (157, 171): 0.9990422039929501,
    (157, 180): 0.5957267190986004,
    (157, 181): 0.5863017762553826,
"""
weight_factor2 = {}

"""
near_elm is a dictionary of element number by list of near element numbers.
{
    157: [171, 180, 181, 197, 1234, 1235, 1236, 198],
    171: [157, 197, 1234, 1235, 1236, 164, 198, 199, 172],
    180: [157, 181, 197, 1236],
    ...
}
"""
near_elm = {}
for ft in filter_list:
    if ft[0] and ft[1]:
        f_range = ft[1]
        domains_to_filter = opt_domains
        [weight_factor2, near_elm] = beso_filters.prepare2s(cg, cg_min, cg_max, f_range, domains_to_filter,
                                                            weight_factor2, near_elm)
# =============================================================================================================

# writing log table header
msg = "\n"
msg += "domain order: \n"
dorder = 0
for dn in domains_from_config:
    msg += str(dorder) + ") " + dn + "\n"
    dorder += 1
msg += "\n   i              mass"
if optimization_base == "stiffness":
    msg += "    ener_dens_mean"

msg += "\n"
logging.info(msg)

# preparing for writing quick results
file_name_resulting_states = os.path.join(path, "resulting_states")
[en_all_vtk, associated_nodes] = beso_lib.vtk_mesh(
    file_name_resulting_states, nodes, Elements)

# ===================================================
#                     MAIN LOOP
# ===================================================

# ITERATION CYCLE
sensitivity_number = {}
sensitivity_number_old = {}
energy_density_mean = []  # list of mean energy density in every iteration
i = 0
i_violated = 0
continue_iterations = True
check_tolerance = False
elm_states_before_last = {}
elm_states_last = elm_states
oscillations = False
# the maximum relative difference in mean stress in optimization domains between the last 5 iterations needed to finish
TOLERANCE = 0.001

# set an environmental variable driving number of cpu cores to be used by CalculiX
cpu_cores = multiprocessing.cpu_count()
os.putenv('OMP_NUM_THREADS', str(cpu_cores))
while True:
    # creating the new .inp file for CalculiX
    file_nameW = os.path.join(path, "file" + str(i).zfill(3))
    beso_lib.write_inp(file_name, file_nameW, elm_states, number_of_states, domains, domains_from_config,
                       domain_optimized, domain_thickness, domain_offset, domain_orientation, domain_material,
                       domain_volumes, domain_shells, plane_strain, plane_stress, axisymmetry, save_iteration_results,
                       i, shells_as_composite, optimization_base)
    # running CalculiX analysis
    ccx_path = shutil.which('ccx')
    if ccx_path is None:
        print('ccx must be installed, and available in your PATH.')
        exit(0)
    if sys.platform == 'linux':
        subprocess.call([ccx_path, file_nameW], cwd=path)
    else:
        subprocess.call([ccx_path, file_nameW], cwd=path, shell=True)

    # reading results and computing failure indices
    # if reference_points == "integration points" or optimization_base == stiffness
    # from .dat file
    [energy_density_step, energy_density_eigen] = \
        beso_lib.import_FI_int_pt(file_nameW, domains, file_name, elm_states,
                                  domains_from_config)

    # check if results were found
    missing_ccx_results = False
    if (optimization_base == "stiffness") and (not energy_density_step):
        missing_ccx_results = True
    if missing_ccx_results:
        msg = "CalculiX results not found, check CalculiX for errors."
        logging.error("\nERROR: " + msg + "\n")
        assert False, msg

    # handling with more steps
    # {en1: [energy from sn1, energy from sn2, ...], en2: [], ...}
    energy_density_enlist = {}
    dno = 0
    for dn in domains_from_config:
        for en in domains[dn]:
            if optimization_base == "stiffness":
                energy_density_enlist[en] = []
            for sn in range(len(energy_density_step)):
                if optimization_base == "stiffness":
                    energy_density_enlist[en].append(energy_density_step[sn][en])
            if optimization_base == "stiffness":
                sensitivity_number[en] = max(energy_density_enlist[en])
        dno += 1

    # filtering sensitivity number
    kp = 0
    kn = 0
    for ft in filter_list:
        if ft[0] and ft[1]:
            domains_to_filter = opt_domains
            sensitivity_number = beso_filters.run2(file_name, sensitivity_number, weight_factor2, near_elm,
                                                   domains_to_filter)

    # TODO: sensitivity_averaging is a config option.
    #       why is it needed, and what does it do?
    #       If it should stabilize iterations, then why not always use it?
    #       See Andrea_De_Marco_MSc_thesis.pdf p. 18
    #       Application of Evolutionary Structural Optimization to Reinforced Concrete Structures
    #       Andrea De Marco
    if sensitivity_averaging:
        for en in opt_domains:
            # averaging with the last iteration should stabilize iterations
            if i > 0:
                sensitivity_number[en] = (
                    sensitivity_number[en] + sensitivity_number_old[en]) / 2.0
            # for averaging in the next step
            sensitivity_number_old[en] = sensitivity_number[en]

    # computing mean stress from maximums of each element in all steps in the optimization domain
    if optimization_base == "stiffness":
        energy_density_mean_sum = 0  # mean of element maximums
    for dn in domain_optimized:
        if domain_optimized[dn] is True:
            for en in domain_shells[dn]:
                mass_elm = domain_density[dn][elm_states[en]] * \
                    area_elm[en] * domain_thickness[dn][elm_states[en]]
                if optimization_base == "stiffness":
                    energy_density_mean_sum += max(
                        energy_density_enlist[en]) * mass_elm
            for en in domain_volumes[dn]:
                mass_elm = domain_density[dn][elm_states[en]] * volume_elm[en]
                if optimization_base == "stiffness":
                    energy_density_mean_sum += max(
                        energy_density_enlist[en]) * mass_elm
    if optimization_base == "stiffness":
        energy_density_mean.append(energy_density_mean_sum / mass[i])
        print("energy_density_mean    = {}".format(energy_density_mean[i]))

    # writing log table row
    msg = str(i).rjust(4, " ") + " " + str(mass[i]).rjust(17, " ") + " "
    if optimization_base == "stiffness":
        msg += " " + str(energy_density_mean[i]).rjust(17, " ")
    logging.info(msg)

    # export element values
    if save_iteration_results and np.mod(float(i), save_iteration_results) == 0:
        if "csv" in save_resulting_format:
            beso_lib.export_csv(domains_from_config, domains, file_nameW, cg,
                                elm_states, sensitivity_number)
        if "vtk" in save_resulting_format:
            beso_lib.export_vtk(file_nameW, nodes, Elements, elm_states, sensitivity_number)

    # relative difference in a mean energy density for the last 5 iterations must be < tolerance
    if len(energy_density_mean) > 5:
        difference_last = []
        for last in range(1, 6):
            difference_last.append(abs(
                energy_density_mean[i] - energy_density_mean[i - last]) / energy_density_mean[i])
        difference = max(difference_last)
        if check_tolerance is True:
            print("maximum relative difference in energy_density_mean for the last 5 iterations = {}".format(
                difference))
        if difference < TOLERANCE:
            continue_iterations = False
        elif energy_density_mean[i] == energy_density_mean[i - 1] == energy_density_mean[i - 2]:
            continue_iterations = False
            print(
                "energy_density_mean[i] == energy_density_mean[i-1] == energy_density_mean[i-2]")

    # finish or start new iteration
    if continue_iterations is False or i >= iterations_limit:
        if not(save_iteration_results and np.mod(float(i), save_iteration_results) == 0):
            if "csv" in save_resulting_format:
                beso_lib.export_csv(domains_from_config, domains, file_nameW, cg,
                                    elm_states, sensitivity_number)
            if "vtk" in save_resulting_format:
                beso_lib.export_vtk(file_nameW, nodes, Elements, elm_states, sensitivity_number)
        break
    i += 1  # iteration number
    print("\n----------- new iteration number %d ----------" % i)

    # set mass_goal for i-th iteration, check for number of violated elements
    if mass_removal_ratio - mass_addition_ratio > 0:  # removing from initial mass
        if mass[i - 1] <= mass_goal_ratio * mass_full:  # goal mass achieved
            if not i_violated:
                i_violated = i  # to start decaying
                check_tolerance = True
            try:
                mass_goal_i
            except NameError:
                msg = "\nWARNING: mass goal is lower than initial mass. Check mass_goal_ratio."
                logging.warning(msg + "\n")
        else:
            mass_goal_i = mass_goal_ratio * mass_full
    else:  # adding to initial mass  TODO include stress limit
        if mass[i - 1] < mass_goal_ratio * mass_full:
            mass_goal_i = mass[i - 1] + \
                (mass_addition_ratio - mass_removal_ratio) * mass_full
        elif mass[i - 1] >= mass_goal_ratio * mass_full:
            if not i_violated:
                i_violated = i  # to start decaying
                check_tolerance = True
            mass_goal_i = mass_goal_ratio * mass_full

    # switch element states
    mass_referential = mass[i - 1]
    [elm_states, mass] = beso_lib.switching(elm_states, domains_from_config, domain_optimized, domains,
                                            domain_density, domain_thickness, domain_shells, area_elm, volume_elm,
                                            sensitivity_number, mass, mass_referential, mass_addition_ratio,
                                            mass_removal_ratio, decay_coefficient, i_violated, i, mass_goal_i)

    # export the present mesh
    beso_lib.append_vtk_states(
        file_name_resulting_states, i, en_all_vtk, elm_states)

    file_nameW2 = os.path.join(path, "file" + str(i).zfill(3))
    if save_iteration_results and np.mod(float(i), save_iteration_results) == 0:
        if "frd" in save_resulting_format:
            beso_lib.export_frd(file_nameW2, nodes, Elements,
                                elm_states, number_of_states)
        if "inp" in save_resulting_format:
            beso_lib.export_inp(file_nameW2, nodes, Elements,
                                elm_states, number_of_states)

    # check for oscillation state
    if elm_states_before_last == elm_states:  # oscillating state
        msg = "\nOSCILLATION: model turns back to " + \
            str(i - 2) + "th iteration.\n"
        logging.info(msg)
        print(msg)
        oscillations = True
        break
    elm_states_before_last = elm_states_last.copy()
    elm_states_last = elm_states.copy()

    # removing solver files
    if save_iteration_results and np.mod(float(i - 1), save_iteration_results) == 0:
        if "inp" not in save_solver_files:
            os.remove(file_nameW + ".inp")
        if "dat" not in save_solver_files:
            os.remove(file_nameW + ".dat")
        if "frd" not in save_solver_files:
            os.remove(file_nameW + ".frd")
        if "sta" not in save_solver_files:
            os.remove(file_nameW + ".sta")
        if "cvg" not in save_solver_files:
            os.remove(file_nameW + ".cvg")
    else:
        os.remove(file_nameW + ".inp")
        os.remove(file_nameW + ".dat")
        os.remove(file_nameW + ".frd")
        os.remove(file_nameW + ".sta")
        os.remove(file_nameW + ".cvg")


# ===================================================
#                   END OF MAIN LOOP
# ===================================================

# ---------------------------------------------------------------------

# EXPORTING RESULT MESH
# ================================
if not (save_iteration_results and np.mod(float(i), save_iteration_results) == 0):
    if "frd" in save_resulting_format:
        beso_lib.export_frd(file_nameW, nodes, Elements,
                            elm_states, number_of_states)
    if "inp" in save_resulting_format:
        beso_lib.export_inp(file_nameW, nodes, Elements,
                            elm_states, number_of_states)
# ================================

# ---------------------------------------------------------------------

# REMOVING SOLVER FILES
# TODO: This block is duplicated above.
# ================================
if "inp" not in save_solver_files:
    os.remove(file_nameW + ".inp")
if "dat" not in save_solver_files:
    os.remove(file_nameW + ".dat")
if "frd" not in save_solver_files:
    os.remove(file_nameW + ".frd")
if "sta" not in save_solver_files:
    os.remove(file_nameW + ".sta")
if "cvg" not in save_solver_files:
    os.remove(file_nameW + ".cvg")
# ================================

# ---------------------------------------------------------------------

# PRINT TOTAL TIME
# =====================================================================
total_time = time.time() - start_time
total_time_h = int(total_time / 3600.0)
total_time_min = int((total_time % 3600) / 60.0)
total_time_s = int(round(total_time % 60))
msg = "\n"
msg += ("Finished at  " + time.ctime() + "\n")
msg += ("Total time   " + str(total_time_h) + " h " +
        str(total_time_min) + " min " + str(total_time_s) + " s\n")
msg += "\n"
logging.info(msg)
print("total time: " + str(total_time_h) + " h " +
      str(total_time_min) + " min " + str(total_time_s) + " s")
# =====================================================================

# ---------------------------------------------------------------------

# TODO: Separate plotting from main beso algorithm
#       Remove dependency on matplotlib
# ==============================================================================
# BEGIN PLOTTING
# ==============================================================================
plt.close("all")

fn = 0  # figure number
# plot mass
fn += 1
plt.figure(fn)
plt.plot(range(i+1), mass, label="mass")
plt.title("Mass of optimization domains")
plt.xlabel("Iteration")
plt.ylabel("Mass")
plt.grid()
plt.tight_layout()
plt.savefig(os.path.join(path, "Mass"), dpi=100)

if oscillations is True:
    i -= 1  # because other values for i-th iteration are not evaluated

if optimization_base == "stiffness":
    # plot mean energy density
    fn += 1
    plt.figure(fn)
    plt.plot(range(i+1), energy_density_mean)
    plt.title("Mean Energy Density weighted by element mass")
    plt.xlabel("Iteration")
    plt.ylabel("energy_density_mean")
    plt.grid()
    plt.tight_layout()
    plt.savefig(os.path.join(path, "energy_density_mean"), dpi=100)

plt.show()
# ==============================================================================
