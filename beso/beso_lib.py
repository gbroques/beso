import numpy as np
import operator
from math import *
import logging

# function for computing volumes or area (shell elements) and centres of gravity
# approximate for 2nd order elements!
# A Linear element or First order element will have nodes only at the corners.
# However, a Second order element or Quadratic element will have mid side nodes in addition to nodes at the corner.
# https://www.quora.com/Finite-Element-Analysis-whats-the-difference-between-first-order-and-second-order-elements#:~:text=A%20Linear%20element%20or%20First,to%20nodes%20at%20the%20corner.
def elm_volume_cg(file_name, nodes, Elements):
    u = [0.0, 0.0, 0.0]
    v = [0.0, 0.0, 0.0]
    w = [0.0, 0.0, 0.0]

    def tria_area_cg(nod):
        # compute volume
        for i in [0, 1, 2]:  # denote x, y, z directions
            u[i] = nodes[nod[2]][i] - nodes[nod[1]][i]
            v[i] = nodes[nod[0]][i] - nodes[nod[1]][i]
        area_tria = np.linalg.linalg.norm(np.cross(u, v)) / 2.0
        # compute centre of gravity
        x_cg = (nodes[nod[0]][0] + nodes[nod[1]][0] + nodes[nod[2]][0]) / 3.0
        y_cg = (nodes[nod[0]][1] + nodes[nod[1]][1] + nodes[nod[2]][1]) / 3.0
        z_cg = (nodes[nod[0]][2] + nodes[nod[1]][2] + nodes[nod[2]][2]) / 3.0
        cg_tria = [x_cg, y_cg, z_cg]
        return area_tria, cg_tria

    def tetra_volume_cg(nod):
        # compute volume
        for i in [0, 1, 2]:  # denote x, y, z directions
            u[i] = nodes[nod[2]][i] - nodes[nod[1]][i]
            v[i] = nodes[nod[3]][i] - nodes[nod[1]][i]
            w[i] = nodes[nod[0]][i] - nodes[nod[1]][i]
            volume_tetra = abs(np.dot(np.cross(u, v), w)) / 6.0
        # compute centre of gravity
        x_cg = (nodes[nod[0]][0] + nodes[nod[1]][0] + nodes[nod[2]][0] + nodes[nod[3]][0]) / 4.0
        y_cg = (nodes[nod[0]][1] + nodes[nod[1]][1] + nodes[nod[2]][1] + nodes[nod[3]][1]) / 4.0
        z_cg = (nodes[nod[0]][2] + nodes[nod[1]][2] + nodes[nod[2]][2] + nodes[nod[3]][2]) / 4.0
        cg_tetra = [x_cg, y_cg, z_cg]
        return volume_tetra, cg_tetra

    def second_order_info(elm_type):
        msg = "\nINFO: areas and centres of gravity of " + elm_type.upper() + " elements ignore mid-nodes' positions\n"
        print(msg)
        logging.info(msg)

    # defining volume and centre of gravity for all element types
    volume_elm = {}
    area_elm = {}
    cg = {}

    for en, nod in Elements.tria3.items():
        [area_elm[en], cg[en]] = tria_area_cg(nod)

    if Elements.tria6:
        second_order_info("tria6")
    for en, nod in Elements.tria6.items():  # copy from tria3
        [area_elm[en], cg[en]] = tria_area_cg(nod)

    for en, nod in Elements.quad4.items():
        [a1, cg1] = tria_area_cg(nod[0:3])
        [a2, cg2] = tria_area_cg(nod[0:1] + nod[2:4])
        area_elm[en] = float(a1 + a2)
        cg[en] = [[], [], []]
        for k in [0, 1, 2]:  # denote x, y, z dimensions
            cg[en][k] = (a1 * cg1[k] + a2 * cg2[k]) / area_elm[en]

    if Elements.quad8:
        second_order_info("quad8")
    for en, nod in Elements.quad8.items():  # copy from quad4
        [a1, cg1] = tria_area_cg(nod[0:3])
        [a2, cg2] = tria_area_cg(nod[0:1] + nod[2:4])
        area_elm[en] = float(a1 + a2)
        cg[en] = [[], [], []]
        for k in [0, 1, 2]:  # denote x, y, z dimensions
            cg[en][k] = (a1 * cg1[k] + a2 * cg2[k]) / area_elm[en]

    for en, nod in Elements.tetra4.items():
        [volume_elm[en], cg[en]] = tetra_volume_cg(nod)

    if Elements.tetra10:
        second_order_info("tetra10")
    for en, nod in Elements.tetra10.items():  # copy from tetra4
        [volume_elm[en], cg[en]] = tetra_volume_cg(nod)

    for en, nod in Elements.hexa8.items():
        [v1, cg1] = tetra_volume_cg(nod[0:3] + nod[5:6])
        [v2, cg2] = tetra_volume_cg(nod[0:1] + nod[2:3] + nod[4:6])
        [v3, cg3] = tetra_volume_cg(nod[2:3] + nod[4:7])
        [v4, cg4] = tetra_volume_cg(nod[0:1] + nod[2:5])
        [v5, cg5] = tetra_volume_cg(nod[3:5] + nod[6:8])
        [v6, cg6] = tetra_volume_cg(nod[2:5] + nod[6:7])
        volume_elm[en] = float(v1 + v2 + v3 + v4 + v5 + v6)
        cg[en] = [[], [], []]
        for k in [0, 1, 2]:  # denote x, y, z dimensions
            cg[en][k] = (v1 * cg1[k] + v2 * cg2[k] + v3 * cg3[k] + v4 * cg4[k] + v5 * cg5[k] + v6 * cg6[k]
                         ) / volume_elm[en]

    if Elements.hexa20:
        second_order_info("hexa20")
    for en, nod in Elements.hexa20.items():  # copy from hexa8
        [v1, cg1] = tetra_volume_cg(nod[0:3] + nod[5:6])
        [v2, cg2] = tetra_volume_cg(nod[0:1] + nod[2:3] + nod[4:6])
        [v3, cg3] = tetra_volume_cg(nod[2:3] + nod[4:7])
        [v4, cg4] = tetra_volume_cg(nod[0:1] + nod[2:5])
        [v5, cg5] = tetra_volume_cg(nod[3:5] + nod[6:8])
        [v6, cg6] = tetra_volume_cg(nod[2:5] + nod[6:7])
        volume_elm[en] = float(v1 + v2 + v3 + v4 + v5 + v6)
        cg[en] = [[], [], []]
        for k in [0, 1, 2]:  # denote x, y, z dimensions
            cg[en][k] = (v1 * cg1[k] + v2 * cg2[k] + v3 * cg3[k] + v4 * cg4[k] + v5 * cg5[k] + v6 * cg6[k]
                         ) / volume_elm[en]

    for en, nod in Elements.penta6.items():
        [v1, cg1] = tetra_volume_cg(nod[0:4])
        [v2, cg2] = tetra_volume_cg(nod[1:5])
        [v3, cg3] = tetra_volume_cg(nod[2:6])
        volume_elm[en] = float(v1 + v2 + v3)
        cg[en] = [[], [], []]
        for k in [0, 1, 2]:  # denote x, y, z dimensions
            cg[en][k] = (v1 * cg1[k] + v2 * cg2[k] + v3 * cg3[k]) / volume_elm[en]

    if Elements.penta15:
        second_order_info("penta15")  # copy from penta6
    for en, nod in Elements.penta15.items():
        [v1, cg1] = tetra_volume_cg(nod[0:4])
        [v2, cg2] = tetra_volume_cg(nod[1:5])
        [v3, cg3] = tetra_volume_cg(nod[2:6])
        volume_elm[en] = float(v1 + v2 + v3)
        cg[en] = [[], [], []]
        for k in [0, 1, 2]:  # denote x, y, z dimensions
            cg[en][k] = (v1 * cg1[k] + v2 * cg2[k] + v3 * cg3[k]) / volume_elm[en]

    # finding the minimum and maximum cg position
    x_cg = []
    y_cg = []
    z_cg = []
    for xyz in cg.values():
        x_cg.append(xyz[0])
        y_cg.append(xyz[1])
        z_cg.append(xyz[2])
    cg_min = [min(x_cg), min(y_cg), min(z_cg)]
    cg_max = [max(x_cg), max(y_cg), max(z_cg)]

    return cg, cg_min, cg_max, volume_elm, area_elm


