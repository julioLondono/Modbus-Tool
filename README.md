# Modbus RTU Tool

A desktop application for testing and debugging Modbus RTU slave devices. Built with Python and tkinter, this tool provides a user-friendly interface for Modbus communication and device discovery.

## Features

- **COMM Port Configuration**
  - Serial port selection
  - Configurable baud rate, data bits, and parity
  - Settings persistence across sessions

- **Device Discovery**
  - Scan for Modbus devices in a specified address range
  - Real-time progress tracking
  - Visual feedback with progress bar
  - Device list with connection status

- **Connection Management**
  - Double-click to connect/disconnect from devices
  - Robust port handling with automatic cleanup
  - Connection retry mechanism
  - Clear status indicators

## Requirements

- Python 3.x
- Windows 10/11
- USB-to-Serial adapter

## Installation

1. Clone the repository:
```bash
git clone https://github.com/julioLondono/Modbus-Tool.git
cd Modbus-Tool
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the application:
```bash
python main_window.py
```

2. Configure COM Port:
   - Click "COMM Setup"
   - Select your COM port
   - Configure baud rate, data bits, and parity
   - Click "OK" to save settings

3. Discover Devices:
   - Enter start and end addresses (1-247)
   - Click "Start Scan"
   - Monitor progress in the status bar
   - View discovered devices in the list

4. Connect to Devices:
   - Double-click a discovered device to connect
   - Double-click again to disconnect

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [pymodbus](https://github.com/pymodbus-dev/pymodbus)
- Uses [pyserial](https://github.com/pyserial/pyserial) for serial communication
