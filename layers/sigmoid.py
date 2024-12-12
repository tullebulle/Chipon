import numpy as np
from layers.utils import range_to_bits

class Sigmoid:
    def __init__(self, shape: int, index: int):
        self.shape = (shape,)
        self.name = f'layer_{index}_sigmoid_{shape}'
        self.in_bits, self.out_bits = None, None

    def __str__(self):
        return f'Sigmoid({self.shape})'

    def forward_range(self, in_range: np.ndarray):
        # Sigmoid output is always between 0 and 1
        out_range = np.array([[0, 1] for _ in range(self.shape[0])])

        self.in_bits = [range_to_bits(*in_range[i]) for i in range(self.shape[0])]
        self.out_bits = [range_to_bits(*out_range[i]) + 1 for i in range(self.shape[0])]

        return out_range

    def emit(self):
        """
        Emit the Verilog code for this layer.
        Using a piece-wise linear approximation of sigmoid:
        if x < -4:     return 0
        if x > 4:      return 1
        if -4 ≤ x ≤ 4: return 0.5 + 0.125*x
        """
        # Using fixed-point arithmetic with 8 fractional bits
        sigmoid_code = [
            f'''
            if (in{i} <= -4 << 8) begin
                out{i} = 0;
            end else if (in{i} >= 4 << 8) begin
                out{i} = 1;  // 1.0 in fixed point
            end else begin
                // 0.5 + 0.125*x implementation
                // (128 + x/8) in fixed point arithmetic
                out{i} = (128 << 8) + (in{i} >>> 3);
            end
            ''' for i in range(self.shape[0])
        ]

        in_params = [f"in{i}" for i in range(self.shape[0])]
        out_params = [f"out{i}" for i in range(self.shape[0])]

        in_definitions = [
            f"input signed [{self.in_bits[i] - 1}:0] {in_params[i]};\n"
            for i in range(self.shape[0])
        ]

        out_definitions = [
            f"output reg signed [{self.out_bits[i] - 1}:0] {out_params[i]};\n"
            for i in range(self.shape[0])
        ]

        return f"""
module {self.name}({",".join(in_params)}, {",".join(out_params)});
    {'    '.join(in_definitions)}
    {'    '.join(out_definitions)}
                
    always @(*) 
    begin
        {"        ".join(sigmoid_code)}
    end
endmodule
""" 