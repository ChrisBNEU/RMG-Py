#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy
import unittest

import rmgpy.chem.constants as constants
from rmgpy.chem.thermo import *

################################################################################

class ThermoTest(unittest.TestCase):
    """
    Contains unit tests for the rmgpy.chem.thermo module, used for working with
    thermodynamics models.
    """
    
    def testThermoData(self):
        """
        Tests the ThermoData class.
        """
        Tdata = ([300.0,400.0,500.0,600.0,800.0,1000.0,1500.0],"K")
        Cpdata = ([3.0,4.0,5.0,6.0,8.0,10.0,15.0],"K")

        thermo = ThermoData(Tdata, Cpdata, H298=-2000.0, S298=50.0, Tmin=300.0, Tmax=2000.0, comment='This data is completely made up')
        self.assertEqual(thermo.getHeatCapacity(500), 5)
        self.assertEqual(thermo.getEnthalpy(300), -2000.0)
        self.assertEqual(thermo.getEntropy(300), 50.0)

    def testWilhoit(self):
        """
        Tests the Wilhoit thermodynamics model functions.
        """
        
        # CC(=O)O[O]
        wilhoit = Wilhoit(cp0=4.0*constants.R, cpInf=21.0*constants.R, a0=-3.95, a1=9.26, a2=-15.6, a3=8.55, B=500.0, H0=-6.151e+04, S0=-790.2)
        
        Tlist = numpy.arange(200.0, 2001.0, 200.0, numpy.float64)
        Cplist0 = [ 64.398,  94.765, 116.464, 131.392, 141.658, 148.830, 153.948, 157.683, 160.469, 162.589]
        Hlist0 = [-166312., -150244., -128990., -104110., -76742.9, -47652.6, -17347.1, 13834.8, 45663.0, 77978.1]
        Slist0 = [287.421, 341.892, 384.685, 420.369, 450.861, 477.360, 500.708, 521.521, 540.262, 557.284]
        Glist0 = [-223797., -287002., -359801., -440406., -527604., -620485., -718338., -820599., -926809., -1036590.]

        Cplist = wilhoit.getHeatCapacities(Tlist)
        Hlist = wilhoit.getEnthalpies(Tlist)
        Slist = wilhoit.getEntropies(Tlist)
        Glist = wilhoit.getFreeEnergies(Tlist)

        for i in range(len(Tlist)):
            self.assertAlmostEqual(Cplist[i] / Cplist0[i], 1.0, 4)
            self.assertAlmostEqual( Hlist[i] /  Hlist0[i], 1.0, 4)
            self.assertAlmostEqual( Slist[i] /  Slist0[i], 1.0, 4)
            self.assertAlmostEqual( Glist[i] /  Glist0[i], 1.0, 4)

    def testPickleThermoData(self):
        """
        Test that a ThermoData object can be successfully pickled and
        unpickled with no loss of information.
        """
        Tdata = ([300.0,400.0,500.0,600.0,800.0,1000.0,1500.0],"K")
        Cpdata = [3.0,4.0,5.0,6.0,8.0,10.0,15.0]
        thermo0 = ThermoData(Tdata, Cpdata, H298=-2000.0, S298=50.0, Tmin=300.0, Tmax=2000.0, comment='This data is completely made up')
        import cPickle
        thermo = cPickle.loads(cPickle.dumps(thermo0))

        self.assertEqual(thermo0.Tdata.value, thermo.Tdata.value)
        self.assertEqual(thermo0.Cpdata.value, thermo.Cpdata.value)
        self.assertEqual(thermo0.H298.value, thermo.H298.value)
        self.assertEqual(thermo0.S298.value, thermo.S298.value)
        self.assertEqual(thermo0.Tmin.value, thermo.Tmin.value)
        self.assertEqual(thermo0.Tmax.value, thermo.Tmax.value)
        self.assertEqual(thermo0.comment, thermo.comment)

    def testPickleWilhoit(self):
        """
        Test that a Wilhoit object can be successfully pickled and
        unpickled with no loss of information.
        """
        thermo0 = Wilhoit(cp0=4.0*constants.R, cpInf=21.0*constants.R, a0=-3.95, a1=9.26, a2=-15.6, a3=8.55, B=500.0, H0=-6.151e+04, S0=-790.2, Tmin=300.0, Tmax=2000.0, comment='CC(=O)O[O]')
        import cPickle
        thermo = cPickle.loads(cPickle.dumps(thermo0))

        self.assertAlmostEqual(thermo0.cp0.value, thermo.cp0.value, 4)
        self.assertAlmostEqual(thermo0.cpInf.value, thermo.cpInf.value, 3)
        self.assertAlmostEqual(thermo0.a0.value, thermo.a0.value, 4)
        self.assertAlmostEqual(thermo0.a1.value, thermo.a1.value, 4)
        self.assertAlmostEqual(thermo0.a2.value, thermo.a2.value, 4)
        self.assertAlmostEqual(thermo0.a3.value, thermo.a3.value, 4)
        self.assertAlmostEqual(thermo0.H0.value, thermo.H0.value, 4)
        self.assertAlmostEqual(thermo0.S0.value, thermo.S0.value, 4)
        self.assertAlmostEqual(thermo0.B.value, thermo.B.value, 4)
        self.assertEqual(thermo0.Tmin.value, thermo.Tmin.value)
        self.assertEqual(thermo0.Tmax.value, thermo.Tmax.value)
        self.assertEqual(thermo0.comment, thermo.comment)

    def testPickleNASA(self):
        """
        Test that a MultiNASA object can be successfully pickled and
        unpickled with no loss of information.
        """

        nasa0 = NASA(coeffs=[11.0,12.0,13.0,14.0,15.0,16.0,17.0], Tmin=300.0, Tmax=1000.0, comment='This data is completely made up and unphysical')
        nasa1 = NASA(coeffs=[21.0,22.0,23.0,24.0,25.0,26.0,27.0], Tmin=1000.0, Tmax=6000.0, comment='This data is also completely made up and unphysical')

        thermo0 = MultiNASA(polynomials=[nasa0, nasa1], Tmin=300.0, Tmax=6000.0, comment='This data is completely made up and unphysical')
        import cPickle
        thermo = cPickle.loads(cPickle.dumps(thermo0))

        self.assertEqual(len(thermo0.polynomials), len(thermo.polynomials))
        for poly0, poly in zip(thermo0.polynomials, thermo.polynomials):
            self.assertEqual(poly0.cm2, poly.cm2)
            self.assertEqual(poly0.cm1, poly.cm1)
            self.assertEqual(poly0.c0, poly.c0)
            self.assertEqual(poly0.c1, poly.c1)
            self.assertEqual(poly0.c2, poly.c2)
            self.assertEqual(poly0.c3, poly.c3)
            self.assertEqual(poly0.c4, poly.c4)
            self.assertEqual(poly0.c5, poly.c5)
            self.assertEqual(poly0.c6, poly.c6)
            self.assertEqual(poly0.Tmin.value, poly.Tmin.value)
            self.assertEqual(poly0.Tmax.value, poly.Tmax.value)
            self.assertEqual(poly0.comment, poly.comment)

        self.assertEqual(thermo0.Tmin.value, thermo.Tmin.value)
        self.assertEqual(thermo0.Tmax.value, thermo.Tmax.value)
        self.assertEqual(thermo0.comment, thermo.comment)

    def testOutputThermoData(self):
        """
        Test that we can reconstruct a ThermoData object from its repr()
        output with no loss of information.
        """
        Tdata = ([300.0,400.0,500.0,600.0,800.0,1000.0,1500.0],"K")
        Cpdata = [3.0,4.0,5.0,6.0,8.0,10.0,15.0]
        thermo0 = ThermoData(Tdata, Cpdata, H298=-2000.0, S298=50.0, Tmin=300.0, Tmax=2000.0, comment='This data is completely made up')
        exec('thermo = %r' % thermo0)

        self.assertEqual(thermo0.Tdata.value, thermo.Tdata.value)
        self.assertEqual(thermo0.Cpdata.value, thermo.Cpdata.value)
        self.assertEqual(thermo0.H298.value, thermo.H298.value)
        self.assertEqual(thermo0.S298.value, thermo.S298.value)
        self.assertEqual(thermo0.Tmin.value, thermo.Tmin.value)
        self.assertEqual(thermo0.Tmax.value, thermo.Tmax.value)
        self.assertEqual(thermo0.comment, thermo.comment)

    def testOutputWilhoit(self):
        """
        Test that we can reconstruct a Wilhoit object from its repr()
        output with no loss of information.
        """
        thermo0 = Wilhoit(cp0=4.0*constants.R, cpInf=21.0*constants.R, a0=-3.95, a1=9.26, a2=-15.6, a3=8.55, B=500.0, H0=-6.151e+04, S0=-790.2, Tmin=300.0, Tmax=2000.0, comment='CC(=O)O[O]')
        exec('thermo = %r' % thermo0)

        self.assertAlmostEqual(thermo0.cp0.value, thermo.cp0.value, 4)
        self.assertAlmostEqual(thermo0.cpInf.value, thermo.cpInf.value, 3)
        self.assertAlmostEqual(thermo0.a0.value, thermo.a0.value, 4)
        self.assertAlmostEqual(thermo0.a1.value, thermo.a1.value, 4)
        self.assertAlmostEqual(thermo0.a2.value, thermo.a2.value, 4)
        self.assertAlmostEqual(thermo0.a3.value, thermo.a3.value, 4)
        self.assertAlmostEqual(thermo0.H0.value, thermo.H0.value, 4)
        self.assertAlmostEqual(thermo0.S0.value, thermo.S0.value, 4)
        self.assertAlmostEqual(thermo0.B.value, thermo.B.value, 4)
        self.assertEqual(thermo0.Tmin.value, thermo.Tmin.value)
        self.assertEqual(thermo0.Tmax.value, thermo.Tmax.value)
        self.assertEqual(thermo0.comment, thermo.comment)

    def testOutputNASA(self):
        """
        Test that we can reconstruct a MultiNASA object from its repr()
        output with no loss of information.
        """

        nasa0 = NASA(coeffs=[11.0,12.0,13.0,14.0,15.0,16.0,17.0], Tmin=300.0, Tmax=1000.0, comment='This data is completely made up and unphysical')
        nasa1 = NASA(coeffs=[21.0,22.0,23.0,24.0,25.0,26.0,27.0], Tmin=1000.0, Tmax=6000.0, comment='This data is also completely made up and unphysical')

        thermo0 = MultiNASA(polynomials=[nasa0, nasa1], Tmin=300.0, Tmax=6000.0, comment='This data is completely made up and unphysical')
        exec('thermo = %r' % thermo0)

        self.assertEqual(len(thermo0.polynomials), len(thermo.polynomials))
        for poly0, poly in zip(thermo0.polynomials, thermo.polynomials):
            self.assertEqual(poly0.cm2, poly.cm2)
            self.assertEqual(poly0.cm1, poly.cm1)
            self.assertEqual(poly0.c0, poly.c0)
            self.assertEqual(poly0.c1, poly.c1)
            self.assertEqual(poly0.c2, poly.c2)
            self.assertEqual(poly0.c3, poly.c3)
            self.assertEqual(poly0.c4, poly.c4)
            self.assertEqual(poly0.c5, poly.c5)
            self.assertEqual(poly0.c6, poly.c6)
            self.assertEqual(poly0.Tmin.value, poly.Tmin.value)
            self.assertEqual(poly0.Tmax.value, poly.Tmax.value)
            self.assertEqual(poly0.comment, poly.comment)

        self.assertEqual(thermo0.Tmin.value, thermo.Tmin.value)
        self.assertEqual(thermo0.Tmax.value, thermo.Tmax.value)
        self.assertEqual(thermo0.comment, thermo.comment)


################################################################################

if __name__ == '__main__':
    unittest.main( testRunner = unittest.TextTestRunner(verbosity=2) )
