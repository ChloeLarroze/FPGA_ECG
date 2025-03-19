import logging
from ascon_pcsn import ascon_encrypt, ascon_decrypt#on importe que les fonctions dont on a besoin

#classe pour chiffrer et déchiffrer EGC
class ECGAsconCipher:
    def __init__(self, key, nonce, associated_data=b"", variant="Ascon-128"):
        """ Initialise les paramètres du chiffrement.
        :param key: bytes, clé de chiffrement.
        :param nonce: bytes, nonce pour le chiffrement.
        :param associated_data: bytes, données associées pour le chiffrement (par défaut vide).
        :param variant: str, variante d'Ascon à utiliser (par défaut "Ascon-128").
        """
        self.key = key
        self.nonce = nonce
        self.associated_data = associated_data
        self.variant = variant
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s') #on configure le logger pour les messages

    def encrypt_ecg_data(self, plaintext):
        """
        :param plaintext: bytes, les données ECG à chiffrer.
        :return: bytes, les données ECG chiffrées (ciphertext + tag).
        """
        logging.info("début chiffrement ECG data.")
        ciphertext = ascon_encrypt(self.key, self.nonce, self.associated_data, plaintext, self.variant)
        logging.info("finish.")
        return ciphertext

    def decrypt_ecg_data(self, ciphertext):
        """
        déchiffrement :
        :param ciphertext: bytes, les données ECG chiffrées (ciphertext + tag).
        :return: bytes, les données ECG déchiffrées.
        """
        logging.info("début déchiffrement ECG data.")
        plaintext = ascon_decrypt(self.key, self.nonce, self.associated_data, ciphertext, self.variant)
        if plaintext is not None:
            logging.info("finish")
        else:
            logging.error("erreur bon chance.")
        return plaintext

    @staticmethod 
    def read_ecg_from_csv(file_path):
        logging.info(f"lecture fic CSV: {file_path}")
        ecg_data = [] #on stocke les data ECG
        with open(file_path, 'r') as csvfile:
            for line in csvfile:
                line = line.strip()  #enlever les espaces
                if line:  #skip les lignes vide(en pp y en a pas)
                    try:
                        #on convertit la ligne en octets (23 blocs de 64 bits)
                        ecg_bytes = bytes.fromhex(line)
                        ecg_data.append(ecg_bytes)
                    except ValueError as e:
                        logging.warning(f"ligne invalide: {line}. Error: {e}")
        return ecg_data

    @staticmethod
    def write_ecg_to_csv(file_path, ecg_data):
        logging.info(f"écrirure ds le fic: {file_path}")
        with open(file_path, 'w') as csvfile:
            for line in ecg_data:
                #conv hexa 
                hex_line = line.hex()
                csvfile.write(hex_line + '\n')

# Example usage
if __name__ == "__main__":
    #ex 
    key = bytes.fromhex("8A55114D1CB6A9A2BE263D4D7AECAAFF")
    nonce = bytes.fromhex("4ED0EC0B98C529B7C8CDDF37BCD0284A")
    associated_data = b"A to B"

    #init cipher
    ecg_cipher = ECGAsconCipher(key, nonce, associated_data)

    #lecture
    csv_file_path = "/Users/chloelarroze/Desktop/FPGA_TP2/waveform_example_ecg.csv" 
    ecg_data = ecg_cipher.read_ecg_from_csv(csv_file_path)
    #print(f"donnée originelle: {ecg_data[0].hex()}") #debug print

    #chiffrement
    encrypted_data = []
    for line in ecg_data:
        encrypted_line = ecg_cipher.encrypt_ecg_data(line)
        encrypted_data.append(encrypted_line)
    #print(f"donnée chiffrée): {encrypted_data[0].hex()}") #idem

    #dechiffremnet 
    decrypted_data = []
    for line in encrypted_data:
        decrypted_line = ecg_cipher.decrypt_ecg_data(line)
        if decrypted_line is not None:
            decrypted_data.append(decrypted_line)
        else:
            logging.error("erreur on skip la ligne.")
    #print(f"donnée déchiffrée: {decrypted_data[0].hex()}") #idem

    #vers le csv output
    output_csv_file_path = "decrypted_waveform_example_ecg.csv"
    ecg_cipher.write_ecg_to_csv(output_csv_file_path, decrypted_data)
    print(f"Decrypted ECG data written to: {output_csv_file_path}")