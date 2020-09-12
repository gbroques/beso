from typing import List


def get_axisymmetry_elements(element_dict_by_type: dict) -> set:
    axisymmetry_types = ['CAX3', 'CAX6', 'CAX4', 'CAX4R', 'CAX8', 'CAX8R']
    return get_special_type_elements(element_dict_by_type, axisymmetry_types)


def get_plane_strain_elements(element_dict_by_type: dict) -> set:
    plane_strain_types = ['CPE3', 'CPE6', 'CPE4', 'CPE4R', 'CPE8', 'CPE8R']
    return get_special_type_elements(element_dict_by_type, plane_strain_types)


def get_plane_stress_elements(element_dict_by_type: dict) -> set:
    plane_stress_types = ['CPS3', 'CPS6', 'CPS4', 'CPS4R', 'CPS8', 'CPS8R']
    return get_special_type_elements(element_dict_by_type, plane_stress_types)


def get_special_type_elements(element_dict_by_type: dict, types: List[str]):
    elements = set()
    for special_type in types:
        if special_type in element_dict_by_type:
            element_dict = element_dict_by_type[special_type]
            for element_number in element_dict.keys():
                elements.add(element_number)
    return elements