# function for copying .inp file with additional elsets, materials, solid and shell sections, different output request
# elm_states is a dict of the elements containing 0 for void element or 1 for full element
def write_inp(file_name, file_nameW, elm_states, number_of_states, domains, domains_from_config, domain_optimized,
              domain_thickness, domain_offset, domain_orientation, domain_material, domain_volumes, domain_shells,
              plane_strain, plane_stress, axisymmetry, save_iteration_results, i):
    fR = open(file_name, "r")
    check_line_endings = False
    try:
        fW = open(file_nameW + ".inp", "w", newline="\n")
    except TypeError:  # python 2.x do not have newline argument
        fW = open(file_nameW + ".inp", "w")
        check_line_endings = True

    # function for writing ELSETs of each state
    def write_elset():
        fW.write(" \n")
        fW.write("** Added ELSETs by optimization:\n")
        for dn in domains_from_config:
            if domain_optimized[dn] is True:
                elsets_used[dn] = []
                elset_new[dn] = {}
                for sn in range(number_of_states):
                    elset_new[dn][sn] = []
                    for en in domains[dn]:
                        if elm_states[en] == sn:
                            elset_new[dn][elm_states[en]].append(en)
                for sn, en_list in elset_new[dn].items():
                    if en_list:
                        elsets_used[dn].append(sn)
                        fW.write("*ELSET,ELSET=" + dn + str(sn) + "\n")
                        position = 0
                        for en in en_list:
                            if position < 8:
                                fW.write(str(en) + ", ")
                                position += 1
                            else:
                                fW.write(str(en) + ",\n")
                                position = 0
                        fW.write("\n")
        fW.write(" \n")

    # function to add orientation to solid or shell section
    def add_orientation():
        try:
            fW.write(", ORIENTATION=" + domain_orientation[dn][sn] + "\n")
        except (KeyError, IndexError):
            fW.write("\n")

    elsets_done = 0
    sections_done = 0
    outputs_done = 1
    commenting = False
    elset_new = {}
    elsets_used = {}
    msg_error = ""
    for line in fR:
        if line[0] == "*":
            commenting = False

        # writing ELSETs
        if (line[:6].upper() == "*ELSET" and elsets_done == 0) or (line[:5].upper() == "*STEP" and elsets_done == 0):
            write_elset()
            elsets_done = 1

        # optimization materials, solid and shell sections
        if line[:5].upper() == "*STEP" and sections_done == 0:
            if elsets_done == 0:
                write_elset()
                elsets_done = 1

            fW.write(" \n")
            fW.write("** Materials and sections in optimized domains\n")
            fW.write("** (redefines elements properties defined above):\n")
            for dn in domains_from_config:
                if domain_optimized[dn]:
                    for sn in elsets_used[dn]:
                        fW.write("*MATERIAL, NAME=" + dn + str(sn) + "\n")
                        fW.write(domain_material[dn][sn] + "\n")
                        if domain_volumes[dn]:
                            fW.write("*SOLID SECTION, ELSET=" + dn + str(sn) + ", MATERIAL=" + dn + str(sn))
                            add_orientation()
                        elif len(plane_strain.intersection(domain_shells[dn])) == len(domain_shells[dn]):
                            fW.write("*SOLID SECTION, ELSET=" + dn + str(sn) + ", MATERIAL=" + dn + str(sn))
                            add_orientation()
                            fW.write(str(domain_thickness[dn][sn]) + "\n")
                        elif plane_strain.intersection(domain_shells[dn]):
                            msg_error = dn + " domain does not contain only plane strain types for 2D elements"
                        elif len(plane_stress.intersection(domain_shells[dn])) == len(domain_shells[dn]):
                            fW.write("*SOLID SECTION, ELSET=" + dn + str(sn) + ", MATERIAL=" + dn + str(sn))
                            add_orientation()
                            fW.write(str(domain_thickness[dn][sn]) + "\n")
                        elif plane_stress.intersection(domain_shells[dn]):
                            msg_error = dn + " domain does not contain only plane stress types for 2D elements"
                        elif len(axisymmetry.intersection(domain_shells[dn])) == len(domain_shells[dn]):
                            fW.write("*SOLID SECTION, ELSET=" + dn + str(sn) + ", MATERIAL=" + dn + str(sn))
                            add_orientation()
                        elif axisymmetry.intersection(domain_shells[dn]):
                            msg_error = dn + " domain does not contain only axisymmetry types for 2D elements"
                        else:
                            fW.write("*SHELL SECTION, ELSET=" + dn + str(sn) + ", MATERIAL=" + dn + str(sn) +
                                     ", OFFSET=" + str(domain_offset[dn]))
                            add_orientation()
                            fW.write(str(domain_thickness[dn][sn]) + "\n")
                        fW.write(" \n")
                        if msg_error:
                            logging.error("\nERROR: " + msg_error + "\n")
                            raise Exception(msg_error)
            sections_done = 1

        if line[:5].upper() == "*STEP":
            outputs_done -= 1

        # output request only for element stresses in .dat file:
        if line[0:10].upper() == "*NODE FILE" or line[0:8].upper() == "*EL FILE" or \
                        line[0:13].upper() == "*CONTACT FILE" or line[0:11].upper() == "*NODE PRINT" or \
                        line[0:9].upper() == "*EL PRINT" or line[0:14].upper() == "*CONTACT PRINT":
            if outputs_done < 1:
                fW.write(" \n")
                for dn in domains_from_config:
                    fW.write("*EL PRINT, " + "ELSET=" + dn + "\n")
                    fW.write("ENER\n")
                fW.write(" \n")
                outputs_done += 1
            commenting = True
            if not save_iteration_results or np.mod(float(i - 1), save_iteration_results) != 0:
                continue
        elif commenting is True:
            if not save_iteration_results or np.mod(float(i - 1), save_iteration_results) != 0:
                continue

        fW.write(line)
    fR.close()
    fW.close()
    if check_line_endings:
        fW = open(file_nameW + ".inp", "rb")
        content = fW.read().replace("\r\n", "\n")
        fW.close()
        fW = open(file_nameW + ".inp", "wb")
        fW.write(content)
        fW.close()


