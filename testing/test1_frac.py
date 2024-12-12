from main_transpile_frac import make_model_frac
from layers.utils import fixed_point_to_float_decimal
import torch

def calculate_expected_output(model):
    torch_model = model.model
    inputs = model.random_test_inputs
    torch_model.eval()
    with torch.no_grad():
        output = torch_model(torch.tensor([inputs], dtype=torch.float32))
    return output.item()

def verify_results(model, int_bits, frac_bits):
    with open('output_files_frac/test_values.txt', 'r') as f:
        # Read both lines
        inputs_line = f.readline().strip()
        output_line = f.readline().strip()
        
        try:
            # Parse inputs and output
            inputs = [int(x) for x in inputs_line.split(',')]
            actual_out = int(output_line)
            # convert to float
            actual_out = fixed_point_to_float_decimal(actual_out, int_bits, frac_bits)
            
            # Calculate expected output
            expected_out = calculate_expected_output(model)
            
            # Compare results
            if abs(expected_out - actual_out) < 1e-2:
                print(f"✅ Test passed!")
                print(f"Inputs: {inputs}")
                print(f"Expected: {expected_out}, Got: {actual_out}")
            else:
                print(f"❌ Test failed!")
                print(f"Inputs: {inputs}")
                print(f"Expected: {expected_out}, Got: {actual_out}")
                
        except ValueError as e:
            print(f"Error parsing file: {e}")
            print(f"Input line: {inputs_line!r}")
            print(f"Output line: {output_line!r}")

if __name__ == "__main__":
    model = make_model_frac()
    FW = model.FW
    tot_bits = model.layers[-1].out_bits[0]
    int_bits = tot_bits - FW
    verify_results(model, int_bits, FW) 

