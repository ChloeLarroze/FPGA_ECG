import serial
import time

# UART Configuration
PORT = '/dev/tty.usbserial-AV0KRXPV'  # Replace with your UART port (e.g., '/dev/ttyUSB0' on Linux/Mac)
BAUD_RATE = 115200  # Baud rate
PARITY = serial.PARITY_NONE  # Parity: PARITY_NONE, PARITY_EVEN, PARITY_ODD
STOP_BITS = serial.STOPBITS_ONE  # Stop bits: STOPBITS_ONE, STOPBITS_TWO
BYTE_SIZE = serial.EIGHTBITS  # Data bits: EIGHTBITS, SEVENBITS

# Message to send
TEST_MESSAGE = "Greetings from UART!"

# Initialize UART
try:
    # Open the serial port
    uart = serial.Serial(
        port=PORT,
        baudrate=BAUD_RATE,
        parity=PARITY,
        stopbits=STOP_BITS,
        bytesize=BYTE_SIZE,
        timeout=1  # Timeout for read operations
    )
    print(f"UART port {PORT} opened successfully.")

    # Send a test message
    print(f"Sending message: {TEST_MESSAGE}")
    uart.write(TEST_MESSAGE.encode('utf-8'))  # Encode string to bytes and send

    # Wait for a response (optional)
    time.sleep(0.5)  # Give the device time to respond

    # Read the response
    response = uart.read_all()  # Read all available data
    if response:
        print(f"Received response: {response.decode('utf-8')}")
    else:
        print("No response received.")

except serial.SerialException as e:
    print(f"Error opening UART port: {e}")

finally:
    # Close the UART port
    if 'uart' in locals() and uart.is_open:
        uart.close()
        print("UART port closed.")