# function for importing results from .dat file
# Failure Indices are computed at each integration point and maximum or average above each element is returned
def import_FI_int_pt(file_nameW, domains, file_name, elm_states, domains_from_config):
    try:
        f = open(file_nameW + ".dat", "r")
    except IOError:
        msg = "CalculiX result file not found, check your inputs"
        logging.error("\nERROR: " + msg + "\n")
        assert False, msg
    last_time = "initial"  # TODO solve how to read a new step which differs in time
    step_number = -1
    energy_density_step = []  # list for steps - [{en1: energy_density, en2: ..., ...}, {en1: ..., ...}, next step]
    energy_density_eigen = {}  # energy_density_eigen[eigen_number][en_last] = np.average(ener_int_pt)

    read_stresses = 0
    read_energy_density = 0
    read_eigenvalues = 0
    for line in f:
        line_split = line.split()
        if line.replace(" ", "") == "\n":
            if read_energy_density == 1:
                if read_eigenvalues:
                    energy_density_eigen[eigen_number][en_last] = np.average(ener_int_pt)
                else:
                    energy_density_step[step_number][en_last] = np.average(ener_int_pt)
            read_stresses -= 1
            read_energy_density -= 1
            ener_int_pt = []
            en_last = None

        elif line[:9] == " stresses":
            if line.split()[-4] in map(lambda x: x.upper(), domains_from_config):  # TODO upper already on user input
                read_stresses = 2
                if last_time != line_split[-1]:
                    step_number += 1
                    energy_density_step.append({})
                    last_time = line_split[-1]
                    read_eigenvalues = False  # TODO not for frequencies?
        elif line[:24] == " internal energy density":
            if line.split()[-4] in map(lambda x: x.upper(), domains_from_config):  # TODO upper already on user input
                read_energy_density = 2
                if last_time != line_split[-1]:
                    step_number += 1
                    energy_density_step.append({})
                    last_time = line_split[-1]
                    read_eigenvalues = False  # TODO not for frequencies?
        elif line[:54] == "                    E I G E N V A L U E    N U M B E R":
            eigen_number = int(line_split[-1])
            read_eigenvalues = True
            energy_density_eigen[eigen_number] = {}
        elif read_energy_density == 1:
            en = int(line_split[0])
            if en_last != en:
                if en_last:
                    if read_eigenvalues:
                        energy_density_eigen[eigen_number][en_last] = np.average(ener_int_pt)
                    else:
                        energy_density_step[step_number][en_last] = np.average(ener_int_pt)
                    ener_int_pt = []
                en_last = en
            energy_density = float(line_split[2])
            ener_int_pt.append(energy_density)

    if read_energy_density == 1:
        if read_eigenvalues:
            energy_density_eigen[eigen_number][en_last] = np.average(ener_int_pt)
        else:
            energy_density_step[step_number][en_last] = np.average(ener_int_pt)
    f.close()

    return energy_density_step, energy_density_eigen

