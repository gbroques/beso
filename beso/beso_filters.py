# Filters to prevent "checkerboard" effect, to fit different tasks
# From the following paper:
#   A simple checkerboard suppression algorithm for evolutionary structural optimization
# "Checkerboard patterns refer to the phenomena of alternating presence of solid and void elements ordered in a checkerboard like fashion
#  Such shapes and topologies with checkerboard patterns may be unacceptable in practice."
import numpy as np
import beso.beso_lib as beso_lib
import logging

def sround(x, s):
    """round float number x to s significant digits"""
    if x > 0:
        result = round(x, -int(np.floor(np.log10(x))) + s - 1)
    elif x < 0:
        result = round(x, -int(np.floor(np.log10(-x))) + s - 1)
    elif x == 0:
        result = 0
    return result

# function preparing values for filtering element to suppress checkerboard
# uses sectoring to prevent computing distance of far points
# See the following paper for more information:
# Convergent and mesh-independent solutions for the bi-directional evolutionary structural optimization method
# 2.3. Filter scheme
# The defined filter functions are based on a length
# scale r_min that does not change with mesh refinement. The primary role of the scale parameter rmin in the filter scheme is to
# identify the nodes that influence the sensitivity of the ith element. This can be visualized by drawing a circle of radius rmin
# centred at the centroid of the ith element
# r_min should be larger than half of
# the size of one element. It is recommended that r_min is selected
# to be about 1–3 times of the size of one element.
# Also described in
#   "Using BESO method to optimize the shape and reinforcement of the underground openings"
def prepare2s(cg, cg_min, cg_max, r_min, opt_domains, weight_factor2, near_elm):
    sector_elm = {}
    # preparing empty sectors
    x = cg_min[0] + 0.5 * r_min
    while x <= cg_max[0] + 0.5 * r_min:
        y = cg_min[1] + 0.5 * r_min
        while y <= cg_max[1] + 0.5 * r_min:
            z = cg_min[2] + 0.5 * r_min
            while z <= cg_max[2] + 0.5 * r_min:
                # 6 significant digit round because of small declination (6 must be used for all sround below)
                sector_elm[(sround(x, 6), sround(y, 6), sround(z, 6))] = []
                z += r_min
            y += r_min
        x += r_min
    # assigning elements to the sectors
    for en in opt_domains:
        sector_centre = []
        for k in range(3):
            position = cg_min[k] + r_min * (0.5 + np.floor((cg[en][k] - cg_min[k]) / r_min))
            sector_centre.append(sround(position, 6))
        sector_elm[tuple(sector_centre)].append(en)
    # finding near elements inside each sector
    for sector_centre in sector_elm:
        for en in sector_elm[sector_centre]:
            near_elm[en] = []
        for en in sector_elm[sector_centre]:
            for en2 in sector_elm[sector_centre]:
                if en == en2:
                    continue
                ee = (min(en, en2), max(en, en2))
                try:
                    weight_factor2[ee]
                except KeyError:
                    dx = cg[en][0] - cg[en2][0]
                    dy = cg[en][1] - cg[en2][1]
                    dz = cg[en][2] - cg[en2][2]
                    distance = (dx ** 2 + dy ** 2 + dz ** 2) ** 0.5
                    if distance < r_min:
                        weight_factor2[ee] = r_min - distance
                        near_elm[en].append(en2)
                        near_elm[en2].append(en)
    # finding near elements in neighbouring sectors by comparing distance with neighbouring sector elements
    x = cg_min[0] + 0.5 * r_min
    while x <= cg_max[0] + 0.5 * r_min:
        y = cg_min[1] + 0.5 * r_min
        while y <= cg_max[1] + 0.5 * r_min:
            z = cg_min[2] + 0.5 * r_min
            while z <= cg_max[2] + 0.5 * r_min:
                position = (sround(x, 6), sround(y, 6), sround(z, 6))
                # down level neighbouring sectors:
                # o  o  -
                # o  -  -
                # o  -  -
                # middle level neighbouring sectors:
                # o  o  -
                # o self -
                # o  -  -
                # upper level neighbouring sectors:
                # o  o  -
                # o  o  -
                # o  -  -
                for position_neighbour in [(x + r_min, y - r_min, z - r_min),
                                           (x + r_min, y, z - r_min),
                                           (x + r_min, y + r_min, z - r_min),
                                           (x, y + r_min, z - r_min),
                                           (x + r_min, y - r_min, z),
                                           (x + r_min, y, z),
                                           (x + r_min, y + r_min, z),
                                           (x, y + r_min, z),
                                           (x + r_min, y - r_min, z + r_min),
                                           (x + r_min, y, z + r_min),
                                           (x + r_min, y + r_min, z + r_min),
                                           (x, y + r_min, z + r_min),
                                           (x, y, z + r_min)]:
                    position_neighbour = (sround(position_neighbour[0], 6), sround(position_neighbour[1], 6),
                                          sround(position_neighbour[2], 6))
                    for en in sector_elm[position]:
                        try:
                            for en2 in sector_elm[position_neighbour]:
                                dx = cg[en][0] - cg[en2][0]
                                dy = cg[en][1] - cg[en2][1]
                                dz = cg[en][2] - cg[en2][2]
                                distance = (dx ** 2 + dy ** 2 + dz ** 2) ** 0.5
                                if distance < r_min:
                                    ee = (min(en, en2), max(en, en2))
                                    weight_factor2[ee] = r_min - distance
                                    near_elm[en].append(en2)
                                    near_elm[en2].append(en)
                        except KeyError:
                            pass
                z += r_min
            y += r_min
        x += r_min
    # print ("near elements have been associated, weight factors computed")
    return weight_factor2, near_elm


# function to filter sensitivity number to suppress checkerboard
# simplified version: makes weighted average of sensitivity numbers from near elements
def run2(file_name, sensitivity_number, weight_factor2, near_elm, opt_domains):
    sensitivity_number_filtered = sensitivity_number.copy()  # sensitivity number of each element after filtering
    for en in opt_domains:
        numerator = 0
        denominator = 0
        for en2 in near_elm[en]:
            ee = (min(en, en2), max(en, en2))
            numerator += weight_factor2[ee] * sensitivity_number[en2]
            denominator += weight_factor2[ee]
        if denominator != 0:
            sensitivity_number_filtered[en] = numerator / denominator
        else:
            msg = "\nERROR: simple filter failed due to division by 0." \
                  "Some element has not a near element in distance <= r_min.\n"
            print(msg)
            logging.error(msg)
            return sensitivity_number
    return sensitivity_number_filtered
