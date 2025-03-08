`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 07.03.2025 14:44:27
// Design Name: 
// Module Name: fsm_ascon
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
//FSM Moore pour piloter le module ASCON
import ascon_pack::*;

module fsm_ascon (
    //clock et reset
    input logic clock_i,
    input logic reset_i,
    
    //outputs (correspondent au entrées de ascon)
    output logic init_o,
    output logic associate_data_o,
    output logic finalisation_o,
    output logic data_valid_o,
    output logic [63:0] data_o,
    
    //inputs (correspondent au sorties de ascon)
    input logic end_initialisation_i,
    input logic end_associate_i,
    input logic end_cipher_i,
    input logic end_tag_i
);
  
    typedef enum logic [3:0] {
        IDLE,
        INIT,
        WAIT_INIT,
        ASSOCIATE,
        WAIT_ASSOCIATE,
        PROCESS_BLOCKS,
        WAIT_BLOCK,
        FINALIZE,
        WAIT_FINALIZE,
        DONE
    } state_t;

    state_t etat_p, etat_f;
    int counter; //counter pour les 23 blocs de 63 bits

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

    // FSM : Transition d'état
    always_ff @(posedge clock_i or posedge reset_i) begin
        if (reset_i) begin
            etat_p <= IDLE;
            counter <= 0; //init du counter dans l'idle
        end else begin
            etat_p <= etat_f;
        end
    end

    // FSM : Logique combinatoire pour déterminer le prochain état
    always_comb begin
        etat_f = etat_p;
        // on initialise 
        init_o = 0;
        associate_data_o = 0;
        finalisation_o = 0;
        data_valid_o = 0;
        data_o = 64'h0;

        case (etat_p)
            IDLE: begin
                etat_f = INIT;
            end

            INIT: begin
                init_o = 1;
                etat_f = WAIT_INIT;
            end

            WAIT_INIT: begin
                if (end_initialisation_i)
                    etat_f = ASSOCIATE;
            end

            ASSOCIATE: begin
                associate_data_o = 1;
                data_o = 64'h4120746F20428000; // Premier bloc de données associées
                data_valid_o = 1;
                etat_f = WAIT_ASSOCIATE;
            end

            WAIT_ASSOCIATE: begin
                if (end_associate_i)
                    etat_f = PROCESS_BLOCKS;
            end

            PROCESS_BLOCKS: begin
                if (counter < 22) begin
                    data_o = ecg_data[counter];
                    data_valid_o = 1;
                    etat_f = WAIT_BLOCK;
                end else begin
                    etat_f = FINALIZE;
                end
            end

            WAIT_BLOCK: begin
                etat_f = PROCESS_BLOCKS;
                counter = counter + 1;
            end

            FINALIZE: begin
                data_o = ecg_data[22];
                data_valid_o = 1;
                finalisation_o = 1;
                etat_f = WAIT_FINALIZE;
            end

            WAIT_FINALIZE: begin
                if (end_cipher_i && end_tag_i)
                    etat_f = DONE;
            end

            DONE: begin
                // Fin du FSM, peut rester ici ou revenir à IDLE si besoin
            end
        endcase
    end

endmodule