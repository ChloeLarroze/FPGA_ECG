import serial
import time
import sys
import logging
import os
from datetime import datetime
import binascii

class FPGA:
    """
    Class for UART communication with an FPGA.
    
    This class provides methods to interact with an FPGA via a UART interface,
    including reading and writing to memory, setting memory addresses, and 
    displaying values on LEDs. It also supports ASCON encryption for ECG data.
    """
    
    def __init__(self, port, baud_rate=115200, parity=serial.PARITY_NONE, 
                 stop_bits=serial.STOPBITS_ONE, timeout=1, log_level=logging.INFO,
                 log_file=None):
        """
        Initialize the FPGA UART connection with specified parameters.
        
        Args:
            port (str): Serial port name (e.g., 'COM3', '/dev/ttyUSB0')
            baud_rate (int): Baud rate for UART communication (default: 115200)
            parity (str): Parity bit setting (default: PARITY_NONE)
            stop_bits (float): Number of stop bits (default: STOPBITS_ONE)
            timeout (float): Read timeout in seconds (default: 1)
            log_level (int): Logging level (default: logging.INFO)
            log_file (str): Path to log file (default: None, generates timestamp-based filename)
        """
        self.port = port
        self.baud_rate = baud_rate
        self.parity = parity
        self.stop_bits = stop_bits
        self.timeout = timeout
        self.uart = None
        
        # Setup logging
        self._setup_logging(log_level, log_file)
        
        self.logger.info(f"FPGA initialized with parameters: port={port}, "
                         f"baud_rate={baud_rate}, parity={parity}, "
                         f"stop_bits={stop_bits}, timeout={timeout}")

    # Keep all existing methods...
    
    def _setup_logging(self, log_level, log_file):
        """
        Set up the logging system with file and console handlers.
        
        Args:
            log_level (int): Logging level (e.g., logging.INFO, logging.DEBUG)
            log_file (str): Path to log file or None for auto-generated name
        """
        # Create logger
        self.logger = logging.getLogger(f"FPGA_{self.port}")
        self.logger.setLevel(log_level)
        self.logger.handlers.clear()  # Clear any existing handlers
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # Create file handler
        if log_file is None:
            # Create logs directory if it doesn't exist
            os.makedirs('logs', exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = f"logs/fpga_uart_{timestamp}.log"
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)  # Only INFO and above goes to console
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        self.logger.debug(f"Logging initialized at level {log_level} to file: {log_file}")

    def open_instrument(self):
        """
        Open the UART connection to the FPGA.
        
        Returns:
            bool: True if connection was successful, False otherwise
        """
        try:
            self.uart = serial.Serial(
                port=self.port,
                baudrate=self.baud_rate,
                parity=self.parity,
                stopbits=self.stop_bits,
                timeout=self.timeout
            )
            self.logger.info(f"UART port {self.port} opened successfully")
            return True
        except serial.SerialException as e:
            self.logger.error(f"Error opening UART port: {e}")
            return False

    def close_instrument(self):
        """
        Close the UART connection to the FPGA.
        """
        if self.uart and self.uart.is_open:
            self.uart.close()
            self.logger.info("UART port closed")
        else:
            self.logger.debug("No open UART connection to close")

    def send_command(self, command):
        """
        Send a command to the FPGA and wait for a response.
        
        Args:
            command (str): Command to send
            
        Returns:
            bytes: Raw response from the FPGA
            
        Raises:
            ValueError: If command is not a string
            RuntimeError: If UART connection is not open
        """
        if not isinstance(command, str):
            error_msg = "Command must be a string"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        
        if not self.uart or not self.uart.is_open:
            error_msg = "UART connection is not open"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        # Add line feed to command if not already present
        if not command.endswith('\n'):
            command += '\n'
        
        self.logger.debug(f"Sending command: {command.strip()}")
        
        # Send command
        self.uart.write(command.encode('utf-8'))
        
        # Wait for response
        time.sleep(0.1)
        
        # Read raw response
        raw_response = self.uart.read_all()
        
        # For debug logging, show both raw bytes and decoded string
        if raw_response:
            hex_bytes = ' '.join([f'0x{b:02X}' for b in raw_response])
            try:
                str_repr = raw_response.decode('latin-1')
                self.logger.debug(f"Received raw bytes: {hex_bytes}")
                self.logger.debug(f"Decoded response: {str_repr}")
            except Exception as e:
                self.logger.debug(f"Received raw bytes: {hex_bytes} (decoding failed: {e})")
        else:
            self.logger.debug("Received empty response")
        
        return raw_response

    def send_binary_data(self, prefix_char, data, wait_for_ok=True):
        """
        Send binary data with a prefix character to the FPGA.
        
        Args:
            prefix_char (str): Single character prefix for the data
            data (bytes): Binary data to send
            wait_for_ok (bool): Whether to wait for 'OK' response
            
        Returns:
            bytes: Raw response from the FPGA
            
        Raises:
            ValueError: If prefix_char is not a single character
            RuntimeError: If UART connection is not open
        """
        if not isinstance(prefix_char, str) or len(prefix_char) != 1:
            error_msg = "Prefix must be a single character"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        
        if not self.uart or not self.uart.is_open:
            error_msg = "UART connection is not open"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        # Convert prefix to uppercase and then to hex
        prefix_byte = prefix_char.upper().encode('ascii')[0]
        
        # Create the complete message
        message = bytes([prefix_byte]) + data
        
        self.logger.debug(f"Sending binary data with prefix '{prefix_char}' ({hex(prefix_byte)}), data length: {len(data)} bytes")
        hex_preview = ' '.join([f'{b:02X}' for b in data[:10]])
        self.logger.debug(f"First 10 bytes: {hex_preview}{'...' if len(data) > 10 else ''}")
        
        # Send data
        self.uart.write(message)
        
        # Wait for response
        if wait_for_ok:
            time.sleep(0.5)  # Longer wait for binary data
            raw_response = self.uart.read_all()
            
            # Log the response
            if raw_response:
                hex_bytes = ' '.join([f'{b:02X}' for b in raw_response[:20]])
                self.logger.debug(f"Received response (first 20 bytes): {hex_bytes}{'...' if len(raw_response) > 20 else ''}")
                
                # Check for OK
                if b"OK" in raw_response:
                    self.logger.debug("Response contains 'OK'")
                else:
                    self.logger.warning("Response does not contain 'OK'")
            else:
                self.logger.debug("Received empty response")
            
            return raw_response
        
        return None

    # --- ASCON Encryption Methods ---
    
    def send_ascon_key(self, key):
        """
        Send the ASCON encryption key to the FPGA.
        
        Args:
            key (bytes or str): 16-byte key (128-bit)
            
        Returns:
            bool: True if operation was successful
            
        Raises:
            ValueError: If key format or length is invalid
        """
        # Convert hex string to bytes if needed
        if isinstance(key, str):
            try:
                # Remove any spaces or 0x prefixes
                clean_key = key.replace(" ", "").replace("0x", "").upper()
                key = bytes.fromhex(clean_key)
            except ValueError as e:
                error_msg = f"Invalid key format: {e}"
                self.logger.error(error_msg)
                raise ValueError(error_msg)
        
        # Validate key length
        if len(key) != 16:
            error_msg = f"Key must be 16 bytes (128 bits), got {len(key)} bytes"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        
        self.logger.info("Sending ASCON encryption key")
        response = self.send_binary_data('L', key)
        
        # Check response
        if response and b"OK" in response:
            self.logger.info("Key successfully sent")
            return True
        else:
            error_msg = "Failed to send key"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)

    def send_ascon_nonce(self, nonce):
        """
        Send the ASCON nonce to the FPGA.
        
        Args:
            nonce (bytes or str): 16-byte nonce
            
        Returns:
            bool: True if operation was successful
            
        Raises:
            ValueError: If nonce format or length is invalid
        """
        # Convert hex string to bytes if needed
        if isinstance(nonce, str):
            try:
                # Remove any spaces or 0x prefixes
                clean_nonce = nonce.replace(" ", "").replace("0x", "").upper()
                nonce = bytes.fromhex(clean_nonce)
            except ValueError as e:
                error_msg = f"Invalid nonce format: {e}"
                self.logger.error(error_msg)
                raise ValueError(error_msg)
        
        # Validate nonce length
        if len(nonce) != 16:
            error_msg = f"Nonce must be 16 bytes, got {len(nonce)} bytes"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        
        self.logger.info("Sending ASCON nonce")
        response = self.send_binary_data('O', nonce)
        
        # Check response
        if response and b"OK" in response:
            self.logger.info("Nonce successfully sent")
            return True
        else:
            error_msg = "Failed to send nonce"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)

    def send_ascon_associated_data(self, data):
        """
        Send the ASCON associated data to the FPGA with proper padding.
        
        Args:
            data (bytes or str): Associated data (8 bytes before padding)
            
        Returns:
            bool: True if operation was successful
            
        Raises:
            ValueError: If data format is invalid
        """
        # Convert hex string to bytes if needed
        if isinstance(data, str):
            try:
                # Remove any spaces or 0x prefixes
                clean_data = data.replace(" ", "").replace("0x", "").upper()
                data = bytes.fromhex(clean_data)
            except ValueError as e:
                error_msg = f"Invalid associated data format: {e}"
                self.logger.error(error_msg)
                raise ValueError(error_msg)
        
        # Validate data length
        if len(data) != 6:
            error_msg = f"Associated data must be 8 bytes before padding, got {len(data)} bytes"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Add padding: ending in 80 00
        padded_data = data + bytes([0x80, 0x00])
        
        self.logger.info("Sending ASCON associated data with padding")
        self.logger.debug(f"Original data ({len(data)} bytes): {data.hex().upper()}")
        self.logger.debug(f"Padded data ({len(padded_data)} bytes): {padded_data.hex().upper()}")
        
        response = self.send_binary_data('B', padded_data)
        
        # Check response
        if response and b"OK" in response:
            self.logger.info("Associated data successfully sent")
            return True
        else:
            error_msg = "Failed to send associated data"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)

    def send_ascon_ecg_data(self, ecg_data):
        """
        Send the ECG waveform data to be encrypted with proper padding.
        
        Args:
            ecg_data (bytes or str): ECG waveform data (181 bytes before padding)
            
        Returns:
            bool: True if operation was successful
            
        Raises:
            ValueError: If data format is invalid
        """
        # Convert hex string to bytes if needed
        if isinstance(ecg_data, str):
            try:
                # Remove any spaces or 0x prefixes
                clean_data = ecg_data.replace(" ", "").replace("0x", "").upper()
                ecg_data = bytes.fromhex(clean_data)
            except ValueError as e:
                error_msg = f"Invalid ECG data format: {e}"
                self.logger.error(error_msg)
                raise ValueError(error_msg)
        
        # Validate data length
        if len(ecg_data) != 181:
            error_msg = f"ECG data must be 181 bytes before padding, got {len(ecg_data)} bytes"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Add padding: ending in 80 00 00
        padded_data = ecg_data + bytes([0x80, 0x00, 0x00])
        
        self.logger.info("Sending ECG waveform data with padding")
        self.logger.debug(f"Original data ({len(ecg_data)} bytes): {ecg_data[:10].hex().upper()}...")
        self.logger.debug(f"Padded data ({len(padded_data)} bytes): ...{padded_data[-5:].hex().upper()}")
        
        response = self.send_binary_data('X', padded_data)
        
        # Check response
        if response and b"OK" in response:
            self.logger.info("ECG data successfully sent")
            return True
        else:
            error_msg = "Failed to send ECG data"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)

    def start_ascon_encryption(self):
        """
        Start the ASCON encryption process on the FPGA.
        
        Returns:
            bool: True if encryption was successfully initiated
            
        Raises:
            RuntimeError: If FPGA reports an error
        """
        self.logger.info("Starting ASCON encryption")
        response = self.send_binary_data('H', b'')  # 'H' for "go" command with no data
        
        # Check response
        if response and b"OK" in response:
            self.logger.info("Encryption successfully initiated")
            return True
        else:
            error_msg = "Failed to initiate encryption"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)

    def get_ascon_tag(self):
        """
        Retrieve the authentication tag produced by ASCON encryption.
        
        Returns:
            bytes: 16-byte (128-bit) authentication tag
            
        Raises:
            RuntimeError: If retrieval fails
        """
        self.logger.info("Retrieving ASCON authentication tag")
        
        # Send request for tag
        self.uart.write(b'U')
        time.sleep(0.5)  # Give FPGA time to respond
        
        # Read response
        raw_response = self.uart.read_all()
        
        if not raw_response or len(raw_response) < 16:
            error_msg = f"Invalid tag response, got {len(raw_response) if raw_response else 0} bytes"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        # Extract the 16-byte tag from the beginning of the response
        tag = raw_response[:16]
        
        # Check for OK in remaining response
        remaining = raw_response[16:]
        if b"OK" not in remaining:
            self.logger.warning("Tag response doesn't contain 'OK' confirmation")
        
        self.logger.info(f"Retrieved tag: {tag.hex().upper()}")
        return tag

    def get_ascon_ciphertext(self):
        """
        Retrieve the ciphertext produced by ASCON encryption.
        
        Returns:
            bytes: Ciphertext (181 bytes + 3 bytes padding)
            
        Raises:
            RuntimeError: If retrieval fails
        """
        self.logger.info("Retrieving ASCON ciphertext")
        
        # Send request for ciphertext
        self.uart.write(b'D')
        time.sleep(1.0)  # Longer wait for larger data
        
        # Read response
        raw_response = self.uart.read_all()
        
        expected_length = 181 + 3  # 181 bytes data + 3 bytes padding
        if not raw_response or len(raw_response) < expected_length:
            error_msg = f"Invalid ciphertext response, expected at least {expected_length} bytes, got {len(raw_response) if raw_response else 0}"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        # Extract the ciphertext from the beginning of the response
        ciphertext = raw_response[:expected_length]
        
        # Check for OK in remaining response
        remaining = raw_response[expected_length:]
        if b"OK" not in remaining:
            self.logger.warning("Ciphertext response doesn't contain 'OK' confirmation")
        
        self.logger.info(f"Retrieved ciphertext ({len(ciphertext)} bytes): {ciphertext.hex().upper()}")
        return ciphertext

    def encrypt_ecg_data(self, key, nonce, associated_data, ecg_data):
        """
        Complete ASCON encryption workflow for ECG data.
        
        Args:
            key (bytes or str): 16-byte encryption key
            nonce (bytes or str): 16-byte nonce
            associated_data (bytes or str): 8-byte associated data
            ecg_data (bytes or str): 181-byte ECG waveform data
            
        Returns:
            tuple: (tag, ciphertext) where tag is 16 bytes and ciphertext is 184 bytes
        """
        self.logger.info("Beginning complete ASCON encryption workflow")
        
        # Send all required parameters
        self.send_ascon_key(key)
        self.send_ascon_nonce(nonce)
        self.send_ascon_associated_data(associated_data)
        self.send_ascon_ecg_data(ecg_data)
        
        # Start encryption
        self.start_ascon_encryption()
        
        # Retrieve results
        tag = self.get_ascon_tag()
        ciphertext = self.get_ascon_ciphertext()
        
        self.logger.info("ASCON encryption workflow completed successfully")
        return tag, ciphertext


