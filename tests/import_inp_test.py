import unittest
from beso import beso_lib
import os


class ImportImpTest(unittest.TestCase):

    def test_import_inp(self):
        os.path.abspath(os.path.dirname(__file__))

        filename = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'FEMMeshGmsh.inp')
        domains_from_config = ['SolidMaterialElementGeometry2D']
        domain_optimized = {'SolidMaterialElementGeometry2D': True}
        shells_as_composite = False
        [
            nodes,
            Elements,
            domains,
            opt_domains,
            en_all,
            plane_strain,
            plane_stress,
            axisymmetry
        ] = beso_lib.import_inp(
            filename,
            domains_from_config,
            domain_optimized,
            shells_as_composite
        )
        self.assertEqual(len(nodes), 1159)


if __name__ == '__main__':
    unittest.main()
