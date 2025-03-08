import serial
import time

class FPGA:
    def __init__(self, port, baud_rate=115200, timeout=1, parity=serial.PARITY_NONE, stop_bits=serial.STOPBITS_ONE, byte_size=serial.EIGHTBITS):
        """
        Initialize the FPGA UART connection.
        """
        self.port = port
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.parity = parity
        self.stop_bits = stop_bits
        self.byte_size = byte_size
        self.uart = None

    def open_instrument(self):
        """
        Open the UART connection to the FPGA.
        """
        try:
            self.uart = serial.Serial(
                port=self.port,
                baudrate=self.baud_rate,
                parity=self.parity,
                stopbits=self.stop_bits,
                bytesize=self.byte_size,
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

    def set_memory_addr(self, addr):
        """
        Set the memory address on the FPGA.
        :param addr: Memory address (integer).
        """
        if not isinstance(addr, int) or addr < 0:
            raise ValueError("Memory address must be a non-negative integer.")
        # Send command to set memory address
        command = f"SET_ADDR {addr}\n"
        self.uart.write(command.encode('utf-8'))
        print(f"Memory address set to: {addr}")

    def write_val_mem(self, value):
        """
        Write a value to the current memory address on the FPGA.
        :param value: Value to write (integer).
        """
        if not isinstance(value, int) or value < 0:
            raise ValueError("Value must be a non-negative integer.")
        # Send command to write value to memory
        command = f"WRITE_MEM {value}\n"
        self.uart.write(command.encode('utf-8'))
        print(f"Value {value} written to memory.")

    def read_mem_val(self, addr):
        """
        Read a value from a specific memory address on the FPGA.
        :param addr: Memory address (integer).
        :return: Value read from memory.
        """
        if not isinstance(addr, int) or addr < 0:
            raise ValueError("Memory address must be a non-negative integer.")
        # Send command to read value from memory
        command = f"READ_MEM {addr}\n"
        self.uart.write(command.encode('utf-8'))
        # Wait for response
        time.sleep(0.1)
        response = self.uart.read_all().decode('utf-8').strip()
        print(f"Value read from memory address {addr}: {response}")
        return response

    def display_mem_vals_leds(self, addr):
        """
        Display the value at a specific memory address on the FPGA's LEDs.
        :param addr: Memory address (integer).
        """
        if not isinstance(addr, int) or addr < 0:
            raise ValueError("Memory address must be a non-negative integer.")
        # Send command to display memory value on LEDs
        command = f"DISPLAY_LED {addr}\n"
        self.uart.write(command.encode('utf-8'))
        print(f"Displaying value at memory address {addr} on LEDs.")


if __name__ == '__main__':
    # Initialize FPGA
    fpga = FPGA(port='/dev/tty.usbserial-AV0KRXPV', baud_rate=115200, timeout=1)  # Replace with your UART port

    try:
        # Open the UART connection
        fpga.open_instrument()

        # Set memory address
        fpga.set_memory_addr(0x10)

        # Write value to memory
        fpga.write_val_mem(42)

        # Display memory value on LEDs
        fpga.display_mem_vals_leds(0x10)

        # Read value from memory
        mem_val = fpga.read_mem_val(0x10)
        print(f"Read value from memory: {mem_val}")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Close the UART connection
        fpga.close_instrument()