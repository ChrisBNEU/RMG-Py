#!/usr/bin/env python3

###############################################################################
#                                                                             #
# RMG - Reaction Mechanism Generator                                          #
#                                                                             #
# Copyright (c) 2002-2023 Prof. William H. Green (whgreen@mit.edu),           #
# Prof. Richard H. West (r.west@neu.edu) and the RMG Team (rmg_dev@mit.edu)   #
#                                                                             #
# Permission is hereby granted, free of charge, to any person obtaining a     #
# copy of this software and associated documentation files (the 'Software'),  #
# to deal in the Software without restriction, including without limitation   #
# the rights to use, copy, modify, merge, publish, distribute, sublicense,    #
# and/or sell copies of the Software, and to permit persons to whom the       #
# Software is furnished to do so, subject to the following conditions:        #
#                                                                             #
# The above copyright notice and this permission notice shall be included in  #
# all copies or substantial portions of the Software.                         #
#                                                                             #
# THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR  #
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,    #
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE #
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER      #
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING     #
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER         #
# DEALINGS IN THE SOFTWARE.                                                   #
#                                                                             #
###############################################################################

"""

"""
import os.path
import re
import logging

from rmgpy.data.base import Database, Entry, DatabaseError
import rmgpy.quantity


################################################################################

def save_entry(f, entry):
    """
    Write a Pythonic string representation of the given `entry` in the metal
    database to the file object `f`.
    """
    f.write('entry(\n')
    f.write('    index = {0:d},\n'.format(entry.index))
    f.write('    label = "{0}",\n'.format(entry.label))
    if entry.binding_energies:
        f.write('    bindingEnergies = {\n')
        for key, value in entry.binding_energies.items():
            f.write(f"        {key!r}: {value!r},\n")
        f.write("    },\n")
    if entry.surface_site_density:
        f.write("    surfaceSiteDensity = ({0}, '{1}'),\n".format(entry.surface_site_density.value,
                                                                  entry.surface_site_density.units))
    if entry.facet:
        f.write('    facet = "{0}",\n'.format(entry.facet))
    if entry.metal:
        f.write('    metal = "{0}",\n'.format(entry.metal))
    f.write(f'    shortDesc = """{entry.short_desc.strip()}""",\n')
    f.write(f'    longDesc = \n"""\n{entry.long_desc.strip()}\n""",\n')
    f.write(')\n\n')


################################################################################


################################################################################

class MetalLibrary(Database):
    """
    A class for working with a RMG metal library.
    """

    def __init__(self, label='', name='', short_desc='', long_desc=''):
        Database.__init__(self, label=label, name=name, short_desc=short_desc, long_desc=long_desc)

    def load_entry(self,
                   index,
                   label,
                   metal='',
                   facet='',
                   surfaceSiteDensity=None,
                   bindingEnergies=None,
                   shortDesc='',
                   longDesc='',
                   ):
        """
        Method for parsing entries in database files.
        Note that these argument names are retained for backward compatibility.
        """
        if bindingEnergies:
            binding_energies = dict()
            for element, energy in bindingEnergies.items():
                binding_energies[element] = rmgpy.quantity.Energy(energy)
        else:
            binding_energies = None
        
        if surfaceSiteDensity:
            surface_site_density = rmgpy.quantity.SurfaceConcentration(*surfaceSiteDensity)
        else:
            surface_site_density = None

        self.entries[label] = Entry(
            index=index,
            label=label,
            metal=metal,
            facet=facet,
            surface_site_density=surface_site_density,
            binding_energies=binding_energies,
            short_desc=shortDesc,
            long_desc=longDesc.strip(),
        )

    def load(self, path):
        """
        Load the metal library from the given path
        """
        Database.load(self, path, local_context={}, global_context={})

    def save_entry(self, path, entry):
        """
        Write the given `entry` in the metal database to the file object `f`.
        """
        return save_entry(path, entry)

    def get_binding_energies(self, label):
        """
        Get a metal's binding energies from its label.

        Raises DatabaseError (rather than returning None) if it can't be found.
        """
        try:
            binding_energies = self.entries[label].binding_energies
        except KeyError:
            raise DatabaseError(f'Metal {label!r} not found in metal library database. \
            Labels should be formatted MetalFacet (ex. Pt111).')
        if binding_energies is None:
            raise DatabaseError(f'Metal {label!r} has no binding energies in metal library database.')
        return binding_energies

    def get_surface_site_density(self, label):
        """
        Get a metal's surface site density from its label.

        Raises DatabaseError (rather than returning None) if it can't be found.
        """
        try:
            surface_site_density = self.entries[label].surface_site_density
        except KeyError:
            raise DatabaseError(f'Metal {label!r} not found in metal library database.')
        if surface_site_density is None:
            raise DatabaseError(f'Metal {label!r} has no surface site density in metal library database.')
        return surface_site_density

    def get_all_entries_on_metal(self, metal_name):
        """
        Get all entries from the database that are on a certain metal, for any facet,
        returning the labels.

        Raises DatabaseError (rather than an empty list) if none can be found.
        """
        matches = []
        for label, entry in self.entries.items():
            if entry.metal == metal_name:
                matches.append(label)

        if len(matches) == 0:
            raise DatabaseError(f'Metal {metal_name!r} not found in database.')

        return matches

