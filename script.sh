#! /bin/bash
# INTEGER

echo "SIMULATING ON INTEGERS\n"

python main_transpile.py

iverilog -o output_files/out.vvp output_files/test_tb.v output_files/test.v

vvp output_files/out.vvp

# gtkwave output_files/tb_top.vcd # uncomment to view waveform


python testing/test1.py

echo "\n"

# FRACTIONAL

echo "SIMULATING ON FRACTIONALS \n"

python main_transpile_frac.py

iverilog -o output_files_frac/out.vvp output_files_frac/test_tb.v output_files_frac/test.v

vvp output_files_frac/out.vvp

# gtkwave output_files/tb_top.vcd # uncomment to view waveform

python testing/test1_frac.py


# #  EXPERIMENTING WITH FP
# iverilog -o experimenting_fixpoint/out.vvp experimenting_fixpoint/test_tb.v experimenting_fixpoint/test.v

# vvp experimenting_fixpoint/out.vvp

