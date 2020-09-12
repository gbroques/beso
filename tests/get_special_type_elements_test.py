import unittest

from beso.get_special_type_elements import (get_axisymmetry_elements,
                                            get_plane_strain_elements,
                                            get_plane_stress_elements)


class GetSpecialElementsTest(unittest.TestCase):

    def test_group_elements_by_category(self):
        element_dict_by_type = {
            # axisymmetry
            'CAX3': {
                1: [5, 6, 7],
                2: [8, 9]
            },
            # plane strain
            'CPE3': {
                11: [22, 33, 44]
            },
            # plane stress
            'CPS3': {
                3: [10, 20, 30],
                4: [40, 50, 60]
            }
        }
        self.assertEqual(get_axisymmetry_elements(element_dict_by_type), {1, 2})
        self.assertEqual(get_plane_strain_elements(element_dict_by_type), {11})
        self.assertEqual(get_plane_stress_elements(element_dict_by_type), {3, 4})

if __name__ == '__main__':
    unittest.main()