class MetalPropertyLibrary(Database):
    """
    A class for working with a RMG metal library.
    """

    def __init__(self, label='', name='', short_desc='', long_desc=''):
        Database.__init__(self, label=label, name=name, short_desc=short_desc, long_desc=long_desc)

    def load_entry(self,
                   index,
                   label,
                   metal='',
                   valence_electrons=None,
                   electronegativity=None,
                   psi=None,
                   beta=None,
                   shortDesc='',
                   longDesc='',
                   ):
        """
        Method for parsing entries in database files.
        Note that these argument names are retained for backward compatibility.
        """
        if valence_electrons:
            valence_electrons = int(valence_electrons)
        else:
            valence_electrons = None
        
        if electronegativity:
            electronegativity = float(electronegativity)
        else:
            electronegativity = None

        if psi:
            psi = float(psi)
        else:
            psi = None

        if beta:
            beta = float(beta)
        else:
            beta = None

        self.entries[label] = Entry(
            index=index,
            label=label,
            metal=metal,
            valence_electrons=valence_electrons,
            electronegativity=electronegativity,
            psi=psi,
            beta=beta,
            short_desc=shortDesc,
            long_desc=longDesc.strip(),
        )
        

    def load(self, path):
        """
        Load the metal library from the given path
        """
        Database.load(self, path, local_context={}, global_context={})

    def save_entry(self, path, entry):
        """
        Write the given `entry` in the metal database to the file object `f`.
        """
        return save_entry(path, entry)

    def get_valence_electrons(self, label):
        """
        Get a metal's valence electrons from its label.

        Raises DatabaseError (rather than returning None) if it can't be found.
        """
        try:
            valence_electrons = self.entries[label].valence_electrons
        except KeyError:
            raise DatabaseError(f'Metal {label!r} not found in metal property database. \
            use the abbreviated element name (ex. Pt).')
        if valence_electrons is None:
            raise DatabaseError(f'Metal {label!r} has no valence electrons in metal properties database.')
        return valence_electrons
    
    def get_electronegativity(self, label):
        """
        Get a metal's electronegativity from its label.

        Raises DatabaseError (rather than returning None) if it can't be found.
        """
        try:
            electronegativity = self.entries[label].electronegativity
        except KeyError:
            raise DatabaseError(f'Metal {label!r} not found in metal property database. \
            use the abbreviated element name (ex. Pt).')
        if electronegativity is None:
            raise DatabaseError(f'Metal {label!r} has no electronegativity in metal properties database.')
        return electronegativity
    
    def get_psi(self, label):
        """
        Get a metal's psi from its label.

        Raises DatabaseError (rather than returning None) if it can't be found.
        """
        try:
            psi = self.entries[label].psi
        except KeyError:
            raise DatabaseError(f'Metal {label!r} not found in metal property database. \
            use the abbreviated element name (ex. Pt).')
        if psi is None:
            raise DatabaseError(f'Metal {label!r} has no psi in metal properties database.')
        return psi
    
    def get_beta(self, label):
        """
        Get a metal's beta from its label.

        Raises DatabaseError (rather than returning None) if it can't be found.
        """
        try:
            beta = self.entries[label].beta
        except KeyError:
            raise DatabaseError(f'Metal {label!r} not found in metal property database. \
            use the abbreviated element name (ex. Pt).')
        if beta is None:
            raise DatabaseError(f'Metal {label!r} has no beta in metal properties database.')
        return beta
    

