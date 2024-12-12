from main_transpile import make_model
import torch

def calculate_expected_output(model):
    torch_model = model.model
    inputs = model.random_int_test_inputs
    print("inputs", inputs)
    torch_model.eval()
    with torch.no_grad():
        output = torch_model(torch.tensor([inputs], dtype=torch.int32))
    return output.item()

def verify_results(model):
    with open('output_files/test_values.txt', 'r') as f:
        # Read both lines
        inputs_line = f.readline().strip()
        output_line = f.readline().strip()
        
        try:
            # Parse inputs and output
            inputs = [int(x) for x in inputs_line.split(',')]
            actual_out = int(output_line)
            
            # Calculate expected output
            expected_out = calculate_expected_output(model)
            
            # Compare results
            if expected_out == actual_out:
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
    model = make_model()
    verify_results(model) 
