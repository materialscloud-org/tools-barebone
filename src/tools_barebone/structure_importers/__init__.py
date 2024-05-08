import ase.io
from ase.data import atomic_numbers
from pymatgen.io.cif import CifParser as PMGCifParser
import qe_tools
import numpy as np


class UnknownFormatError(ValueError):
    pass


atoms_num_dict = {
    "H": 1,
    "He": 2,
    "Li": 3,
    "Be": 4,
    "B": 5,
    "C": 6,
    "N": 7,
    "O": 8,
    "F": 9,
    "Ne": 10,
    "Na": 11,
    "Mg": 12,
    "Al": 13,
    "Si": 14,
    "P": 15,
    "S": 16,
    "Cl": 17,
    "Ar": 18,
    "K": 19,
    "Ca": 20,
    "Sc": 21,
    "Ti": 22,
    "V": 23,
    "Cr": 24,
    "Mn": 25,
    "Fe": 26,
    "Co": 27,
    "Ni": 28,
    "Cu": 29,
    "Zn": 30,
    "Ga": 31,
    "Ge": 32,
    "As": 33,
    "Se": 34,
    "Br": 35,
    "Kr": 36,
    "Rb": 37,
    "Sr": 38,
    "Y": 39,
    "Zr": 40,
    "Nb": 41,
    "Mo": 42,
    "Tc": 43,
    "Ru": 44,
    "Rh": 45,
    "Pd": 46,
    "Ag": 47,
    "Cd": 48,
    "In": 49,
    "Sn": 50,
    "Sb": 51,
    "Te": 52,
    "I": 53,
    "Xe": 54,
    "Cs": 55,
    "Ba": 56,
    "La": 57,
    "Ce": 58,
    "Pr": 59,
    "Nd": 60,
    "Pm": 61,
    "Sm": 62,
    "Eu": 63,
    "Gd": 64,
    "Tb": 65,
    "Dy": 66,
    "Ho": 67,
    "Er": 68,
    "Tm": 69,
    "Yb": 70,
    "Lu": 71,
    "Hf": 72,
    "Ta": 73,
    "W": 74,
    "Re": 75,
    "Os": 76,
    "Ir": 77,
    "Pt": 78,
    "Au": 79,
    "Hg": 80,
    "Tl": 81,
    "Pb": 82,
    "Bi": 83,
    "Po": 84,
    "At": 85,
    "Rn": 86,
    "Fr": 87,
    "Ra": 88,
    "Ac": 89,
    "Th": 90,
    "Pa": 91,
    "U": 92,
    "Np": 93,
    "Pu": 94,
    "Am": 95,
    "Cm": 96,
    "Bk": 97,
    "Cf": 98,
    "Es": 99,
    "Fm": 100,
    "Md": 101,
    "No": 102,
    "Lr": 103,
    "Rf": 104,
    "Db": 105,
    "Sg": 106,
    "Bh": 107,
    "Hs": 108,
    "Mt": 109,
    "Ds": 110,
    "Rg": 111,
    "Cn": 112,
}


def get_atomic_numbers(symbols):
    """
    Given a list of symbols, return the corresponding atomic numbers.

    :raise ValueError: if the symbol is not recognized
    """
    retlist = []
    for s in symbols:
        try:
            retlist.append(atomic_numbers[s])
        except KeyError:
            raise ValueError("Unknown symbol '{}'".format(s))
    return retlist


def tuple_from_ase(asestructure):
    """
    Given a ASE structure, return a structure tuple as expected from seekpath

    :param asestructure: a ASE Atoms object

    :return: a structure tuple (cell, positions, numbers) as accepted
        by seekpath.
    """
    atomic_numbers = get_atomic_numbers(asestructure.get_chemical_symbols())
    structure_tuple = (
        asestructure.cell.tolist(),
        asestructure.get_scaled_positions().tolist(),
        atomic_numbers,
    )
    return structure_tuple