class SitePropertyLibrary(Database):
    """
    A class for working with a RMG site properties
    """

    def __init__(self, label='', name='', short_desc='', long_desc=''):
        Database.__init__(self, label=label, name=name, short_desc=short_desc, long_desc=long_desc)

    def load_entry(self,
                   index,
                   label,
                   metal='',
                   facet='',
                   site='',
                   coordination_number=None,
                   shortDesc='',
                   longDesc='',
                   ):
        """
        Method for parsing entries in database files.
        Note that these argument names are retained for backward compatibility.
        """
        if coordination_number:
            coordination_number = float(coordination_number)
        else:
            coordination_number = None

        self.entries[label] = Entry(
            index=index,
            label=label,
            metal=metal,
            facet=facet,
            site=site,
            coordination_number=coordination_number,
            short_desc=shortDesc,
            long_desc=longDesc.strip(),
        )

    def load(self, path):
        """
        Load the metal library from the given path
        """
        Database.load(self, path, local_context={}, global_context={})

    def save_entry(self, path, entry):
        """
        Write the given `entry` in the metal database to the file object `f`.
        """
        return save_entry(path, entry)
    

    def get_coordination_number(self, label):
        """
        Get a metal's coordination number from its label.

        Raises DatabaseError (rather than returning None) if it can't be found.
        """
        try:
            coordination_number = self.entries[label].coordination_number
        except KeyError:
            raise DatabaseError(f'Metal {label!r} not found in site property database. \
            Labels should be formatted MetalFacet (ex. Pt111).')
        if coordination_number is None:
            raise DatabaseError(f'Metal {label!r} has no coordination number in site property database.')
        return coordination_number
    

    def get_all_entries_on_facet(self, facet_name):
        """
        Get all the sites for a specific facet 

        Raises DatabaseError (rather than an empty list) if none can be found.
        """
        matches = []
        for label, entry in self.entries.items():
            if entry.facet == facet_name:
                matches.append(label)

        if len(matches) == 0:
            raise DatabaseError(f'Metal {facet_name!r} not found in database.')

        return matches
    
    def get_all_coordination_numbers_on_facet(self, facet_name):
        """
        Get all the sites for a specific facet 

        Raises DatabaseError (rather than an empty list) if none can be found.
        """
        matches = {}
        for label, entry in self.entries.items():
            if entry.facet == facet_name:
                matches[label] = entry.coordination_number

        if len(matches) == 0:
            raise DatabaseError(f'Metal {facet_name!r} not found in database.')

        return matches


################################################################################

