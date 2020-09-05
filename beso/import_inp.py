import logging


def import_inp(filename, domains_from_config, domain_optimized, shells_as_composite):
    """function importing a mesh consisting of nodes, volume and shell elements"""
    print('filename', filename)
    nodes = {}  # dict with nodes position

    class Elements:
        tria3 = {}
        tria6 = {}
        quad4 = {}
        quad8 = {}
        tetra4 = {}
        tetra10 = {}
        hexa8 = {}
        hexa20 = {}
        penta6 = {}
        penta15 = {}

    all_tria3 = {}
    all_tria6 = {}
    all_quad4 = {}
    all_quad8 = {}
    all_tetra4 = {}
    all_tetra10 = {}
    all_hexa8 = {}
    all_hexa20 = {}
    all_penta6 = {}
    all_penta15 = {}

    model_definition = True
    domains = {}
    read_domain = False
    read_node = False
    elm_category = []
    elm_2nd_line = False
    elset_generate = False
    special_type = ""  # for plane strain, plane stress, or axisymmetry
    plane_strain = set()
    plane_stress = set()
    axisymmetry = set()

    try:
        f = open(filename, "r")
    except IOError:
        msg = ("CalculiX input file " + filename +
               " not found. Check your inputs.")
        logging.error("\nERROR: " + msg + "\n")
        raise Exception(msg)
    line = "\n"
    include = ""
    while line != "":
        if include:
            line = f_include.readline()
            if line == "":
                f_include.close()
                include = ""
                line = f.readline()
        else:
            line = f.readline()
        if line.strip() == '':
            continue
        elif line[0] == '*':  # start/end of a reading set
            if line[0:2] == '**':  # comments
                continue
            if line[:8].upper() == "*INCLUDE":
                start = 1 + line.index("=")
                include = line[start:].strip().strip('"')
                f_include = open(include, "r")
                continue
            read_node = False
            elm_category = []
            elm_2nd_line = False
            read_domain = False
            elset_generate = False

        # reading nodes
        if (line[:5].upper() == "*NODE") and (model_definition is True):
            read_node = True
        elif read_node is True:
            line_list = line.split(',')
            number = int(line_list[0])
            x = float(line_list[1])
            y = float(line_list[2])
            z = float(line_list[3])
            nodes[number] = [x, y, z]

        # reading elements
        elif line[:8].upper() == "*ELEMENT":
            current_elset = ""
            line_list = line[8:].split(',')
            for line_part in line_list:
                if line_part.split('=')[0].strip().upper() == "TYPE":
                    elm_type = line_part.split('=')[1].strip().upper()
                elif line_part.split('=')[0].strip().upper() == "ELSET":
                    current_elset = line_part.split('=')[1].strip()

            # Five aspects of an element characterize its behavior:
            # 1. Family
            # 2. Degrees of freedom (directly related to the element family)
            # 3. Number of nodes
            # 4. Formulation
            # 5. Integration
            #
            # Each element in Abaqus has a unique name (e.g T2D2, S4R, C3D8I, or C3D8R).
            # The element name identifies each of the five aspects of an element.

            # Sources:
            # https://abaqus-docs.mit.edu/2017/English/SIMACAEELMRefMap/simaelm-c-ov.htm#simaelm-c-ov
            # https://abaqus-docs.mit.edu/2017/English/SIMACAEELMRefMap/simaelm-c-general.htm

            # Abaqus uses the letter R at the end of the element name to label reduced-integration elements.
            # https://abaqus-docs.mit.edu/2017/English/SIMACAEGSARefMap/simagsa-c-ctmreduced.htm

            # Shell element names in Abaqus begin with the letter “S.”
            # Axisymmetric shells all begin with the letters “SAX.”
            # Source: https://abaqus-docs.mit.edu/2017/English/SIMACAEGSARefMap/simagsa-c-elmshell.htm

            # "C" is for solid (continuum) elements.
            # "PE" is for plane strain
            # "PS" is for plane stress
            # Source: https://abaqus-docs.mit.edu/2017/English/SIMACAEELMRefMap/simaelm-c-solidcont.htm

            # "M" is for membrane elements.
            # https://abaqus-docs.mit.edu/2017/English/SIMACAEELMRefMap/simaelm-c-membrane.htm
            # 3D is for three-dimensional

            # See element types CalculiX:
            # http://www.dhondt.de/ccx_2.11.pdf
            if elm_type in ["S3", "CPS3", "CPE3", "CAX3", "M3D3"]:
                elm_category = all_tria3
                number_of_nodes = 3
            elif elm_type in ["S6", "CPS6", "CPE6", "CAX6", "M3D6"]:
                elm_category = all_tria6
                number_of_nodes = 6
            elif elm_type in ["S4", "S4R", "CPS4", "CPS4R", "CPE4", "CPE4R", "CAX4", "CAX4R", "M3D4", "M3D4R"]:
                elm_category = all_quad4
                number_of_nodes = 4
            elif elm_type in ["S8", "S8R", "CPS8", "CPS8R", "CPE8", "CPE8R", "CAX8", "CAX8R", "M3D8", "M3D8R"]:
                elm_category = all_quad8
                number_of_nodes = 8
            elif elm_type == "C3D4":
                elm_category = all_tetra4
                number_of_nodes = 4
            elif elm_type == "C3D10":
                elm_category = all_tetra10
                number_of_nodes = 10
            elif elm_type in ["C3D8", "C3D8R", "C3D8I"]:
                elm_category = all_hexa8
                number_of_nodes = 8
            elif elm_type in ["C3D20", "C3D20R", "C3D20RI"]:
                elm_category = all_hexa20
                number_of_nodes = 20
            elif elm_type == "C3D6":
                elm_category = all_penta6
                number_of_nodes = 6
            elif elm_type == "C3D15":
                elm_category = all_penta15
                number_of_nodes = 15
            if elm_type in ["CPE3", "CPE6", "CPE4", "CPE4R", "CPE8", "CPE8R"]:
                special_type = "plane strain"
            elif elm_type in ["CPS3", "CPS6", "CPS4", "CPS4R", "CPS8", "CPS8R"]:
                special_type = "plane stress"
            elif elm_type in ["CAX3", "CAX6", "CAX4", "CAX4R", "CAX8", "CAX8R"]:
                special_type = "axisymmetry"
            else:
                special_type = ""
                if (shells_as_composite is True) and (elm_type in ["S3", "S4", "S4R", "S8"]):
                    msg = ("\nERROR: " + elm_type + "element type found. CalculiX might need S6 or S8R elements for "
                           "composite\n")
                    print(msg)
                    logging.error(msg)

        elif elm_category != []:
            line_list = line.split(',')
            if elm_2nd_line is False:
                en = int(line_list[0])  # element number
                elm_category[en] = []
                pos = 1
                if current_elset:  # save en to the domain
                    try:
                        domains[current_elset].add(en)
                    except KeyError:
                        domains[current_elset] = {en}
                if special_type == "plane strain":
                    plane_strain.add(en)
                elif special_type == "plane stress":
                    plane_stress.add(en)
                elif special_type == "axisymmetry":
                    axisymmetry.add(en)
            else:
                pos = 0
                elm_2nd_line = False
            for nn in range(pos, pos + number_of_nodes - len(elm_category[en])):
                try:
                    enode = int(line_list[nn])
                    elm_category[en].append(enode)
                except(IndexError, ValueError):
                    elm_2nd_line = True
                    break

        # reading domains from elset
        elif line[:6].upper() == "*ELSET":
            line_split_comma = line.split(",")
            if "=" in line_split_comma[1]:
                name_member = 1
                try:
                    if "GENERATE" in line_split_comma[2].upper():
                        elset_generate = True
                except IndexError:
                    pass
            else:
                name_member = 2
                if "GENERATE" in line_split_comma[1].upper():
                    elset_generate = True
            member_split = line_split_comma[name_member].split("=")
            current_elset = member_split[1].strip()
            try:
                domains[current_elset]
            except KeyError:
                domains[current_elset] = set()
            if elset_generate is False:
                read_domain = True
        elif read_domain is True:
            for en in line.split(","):
                en = en.strip()
                if en.isdigit():
                    domains[current_elset].add(int(en))
                elif en.isalpha():  # else: en is name of a previous elset
                    domains[current_elset].update(domains[en])
        elif elset_generate is True:
            line_split_comma = line.split(",")
            try:
                if line_split_comma[3]:
                    en_generated = list(range(int(line_split_comma[0]), int(line_split_comma[1]) + 1,
                                              int(line_split_comma[2])))
            except IndexError:
                en_generated = list(
                    range(int(line_split_comma[0]), int(line_split_comma[1]) + 1))
            domains[current_elset].update(en_generated)

        elif line[:5].upper() == "*STEP":
            model_definition = False
    f.close()

    for dn in domains:
        domains[dn] = list(domains[dn])
    en_all = []
    opt_domains = []
    for dn in domains_from_config:
        try:
            en_all.extend(domains[dn])
        except KeyError:
            msg = "Element set '{}' not found in the inp file.".format(dn)
            logging.error("\nERROR: " + msg + "\n")
            raise Exception(msg)
        if domain_optimized[dn] is True:
            opt_domains.extend(domains[dn])
    msg = ("\ndomains: %.f\n" % len(domains_from_config))

    # only elements in domains_from_config are stored, the rest is discarded
    keys = set(en_all).intersection(set(all_tria3.keys()))
    Elements.tria3 = {k: all_tria3[k] for k in keys}
    keys = set(en_all).intersection(set(all_tria6.keys()))
    Elements.tria6 = {k: all_tria6[k] for k in keys}
    keys = set(en_all).intersection(set(all_quad4.keys()))
    Elements.quad4 = {k: all_quad4[k] for k in keys}
    keys = set(en_all).intersection(set(all_quad8.keys()))
    Elements.quad8 = {k: all_quad8[k] for k in keys}
    keys = set(en_all).intersection(set(all_tetra4.keys()))
    Elements.tetra4 = {k: all_tetra4[k] for k in keys}
    keys = set(en_all).intersection(set(all_tetra10.keys()))
    Elements.tetra10 = {k: all_tetra10[k] for k in keys}
    keys = set(en_all).intersection(set(all_hexa8.keys()))
    Elements.hexa8 = {k: all_hexa8[k] for k in keys}
    keys = set(en_all).intersection(set(all_hexa20.keys()))
    Elements.hexa20 = {k: all_hexa20[k] for k in keys}
    keys = set(en_all).intersection(set(all_penta6.keys()))
    Elements.penta6 = {k: all_penta6[k] for k in keys}
    keys = set(en_all).intersection(set(all_penta15.keys()))
    Elements.penta15 = {k: all_penta15[k] for k in keys}
    en_all = list(Elements.tria3.keys()) + list(Elements.tria6.keys()) + list(Elements.quad4.keys()) + \
        list(Elements.quad8.keys()) + list(Elements.tetra4.keys()) + list(Elements.tetra10.keys()) + \
        list(Elements.hexa8.keys()) + list(Elements.hexa20.keys()) + list(Elements.penta6.keys()) + \
        list(Elements.penta15.keys())

    msg += ("nodes  : %.f\nTRIA3  : %.f\nTRIA6  : %.f\nQUAD4  : %.f\nQUAD8  : %.f\nTETRA4 : %.f\nTETRA10: %.f\n"
            "HEXA8  : %.f\nHEXA20 : %.f\nPENTA6 : %.f\nPENTA15: %.f\n"
            % (len(nodes), len(Elements.tria3), len(Elements.tria6), len(Elements.quad4), len(Elements.quad8),
               len(Elements.tetra4), len(Elements.tetra10), len(
                Elements.hexa8), len(Elements.hexa20),
               len(Elements.penta6), len(Elements.penta15)))
    print(msg)
    logging.info(msg)

    if not opt_domains:
        row = "None optimized domain has been found. Check your inputs."
        msg = ("\nERROR: " + row + "\n")
        logging.error(msg)
        assert False, row

    return nodes, Elements, domains, opt_domains, plane_strain, plane_stress, axisymmetry
