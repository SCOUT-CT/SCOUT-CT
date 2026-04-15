# SCOUT-CT

A sound binary analysis tool for constant-time verification that uses multi-taint analysis to track overapproximation.

## Installing SCOUT-CT

### Prerequisites
- SCOUT-CT requires Python 3.12.
- SCOUT-CT is built with [PDM](https://pdm-project.org/en/latest/). To use SCOUT-CT, install PDM.

### Install

- Run the command `pdm install` from the root directory of the repository. This will create a Python virtual environement and install all the required Python packages.
- Run `source .venv/bin/activate` to activate the Python environement.
- Run `scoutct --help` to see if CTTBench is correctly installed. This should print the help message of `cttbench`.
- External libraries are imported as git submodules. They are only needed to run the tests. To fetch the submodules, run:
    1. `git submodule init`
    2. `git submodule update`

### Run an analysis

To run analysis, you need a configuration file and a target program. A configuration example is available in `config/app.yml`.

The file `config/common.yml` contains configurations on where the results are writen. They are saved by default in the `results` directory within the project's base directory. If the key `outputs.save_results` in `config/common.yaml` is set to `false`, the reslults are printed in the console and not saved in a file.

The analysis is composed of two phases, `analyze` and `results`. You can run them seperately or at once by using the `full` subcommand.

**Example 1:**

```bash
scoutct analyze --config config/app.yml --target tests/build/ci/aes-enc-of
scoutct results --config config/app.yml --target tests/build/ci/aes-enc-of
```

**Example 2:**
```bash
scoutct full --config config/app.yml --target tests/build/ci/aes-enc-of
```

## Target program

The program to be tested must accept two arguments.
The first argument is considered to be the secret input while the second argument is considered to be the public input.

The target program must have been compiled with the debug symbols (-g) and without optimizations.


## Implementation

The tool is implemented on top of the symbolic execution framework `angr`.
The key implementation aspects are :

- An abstract state is represented by an `angr` program state, where tainted bytes are represented as symbolic expressions.
- The secret input is represented by a "red" symbol, the public input by a "green" symbol, and overapproximated data appearing during the analysis by an "orange" symbol. 
- Expressions are considered red tainted if they depend on the red symbol, otherwise orange tainted if they depend on the orange symbol, otherwise green tainted.
- We disable the collection of path constraints and the calls to the SMT solver. When a branch with a tainted (symbolic) condition is encountered, both directions are systematically explored.

The core implementation is in files `src/ya_cttool/core/cfgexploration.py` and `src/ya_cttool/core/tainting.py`.
See the documentation of those files for more details.

