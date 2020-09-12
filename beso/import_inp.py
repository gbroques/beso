import logging
from ccxmeshreader import read_mesh
from beso.group_elements_by_category import group_elements_by_category
from beso.get_special_type_elements import (get_axisymmetry_elements,
                                            get_plane_strain_elements,
                                            get_plane_stress_elements)

def import_inp(filename, domains_from_config, domain_optimized):
    """function importing a mesh consisting of nodes, volume and shell elements"""

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

    mesh = read_mesh(filename)
    element_dict_by_type = mesh['element_dict_by_type']

    # cast tuple coordinate values to list to not accidentally break something downstream
    nodes = {}
    for node_number, coordinates in mesh['node_coordinates_by_number'].items():
        nodes[node_number] = list(coordinates)

    domains = mesh['element_set_by_name']
    for dn in domains:
        domains[dn] = list(domains[dn])
    en_all = []
    opt_domains = []
    for dn in domains_from_config:
        if dn not in domains:
            msg = "Element set '{}' not found in the inp file.".format(dn)
            logging.error("\nERROR: " + msg + "\n")
            raise Exception(msg)
        en_all.extend(domains[dn])
        if domain_optimized[dn] is True:
            opt_domains.extend(domains[dn])

    if not opt_domains:
        row = "None optimized domain has been found. Check your inputs."
        msg = ("\nERROR: " + row + "\n")
        logging.error(msg)
        assert False, row

    msg = ("\ndomains: %.f\n" % len(domains_from_config))

    # only elements in domains_from_config are stored, the rest is discarded
    element_dict_by_category = group_elements_by_category(element_dict_by_type)

    all_tria3 = element_dict_by_category['tria3']
    keys = set(en_all).intersection(set(all_tria3.keys()))
    Elements.tria3 = {k: all_tria3[k] for k in keys}

    all_tria6 = element_dict_by_category['tria6']
    keys = set(en_all).intersection(set(all_tria6.keys()))
    Elements.tria6 = {k: all_tria6[k] for k in keys}

    all_quad4 = element_dict_by_category['quad4']
    keys = set(en_all).intersection(set(all_quad4.keys()))
    Elements.quad4 = {k: all_quad4[k] for k in keys}

    all_quad8 = element_dict_by_category['quad8']
    keys = set(en_all).intersection(set(all_quad8.keys()))
    Elements.quad8 = {k: all_quad8[k] for k in keys}

    all_tetra4 = element_dict_by_category['tetra4']
    keys = set(en_all).intersection(set(all_tetra4.keys()))
    Elements.tetra4 = {k: all_tetra4[k] for k in keys}

    all_tetra10 = element_dict_by_category['tetra10']
    keys = set(en_all).intersection(set(all_tetra10.keys()))
    Elements.tetra10 = {k: all_tetra10[k] for k in keys}

    all_hexa8 = element_dict_by_category['hexa8']
    keys = set(en_all).intersection(set(all_hexa8.keys()))
    Elements.hexa8 = {k: all_hexa8[k] for k in keys}

    all_hexa20 = element_dict_by_category['hexa20']
    keys = set(en_all).intersection(set(all_hexa20.keys()))
    Elements.hexa20 = {k: all_hexa20[k] for k in keys}

    all_penta6 = element_dict_by_category['penta6']
    keys = set(en_all).intersection(set(all_penta6.keys()))
    Elements.penta6 = {k: all_penta6[k] for k in keys}

    all_penta15 = element_dict_by_category['penta15']
    keys = set(en_all).intersection(set(all_penta15.keys()))
    Elements.penta15 = {k: all_penta15[k] for k in keys}

    msg += ("nodes  : %.f\nTRIA3  : %.f\nTRIA6  : %.f\nQUAD4  : %.f\nQUAD8  : %.f\nTETRA4 : %.f\nTETRA10: %.f\n"
            "HEXA8  : %.f\nHEXA20 : %.f\nPENTA6 : %.f\nPENTA15: %.f\n"
            % (len(nodes), len(Elements.tria3), len(Elements.tria6), len(Elements.quad4), len(Elements.quad8),
               len(Elements.tetra4), len(Elements.tetra10), len(
                Elements.hexa8), len(Elements.hexa20),
               len(Elements.penta6), len(Elements.penta15)))
    print(msg)
    logging.info(msg)

    plane_strain = get_plane_strain_elements(element_dict_by_type)
    plane_stress = get_plane_stress_elements(element_dict_by_type)
    axisymmetry = get_axisymmetry_elements(element_dict_by_type)

    return nodes, Elements, domains, opt_domains, plane_strain, plane_stress, axisymmetry
