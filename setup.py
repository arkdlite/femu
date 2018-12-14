from setuptools import setup, find_packages
from os import system, path, chdir


DIR = path.dirname(path.abspath( __file__ ))

with open("README.md", "r") as fh:
    long_description = fh.read()

chdir(path.join(DIR, "femu"))
system("glib-compile-resources --target=res.gresource res.gresource.xml")
chdir(DIR)

setup(
    name="femu",
    version="0.3.0",
    author="Arkadii Chekha",
    author_email="arkdlite@protonmail.com",
    description="The mining setup utility",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/arkdlite/femu",
    scripts=['femu/femu'],
    py_modules=[
                'femu/main'
                'femu/nvidia_oc',
                'femu/driver_installer',
                'femu/femu_config',
                'femu/amd_oc'
                ],
    data_files=[('/usr/share/femu/resources', ['femu/res.gresource'])],
    packages=['femu'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Environment :: X11 Applications :: GTK",
        "License :: OSI Approved :: GNU General Public License (GPL)",
    ],
)
