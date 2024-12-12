# PyTorch to Verilog Transpiler

Running the test.

Make sure you have iverilog and gtkwave installed.

run `$ zsh script.sh`

-----

This project is a PyTorch to Verilog transpiler, designed to convert neural network models created in PyTorch into hardware description language (HDL) code written in Verilog. This conversion allows for the deployment of machine learning models on hardware accelerators such as FPGAs, enabling real-time inference at low power consumption.

This project is an extension of the chipon repo developed by [rohittp0](https://github.com/rohittp0/chipon) for the class CS252R at Harvard University. This repo has generalized the number of inputs it can handle, added new layers to it, and added support for fractional numbers.



## Overview

The PyTorch to Verilog transpiler takes a PyTorch model, represented as an instance of `nn.Sequential`, and converts it into Verilog code that can be synthesized and deployed on FPGA or other hardware platforms. The generated Verilog code represents the neural network as a hardware module, enabling efficient and low-latency inference.


## Prerequisites

Before using this transpiler, make sure you have the following prerequisites installed:

- PyTorch: The PyTorch deep learning framework for defining and training neural networks.
- Python: The Python programming language, used to run the transpiler script.

## Usage

1. **Define Your PyTorch Model**: 
The endpoint where you can define your model is in `main_transpile.py` and `main_transpile_frac.py`, for the integer and fractional versions respectively. They will be refactored and merged at a later date. The fractional version currently only supports one linear layer.

After defining the different models, test it running the `script.sh` script. 

In the script, both the fractional and the integer versions are simulated and tested against the pytorch models actual output. In the back end, we generate two verilog files, `test.v` and `test_tb.v`, which are the actual verilog code and the test bench respectively. Then we use iverilog to compile the verilog code and vvp to simulate it. The output is then written to the test_values.txt file. We then run the python test scripts which reads from this file, converts the output to a float in the fractional case, and compares it to the pytorch model's output.