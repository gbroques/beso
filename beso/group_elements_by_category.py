# tria3
THREE_NODE_SHELL_TYPES = ['S3', 'CPS3', 'CPE3', 'CAX3', 'M3D3']

# tria6
SIX_NODE_SHELL_TYPES = ['S6', 'CPS6', 'CPE6', 'CAX6', 'M3D6']

# quad4
FOUR_NODE_SHELL_TYPES = ['S4', 'S4R', 'CPS4', 'CPS4R',
                         'CPE4', 'CPE4R', 'CAX4', 'CAX4R', 'M3D4', 'M3D4R']

# quad8
EIGHT_NODE_SHELL_TYPES = ['S8', 'S8R', 'CPS8', 'CPS8R',
                          'CPE8', 'CPE8R', 'CAX8', 'CAX8R', 'M3D8', 'M3D8R']

# tetra4
FOUR_NODE_TETRAHEDRAL_TYPES = ['C3D4']

# tetra10
TEN_NODE_TETRAHEDRAL_TYPES = ['C3D10']

# hexa8
EIGHT_NODE_BRICK_TYPES = ['C3D8', 'C3D8R', 'C3D8I']

# hexa20
TWENTY_NODE_BRICK_TYPES = ['C3D20', 'C3D20R', 'C3D20RI']

# PENTAHEDRON
# a pentahedron is a polyhedron with five faces or sides.
# -------------------------------------------------------

# penta6
SIX_NODE_WEDGE_TYPES = ['C3D6']

# penta15
FIFTEEN_NODE_WEDGE_TYPES = ['C3D15']

element_types_by_category = {
    # shell elements
    'tria3': THREE_NODE_SHELL_TYPES,
    'tria6': SIX_NODE_SHELL_TYPES,
    'quad4': FOUR_NODE_SHELL_TYPES,
    'quad8': EIGHT_NODE_SHELL_TYPES,

    # volume elements
    'tetra4': FOUR_NODE_TETRAHEDRAL_TYPES,
    'tetra10': TEN_NODE_TETRAHEDRAL_TYPES,
    'hexa8': EIGHT_NODE_SHELL_TYPES,
    'hexa20': TWENTY_NODE_BRICK_TYPES,
    'penta6': SIX_NODE_WEDGE_TYPES,
    'penta15': FIFTEEN_NODE_WEDGE_TYPES
}


def group_elements_by_category(element_dict_by_type: dict) -> dict:
    """Group elements by "category".

    A category is a group of tightly related elements.

    For example, all three-node shell elements.

    :param elements_by_type: A dictionary of elements by type.
    """
    elements_by_category = {
        # shell elements
        'tria3': {},
        'tria6': {},
        'quad4': {},
        'quad8': {},

        # volume elements
        'tetra4': {},
        'tetra10': {},
        'hexa8': {},
        'hexa20': {},
        'penta6': {},
        'penta15': {}
    }
    for element_type, element_dict in element_dict_by_type.items():
        for category, types in element_types_by_category.items():
            if element_type in types:
                elements_by_category[category].update(element_dict)
    return elements_by_category
