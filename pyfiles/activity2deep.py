import csv
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
import neurokit2 as nk
from ascon_pcsn import ascon_encrypt, ascon_decrypt #on importe que les fonctions dont on a besoin

# === Functions ===

def read_csv(file_path):
    """Read ECG waveform data from a CSV file where each line is a hexadecimal string."""
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        # Read each line as a hexadecimal string
        data = [row[0] for row in reader]
    return data

def hex_to_waveform(hex_string):
    """Convert a hexadecimal string into a list of integer values."""
    # Split the hex string into pairs of characters (each pair represents a byte)
    hex_pairs = [hex_string[i:i+2] for i in range(0, len(hex_string), 2)]
    # Convert each hex pair to an integer
    waveform = [int(pair, 16) for pair in hex_pairs]
    return waveform

def extract_waveform(data, index):
    """Extract a specific waveform from the ECG data."""
    hex_string = data[index]
    return hex_to_waveform(hex_string)

def encrypt_waveform(waveform, key, nonce, associateddata, variant="Ascon-128"):
    """Encrypt the ECG waveform using ASCON."""
    plaintext = bytes(int(val) for val in waveform)
    ciphertext = ascon_encrypt(key, nonce, associateddata, plaintext, variant)
    return ciphertext

def decrypt_waveform(ciphertext, key, nonce, associateddata, variant="Ascon-128"):
    """Decrypt the ECG waveform using ASCON."""
    receivedplaintext = ascon_decrypt(key, nonce, associateddata, ciphertext, variant)
    return list(receivedplaintext)

def plot_waveform(waveform, title="ECG Waveform"):
    """Plot the ECG waveform using Matplotlib."""
    plt.plot(waveform)
    plt.title(title)
    plt.xlabel("Time")
    plt.ylabel("Amplitude")
    plt.show()

def live_plot_waveform(waveform, title="ECG Waveform"):
    """Create a live plot that updates in real-time."""
    fig, ax = plt.subplots()
    line, = ax.plot(waveform)
    ax.set_title(title)
    ax.set_xlabel("Time")
    ax.set_ylabel("Amplitude")

    def update(data):
        line.set_ydata(data)
        return line,

    ani = animation.FuncAnimation(fig, update, frames=waveform, interval=50, blit=True)
    plt.show()

def analyze_ecg(waveform):
    """Analyze the ECG waveform using NeuroKit2."""
    signals, info = nk.ecg_process(waveform, sampling_rate=1000)
    nk.ecg_plot(signals, sampling_rate=1000)
    return signals, info

# === Main Function ===

def main():
    # Read ECG data from CSV
    file_path = "/Users/chloelarroze/Desktop/FPGA_TP2/waveform_example_ecg.csv" 
    ecg_data = read_csv(file_path)
    
    # Extract the second waveform (index 1)
    waveform = extract_waveform(ecg_data, 1)
    
    # Define key, nonce, and associated data
    key = bytes.fromhex("8A55114D1CB6A9A2BE263D4D7AECAAFF")
    nonce = bytes.fromhex("4ED0EC0B98C529B7C8CDDF37BCD0284A")
    associateddata = b"A to B"
    
    # Encrypt the waveform
    ciphertext = encrypt_waveform(waveform, key, nonce, associateddata)
    
    # Decrypt the waveform
    decrypted_waveform = decrypt_waveform(ciphertext, key, nonce, associateddata)
    
    # Validate decryption
    if decrypted_waveform == waveform:
        print("Decryption successful!")
    else:
        print("Decryption failed!")
    
    # Plot the original and decrypted waveforms
    #do a subplot for the following two plots
    
    plot_waveform(waveform, "Original ECG Waveform")
    plot_waveform(decrypted_waveform, "Decrypted ECG Waveform")
    
    # Analyze the ECG waveform
    signals, info = analyze_ecg(decrypted_waveform)
    print("ECG Analysis Info:", info)

if __name__ == "__main__":
    main()