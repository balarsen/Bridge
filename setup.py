import setuptools

with open("README", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Bridge",
    version="0.0.1",
    author="Brian Larsen",
    author_email="balarsen@gmail.com",
    description="A Bridge simulator for learning/playing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/balarsen/Bridge",
    project_urls={
        "Bug Tracker": "https://github.com/balarsen/Bridge/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD-3-Clause",
        "Operating System :: OS Independent",
    ],
    # package_dir={"": "Bridge"},
    # packages=setuptools.find_packages(where="Bridge"),
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
)