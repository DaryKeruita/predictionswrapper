from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.0.1'
DESCRIPTION = 'Wrapper for Popular Prediction Platforms'
LONG_DESCRIPTION = 'Helps to manage your positions across the most popular BNB/USDT Prediction Platforms'

# Setting up
setup(
    name="PredictionsWrapper",
    version=VERSION,
    author="Dary Keruita",
    author_email="<darykeruita@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['pydantic', 'web3'],
    keywords=['pancakeswap', 'prediction', 'predictions', 'pancakeswap prediction', 'dogebet', 'dogebets',
              'candle genie', 'candle genie prediction', 'dogebets prediction', 'winning predictions',
              'winning pancakeswap', 'dogebets winner'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
