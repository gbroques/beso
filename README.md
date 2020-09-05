# beso simple
Python code for a topology optimization using CalculiX FEM solver.
Description with a simple example are in [wiki](https://github.com/fandaL/beso/wiki).

A fork of [fandaL/beso](https://github.com/fandaL/beso) designed to be simpler.

## Environment Setup
1. Install [Miniconda](https://docs.conda.io/en/latest/miniconda.html).
2. Create a dedicated `beso` conda environment:

       conda env create -f environment.yml

3. You can activate the newly created `beso` conda environment with:

       conda activate beso

4. and decactivate it with:

       conda deactivate beso

## Unit Tests
Unit tests are included in the `tests/` directory and can be executed with the following command:

    python -m unittest discover tests "*_test.py"

Note, create and activate the `beso` conda environment by following the instructions under [Environment Setup](#environment-setup) first.
