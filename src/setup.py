# // ---------------------------------------------------------------------
# // ------- [EZSQL] EZSQL Setup
# // ---------------------------------------------------------------------

# // ---- Imports
from setuptools import setup, find_packages

# // ---- Variables
VERSION = "0.0.1"
DESCRIPTION = "A Python package that makes working with SQLite easier."
LONG_DESCRIPTION = "A Python package that makes working with SQLite easier by removing the need to use SQL syntax."

# // ---- Main
setup(
    name = "EZSQL",
    version = "0.0.1",
    author = "Cuh4",

    description = "A Python package that makes working with SQLite easier.",
    long_description = "A Python package that makes working with SQLite easier by removing the need to use SQL syntax.",
    
    packages = find_packages(),
    install_requires = [
        "os",
        "sqlite3",
        "pathlib"
    ],
    
    keywords = [
        "SQL",
        "SQLite",
        "Python Package"
    ]
)

# py setup.py sdist bdist_wheel
# py -m twine upload dist/*