# function for switch element states
def switching(elm_states, domains_from_config, domain_optimized, domains, domain_density, domain_thickness,
              domain_shells, area_elm, volume_elm, sensitivity_number, mass, mass_referential, mass_addition_ratio,
              mass_removal_ratio, i_violated, i,
              mass_goal_i, decay_coefficient=-0.2):
    # k - exponential decay coefficient to dump mass_additive_ratio and mass_removal_ratio after freezing mass
    # fits to equation: exp(k * i), where i is iteration number from triggering by reaching goal mass ratio?
    # k = -0.2 ~ after 10 iterations slows down approximately 10 times
    # k = 0 ~ no decaying
    def compute_difference():
        if en in domain_shells[dn]:  # shells mass difference
            mass[i] += area_elm[en] * domain_density[dn][elm_states_en] * domain_thickness[dn][elm_states_en]
            if elm_states_en != 0:  # for potential switching down
                mass_decrease[en] = area_elm[en] * (
                    domain_density[dn][elm_states_en] * domain_thickness[dn][elm_states_en] -
                    domain_density[dn][elm_states_en - 1] * domain_thickness[dn][elm_states_en - 1])
            if elm_states_en < len(domain_density[dn]) - 1:  # for potential switching up
                mass_increase[en] = area_elm[en] * (
                    domain_density[dn][elm_states_en + 1] * domain_thickness[dn][elm_states_en + 1] -
                    domain_density[dn][elm_states_en] * domain_thickness[dn][elm_states_en])
        else:  # volumes mass difference
            mass[i] += volume_elm[en] * domain_density[dn][elm_states_en]
            if elm_states_en != 0:  # for potential switching down
                mass_decrease[en] = volume_elm[en] * (
                    domain_density[dn][elm_states_en] - domain_density[dn][elm_states_en - 1])
            if elm_states_en < len(domain_density[dn]) - 1:  # for potential switching up
                mass_increase[en] = volume_elm[en] * (
                    domain_density[dn][elm_states_en + 1] - domain_density[dn][elm_states_en])

    mass_increase = {}
    mass_decrease = {}
    sensitivity_number_opt = {}
    mass.append(0)
    mass_overloaded = 0.0
    # switch up overloaded elements
    for dn in domains_from_config:
        if domain_optimized[dn] is True:
            for en in domains[dn]:
                # rest of elements prepare to sorting and switching
                elm_states_en = elm_states[en]
                compute_difference()  # mass to add or remove
                sensitivity_number_opt[en] = sensitivity_number[en]
    # sorting
    sensitivity_number_sorted = sorted(sensitivity_number_opt.items(), key=operator.itemgetter(1))
    sensitivity_number_sorted2 = list(sensitivity_number_sorted)
    if i_violated:
        if mass_removal_ratio - mass_addition_ratio > 0:  # removing from initial mass
            mass_to_add = mass_addition_ratio * mass_referential * np.exp(decay_coefficient * (i - i_violated))
            mass_to_remove = mass_removal_ratio * mass_referential * np.exp(decay_coefficient * (i - i_violated)) \
                                - mass_overloaded
        else:  # adding to initial mass  TODO include stress limit
            mass_to_add = mass_removal_ratio * mass_referential * np.exp(decay_coefficient * (i - i_violated))
            mass_to_remove = mass_to_add
    else:
        mass_to_add = mass_addition_ratio * mass_referential
        mass_to_remove = mass_removal_ratio * mass_referential
    mass_added = mass_overloaded
    mass_removed = 0.0
    # if mass_goal_i < mass[i - 1]:  # going from bigger mass to lower
    added_elm = set()
    while mass_added < mass_to_add:
        if sensitivity_number_sorted:
            en = sensitivity_number_sorted.pop(-1)[0]  # highest sensitivity number
            try:
                mass[i] += mass_increase[en]
                mass_added += mass_increase[en]
                if isinstance(en, int):
                    elm_states[en] += 1
                else:  # same state domain en
                    if mass_increase[en] == 0:
                        raise KeyError
                    for en2 in domains[en]:
                        elm_states[en2] += 1
                added_elm.add(en)
            except KeyError:  # there is no mass_increase due to highest element state
                pass
        else:
            break
    popped = 0
    while mass_removed < mass_to_remove:
        if mass[i] <= mass_goal_i:
            break
        if sensitivity_number_sorted:
            en = sensitivity_number_sorted.pop(0)[0]  # lowest sensitivity number
            popped += 1
            if isinstance(en, int):
                if elm_states[en] != 0:
                    mass[i] -= mass_decrease[en]
                    mass_removed += mass_decrease[en]
                    elm_states[en] -= 1
            else:  # same state domain en
                if mass_decrease[en] != 0:
                    mass[i] -= mass_decrease[en]
                    mass_removed += mass_decrease[en]
                    for en2 in domains[en]:
                        elm_states[en2] -= 1
        else:  # switch down elements just switched up or tried to be switched up (already in the highest state)
            try:
                en = sensitivity_number_sorted2[popped][0]
                popped += 1
            except IndexError:
                break
            if isinstance(en, int):
                if elm_states[en] != 0:
                    elm_states[en] -= 1
                    if en in added_elm:
                        mass[i] -= mass_increase[en]
                        mass_removed += mass_increase[en]
                    else:
                        mass[i] -= mass_decrease[en]
                        mass_removed += mass_decrease[en]
            else:  # same state domain en
                if mass_decrease[en] != 0:
                    for en2 in domains[en]:
                        elm_states[en2] -= 1
                    if en in added_elm:
                        mass[i] -= mass_increase[en]
                        mass_removed += mass_increase[en]
                    else:
                        mass[i] -= mass_decrease[en]
                        mass_removed += mass_decrease[en]
    return elm_states, mass


