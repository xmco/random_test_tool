from setuptools import setup, find_packages
import re


def process_readme_for_pypi():
    new_lines = []
    with open('README.md') as f:
        for line in f.readlines():
            new_line = re.subn(":x:", "O", line)[0]
            new_line = re.subn(":white_check_mark:", "XX", new_line)[0]
            new_line = re.subn(":heavy_check_mark:", "X", new_line)[0]
            new_line = re.subn(":[^ /-]*:", "", new_line)[0]
            new_lines.append(new_line)
    return "".join(new_lines)


setup(
    name='random_test_tool',
    version='1.0.4',
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
    long_description=process_readme_for_pypi(),
    long_description_content_type="text/markdown",
    url="https://github.com/xmco/random_test_tool/"
)
