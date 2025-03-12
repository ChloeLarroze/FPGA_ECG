import serial
import time
import sys
import logging
import os
from datetime import datetime

class FPGA:
    """
    Class for UART communication with an FPGA.
    
    Provides methods to interact with the PYNQ-Z2 using the CLI to send various commands.
    """
    
    def __init__(self, port, baud_rate=115200, parity=serial.PARITY_NONE, 
                 stop_bits=serial.STOPBITS_ONE, timeout=1, log_level=logging.INFO,
                 log_file=None):
        """
        Initializes the FPGA UART connection with specified parameters.
        
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

    def _setup_logging(self, log_level, log_file):
        """
        Sets up the logging system with file and console handlers.
        
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
        Opens the UART connection to the FPGA.
        
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
        Closes the UART connection to the FPGA.
        """
        if self.uart and self.uart.is_open:
            self.uart.close()
            self.logger.info("UART port closed")
        else:
            self.logger.debug("No open UART connection to close")

    def send_command(self, command):
        """
        Sends a command to the FPGA and waits for a response.
        
        Args:
            command (str): Command to send
            
        Returns:
            str: Response from the FPGA
            
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
        
        # Read response
        response = self.uart.read_all().decode('latin-1').strip()
        self.logger.debug(f"Received response: {response}")
        
        return response

    def set_memory_addr(self, addr):
        """
        Sets the memory address on the FPGA.
        
        Args:
            addr (str or int): Memory address as hex string (e.g., '0x00') or integer
            
        Returns:
            bool: True if operation was successful
            
        Raises:
            ValueError: If address format is invalid or response is unexpected
        """
        # Convert integer to hex string if needed
        if isinstance(addr, int):
            addr = f"0x{addr:02X}"
        
        # Validate address format
        if not isinstance(addr, str) or not addr.startswith('0x'):
            error_msg = f"Address must be a hex string (e.g., '0x00'), got {addr}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Remove '0x' prefix and format command
        addr_value = addr[2:].upper()
        command = f"A{addr_value}"
        
        self.logger.info(f"Setting memory address to: {addr}")
        response = self.send_command(command)
        
        if response != "OK":
            error_msg = f"Unexpected response when setting address: {response}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        
        self.logger.info(f"Memory address successfully set to: {addr}")
        return True

    def write_val_mem(self, value):
        """
        Writes a value to the assigned memory address.
        
        Args:
            value (str or int): Value to write as hex string (e.g., '0xF5') or integer
            
        Returns:
            bool: True if operation was successful
            
        Raises:
            ValueError: If value format is invalid or response is unexpected
        """
        # Convert integer to hex string if needed
        if isinstance(value, int):
            value = f"0x{value:02X}"
        
        # Validate value format
        if not isinstance(value, str) or not value.startswith('0x'):
            error_msg = f"Value must be a hex string (e.g., '0xF5'), got {value}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Remove '0x' prefix and format command
        val = value[2:].upper()
        command = f"W{val}"
        
        self.logger.info(f"Writing value {value} to memory")
        response = self.send_command(command)
        
        if response != "OK":
            error_msg = f"Unexpected response when writing value: {response}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        
        self.logger.info(f"Value {value} successfully written to memory")
        return True

    def display_mem_vals_leds(self):
        """
        Displays the stored value on the FPGA LEDs.
        
        Returns:
            bool: True if operation was successful
            
        Raises:
            ValueError: If response is unexpected
        """
        command = "G"
        
        self.logger.info("Displaying memory value on LEDs")
        response = self.send_command(command)
        
        if response != "OK":
            error_msg = f"Unexpected response when displaying on LEDs: {response}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        
        self.logger.info("Memory value successfully displayed on LEDs")
        return True

    def read_mem_val(self):
        """
        Reads the stored value from the assigned memory address.
        
        Returns:
            str: Value read from memory (hex string)
            
        Raises:
            ValueError: If response format is unexpected
        """
        command = "R"
        
        self.logger.info("Reading value from memory")
        response = self.send_command(command)
        
        # Parse and validate response
        if not response.startswith("0x") or not response.endswith(" OK"):
            error_msg = f"Unexpected response format when reading memory: {response}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Extract the value from the response
        value = response.split()[0]
        self.logger.info(f"Value {value} successfully read from memory")
        return value