# function for exporting the resulting mesh in separate files for each state of elm_states
# only elements found by import_inp function are taken into account
def export_frd(file_nameW, nodes, Elements, elm_states, number_of_states):

    def get_associated_nodes(elm_category):
        for en in elm_category:
            if elm_states[en] == state:
                associated_nodes.extend(elm_category[en])

    def write_elm(elm_category, category_symbol):
        for en in elm_category:
            if elm_states[en] == state:
                f.write(" -1" + str(en).rjust(10, " ") + category_symbol.rjust(5, " ") + "\n")
                line = ""
                nodes_done = 0
                if category_symbol == "4":  # hexa20 different node numbering in inp and frd file
                    for np in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
                               10, 11, 16, 17, 18, 19, 12, 13, 14, 15]:
                        nn = elm_category[en][np]
                        line += str(nn).rjust(10, " ")
                        if np in [9, 15]:
                            f.write(" -2" + line + "\n")
                            line = ""
                elif category_symbol == "5":  # penta15 has different node numbering in inp and frd file
                    for np in [0, 1, 2, 3, 4, 5, 6, 7, 8, 12,
                               13, 14, 9, 10, 11]:
                        nn = elm_category[en][np]
                        line += str(nn).rjust(10, " ")
                        if np in [12, 11]:
                            f.write(" -2" + line + "\n")
                            line = ""
                else:
                    for nn in elm_category[en]:
                        line += str(nn).rjust(10, " ")
                        nodes_done += 1
                        if nodes_done == 10 and elm_category != Elements.tetra10:
                            f.write(" -2" + line + "\n")
                            line = ""
                    f.write(" -2" + line + "\n")

    # find all possible states in elm_states and run separately for each of them
    for state in range(number_of_states):
        f = open(file_nameW + "_state" + str(state) + ".frd", "w")

        # print nodes
        associated_nodes = []
        get_associated_nodes(Elements.tria3)
        get_associated_nodes(Elements.tria6)
        get_associated_nodes(Elements.quad4)
        get_associated_nodes(Elements.quad8)
        get_associated_nodes(Elements.tetra4)
        get_associated_nodes(Elements.tetra10)
        get_associated_nodes(Elements.penta6)
        get_associated_nodes(Elements.penta15)
        get_associated_nodes(Elements.hexa8)
        get_associated_nodes(Elements.hexa20)

        associated_nodes = sorted(list(set(associated_nodes)))
        f.write("    1C\n")
        f.write("    2C" + str(len(associated_nodes)).rjust(30, " ") + 37 * " " + "1\n")
        for nn in associated_nodes:
            f.write(" -1" + str(nn).rjust(10, " ") + "% .5E% .5E% .5E\n" % (nodes[nn][0], nodes[nn][1], nodes[nn][2]))
        f.write(" -3\n")

        # print elements
        elm_sum = 0
        for en in elm_states:
            if elm_states[en] == state:
                elm_sum += 1
        f.write("    3C" + str(elm_sum).rjust(30, " ") + 37 * " " + "1\n")
        write_elm(Elements.tria3, "7")
        write_elm(Elements.tria6, "8")
        write_elm(Elements.quad4, "9")
        write_elm(Elements.quad8, "10")
        write_elm(Elements.tetra4, "3")
        write_elm(Elements.tetra10, "6")
        write_elm(Elements.penta6, "2")
        write_elm(Elements.penta15, "5")
        write_elm(Elements.hexa8, "1")
        write_elm(Elements.hexa20, "4")
        f.write(" -3\n")
        f.close()


