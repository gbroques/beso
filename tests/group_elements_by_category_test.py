import unittest
from beso.group_elements_by_category import group_elements_by_category
import os


class GroupElementsByCategory(unittest.TestCase):

    def test_group_elements_by_category(self):
        element_dict_by_type = {
            'S4': {
                1: [5, 6, 7],
                2: [8, 9]
            },
            'CPS4': {
                11: [22, 33, 44]
            },
            'C3D4': {
                3: [10, 20, 30],
                4: [40, 50, 60]
            }
        }
        element_dict_by_category = group_elements_by_category(element_dict_by_type)

        self.assertDictEqual(element_dict_by_category['quad4'], {
            1: [5, 6, 7],
            2: [8, 9],
            11: [22, 33, 44]
        })
        self.assertDictEqual(element_dict_by_category['tetra4'], {
            3: [10, 20, 30],
            4: [40, 50, 60]
        })


if __name__ == '__main__':
    unittest.main()