def print_help():
    """
    Print help information for available commands.
    """
    print("\n===== FPGA UART Interface Help =====")
    print("Available commands:")
    print("  addr <hex>     - Sets memory address (e.g., addr 0x00)")
    print("  write <hex>    - Writes value to memory (e.g., write 0xF5)")
    print("  read           - Reads value from current memory address")
    print("  display        - Displays memory value on FPGA LEDs")
    print("  test           - Runs a series of test read/write cycles")
    print("  debug <on/off> - Turns debug logging on or off")
    print("  help           - Shows this help message")
    print("  exit           - Exits the program")
    print("====================================\n")


def run_test_cycles(fpga, cycles=5):
    """
    Run automated test cycles of reading and writing to FPGA memory.
    
    Args:
        fpga (FPGA): FPGA object to use for testing
        cycles (int): Number of test cycles to run
    """
    print(f"\nRunning {cycles} test cycles...")
    
    try:
        for i in range(cycles):
            # Set address to cycle number
            addr = i % 256
            addr_hex = f"0x{addr:02X}"
            
            # Set value based on cycle (just a simple pattern)
            value = (i * 16) % 256
            value_hex = f"0x{value:02X}"
            
            print(f"\nCycle {i+1}/{cycles}:")
            print(f"  Setting address to {addr_hex}")
            fpga.set_memory_addr(addr_hex)
            
            print(f"  Writing value {value_hex}")
            fpga.write_val_mem(value_hex)
            
            print("  Displaying value on LEDs")
            fpga.display_mem_vals_leds()
            
            print("  Reading value back")
            read_value = fpga.read_mem_val()
            
            if read_value.lower() == value_hex.lower():
                print(f"  ✓ Verification successful: wrote {value_hex}, read {read_value}")
            else:
                print(f"  ✗ Verification failed: wrote {value_hex}, read {read_value}")
                
            # Small delay between cycles
            time.sleep(0.5)
            
        print("\nTest cycles completed.")
        
    except Exception as e:
        print(f"\nTest cycles interrupted by error: {e}")


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
                
            elif cmd.lower().startswith('addr '):
                try:
                    addr = cmd.split(' ')[1]
                    fpga.set_memory_addr(addr)
                except (IndexError, ValueError) as e:
                    print(f"Error: {e}")
                    print("Usage: addr 0xXX (e.g., addr 0x00)")
                    
            elif cmd.lower().startswith('write '):
                try:
                    value = cmd.split(' ')[1]
                    fpga.write_val_mem(value)
                except (IndexError, ValueError) as e:
                    print(f"Error: {e}")
                    print("Usage: write 0xXX (e.g., write 0xF5)")
                    
            elif cmd.lower() == 'read':
                try:
                    value = fpga.read_mem_val()
                    print(f"Read value from memory: {value}")
                except ValueError as e:
                    print(f"Error: {e}")
                    
            elif cmd.lower() == 'display':
                try:
                    fpga.display_mem_vals_leds()
                except ValueError as e:
                    print(f"Error: {e}")
                    
            elif cmd.lower() == 'test':
                try:
                    cycles = input("Enter number of test cycles (default: 5): ").strip()
                    cycles = int(cycles) if cycles else 5
                    run_test_cycles(fpga, cycles)
                except ValueError as e:
                    print(f"Error: {e}")
                
            elif cmd.lower().startswith('debug '):
                mode = cmd.split(' ')[1].lower()
                if mode == 'on':
                    # Set logger level to DEBUG
                    for handler in fpga.logger.handlers:
                        handler.setLevel(logging.DEBUG)
                    fpga.logger.setLevel(logging.DEBUG)
                    print("Debug logging enabled")
                elif mode == 'off':
                    # Reset console handler to INFO
                    for handler in fpga.logger.handlers:
                        if isinstance(handler, logging.StreamHandler) and not isinstance(handler, logging.FileHandler):
                            handler.setLevel(logging.INFO)
                    print("Debug logging disabled (file logging continues at original level)")
                else:
                    print("Usage: debug on|off")
                    
            else:
                print(f"Unknown command: {cmd}")
                print("Type 'help' for available commands")
                
        except KeyboardInterrupt:
            print("\nInterrupted by user. Exiting interactive mode...")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == '__main__':
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='FPGA UART Communication Interface')
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