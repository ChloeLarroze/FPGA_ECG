# FPGA UART Communication Interface Documentation

## Overview

This Python script provides a robust interface for communicating with an FPGA via UART. It includes comprehensive input validation, error handling, and a configurable logging system to track all interactions.

## Features

- UART communication with configurable parameters (baud rate, parity, stop bits)
- Memory address setting and value reading/writing
- LED display control
- Interactive command-line interface
- Automated test cycles for verification
- Comprehensive logging system with multiple verbosity levels
- Input validation and error handling

## Requirements

- Python 3.6 or higher
- PySerial library

```bash
pip install pyserial
```

## UART Protocol

The FPGA responds to the following commands over UART:

| Command | Description | Example Input | Expected Response |
|---------|-------------|---------------|-------------------|
| Set Memory Address | Assigns a memory address for subsequent operations | 'A00' (Set address to '0x00') | 'OK \n' |
| Write Value to Memory | Writes a value to the assigned memory address | 'WF5' (Write '0xF5') | 'OK \n' |
| Display Memory Value on LEDs | Shows the stored value on the FPGA LEDs | 'G' | 'OK \n' |
| Read Memory Value via UART | Reads the stored value back through UART | 'R' | '0xF5 OK \n' |

## Usage

### Command Line Arguments

```bash
python fpga_uart.py --port COM3 --baud 115200 --parity none --stop 1 --timeout 1.0 --debug
```

| Argument | Description | Default |
|----------|-------------|---------|
| --port, -p | Serial port (e.g., COM3, /dev/ttyUSB0) | (Required) |
| --baud, -b | Baud rate | 115200 |
| --parity | Parity setting (none, odd, even) | none |
| --stop | Stop bits (1 or 2) | 1 |
| --timeout, -t | Read timeout in seconds | 1.0 |
| --debug, -d | Enable debug logging | (Off by default) |
| --logfile, -l | Log file path | (Auto-generated) |

### Interactive Commands

Once the script is running, you can use the following commands:

- `addr 0xXX`: Set memory address (e.g., addr 0x00)
- `write 0xXX`: Write value to memory (e.g., write 0xF5)
- `read`: Read value from current memory address
- `display`: Display memory value on FPGA LEDs
- `test`: Run a series of test read/write cycles
- `debug on/off`: Toggle debug logging
- `help`: Show help message
- `exit`: Exit the program

## Logging System

The script implements a comprehensive logging system that:

1. Logs to both console and file
2. Supports different verbosity levels (INFO and DEBUG)
3. Automatically creates timestamped log files
4. Tracks all FPGA interactions

### Log Levels

- **INFO**: Important operations like port opening/closing, memory operations
- **DEBUG**: Detailed information including raw commands and responses

### Example Log Entries

```
2025-03-12 10:15:23,045 - FPGA_COM3 - INFO - FPGA initialized with parameters: port=COM3, baud_rate=115200, parity=N, stop_bits=1, timeout=1
2025-03-12 10:15:23,046 - FPGA_COM3 - INFO - UART port COM3 opened successfully
2025-03-12 10:15:23,046 - FPGA_COM3 - INFO - Setting memory address to: 0x00
2025-03-12 10:15:23,047 - FPGA_COM3 - DEBUG - Sending command: A00
2025-03-12 10:15:23,148 - FPGA_COM3 - DEBUG - Received response: OK
2025-03-12 10:15:23,148 - FPGA_COM3 - INFO - Memory address successfully set to: 0x00
```

## Example Implementation Flow

```python
# Initialize FPGA with proper parameters
fpga = FPGA(port="COM3", baud_rate=115200, parity=serial.PARITY_NONE, 
           stop_bits=serial.STOPBITS_ONE, timeout=1.0, log_level=logging.INFO)

# Open communication with FPGA
fpga.open_instrument()

# Set memory address
fpga.set_memory_addr(0x00)

# Write value to memory
fpga.write_val_mem(0xF5)

# Display memory values on LEDs
fpga.display_mem_vals_leds()

# Read memory value
mem_val = fpga.read_mem_val()
print(f"Memory Value: {mem_val}")

# Close communication
fpga.close_instrument()
```

## Error Handling

The script handles various error scenarios:

- Invalid command formats
- Connection issues
- Unexpected FPGA responses
- User input validation
- Edge cases (e.g., incorrect address format)

## Development and Testing

### Manual Testing with Terminal Software

Before using this script, you can verify FPGA communication using terminal software:

1. Use PuTTY, Tera Term, or similar terminal software
2. Configure the UART parameters:
   - Baud rate: 115200 bps
   - Data bits: 8
   - Parity: None
   - Stop bits: 1
   - Flow control: None
3. Connect to the appropriate COM port
4. Send test commands (A00, WF5, G, R) and verify responses

### Automated Testing

The script includes an automated testing function that performs multiple read/write cycles to verify communication reliability:

```bash
# In interactive mode
> test
Enter number of test cycles (default: 5): 10
```

## Troubleshooting

If you encounter issues:

1. Check physical connections
2. Verify UART settings match FPGA configuration
3. Examine log files for detailed error information
4. Test with terminal software to isolate issues
5. Enable debug logging for more detailed information

## License

[Specify license information here]