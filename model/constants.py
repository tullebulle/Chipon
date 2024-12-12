test_bench_template = r"""`timescale 1ns / 1ps

module tb_top;
    {in_definitions}
    {out_definitions}
    integer file;

    top dut(
        {in_params},
        {out_params}
    );

    initial begin
        // Open a file for writing test data
        file = $fopen("output_files/test_values.txt", "w");

        $dumpfile("output_files/tb_top.vcd");
        $dumpvars(0, tb_top);
        
        // Wait a bit before starting simulation
        #2;
        
{assignments}

        // Add some delay to see the changes
        #50;

        // Display the values
        $fwrite(file, {file_in_str});
        $fwrite(file, "\n");
        $display("out0: %0d", out0);

        $fwrite(file, {file_out_str});
        #50;  // Add more delay before finishing

        $fclose(file);
        $finish;
    end
endmodule
"""

test_bench_template_frac = r"""`timescale 1ns / 1ps

module tb_top;
    {in_definitions}
    {out_definitions}
    integer file;

    top dut(
        {in_params},
        {out_params}
    );

    initial begin
        // Open a file for writing test data
        file = $fopen("output_files_frac/test_values.txt", "w");

        $dumpfile("output_files_frac/tb_top.vcd");
        $dumpvars(0, tb_top);
        
        // Wait a bit before starting simulation
        #2;
        
{assignments}

        // Add some delay to see the changes
        #50;

        // Display the values
        $fwrite(file, {file_in_str});
        $fwrite(file, "\n");
        $display("out0: %0d", out0);
        $display("fractional: %f", $itor(out0) / (1 << {FW}));

        $fwrite(file, {file_out_str});
        #50;  // Add more delay before finishing

        $fclose(file);
        $finish;
    end
endmodule
"""



multiplier_module = r"""
module multiplier_module #(parameter IW = 4, FW = 4) (input signed [IW + FW - 1:0] in1, input signed [IW + FW - 1:0] in2, output signed [IW + FW - 1:0] out);
    wire signed [2*(IW + FW) - 1:0] product_full; // Full product width before scaling

    assign product_full = in1 * in2; // Multiply inputs
    assign out = product_full[2*IW + FW - 1:FW]; // Scale down by 16 (Q4.4 format)
endmodule
"""

adder_module = r"""
module adder_module #(parameter IW = 4, FW = 4) (input signed [IW + FW - 1:0] in1, input signed [IW + FW - 1:0] in2, output signed [IW + FW - 1:0] out);
    assign out = in1 + in2; // Direct addition for Q4.4
endmodule
"""
