# Installation Instructions

### Compatibility

*Random Test Tool* runs in Python 3! 

It has minimal dependencies, all of which can be installed with the following commands below.

### Install through package manager 

Available here: https://pypi.org/project/random-test-tool/

```Shell
pip install random-test-tool
```

### Install through repository

We advise to use a python virtual environment:
```Shell
python3.12 -m venv venv
source venv/bin/activate
```

Setuptools is needed for the installation:
```Shell
pip install setuptools
```

You can now install Random Test Tool
```Shell
git clone https://github.com/xmco/random-test-tool
cd random-test-tool
python setup.py install
```

### Run with docker

```Shell
git clone https://github.com/xmco/random-test-tool
cd random-test-tool
docker build -t rtt_image --rm .
docker run -it --name rtt_app --rm rtt_image
```

To create a bind mount with host at `random_generator_samples` use:

```Shell
docker run -it --name rtt_app --mount type=bind,source="$(pwd)"/random_generator_samples,target=/home/rtt_user/random_generator_samples --rm rtt_image
```

### Basic usage example

```Shell
random-test-tool -d random_generator_samples/python_random_bits
```

For usage documentation check Usage section in [README.md](README.md).