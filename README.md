# DuckLogger

<img width="2559" height="1060" alt="image" src="https://github.com/user-attachments/assets/d3178370-de53-4aaa-916b-64b3155cc503" />

## Overview

DuckLogger is an ESP32-S3–based USB Key Logger. It logs keystrokes, log them in a text file, and provides wireless access to download logs through a built-in Wi-Fi access point.

<img width="2560" height="1440" alt="ducklogger" src="https://github.com/user-attachments/assets/f5aa82a2-3fc4-450a-a6cb-c52042ec13ce" />


## Features

1. Records keystrokes and saves them to a log file in internal flash storage
2. Automatically creates a Wi-Fi Access Point
3. Serves the log file over HTTP at:

```
http://192.168.4.1/
```

## Components Used

* ESP32-S3 SuperMini
* CH9350 HID Module
* 4 Female Jumper Wires

---

# Getting Started

## 1. Schematics

(To be updated)



## 2. Flash MicroPython

DuckLogger is written in micropython, flash your board with micropython.
Find flashing instructions [here](https://micropython.org/download/ESP32_GENERIC_S3/)


After flashing, disconnect and reconnect the board via USB.


## 3. Install mpremote

On your development machine:

```bash
pip install mpremote
```

Verify that your board is detected:

```bash
mpremote connect list
```



## 4. Install Required MicroPython Packages

Install required packages directly onto the board:

```bash
mpremote mip install usb-device
mpremote mip install usb-device-keyboard
mpremote mip install microdot
```



## 5. Install DuckLogger on the Board

Clone the repository:

```bash
git clone https://github.com/Itsmmdoha/duckLogger.git
cd duckLogger
```

Make sure your board is connected via USB.

### Copy all ducklogger library files to `/lib` on the device

```bash
mpremote cp lib/*.py :/lib/
```

### Copy main files to the root of the device

```bash
mpremote cp main.py :
```

Reboot the board:

```bash
mpremote reset
```


# Usage

1. Plug the USB keyboard into the CH9350 HID module.
2. Connect the ESP32-S3 SuperMini to the target PC using a USB-C to USB-A cable.
3. The device will automatically:

   * Start logging keystrokes
   * Create a Wi-Fi Access Point
   * Start an HTTP server

Connect to the Wi-Fi Access Point (Password: `duckPass1234`) and open:

```
http://192.168.4.1/
```

to download the log file.


# Repository Structure

```
├── lib
│   ├── access_point.py
│   ├── api.py
│   ├── keyboard.py
│   ├── key_led.py
│   ├── logger.py
│   └── uart_buffer.py
├── main.py
├── README.md
└── resources.md
```
