import unittest
from beso.import_inp import import_inp
import os


class ImportImpTest(unittest.TestCase):

    def test_import_inp_with_simply_supported_2d_beam(self):
        """https://github.com/fandaL/beso/wiki/Example-1:-simply-supported-2D-beam"""
        filename = os.path.join(os.path.abspath(
            os.path.dirname(__file__)), 'inp', '2DBeam.inp')
        domains_from_config = ['SolidMaterialElementGeometry2D']
        domain_optimized = {'SolidMaterialElementGeometry2D': True}
        shells_as_composite = False

        [
            nodes,
            Elements,
            domains,
            optimized_domains,
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
        self.assertListEqual(nodes[1], [0, 0, 0])
        self.assertListEqual(nodes[2], [0, 18, 0])
        self.assertListEqual(
            nodes[530], [1.991512192678, 2.992319281912, 0])
        self.assertListEqual(nodes[1158], [22, 9, 0])
        self.assertListEqual(nodes[1159], [19, 9, 0])

        self.assertEqual(len(Elements.quad4), 1080)
        self.assertEqual(type(Elements.quad4), dict)
        self.assertListEqual(Elements.quad4[157], [193, 283, 392, 282])
        self.assertListEqual(Elements.quad4[179], [852, 987, 1009, 943])
        self.assertListEqual(Elements.quad4[1132], [
                             934, 1053, 1128, 1020])
        self.assertListEqual(Elements.quad4[1236], [6, 5, 193, 282])

        self.assertListEqual(list(domains.keys()), [
                             'Efaces', 'Eall', 'SolidMaterialElementGeometry2D'])
        self.assertEqual(len(domains['SolidMaterialElementGeometry2D']), 1080)
        self.assertEqual(list(Elements.quad4.keys()),
                         domains['SolidMaterialElementGeometry2D'])

        self.assertEqual(len(optimized_domains), 1080)
        self.assertEqual(list(Elements.quad4.keys()),
                         optimized_domains)

        self.assertEqual(plane_strain, set())
        self.assertEqual(plane_stress, set())
        self.assertEqual(axisymmetry, set())

    def test_import_inp_with_engine_bracket(self):
        """https://github.com/fandaL/beso/wiki/Example-2:-engine-bracket"""
        filename = os.path.join(os.path.abspath(
            os.path.dirname(__file__)), 'inp', 'EngineBracket.inp')
        domains_from_config = ['SolidMaterial001Solid', 'SolidMaterialSolid']
        domain_optimized = {'SolidMaterial001Solid': True,
                            'SolidMaterialSolid': False}
        shells_as_composite = False

        [
            nodes,
            Elements,
            domains,
            optimized_domains,
            plane_strain,
            plane_stress,
            axisymmetry
        ] = import_inp(
            filename,
            domains_from_config,
            domain_optimized,
            shells_as_composite
        )

        self.assertEqual(len(nodes), 53900)
        self.assertEqual(type(nodes), dict)
        self.assertListEqual(
            nodes[1], [-152.9677040056, -35.94232712384, 31.79731593681])
        self.assertListEqual(
            nodes[2], [-163.2966, -25.1368705002, 22.23798726787])
        self.assertListEqual(
            nodes[2385], [-91.4908, -5.165291550471, 76.7413436476])
        self.assertListEqual(
            nodes[53899], [-93.0232960993, 37.57124391792, 12.40030788603])
        self.assertListEqual(
            nodes[53900], [-83.36555067316, 16.90226876028, -3.366081740471])

        self.assertEqual(len(Elements.tetra4), 266382)
        self.assertEqual(type(Elements.tetra4), dict)
        print(Elements.tetra4[47442])

        self.assertListEqual(Elements.tetra4[42122], [
                             269, 8064, 5763, 8100])
        self.assertListEqual(Elements.tetra4[42123], [
                             992, 993, 15571, 11196])
        self.assertListEqual(Elements.tetra4[308502], [
                             18877, 19532, 2122, 18864])
        self.assertListEqual(Elements.tetra4[308503], [
                             2122, 19532, 18877, 2419])

        self.assertListEqual(list(domains.keys()), [
                             'Evolumes', 'Eall', 'SolidMaterialSolid', 'SolidMaterial001Solid'])
        self.assertEqual(len(domains['SolidMaterial001Solid']), 261095)
        self.assertEqual(len(domains['SolidMaterialSolid']), 5287)
        self.assertEqual(len(
            domains['SolidMaterial001Solid']) + len(domains['SolidMaterialSolid']), 266382)

        self.assertEqual(len(optimized_domains), 261095)
        self.assertEqual(optimized_domains[0], 42122)
        self.assertEqual(optimized_domains[-1], 307435)

        self.assertEqual(plane_strain, set())
        self.assertEqual(plane_stress, set())
        self.assertEqual(axisymmetry, set())

    def test_import_inp_when_file_not_found_raises_io_error(self):
        with self.assertRaises(IOError) as context:
            import_inp('non-existent-file.inp', [], {}, False)

        self.assertEqual(
            'CalculiX input file non-existent-file.inp not found. Check your inputs.',
            str(context.exception)
        )


if __name__ == '__main__':
    unittest.main()