def tuple_from_pymatgen(pmgstructure):
    """
    Given a pymatgen structure, return a structure tuple as expected from seekpath

    :param pmgstructure: a pymatgen Structure object

    :return: a structure tuple (cell, positions, numbers) as accepted
        by seekpath.
    """
    frac_coords = [site.frac_coords.tolist() for site in pmgstructure.sites]
    structure_tuple = (
        pmgstructure.lattice.matrix.tolist(),
        frac_coords,
        pmgstructure.atomic_numbers,
    )
    return structure_tuple


def get_structure_tuple(  # pylint: disable=too-many-locals
    fileobject, fileformat, extra_data=None
):
    """
    Given a file-like object (using StringIO or open()), and a string
    identifying the file format, return a structure tuple as accepted
    by seekpath.

    :param fileobject: a file-like object containing the file content
    :param fileformat: a string with the format to use to parse the data

    :return: a structure tuple (cell, positions, numbers) as accepted
        by seekpath.
    """
    ase_fileformats = {
        "vasp-ase": "vasp",
        "xsf-ase": "xsf",
        "castep-ase": "castep-cell",
        "pdb-ase": "proteindatabank",
        "xyz-ase": "xyz",
        "cif-ase": "cif",  # currently broken in ASE: https://gitlab.com/ase/ase/issues/15
    }
    if fileformat in ase_fileformats.keys():
        asestructure = ase.io.read(fileobject, format=ase_fileformats[fileformat])

        if fileformat == "xyz-ase":
            # XYZ does not contain cell information, add them back from the
            # additional form data (note that at the moment we are not using the
            # extended XYZ format)
            if extra_data is None:
                raise ValueError(
                    "Please pass also the extra_data with the cell information if you want to use the xyz format"
                )
            # avoid generator expressions by explicitly requesting tuple/list
            cell = list(
                tuple(float(extra_data["xyzCellVec" + v + a]) for a in "xyz")
                for v in "ABC"
            )

            asestructure.set_cell(cell)

        return tuple_from_ase(asestructure)
    if fileformat == "cif-pymatgen":
        # Only get the first structure, if more than one
        pmgstructure = PMGCifParser(fileobject).get_structures()[0]
        return tuple_from_pymatgen(pmgstructure)
    if fileformat == "qeinp-qetools":
        fileobject.seek(0)
        pwfile = qe_tools.parsers.PwInputFile(
            fileobject.read(), validate_species_names=True
        )
        pwparsed = pwfile.structure

        cell = pwparsed["cell"]
        rel_position = np.dot(pwparsed["positions"], np.linalg.inv(cell)).tolist()

        species_dict = dict(
            zip(pwparsed["species"]["names"], pwparsed["species"]["pseudo_file_names"])
        )

        numbers = []
        # Heuristics to get the chemical element
        for name in pwparsed["atom_names"]:
            # Take only characters, take only up to two characters
            chemical_name = "".join(char for char in name if char.isalpha())[
                :2
            ].capitalize()
            number_from_name = atoms_num_dict.get(chemical_name, None)
            # Infer chemical element from element
            pseudo_name = species_dict[name]
            name_from_pseudo = pseudo_name
            for sep in ["-", ".", "_"]:
                name_from_pseudo = name_from_pseudo.partition(sep)[0]
            name_from_pseudo = name_from_pseudo.capitalize()
            number_from_pseudo = atoms_num_dict.get(name_from_pseudo, None)

            if number_from_name is None and number_from_pseudo is None:
                raise KeyError(
                    "Unable to parse the chemical element either from the atom name or for the pseudo name"
                )
            # I make number_from_pseudo prioritary if both are parsed,
            # even if they are different
            if number_from_pseudo is not None:
                numbers.append(number_from_pseudo)
                continue

            # If we are here, number_from_pseudo is None and number_from_name is not
            numbers.append(number_from_name)
            continue

        # Old conversion. This does not work for multiple species
        # for the same chemical element, e.g. Si1 and Si2
        # numbers = [atoms_num_dict[sym] for sym in pwparsed['atom_names']]

        structure_tuple = (cell, rel_position, numbers)
        return structure_tuple

    raise UnknownFormatError(fileformat)
