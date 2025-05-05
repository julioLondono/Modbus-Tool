# Product Requirements Document (PRD): Modbus RTU Slave Tester

## 1. Overview
- **Product Name**: Modbus-Tool
- **Purpose**: To develop a desktop application that tests Modbus RTU slave devices (specifically Siemens, Honeywell, Prolon DDC controllers, and Modbus RTU IoT sensors) from a Windows PC by simulating a Modbus master, sending requests, and displaying raw responses.
- **Target Audience**: Engineers and technicians working with industrial automation and IoT systems using Modbus RTU.
- **Platform**: Windows 10/11 (64-bit).
- **Date**: April 03, 2025

## 2. Objectives
- Enable users to connect to Modbus RTU slave devices via a USB-to-serial adapter on a Windows PC.
- Provide a simple interface to configure serial port settings, send Modbus requests, and view raw responses.
- Support standard Modbus RTU baud rates and flexible Windows COM port configuration.
- Use open-source tools and Node.js, packaged as a standalone Windows executable.

## 3. Key Features

### 3.1 Connection Management
- Support for Modbus RTU protocol only (via USB-to-serial adapter).
- Configurable serial port settings:
  - COM port selection (e.g., COM1, COM2, etc.).
  - Standard Modbus baud rates: 1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200.
  - Parity: None, Even, Odd.
  - Data bits: 7 or 8.
  - Stop bits: 1 or 2.
- Auto-detection of available COM ports on the Windows PC.
- Option to save and load connection profiles.

### 3.2 Modbus Communication
- Support for common Modbus RTU function codes:
  - Read Coils (FC 01), Read Discrete Inputs (FC 02), Read Holding Registers (FC 03), Read Input Registers (FC 04).
  - Write Single Coil (FC 05), Write Single Register (FC 06), Write Multiple Coils (FC 15), Write Multiple Registers (FC 16).
- Configurable slave address (1-247).
- Sequential testing of slave devices (one at a time).
- Adjustable polling rate for continuous data retrieval (manual start/stop).

### 3.3 User Interface
- Main Dashboard:
  - Connection status (e.g., "Connected to COM3 at 9600 baud").
  - Start/stop communication button.
- Port Configuration:
  - Dropdowns for COM port, baud rate, parity, data bits, and stop bits.
- Request Builder:
  - Fields for function code, slave ID, starting address, and quantity.
  - Input for write values (e.g., integers).
- Response Display:
  - Plain text or table showing raw data (register/coil values) in decimal, hex, or binary (user-selectable).
  - Real-time updates for polled data.
- Log Window:
  - Communication log with timestamps (sent requests, responses, errors).
  - Export log as a simple text dump (TXT file).

### 3.4 Debugging Tools
- Error reporting (e.g., timeouts, CRC errors, invalid responses).
- Raw byte-level view of requests and responses.

## 4. Technical Requirements
- **Programming Language**: Python
- **Dependencies** (Open-Source):
  - serialport: For USB-to-serial communication.
  - modbus-serial: For Modbus RTU protocol implementation.
  - PyInstaller: To create a desktop GUI and package as a Windows executable.
- **Hardware Requirements**:
  - Windows PC with a USB-to-serial adapter (e.g., USB-to-RS485 or USB-to-RS232).
  - Minimum 4GB RAM, 500MB disk space.
- **Operating System**: Windows 10/11 (64-bit).
- **Packaging**: Standalone .exe file using PyInstaller.

## 5. User Workflow
1. Launch the .exe on a Windows PC.
2. Plug in the USB-to-serial adapter and select the COM port.
3. Configure baud rate, parity, data bits, and stop bits.
4. Enter the slave ID and connect to the device (e.g., Siemens DDC, IoT sensor).
5. Build and send Modbus requests (e.g., read/write registers).
6. View raw responses and logs in the interface.
7. Export logs as a text file if needed.

## 6. Non-Functional Requirements
- **Performance**: Handle at least 5 requests per second without lag.
- **Reliability**: Robust error handling for serial port issues or slave timeouts.
- **Usability**: Simple design with clear labels and minimal setup steps.
- **Distribution**: Self-contained .exe requiring no manual dependency installation.
