import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="trace",
    version="0.1",
    author="Svirskiy Ivan",
    author_email="fr0ststone878@gmail.com",
    description="package for tracing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DieOfCode/traceroute",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3"
    ],
    python_requires='>=3.6',
)