# Add ASCON commands to interactive_mode function
def interactive_mode(fpga):
    """
    Run in interactive mode, accepting commands from terminal.
    
    Args:
        fpga (FPGA): FPGA object to use for interactive commands
    """
    print_help()
    
    while True:
        try:
            # Get command from user
            cmd = input("\nEnter command (type 'help' for available commands): ").strip()
            
            # Process command
            if cmd.lower() == 'exit':
                print("Exiting interactive mode...")
                break
                
            elif cmd.lower() == 'help':
                print_help()
            
            # New ASCON commands
                
            elif cmd.lower().startswith('key '):
                try:
                    key_hex = cmd.split(' ', 1)[1].strip()
                    fpga.send_ascon_key(key_hex)
                    print("ASCON key successfully sent")
                except (IndexError, ValueError, RuntimeError) as e:
                    print(f"Error: {e}")
                    print("Usage: key <16-byte hex value>")
                    
            elif cmd.lower().startswith('nonce '):
                try:
                    nonce_hex = cmd.split(' ', 1)[1].strip()
                    fpga.send_ascon_nonce(nonce_hex)
                    print("ASCON nonce successfully sent")
                except (IndexError, ValueError, RuntimeError) as e:
                    print(f"Error: {e}")
                    print("Usage: nonce <16-byte hex value>")
                    
            elif cmd.lower().startswith('assoc '):
                try:
                    ad_hex = cmd.split(' ', 1)[1].strip()
                    fpga.send_ascon_associated_data(ad_hex)
                    print("ASCON associated data successfully sent")
                except (IndexError, ValueError, RuntimeError) as e:
                    print(f"Error: {e}")
                    print("Usage: assoc <8-byte hex value> (padding will be added automatically)")
                    
            elif cmd.lower().startswith('ecg '):
                try:
                    ecg_hex = cmd.split(' ', 1)[1].strip()
                    fpga.send_ascon_ecg_data(ecg_hex)
                    print("ECG data successfully sent")
                except (IndexError, ValueError, RuntimeError) as e:
                    print(f"Error: {e}")
                    print("Usage: ecg <181-byte hex value> (padding will be added automatically)")
                    
            elif cmd.lower() == 'encrypt':
                try:
                    fpga.start_ascon_encryption()
                    print("ASCON encryption successfully initiated")
                except RuntimeError as e:
                    print(f"Error: {e}")
                    
            elif cmd.lower() == 'tag':
                try:
                    tag = fpga.get_ascon_tag()
                    print(f"Retrieved authentication tag: {tag.hex().upper()}")
                except RuntimeError as e:
                    print(f"Error: {e}")
                    
            elif cmd.lower() == 'ciphertext':
                try:
                    ciphertext = fpga.get_ascon_ciphertext()
                    print(f"Retrieved ciphertext (first 32 bytes): {ciphertext[:32].hex().upper()}...")
                    print(f"Total ciphertext length: {len(ciphertext)} bytes")
                except RuntimeError as e:
                    print(f"Error: {e}")
                    
            elif cmd.lower() == 'run-ascon':
                try:
                    # Get all required parameters
                    print("\n=== ASCON Encryption Setup ===")
                    key_hex = input("Enter 16-byte key (hex): ").strip()
                    nonce_hex = input("Enter 16-byte nonce (hex): ").strip()
                    ad_hex = input("Enter 8-byte associated data (hex): ").strip()
                    
                    # For ECG data, allow file input or manual entry
                    ecg_input_type = input("Enter ECG data from [f]ile or [m]anual input? (f/m): ").strip().lower()
                    if ecg_input_type == 'f':
                        ecg_file = input("Enter path to ECG data file: ").strip()
                        try:
                            with open(ecg_file, 'rb') as f:
                                ecg_data = f.read()
                                if len(ecg_data) != 181:
                                    print(f"Warning: ECG data file contains {len(ecg_data)} bytes, expected 181 bytes")
                                    if input("Continue anyway? (y/n): ").strip().lower() != 'y':
                                        continue
                        except Exception as e:
                            print(f"Error reading file: {e}")
                            continue
                    else:
                        ecg_hex = input("Enter 181-byte ECG data (hex): ").strip()
                        try:
                            ecg_data = bytes.fromhex(ecg_hex.replace(" ", "").replace("0x", ""))
                        except ValueError as e:
                            print(f"Error: Invalid hex format - {e}")
                            continue
                    
                    # Run encryption workflow
                    print("\nRunning ASCON encryption workflow...")
                    tag, ciphertext = fpga.encrypt_ecg_data(key_hex, nonce_hex, ad_hex, ecg_data)
                    
                    # Display results
                    print("\n=== ASCON Encryption Results ===")
                    print(f"Authentication Tag (16 bytes): {tag.hex().upper()}")
                    print(f"Ciphertext (184 bytes, includes padding):")
                    
                    # Display ciphertext in a readable format, 16 bytes per line
                    ciphertext_hex = ciphertext.hex().upper()
                    for i in range(0, len(ciphertext_hex), 32):
                        print(ciphertext_hex[i:i+32])
                    
                    # Ask if user wants to save results to a file
                    if input("\nSave results to file? (y/n): ").strip().lower() == 'y':
                        result_file = input("Enter output file name: ").strip()
                        with open(result_file, 'w') as f:
                            f.write(f"ASCON Encryption Results\n")
                            f.write(f"----------------------\n")
                            f.write(f"Authentication Tag: {tag.hex().upper()}\n")
                            f.write(f"Ciphertext:\n{ciphertext.hex().upper()}\n")
                        print(f"Results saved to {result_file}")
                    
                except Exception as e:
                    print(f"Error during ASCON encryption: {e}")
            
            elif cmd.lower() == 'debug on':
                # Set logger level to DEBUG
                for handler in fpga.logger.handlers:
                    handler.setLevel(logging.DEBUG)
                fpga.logger.setLevel(logging.DEBUG)
                print("Debug logging enabled")
                
            elif cmd.lower() == 'debug off':
                # Reset console handler to INFO
                for handler in fpga.logger.handlers:
                    if isinstance(handler, logging.StreamHandler) and not isinstance(handler, logging.FileHandler):
                        handler.setLevel(logging.INFO)
                print("Debug logging disabled (file logging continues at original level)")
                
            else:
                print(f"Unknown command: {cmd}")
                print("Type 'help' for available commands, or 'ascon-help' for ASCON-specific commands")
                
        except KeyboardInterrupt:
            print("\nInterrupted by user. Exiting interactive mode...")
            break
        except Exception as e:
            print(f"Error: {e}")


