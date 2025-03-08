`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 03.03.2025 14:49:29
// Design Name: 
// Module Name: ascon_tb
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
module ascon_tb();
// Clock et reset
logic clock_i = 1'b0;
logic reset_i;

//Input
logic [63:0] data_i;
logic data_valid_i;
logic [127:0] key_i;
logic [127:0] nonce_i;
logic init_i;
logic associate_data_i;
logic finalisation_i;

//Output 
logic [63:0] cipher_o;
logic cipher_valid_o;
logic [127:0] tag_o;
logic end_tag_o;
logic end_initialisation_o;
logic end_cipher_o;
logic end_associate_o;

//Instanciation
ascon ascon_inst (
    .clock_i(clock_i),
    .reset_i(reset_i),
    .init_i(init_i),
    .associate_data_i(associate_data_i),
    .finalisation_i(finalisation_i),
    .data_i(data_i),
    .data_valid_i(data_valid_i),
    .key_i(key_i),
    .nonce_i(nonce_i),
    .end_associate_o(end_associate_o),
    .cipher_o(cipher_o),
    .cipher_valid_o(cipher_valid_o),
    .tag_o(tag_o),
    .end_tag_o(end_tag_o),
    .end_initialisation_o(end_initialisation_o),
    .end_cipher_o(end_cipher_o)
);
/*to do : adresse à changer ( que 16 blocs sur les 23 : 
5A5B5B5A5A5A5A5A 59554E4A4C4F5455 5351535456575857 5A5A595756595B5A 5554545252504F4F 4C4C4D4D4A494444 4747464442434140 3B36383E44494947 4746464443424345 4745444546474A49 4745484F58697C92 AECEEDFFFFE3B47C 471600041729363C 3F3E40414141403F 3F403F3E3B3A3B3E 3D3E3C393C414646 46454447464A4C4F 4C505555524F5155 595C5A595A5C5C5B 5959575351504F4F 53575A5C5A5B5D5E 6060615F605F5E5A 5857545252
*/
//donnée ECG (on découpe le truc en plusieurs blocs de 64 bits pour matcher avec la taille des elems) 
logic [63:0] ecg_data [0:22] = {64'h5A5B5B5A5A5A5A5A, 64'h59554E4A4C4F5455, 64'h5351515354565758, 64'h5A5A595756595B5A, 64'h5554545252504F4F, 64'h4C4C4D4D4A494444, 64'h4747464442434140, 64'h3B36383E44494947, 64'h4746464443424345, 64'h4745444546474A49, 64'h4745484F58697C92, 64'hAECEEDFFFFE3B47C, 64'h471600041729363C, 64'h3F3E40414141403F, 64'h3F403F3E3B3A3B3E, 64'h3D3E3C393C414646, 64'h46454447464A4C4F,64'h4C505555524F5155, 64'h595C5A595A5C5C5B,64'h5959575351504F4F, 64'h53575A5C5A5B5D5E, 64'h6060615F605F5E5A, 40'h5857545252  };
// on a 24 bits manquants ici 


//clock gen
always #5 clock_i = ~clock_i;

//reset
initial begin
    reset_i = 1;
    #10 reset_i = 0;
end

//sequence de test
initial begin
    //init  (aka on met tout à 0 et on rentre les bonnes valeurs)
    init_i = 0;
    associate_data_i = 0;
    finalisation_i = 0;
    data_valid_i = 0;
    key_i = 128'h8A55114D1CB6A9A2BE263D4D7AECAAFF;
    nonce_i = 128'h4ED0ECB98C529B7C8CDDF37BCD0284A;

    //start init (test init seul)
    #20 init_i = 1;
    #20 init_i = 0;

    wait(end_initialisation_o); //on attend la fin de l'initialisation
    
    //DA (48 bits + 80 00 (16 bits) de padding)
    associate_data_i = 1; //on envoie la DA
    data_i = 64'h4120746F20428000; // premiers 64 bits (48 bits + 16 bits de padding)
    data_valid_i = 1;
    #20 data_valid_i = 0;
    associate_data_i = 0; //fin de associate data 
 
    wait(end_associate_o); // on attend la fin du calcul de la donnée associée
     
    //loop pour tous les blocs du ecg 
    for (int i = 0; i < 22; i++) begin
        data_i = ecg_data[i]; // bloc courant
        data_valid_i = 1;     // on passe data_valid à 1
        #20;                  
        data_valid_i = 0;     // 
        #20;
        
        //print cipher pour chaque bloc 
        if (cipher_valid_o)begin 
            $display("Cipher : %h", cipher_o);
            end  
    end
    
    //on gère les 24 bits restants 
    data_i = ecg_data[22]; 
    data_valid_i = 1; 
    finalisation_i = 1;
    #20;
    data_valid_i = 0;
    
    //finalisation
     #20 finalisation_i = 0; 
    
    // on attend que le tag se genere 
    #150;
    //print resukt
    $display("Cipher output: %h", cipher_o);
    $display("Tag: %h", tag_o);

    #100 $finish;
end

endmodule