# function for exporting the resulting mesh in separate files for each state of elm_states
# only elements found by import_inp function are taken into account
def export_inp(file_nameW, nodes, Elements, elm_states, number_of_states):

    def get_associated_nodes(elm_category):
        for en in elm_category:
            if elm_states[en] == state:
                associated_nodes.extend(elm_category[en])

    def write_elements_of_type(elm_type, elm_type_inp):
        if elm_type:
            f.write("*ELEMENT, TYPE=" + elm_type_inp + ", ELSET=state" + str(state) + "\n")
            for en, nod in elm_type.items():
                if elm_states[en] == state:
                    f.write(str(en))
                    for nn in nod:
                        f.write(", " + str(nn))
                    f.write("\n")

    # find all possible states in elm_states and run separately for each of them
    for state in range(number_of_states):
        f = open(file_nameW + "_state" + str(state) + ".inp", "w")

        # print nodes
        associated_nodes = []
        get_associated_nodes(Elements.tria3)
        get_associated_nodes(Elements.tria6)
        get_associated_nodes(Elements.quad4)
        get_associated_nodes(Elements.quad8)
        get_associated_nodes(Elements.tetra4)
        get_associated_nodes(Elements.tetra10)
        get_associated_nodes(Elements.penta6)
        get_associated_nodes(Elements.penta15)
        get_associated_nodes(Elements.hexa8)
        get_associated_nodes(Elements.hexa20)

        associated_nodes = sorted(list(set(associated_nodes)))
        f.write("*NODE\n")
        for nn in associated_nodes:
            f.write(str(nn) + ", % .5E, % .5E, % .5E\n" % (nodes[nn][0], nodes[nn][1], nodes[nn][2]))
        f.write("\n")

        # print elements
        # prints only basic element types
        write_elements_of_type(Elements.tria3, "S3")
        write_elements_of_type(Elements.tria6, "S6")
        write_elements_of_type(Elements.quad4, "S4")
        write_elements_of_type(Elements.quad8, "S8")
        write_elements_of_type(Elements.tetra4, "C3D4")
        write_elements_of_type(Elements.tetra10, "C3D10")
        write_elements_of_type(Elements.penta6, "C3D6")
        write_elements_of_type(Elements.penta15, "C3D15")
        write_elements_of_type(Elements.hexa8, "C3D8")
        if Elements.hexa20:
            f.write("*ELEMENT, TYPE=C3D20\n")
            for en, nod in Elements.hexa20.items():
                f.write(str(en))
                for nn in nod[:15]:
                    f.write(", " + str(nn))
                f.write("\n")
                for nn in nod[15:]:
                    f.write(", " + str(nn))
                f.write("\n")
        f.close()


