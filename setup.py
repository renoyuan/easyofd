
import setuptools 
 
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
 
setuptools.setup(
    name="easyofd", 
    version="0.0.8",    
    author="renoyuan",    
    author_email="renoyuan@foxmail.com",    
    description="easy parser OFD",
    long_description=long_description,   
    long_description_content_type="text/markdown",
    url="https://github.com/renoyuan/easyofd",    
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',   
)
