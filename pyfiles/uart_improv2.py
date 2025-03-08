import serial
import time

class FPGA:
    def __init__(self, port, baud_rate=115200, timeout=1):
        """
        Initialize the FPGA UART connection.
        """
        self.port = port
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.uart = None

    def open_instrument(self):
        """
        Open the UART connection to the FPGA.
        """
        try:
            self.uart = serial.Serial(
                port=self.port,
                baudrate=self.baud_rate,
                timeout=self.timeout
            )
            print(f"UART port {self.port} opened successfully.")
        except serial.SerialException as e:
            print(f"Error opening UART port: {e}")

    def close_instrument(self):
        """
        Close the UART connection to the FPGA.
        """
        if self.uart and self.uart.is_open:
            self.uart.close()
            print("UART port closed.")

    #methode additionnelle, elle sert à envoyer une commande à la FPGA et attendre une réponse
    def send_command(self, command):
        """
        Send a command to the FPGA and wait for a response.
        :param command: Command to send (string).
        :return: Response from the FPGA (string).
        """
        if not isinstance(command, str):
            raise ValueError("Command must be a string.")
        
        # ajout d'un retour à la ligne à la fin de la commande
        command += '\n'
        self.uart.write(command.encode('utf-8'))
        
        # Wait 
        time.sleep(0.1)
        #response = self.uart.read_all().decode('utf-8', errors='ignore').strip()

        #response = self.uart.read_all().decode('utf-8').strip()
        response = self.uart.read_all().decode('latin-1').strip()

        return response

    def set_memory_addr(self, addr):
        """
        Set the memory address on the FPGA.
        :param addr: Memory address (hex string, e.g., '0x00').
        :return: Response from the FPGA.
        """
        if not isinstance(addr, str) or not addr.startswith('0x'):
            raise ValueError("Address must be a hex string (e.g., '0x00').")
        
        command = f"A{addr[2:]}"  # Remove '0x' prefix
        response = self.send_command(command)
        if response != "OK":
            raise ValueError(f"Unexpected response: {response}")
        print(f"Memory address set to: {addr}")

    def write_val_mem(self, value):
        """
        Write a value to the assigned memory address.
        :param value: Value to write (hex string, e.g., '0xF5').
        :return: Response from the FPGA.
        """
        if not isinstance(value, str) or not value.startswith('0x'):
            raise ValueError("Value must be a hex string (e.g., '0xF5').")
        
        command = f"W{value[2:]}"  # Remove '0x' prefix
        response = self.send_command(command)
        if response != "OK":
            raise ValueError(f"Unexpected response: {response}")
        print(f"Value {value} written to memory.")

    def display_mem_vals_leds(self):
        """
        Display the stored value on the FPGA LEDs.
        :return: Response from the FPGA.
        """
        command = "G"
        response = self.send_command(command)
        if response != "OK":
            raise ValueError(f"Unexpected response: {response}")
        print("Value displayed on LEDs.")

    def read_mem_val(self):
        """
        Read the stored value from the assigned memory address.
        :return: Value read from memory (hex string).
        """
        command = "R"
        response = self.send_command(command)
        if not response.startswith("0x") or not response.endswith(" OK"):
            raise ValueError(f"Unexpected response: {response}")
        
        # Extract the value from the response
        value = response.split()[0]
        print(f"Value read from memory: {value}")
        return value

if __name__ == '__main__':
    # Initialize FPGA
    fpga = FPGA(port='/dev/tty.usbserial-AV0KRXPV')  # Replace with your UART port

    try:
        # Open the UART connection
        fpga.open_instrument()

        # Set memory address
        fpga.set_memory_addr('0x00')

        # Write value to memory
        fpga.write_val_mem('0xF5') #F5

        # Display memory value on LEDs
        fpga.display_mem_vals_leds()

        # Read value from memory
        mem_val = fpga.read_mem_val()
        print(f"Read value from memory: {mem_val}")

        # Test edge cases (invalid commands)
        try:
            fpga.set_memory_addr('invalid')  # Invalid address format
        except ValueError as e:
            print(f"Edge case test (invalid address): {e}")

        try:
            fpga.write_val_mem('invalid')  # Invalid value format
        except ValueError as e:
            print(f"Edge case test (invalid value): {e}")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Close the UART connection
        fpga.close_instrument()