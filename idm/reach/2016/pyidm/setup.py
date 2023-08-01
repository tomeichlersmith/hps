"""A setuptools based setup module.

I copied this template from
https://github.com/pypa/sampleproject

and followed the Python packaging guide
https://packaging.python.org/guides/distributing-packages-using-setuptools/
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / "README.md").read_text(encoding="utf-8")

# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.

setup(
    name='pyidm',
    version="0.0.1",  # Required
    description="HPS iDM Analysis Python Tools",
    long_description=long_description,  # Optional
    long_description_content_type="text/markdown",  # Optional (see note above)
    classifiers=[  # Optional
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
    ],
    package_dir={"": "src"},  # Optional
    packages=find_packages(where="src"),  # Required
    python_requires=">=3.6, <4",
    install_requires=[
        "coffea==0.7.20",
        "vector==0.9.0",
        "hist==2.4.0"
    ],
    extras_require={  # Optional
        "dev": [
          "pycodestyle",
          "autopep8"
        ],
    },
    #entry_points={  # Optional
    #    "console_scripts": [
    #        "sample=sample:main",
    #    ],
    #},
)
