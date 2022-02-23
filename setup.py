from pathlib import Path

import tomli
from setuptools import find_packages, setup

with open("pyproject.toml", "rb") as f:
    pyproject = tomli.load(f)

setup(
    name=pyproject["tool"]["poetry"]["name"],
    description=pyproject["tool"]["poetry"]["description"],
    long_description=(Path(__file__).parent / "README.md").read_text(),
    long_description_content_type="text/markdown",
    author="zevaryx",
    author_email="zevaryx@gmail.com",
    url="https://github.com/zevaryx/pastypy",
    version=pyproject["tool"]["poetry"]["version"],
    packages=find_packages(),
    package_data={"pastypy": ["py.typed", "*.pyi", "**/*.pyi"]},
    python_requires=">=3.10",
    install_requires=(Path(__file__).parent / "requirements.txt").read_text().splitlines(),
    classifiers=[
        "Framework :: AsyncIO",
        "Framework :: aiohttp",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Documentation",
        "Typing :: Typed",
    ],
)
