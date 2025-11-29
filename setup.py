"""Setup configuration for layering detector package."""

from setuptools import setup, find_packages

try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "Market manipulation detection system"

setup(
    name="layering-detector",
    version="1.0.0",
    author="Sara Golombeck",
    author_email="sara.beck.dev@gmail.com",
    description="Financial market layering manipulation detection system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sara-golombeck/layering-detector",
    
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    
    python_requires=">=3.9",
    install_requires=[
        "pandas>=2.0.0",
        "numpy>=1.24.0",
    ],
    entry_points={
        "console_scripts": [
            "layering-detector=layering_detector.main:main",
        ],
    },
)