# sub-function to write vth mesh
def vtk_mesh(file_nameW, nodes, Elements):
    f = open(file_nameW + ".vtk", "w")
    f.write("# vtk DataFile Version 3.0\n")
    f.write("Results from optimization\n")
    f.write("ASCII\n")
    f.write("DATASET UNSTRUCTURED_GRID\n")

    # nodes
    associated_nodes = set()
    for nn_lists in list(Elements.tria3.values()) + list(Elements.tria6.values()) + list(Elements.quad4.values()) + \
            list(Elements.quad8.values()) + list(Elements.tetra4.values()) + list(Elements.tetra10.values()) + \
            list(Elements.penta6.values()) + list(Elements.penta15.values()) + list(Elements.hexa8.values()) + \
            list(Elements.hexa20.values()):
        associated_nodes.update(nn_lists)
    associated_nodes = sorted(associated_nodes)
    # node renumbering table for vtk format which does not jump over node numbers and contains only associated nodes
    nodes_vtk = [None for _ in range(max(nodes.keys()) + 1)]
    nn_vtk = 0
    for nn in associated_nodes:
        nodes_vtk[nn] = nn_vtk
        nn_vtk += 1

    f.write("\nPOINTS " + str(len(associated_nodes)) + " float\n")
    line_count = 0
    for nn in associated_nodes:
        f.write("{} {} {} ".format(nodes[nn][0], nodes[nn][1], nodes[nn][2]))
        line_count += 1
        if line_count % 2 == 0:
            f.write("\n")
    f.write("\n")

    # elements
    number_of_elements = len(Elements.tria3) + len(Elements.tria6) + len(Elements.quad4) + len(Elements.quad8) + \
                         len(Elements.tetra4) + len(Elements.tetra10) + len(Elements.penta6) + len(Elements.penta15) + \
                         len(Elements.hexa8) + len(Elements.hexa20)
    en_all = list(Elements.tria3.keys()) + list(Elements.tria6.keys()) + list(Elements.quad4.keys()) + \
             list(Elements.quad8.keys()) + list(Elements.tetra4.keys()) + list(Elements.tetra10.keys()) + \
             list(Elements.penta6.keys()) + list(Elements.penta15.keys()) + list(Elements.hexa8.keys()) + \
             list(Elements.hexa20.keys())  # defines vtk element numbering from 0

    size_of_cells = 4 * len(Elements.tria3) + 7 * len(Elements.tria6) + 5 * len(Elements.quad4) + \
                    9 * len(Elements.quad8) + 5 * len(Elements.tetra4) + 11 * len(Elements.tetra10) + \
                    7 * len(Elements.penta6) + 16 * len(Elements.penta15) + 9 * len(Elements.hexa8) + \
                    21 * len(Elements.hexa20)
    f.write("\nCELLS " + str(number_of_elements) + " " + str(size_of_cells) + "\n")

    def write_elm(elm_category, node_length):
        for en in elm_category:
            f.write(node_length)
            for nn in elm_category[en]:
                f.write(" " + str(nodes_vtk[nn]) + " ")
            f.write("\n")

    write_elm(Elements.tria3, "3")
    write_elm(Elements.tria6, "6")
    write_elm(Elements.quad4, "4")
    write_elm(Elements.quad8, "8")
    write_elm(Elements.tetra4, "4")
    write_elm(Elements.tetra10, "10")
    write_elm(Elements.penta6, "6")
    write_elm(Elements.penta15, "15")
    write_elm(Elements.hexa8, "8")
    write_elm(Elements.hexa20, "20")

    f.write("\nCELL_TYPES " + str(number_of_elements) + "\n")
    cell_types = "5 " * len(Elements.tria3) + "22 " * len(Elements.tria6) + "9 " * len(Elements.quad4) + \
                 "23 " * len(Elements.quad8) + "10 " * len(Elements.tetra4) + "24 " * len(Elements.tetra10) + \
                 "13 " * len(Elements.penta6) + "26 " * len(Elements.penta15) + "12 " * len(Elements.hexa8) + \
                 "25 " * len(Elements.hexa20)
    line_count = 0
    for char in cell_types:
        f.write(char)
        if char == " ":
            line_count += 1
            if line_count % 30 == 0:
                f.write("\n")
    f.write("\n")

    f.write("\nCELL_DATA " + str(number_of_elements) + "\n")

    f.close()
    return en_all, associated_nodes