class MetalDatabase(object):
    """
    A class for working with the RMG metal database.
    """

    def __init__(self):
        self.libraries = {}
        self.libraries['surface'] = MetalLibrary()
        self.groups = {}
        self.local_context = {}
        self.global_context = {}

    def __reduce__(self):
        """
        A helper function used when pickling a MetalDatabase object.
        """
        d = {
            'libraries': self.libraries,
        }
        return (MetalDatabase, (), d)

    def __setstate__(self, d):
        """
        A helper function used when unpickling a MetalDatabase object.
        """
        self.libraries = d['libraries']

    def load(self, path, libraries=None, depository=True):
        """
        Load the metal database from the given `path` on disk, where `path`
        points to the top-level folder of the surface database.
        
        Load the metal library
        """
        self.libraries['surface'].load(os.path.join(path, 'libraries', 'metal.py'))

    def get_binding_energies(self, metal_label):
        """
        Get a metal's binding energies from its label
        """
        return self.libraries['surface'].get_binding_energies(metal_label)

    def get_surface_site_density(self, metal_label):
        """
        Get a metal's surface site desnity from its label
        """
        return self.libraries['surface'].get_surface_site_density(metal_label)

    def get_all_entries_on_metal(self, metal):
        """
        Get all entries from the database that are on a certain metal, on any facet,
        returning the labels.
        """
        return self.libraries['surface'].get_all_entries_on_metal(metal)

    def find_binding_energies(self, metal):
        """
        Tries to find a match in the database when given a metal and/or facet and returns the binding energies or a
        best guess of binding energies.
        """
        if metal is None:
            raise DatabaseError("Cannot search for nothing.")
        assert isinstance(metal, str)

        facet = re.search(r'\d+', metal)

        if facet is not None:
            try:
                metal_binding_energies = self.libraries['surface'].get_binding_energies(metal)
            except DatabaseError:
                # no exact match was found, so continue on as if no facet was given
                logging.warning("Requested metal %r not found in database.", metal)
                metal = metal[:facet.span()[0]]
                logging.warning("Searching for generic %r.", metal)
                facet = None

        if facet is None:
            # no facet was specified, so use the first
            metal_entry_matches = self.libraries['surface'].get_all_entries_on_metal(metal)

            if len(metal_entry_matches) == 1:
                metal_binding_energies = self.libraries['surface'].get_binding_energies(metal_entry_matches[0])
            elif metal_entry_matches is None:  # no matches
                raise DatabaseError(f"No metal {metal} found in metal database.")
            else:  # multiple matches
                # average the binding energies together? just pick the first one?
                # just picking the first one for now...
                logging.warning(f"Found multiple binding energies for {metal!r}. Using {metal_entry_matches[0]!r}.")
                metal_binding_energies = self.libraries['surface'].get_binding_energies(metal_entry_matches[0])

        return metal_binding_energies

    def add_entry(self, entry):
        """
        Add an entry to a metal library
        """
        self.libraries['surface'].entries[f'{entry.label}'] = entry

    def remove_entry(self, entry):
        """
        Remove an entry from a metal library
        """
        self.libraries['surface'].entries.pop(f'{entry.label}')

    def save(self, path):
        """
        Save the metal database to the given `path` on disk, where `path`
        points to the top-level folder of the metal database.
        """
        path = os.path.abspath(path)
        if not os.path.exists(path):
            os.mkdir(path)
        self.save_libraries(os.path.join(path, 'libraries/metal.py'))

    def save_libraries(self, path):
        """
        Save the metal libraries to the given `path` on disk, where `path`
        points to the top-level folder of the metal libraries.
        """
        if not os.path.exists(path):
            os.mkdir(path)
        for library in self.libraries.keys():
            self.libraries[library].save(path)

