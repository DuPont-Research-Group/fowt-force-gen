import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='fowt_force_gen',
    version='0.1.0',
    description="A package to use OpenFAST to simulate a floating wind turbine at a certain location",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Michael Devin",
    author_email="michaelcdevin@outlook.com",
    url="https://github.com/michaelcdevin/fowt_force_gen",
    packages=['fowt_force_gen.build', 'fowt_force_gen.tests'],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Natural Language :: English",
    ],
    license='MIT License',
    python_requires='>=3',
    zip_safe=False
)