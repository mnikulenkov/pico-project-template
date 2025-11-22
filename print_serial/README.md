## Identify pico serial number

1. Flash pico with print_serial_BOARD.uf2 file and unplug it
2. Run *python3 monitor_ports.py*
3. Plug in pico and copy device file path (/dev/ttyACMN)
4. Run *sudo screen /dev/ttyACMN 115200* (Ctrl+A+D to exit)