class MetalPropertyDatabase(object):
    """
    A class for working with the RMG metal property database.
    """

    def __init__(self):
        self.libraries = {}
        self.libraries['surface'] = MetalPropertyLibrary()
        self.groups = {}
        self.local_context = {}
        self.global_context = {}

    def __reduce__(self):
        """
        A helper function used when pickling a MetalDatabase object.
        """
        d = {
            'libraries': self.libraries,
        }
        return (MetalPropertyDatabase, (), d)

    def __setstate__(self, d):
        """
        A helper function used when unpickling a MetalDatabase object.
        """
        self.libraries = d['libraries']

    def load(self, path, libraries=None, depository=True):
        """
        Load the metal database from the given `path` on disk, where `path`
        points to the top-level folder of the surface database.
        
        Load the metal library
        """
        self.libraries['surface'].load(os.path.join(path, 'libraries', 'metal_properties.py'))

    def get_valence_electrons(self, metal_label):
        """
        Get a metal's valence electrons from its label
        """
        return self.libraries['surface'].get_valence_electrons(metal_label)
    
    def get_electronegativity(self, metal_label):
        """
        Get a metal's electronegativity from its label
        """
        return self.libraries['surface'].get_electronegativity(metal_label)
    
    def get_psi(self, metal_label):
        """
        Get a metal's psi from its label
        """
        return self.libraries['surface'].get_psi(metal_label)
    
    def get_beta(self, metal_label):
        """
        Get a metal's beta from its label
        """
        return self.libraries['surface'].get_beta(metal_label)

    def add_entry(self, entry):
        """
        Add an entry to a metal library
        """
        self.libraries['surface'].entries[f'{entry.label}'] = entry

    def remove_entry(self, entry):
        """
        Remove an entry from a metal library
        """
        self.libraries['surface'].entries.pop(f'{entry.label}')

    def save(self, path):
        """
        Save the metal database to the given `path` on disk, where `path`
        points to the top-level folder of the metal database.
        """
        path = os.path.abspath(path)
        if not os.path.exists(path):
            os.mkdir(path)
        self.save_libraries(os.path.join(path, 'libraries/metal_properties.py'))

    def save_libraries(self, path):
        """
        Save the metal libraries to the given `path` on disk, where `path`
        points to the top-level folder of the metal libraries.
        """
        if not os.path.exists(path):
            os.mkdir(path)
        for library in self.libraries.keys():
            self.libraries[library].save(path)

class SitePropertyDatabase(object):
    """
    A class for working with the RMG metal property database.
    """

    def __init__(self):
        self.libraries = {}
        self.libraries['surface'] = SitePropertyLibrary()
        self.groups = {}
        self.local_context = {}
        self.global_context = {}

    def __reduce__(self):
        """
        A helper function used when pickling a MetalDatabase object.
        """
        d = {
            'libraries': self.libraries,
        }
        return (SitePropertyDatabase, (), d)

    def __setstate__(self, d):
        """
        A helper function used when unpickling a MetalDatabase object.
        """
        self.libraries = d['libraries']

    def load(self, path, libraries=None, depository=True):
        """
        Load the metal database from the given `path` on disk, where `path`
        points to the top-level folder of the surface database.
        
        Load the metal library
        """
        self.libraries['surface'].load(os.path.join(path, 'libraries', 'site_properties.py'))

    def get_coordination_number(self, metal_label):
        """
        Get a metal's coordination number from its label
        """
        return self.libraries['surface'].get_coordination_number(metal_label)
    
    def get_all_entries_on_facet(self, facet):
        """
        Get all coordination number entries from the database that are on a set facet,
        returning the labels.
        """
        return self.libraries['surface'].get_all_entries_on_facet(facet)
    
    def get_all_coordination_numbers_on_facet(self, facet):
        """
        Get all coordination number entries from the database that are on a set facet,
        returning the labels.
        """
        return self.libraries['surface'].get_all_coordination_numbers_on_facet(facet)

    def add_entry(self, entry):
        """
        Add an entry to a metal library
        """
        self.libraries['surface'].entries[f'{entry.label}'] = entry

    def remove_entry(self, entry):
        """
        Remove an entry from a metal library
        """
        self.libraries['surface'].entries.pop(f'{entry.label}')

    def save(self, path):
        """
        Save the metal database to the given `path` on disk, where `path`
        points to the top-level folder of the metal database.
        """
        path = os.path.abspath(path)
        if not os.path.exists(path):
            os.mkdir(path)
        self.save_libraries(os.path.join(path, 'libraries/metal_properties.py'))

    def save_libraries(self, path):
        """
        Save the metal libraries to the given `path` on disk, where `path`
        points to the top-level folder of the metal libraries.
        """
        if not os.path.exists(path):
            os.mkdir(path)
        for library in self.libraries.keys():
            self.libraries[library].save(path)