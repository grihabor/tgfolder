from setuptools import setup, find_packages

setup(
    name="tgfolder",
    version="0.0.1",
    install_requires=[
        "telethon>=1.19,<2",
        "click>=7.1,<8",
        "pydantic>=1.7,<2",
    ],
    entry_points={
        "console_scripts": ["tgfolder=tgfolder.main:main"],
    },
    package_dir={"": "src"},
    packages=find_packages("src"),
)
