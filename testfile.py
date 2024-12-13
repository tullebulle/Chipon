def float_to_fixed_point(value, int_bits, frac_bits):
    """
    Converts a float to a fixed-point binary representation.
    
    Args:
    - value (float): The decimal number to convert.
    - int_bits (int): Number of integer bits.
    - frac_bits (int): Number of fractional bits.
    
    Returns:
    - str: Binary representation as a string.
    """

    is_negative = value < 0
    # Scale the value by 2^(fractional bits)
    scale_factor = 2 ** frac_bits
    scaled_value = int(value * scale_factor)
    
    # Determine the total number of bits
    total_bits = int_bits + frac_bits
    
    # Handle negative numbers using two's complement
    if scaled_value < 0:
        scaled_value = (1 << total_bits) + scaled_value  # Two's complement
    
    # Convert to binary string with proper bit width
    binary_representation = f"{scaled_value:0{total_bits}b}"

    prefix = str(int_bits + frac_bits) + "'b"
    
    # Format for readability: integer.fractional
    binary_with_point = ("-" if is_negative else "") + prefix + f"{binary_representation[:-frac_bits]}{binary_representation[-frac_bits:]}"
    
    return binary_with_point


# Example usage
# num1 = 0.4975365687586023
# num2 = 0.2661737230725406
# binary_representation1 = float_to_fixed_point(num1, 12, 8)
# binary_representation2 = float_to_fixed_point(num2, 12, 8)
# print(binary_representation1)
# print(binary_representation2)
# print(num1 + num2)
# print(num1 * num2)


def fixed_point_to_float_decimal(decimal_value, int_bits, frac_bits):
    """
    Converts a fixed-point decimal integer representation back to a float.
    
    Args:
    - decimal_value (int): The integer value (in decimal) representing the fixed-point number.
    - int_bits (int): Number of integer bits.
    - frac_bits (int): Number of fractional bits.
    
    Returns:
    - float: The converted float value.
    """
    total_bits = int_bits + frac_bits

    # Check if the value is negative (signed value handling)
    is_negative = (decimal_value & (1 << (total_bits - 1))) != 0
    if is_negative:
        # Convert from two's complement
        decimal_value -= (1 << total_bits)
    
    # Convert back to float
    scale_factor = 2 ** frac_bits
    float_value = decimal_value / scale_factor
    
    return float_value

# Example usage with decimal integer input
# decimal_value = 4028  # Represents 2.375 in Q4.4
# int_bits = 8
# frac_bits = 12
# result = fixed_point_to_float_decimal(decimal_value, int_bits, frac_bits)
# print(result)




import matplotlib.pyplot as plt
import numpy as np

# Data
fractional_bits = [4, 6, 8, 10, 12, 14, 16]
true_value = 1.3044066429138184
calculated_values = [0.75, 1.21875, 1.28515625, 1.30078125, 1.30322265625, 1.30413818359375, 1.3043365478515625]

# Calculate log of the differences
log_errors = [np.log10(abs(true_value - calc)) for calc in calculated_values]

# Plot
plt.figure(figsize=(10, 6))
plt.plot(fractional_bits, log_errors, color='orange', marker='o', label='Log of Error (log10 scale)')

# Labels and title
plt.title('Logarithmic Convergence of Calculated Values to True Value', fontsize=14)
plt.xlabel('Number of Fractional Bits (Precision)', fontsize=12)
plt.ylabel('Log10 of Error', fontsize=12)
plt.grid(which='both', linestyle='--', linewidth=0.5)
plt.legend(fontsize=12)
plt.tight_layout()
plt.savefig('../../../PL/pl_project/latex_writeup/figures/fracerror.png')

# Display plot
plt.show()
