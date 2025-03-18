module ascon_fsm (

    input logic clock_i,
    input logic reset_i,
    
//inputs de ascon    
    output logic init_o,
    output logic associate_data_o,
    output logic finalisation_o,
    output logic data_valid_o,
    output logic [63:0] data_o,
    output logic [127:0] key_o,
    output logic [127:0] nonce_o,
    output logic count_o,
    output logic en_o,
//outputs de ascon
    input  logic [63:0] ecg_data_i [0:22],  
    input logic go_i,  
    input logic cipher_valid_i,
    input logic [63:0] cipher_i, 
    input logic end_initialisation_i,
    input logic end_associate_i,
    input logic end_cipher_i,
    input logic [127:0] tag_i,
    input logic end_tag_i
);
  
    typedef enum logic [3:0] {
        IDLE,
        INIT,
        WAIT_INIT,
        ASSOCIATE,
        WAIT_ASSOCIATE,
        PENDING, 
        INIT_BLOCK,
        PROCESS_BLOCKS,
        PENDING_BLOCK, 
        WAIT_BLOCK,
        INTERMEDIATE_BLOCK,
        FINALIZE,
        WAIT_FINALIZE,
        DONE
    } state_t;

    state_t etat_p, etat_f;
    int counter;

    // FSM
    always_ff @(posedge clock_i or posedge reset_i) begin
        if (reset_i) begin
            etat_p <= IDLE;
            counter <= 0;
        end else begin
            etat_p <= etat_f;
          //  if (etat_p == WAIT_BLOCK) begin
            //    counter <= counter + 1;
            //end
        end
    end

    //logique combinatoire
    always_comb begin
        etat_f = etat_p; //pour remplacer les else, on reste dans l'état présent par défaut si if par rempli
        //valeurs par défaut 
        init_o = 0;
        en_o = 0; 
        //associate_data_o = 0;
        finalisation_o = 0;
        data_valid_o = 0;
        //data_o = 64'h0; //valeur par défaut, on ne dois pas aller le chercher en principe 
        key_o = 128'h8A55114D1CB6A9A2BE263D4D7AECAAFF;
        nonce_o = 128'h4ED0ECB98C529B7C8CDDF37BCD0284A;

        case (etat_p)
            IDLE: begin
                if (go_i)etat_f = INIT;
            end

            INIT: begin
                init_o = 1;
                en_o = 1; 
                etat_f = WAIT_INIT;
            end//

            WAIT_INIT: begin //attend la fin de l'init
                if (end_initialisation_i)etat_f = ASSOCIATE;
            end

            ASSOCIATE: begin
                associate_data_o = 1;
                data_o = 64'h4120746F20428000; //premier bloc de données associées
                etat_f = PENDING;
            end
            
            PENDING : begin 
                data_valid_o = 1;
                etat_f = WAIT_ASSOCIATE;
            end 

            WAIT_ASSOCIATE: begin ///attend la fin du premier bloc de DA
                data_valid_o = 0; 
                associate_data_o = 0;
                
                etat_f = INIT_BLOCK; //if (end_associate_i) etat_f = INIT_BLOCK;
            end

            INIT_BLOCK: begin
                counter = 0;  //nouvelle réinitialisation pour les blocs de données
                if (end_associate_i)  etat_f = PROCESS_BLOCKS;
            end

            PROCESS_BLOCKS: begin
                if (counter < 22) begin
                    data_o = ecg_data_i[counter];
                    etat_f = PENDING_BLOCK;
                end else begin
                    etat_f = FINALIZE;
                end
            end
            
            PENDING_BLOCK: begin
                data_valid_o = 1;  
                etat_f = WAIT_BLOCK;
            end 

            WAIT_BLOCK: begin
                data_valid_o = 0; 
                if (end_cipher_i) etat_f = INTERMEDIATE_BLOCK;
            end
            
            INTERMEDIATE_BLOCK: begin 
                counter ++;
                en_o =1; // le cipher_valid_i vaut systématiquement 1 ici 
                etat_f = PROCESS_BLOCKS;
            end

            FINALIZE: begin
                data_o = ecg_data_i[22];
                data_valid_o = 1;
                finalisation_o = 1;
                etat_f = WAIT_FINALIZE;
            end

            WAIT_FINALIZE: begin
                if (end_cipher_i && end_tag_i)
                    etat_f = DONE;
            end

            DONE: begin
                //fin de la FSM, peut rester ici ou revenir à IDLE si besoin
                $display("Cipher final :%h", cipher_i);
                $display("Tag :%h", tag_i);
            end
        endcase
    end
    //assign en_o = (cipher_valid_i || init_o); pas terrible, on préferera avoir des états stables 
    assign count_o = counter; //to check (see other placement) // à déplaer fin 
endmodule