def append_vtk_states(file_nameW, i, en_all, elm_states):
    f = open(file_nameW + ".vtk", "a")

    # element state
    f.write("\nSCALARS element_states" + str(i).zfill(3) + " float\n")
    f.write("LOOKUP_TABLE default\n")
    line_count = 0
    for en in en_all:
        f.write(str(elm_states[en]) + " ")
        line_count += 1
        if line_count % 30 == 0:
            f.write("\n")
    f.write("\n")
    f.close()


# function for exporting result in the legacy vtk format
# nodes and elements are renumbered from 0 not to jump over values
def export_vtk(file_nameW, nodes, Elements, elm_states, sensitivity_number):
    [en_all, associated_nodes] = vtk_mesh(file_nameW, nodes, Elements)
    f = open(file_nameW + ".vtk", "a")

    # element state
    f.write("\nSCALARS element_states float\n")
    f.write("LOOKUP_TABLE default\n")
    line_count = 0
    for en in en_all:
        f.write(str(elm_states[en]) + " ")
        line_count += 1
        if line_count % 30 == 0:
            f.write("\n")
    f.write("\n")

    # sensitivity number
    f.write("\nSCALARS sensitivity_number float\n")
    f.write("LOOKUP_TABLE default\n")
    line_count = 0
    for en in en_all:
        f.write(str(sensitivity_number[en]) + " ")
        line_count += 1
        if line_count % 6 == 0:
            f.write("\n")
    f.write("\n")

    # element state averaged at nodes
    def append_nodal_state(en, elm_type):
        for nn in elm_type[en]:
            try:
                nodal_state[nn].append(elm_states[en])
            except KeyError:
                nodal_state[nn] = [elm_states[en]]

    nodal_state = {}
    for en in Elements.tria3:
        append_nodal_state(en, Elements.tria3)
    for en in Elements.tria6:
        append_nodal_state(en, Elements.tria6)
    for en in Elements.quad4:
        append_nodal_state(en, Elements.quad4)
    for en in Elements.quad8:
        append_nodal_state(en, Elements.quad8)
    for en in Elements.tetra4:
        append_nodal_state(en, Elements.tetra4)
    for en in Elements.tetra10:
        append_nodal_state(en, Elements.tetra10)
    for en in Elements.penta6:
        append_nodal_state(en, Elements.penta6)
    for en in Elements.penta15:
        append_nodal_state(en, Elements.penta15)
    for en in Elements.hexa8:
        append_nodal_state(en, Elements.hexa8)
    for en in Elements.hexa20:
        append_nodal_state(en, Elements.hexa20)

    f.write("\nPOINT_DATA " + str(len(associated_nodes)) + "\n")
    f.write("FIELD field_data 1\n")
    f.write("\nelement_states_averaged_at_nodes 1 " + str(len(associated_nodes)) + " float\n")
    line_count = 0
    for nn in associated_nodes:
        f.write(str(np.average(nodal_state[nn])) + " ")
        line_count += 1
        if line_count % 10 == 0:
            f.write("\n")
    f.write("\n")

    f.close()


# function for exporting element values to csv file for displaying in Paraview, output format:
# element_number, cg_x, cg_y, cg_z, element_state, sensitivity_number, failure indices 1, 2,..., maximal failure index
# only elements found by import_inp function are taken into account
def export_csv(domains_from_config, domains, file_nameW, cg, elm_states,
               sensitivity_number):
    # write element values to the csv file
    f = open(file_nameW + ".csv", "w")
    line = "element_number, cg_x, cg_y, cg_z, element_state, sensitivity_number"
    f.write(line)
    for dn in domains_from_config:
        for en in domains[dn]:
            line = str(en) + ", " + str(cg[en][0]) + ", " + str(cg[en][1]) + ", " + str(cg[en][2]) + ", " + \
                   str(elm_states[en]) + ", " + str(sensitivity_number[en])
            f.write(line)
    f.close()
