# beso simple
[![Build Status](https://travis-ci.org/gbroques/beso-simple.svg?branch=master)](https://travis-ci.org/gbroques/beso-simple)
[![Coverage Status](https://coveralls.io/repos/github/gbroques/beso-simple/badge.svg?branch=master)](https://coveralls.io/github/gbroques/beso-simple?branch=master)

* [Introduction](#introduction)
* [How to Run](#how-to-run)
* [Unit Tests](#unit-tests)
* [Environment Setup](#environment-setup)

## Introduction
Python code for a topology optimization using CalculiX FEM solver.
Description with a simple example are in [wiki](https://github.com/fandaL/beso/wiki).

A fork of [fandaL/beso](https://github.com/fandaL/beso) designed to be simpler.

## How to Run
1. Install [CalculiX](http://www.calculix.de/). `ccx` must be in your PATH.
2. Create and activate the `beso` conda environment by following the instructions under [Environment Setup](#environment-setup) first.
3. Generate a CalculiX input file (`.inp`), and move it into the root of the repository.
    1. Update the `file_name` in `beso/beso_conf.py`.
4. Run `python main.py`.

## Unit Tests
Unit tests are included in the `tests/` directory.

Create and activate the `beso` conda environment by following the instructions under [Environment Setup](#environment-setup) first.

Execute the test-suite with the following command:

    pytest tests

## Environment Setup
1. Install [Miniconda](https://docs.conda.io/en/latest/miniconda.html).
2. Create a dedicated `beso` conda environment:

       conda env create -f environment.yml

3. You can activate the newly created `beso` conda environment with:

       conda activate beso

4. and decactivate it with:

       conda deactivate beso
