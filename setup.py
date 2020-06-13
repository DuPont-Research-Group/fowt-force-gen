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
    packages=['fowt_force_gen', 'fowt_force_gen.tests'],
    package_data={'fowt_force_gen': ['example_files/*', 'example_files/**/*',
                                          'fast_input_files/*', 'fast_input_files/**/*',
                                          'template_files/*', 'tuning_files/*', '.filepaths/*'],
                  'fowt_force_gen.tests': ['test_data/*', 'test_fast/*', 'test_fast/**/*']},
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