import os
import io

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

modulename = "tools_barebone"
the_license = "The MIT license"

# Get the version number in a dirty way
folder = os.path.split(os.path.abspath(__file__))[0]
fname = os.path.join(folder, modulename, "__init__.py")
with open(fname) as init:
    ns = {}
    # Get lines that match, remove comment part
    # (assuming it's not in the string...)
    versionlines = [
        l.partition("#")[0] for l in init.readlines() if l.startswith("__version__")
    ]
if len(versionlines) != 1:
    raise ValueError("Unable to detect the version lines")
versionline = versionlines[0]
version = versionline.partition("=")[2].replace('"', "").strip()

setup(
    name=modulename,
    description="A base scaffolding to create online web tools",
    url="http://github.com/materialscloud-org/tools-barebone",
    license=the_license,
    author="Materials Cloud team",
    version=version,
    install_requires=[
        "Flask>=1",
        "numpy>=1.16",
        "pyyaml>=5.3.1",
        "ase>=3",
        "qe-tools==2.0.0rc2",
        "pymatgen>=2019.7.2",
    ],
    extras_require={
        "dev": [
            "pre-commit==2.4.0",
            "pylint==2.4.4",
            "prospector==1.2.0",
            "pytest==5.3.5",
            "pytest-selenium==1.17.0",
            "pytest-regressions==2.0.0",
        ]
    },
    packages=find_packages(),
    # Needed to include some static files declared in MANIFEST.in
    include_package_data=True,
    download_url="https://github.com/materialscloud-org/tools-barebone/archive/v{}.tar.gz".format(
        version
    ),
    keywords=["tool", "web tool", "Materials Cloud"],
    long_description=io.open(
        os.path.join(folder, "README.md"), encoding="utf-8"
    ).read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
