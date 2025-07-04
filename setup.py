
import setuptools 
from easyofd import __version__
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
 
setuptools.setup(
    name="easyofd", 
    version=__version__,
    author="renoyuan",    
    author_email="renoyuan@foxmail.com",    
    description="easy operate OFD",
    long_description=long_description,   
    long_description_content_type="text/markdown",
    url="https://github.com/renoyuan/easyofd",    
    packages=setuptools.find_packages(exclude=["README.md",".vscode", ".vscode.*", ".git", ".git.*"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    install_requires=[   ### 依赖包
        "reportlab>=3.6.11",
        "xmltodict>=0.13.0",
        "loguru>=0.7.2",
        "fontTools>=4.43.1",
        "PyMuPDF>=1.23.4",
        "pyasn1>=0.6.0"
                     ],
    python_requires='>=3.8',   
)