import serial
import time

# Define the serial port and baud rate
try:
    ser = serial.Serial('COM1', 9600)  # Update 'COM1' with the appropriate port for your device
    # Wait for the serial port to open
    time.sleep(2)

    # Send a command
    command = b'Hello, Serial!'
    ser.write(command)

    # Close the serial port
    ser.close()

except FileNotFoundError:
    print("COM1 Does not exists")

