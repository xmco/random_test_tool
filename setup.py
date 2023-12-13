from setuptools import setup, find_packages

setup(
    name='random_test_tool',
    version='1.0.2',
    author='Antoine Rigoureau',
    author_email='antoine.rigoureau@xmco.fr',
    description='A simple python tool used form validating pseudo random generators output.',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    install_requires=[
        "numpy==1.24.2",
        "packaging==23.0",
        "pandas==1.5.3",
        "patsy==0.5.3",
        "python-dateutil==2.8.2",
        "pytz==2023.3",
        "scipy==1.10.1",
        "six==1.16.0",
        "statsmodels==0.13.5",
        "tabulate==0.9.0",
        "matplotlib==3.7.1",
        "alive-progress==3.1.4",
        "bitstring==4.1.3",
        "tqdm==4.66.1",
    ],
    python_requires='>=3.9',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/xmco/random_test_tool/"
)