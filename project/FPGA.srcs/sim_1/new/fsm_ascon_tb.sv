`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 10.03.2025 13:52:03
// Design Name: 
// Module Name: fsm_ascon_tb
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////

module ascon_fsm_tb();

    // Clock and reset
    logic clock_i = 0;
    logic reset_i;

    // FSM outputs
    logic init_o;
    logic associate_data_o;
    logic finalisation_o;
    logic data_valid_o;
    logic [63:0] data_o;
    logic [127:0] key_o;
    logic [127:0] nonce_o;

    // FSM inputs
    logic cipher_valid_i;
    logic [63:0] cipher_i; 
    logic end_initialisation_i;
    logic end_associate_i;
    logic end_cipher_i;
    logic [127:0] tag_i;
    logic end_tag_i;
    
     // Données ECG
    logic [63:0] ecg_data [0:22] = {
        64'h5A5B5B5A5A5A5A5A, 64'h59554E4A4C4F5455, 64'h5351515354565758,
        64'h5A5A595756595B5A, 64'h5554545252504F4F, 64'h4C4C4D4D4A494444,
        64'h4747464442434140, 64'h3B36383E44494947, 64'h4746464443424345,
        64'h4745444546474A49, 64'h4745484F58697C92, 64'hAECEEDFFFFE3B47C,
        64'h471600041729363C, 64'h3F3E40414141403F, 64'h3F403F3E3B3A3B3E,
        64'h3D3E3C393C414646, 64'h46454447464A4C4F, 64'h4C505555524F5155,
        64'h595C5A595A5C5C5B, 64'h5959575351504F4F, 64'h53575A5C5A5B5D5E,
        64'h6060615F605F5E5A, 40'h5857545252
    };

    //instanciation
    ascon_fsm uut (
        .clock_i(clock_i),
        .reset_i(reset_i),
        
        .init_o(init_o),
        .associate_data_o(associate_data_o),
        .finalisation_o(finalisation_o),
        .data_valid_o(data_valid_o),
        .data_o(data_o),
        .key_o(key_o),
        .nonce_o(nonce_o),
        .cipher_valid_i(cipher_valid_i),
        .cipher_i(cipher_i),
        
        .end_initialisation_i(end_initialisation_i),
        .ecg_data_i(ecg_data),
        .end_associate_i(end_associate_i),
        .end_cipher_i(end_cipher_i),
        .tag_i(tag_i),
        .end_tag_i(end_tag_i)
    );

    // Clock 
    always #5 clock_i = ~clock_i;

    //sequence test
    initial begin
        // Reset
        reset_i = 1;
        cipher_valid_i = 0;
        end_initialisation_i = 0;
        end_associate_i = 0;
        end_cipher_i = 0;
        end_tag_i = 0;
        #10 reset_i = 0; //Release dureset
        
        //init finish
        #20 end_initialisation_i = 1;
        #10 end_initialisation_i = 0;

        //DA finish
        #40 end_associate_i = 1;
        #10 end_associate_i = 0;

        //chiffrement bloc
        repeat (22) begin
            #30 end_cipher_i = 1; //
            cipher_i = $random; //output du cipher
            #30 end_cipher_i = 0;
        end

        //bloc final
        #30 end_cipher_i = 1;
        tag_i = 128'hDEADBEEFCAFEBABE0123456789ABCDEF;
        end_tag_i = 1;

        // end simulation
        #50;
        $finish;
    end
endmodule