def print_help():
    """
    Print help information for ASCON encryption commands.
    """
    print("\n===== ASCON Encryption Commands =====")
    print("  key <hex>      - Send 16-byte encryption key")
    print("  nonce <hex>    - Send 16-byte nonce")
    print("  assoc <hex>    - Send 8-byte associated data (padding will be added)")
    print("  ecg <hex>      - Send 181-byte ECG data (padding will be added)")
    print("  encrypt        - Start encryption process")
    print("  tag            - Retrieve 16-byte authentication tag")
    print("  ciphertext     - Retrieve encrypted data (181 bytes + padding)")
    print("  run-ascon      - Run complete encryption workflow interactively")
    print("======================================\n")

if __name__ == '__main__':
    import argparse
    
    # Parse command line arguments
    parser =argparse.ArgumentParser(description='FPGA UART Communication Interface')
    parser.add_argument('--port', '-p', type=str, required=True, 
                        help='Serial port (e.g., COM3, /dev/ttyUSB0)')
    parser.add_argument('--baud', '-b', type=int, default=115200, 
                        help='Baud rate (default: 115200)')
    parser.add_argument('--parity', type=str, choices=['none', 'odd', 'even'], default='none',
                        help='Parity setting (default: none)')
    parser.add_argument('--stop', type=int, choices=[1, 2], default=1,
                        help='Stop bits (default: 1)')
    parser.add_argument('--timeout', '-t', type=float, default=1.0,
                        help='Read timeout in seconds (default: 1.0)')
    parser.add_argument('--debug', '-d', action='store_true',
                        help='Enable debug logging')
    parser.add_argument('--logfile', '-l', type=str, default=None,
                        help='Log file path (default: auto-generated)')
    
    args = parser.parse_args()
    
    # Map parity string to serial constants
    parity_map = {
        'none': serial.PARITY_NONE,
        'odd': serial.PARITY_ODD,
        'even': serial.PARITY_EVEN
    }
    
    # Map stop bits to serial constants
    stop_map = {
        1: serial.STOPBITS_ONE,
        2: serial.STOPBITS_TWO
    }
    
    # Set logging level based on debug flag
    log_level = logging.DEBUG if args.debug else logging.INFO
    
    try:
        # Initialize FPGA with command line parameters
        fpga = FPGA(
            port=args.port,
            baud_rate=args.baud,
            parity=parity_map[args.parity],
            stop_bits=stop_map[args.stop],
            timeout=args.timeout,
            log_level=log_level,
            log_file=args.logfile
        )
        
        # Open the UART connection
        if fpga.open_instrument():
            print(f"Connected to FPGA on port {args.port}")
            # Start interactive mode
            interactive_mode(fpga)
        else:
            print(f"Failed to connect to FPGA on port {args.port}")
            
    except Exception as e:
        print(f"An error occurred: {e}")
        
    finally:
        # Close the UART connection if it was opened
        if 'fpga' in locals():
            fpga.close_instrument()