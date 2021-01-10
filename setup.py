from setuptools import setup, find_packages

setup(
    name='tgfolder',
    version='0.0.1',
    install_requires=['telethon', 'click', 'pydantic'],
    entry_points = {
        'console_scripts': ['tgfolder=tgfolder.main:main'],
    },
    package_dir={'': 'src'},
    packages=find_packages('src'),
)
