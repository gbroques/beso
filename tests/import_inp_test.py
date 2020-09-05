import unittest
from beso.import_inp import import_inp
import os


class ImportImpTest(unittest.TestCase):

    def test_import_inp(self):
        filename = os.path.join(os.path.abspath(
            os.path.dirname(__file__)), 'FEMMeshGmsh.inp')
        domains_from_config = ['SolidMaterialElementGeometry2D']
        domain_optimized = {'SolidMaterialElementGeometry2D': True}
        shells_as_composite = False

        [
            nodes,
            Elements,
            domains,
            opt_domains,
            plane_strain,
            plane_stress,
            axisymmetry
        ] = import_inp(
            filename,
            domains_from_config,
            domain_optimized,
            shells_as_composite
        )

        self.assertEqual(len(nodes), 1159)
        self.assertEqual(type(nodes), dict)
        self.assertListEqual(nodes[int(1)], [0, 0, 0])
        self.assertListEqual(nodes[int(2)], [0, 18, 0])
        self.assertListEqual(
            nodes[int(530)], [1.991512192678, 2.992319281912, 0])
        self.assertListEqual(nodes[int(1158)], [22, 9, 0])
        self.assertListEqual(nodes[int(1159)], [19, 9, 0])

        self.assertEqual(len(Elements.quad4), 1080)
        self.assertEqual(type(Elements.quad4), dict)
        self.assertListEqual(Elements.quad4[int(157)], [193, 283, 392, 282])
        self.assertListEqual(Elements.quad4[int(179)], [852, 987, 1009, 943])
        self.assertListEqual(Elements.quad4[int(1132)], [
                             934, 1053, 1128, 1020])
        self.assertListEqual(Elements.quad4[int(1236)], [6, 5, 193, 282])

        self.assertListEqual(list(domains.keys()), [
                             'Efaces', 'Eall', 'SolidMaterialElementGeometry2D'])
        self.assertEqual(len(domains['SolidMaterialElementGeometry2D']), 1080)
        self.assertEqual(list(Elements.quad4.keys()),
                         domains['SolidMaterialElementGeometry2D'])

        self.assertEqual(len(opt_domains), 1080)
        self.assertEqual(list(Elements.quad4.keys()),
                         opt_domains)

        self.assertEqual(plane_strain, set())
        self.assertEqual(plane_stress, set())
        self.assertEqual(axisymmetry, set())


if __name__ == '__main__':
    unittest.main()
