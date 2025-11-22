## Description

A template for Raspberry Pi Pico CMake projects with multiple boards. It streamlines the build process, eliminates the need to unplug boards for reprogramming, and integrates WezTerm for managing multiple GDB instances.

## Installation

1. Clone [pico SDK](https://github.com/raspberrypi/pico-sdk)
2. Navigate to pico SDK folder and execute: git submodule update --init 
3. Build and install [picotool](https://github.com/raspberrypi/picotool)
4. Build and install openocd:
```
$ sudo apt install automake autoconf build-essential texinfo libtool libhidapi-dev libusb-1.0-0-dev
$ git clone https://github.com/raspberrypi/openocd.git
$ cd openocd
$ ./bootstrap
$ ./configure --enable-cmsis-dap
$ make -j4
$ sudo make install
```
5. Install GDB:
```
$ sudo apt install gdb-multiarch
```
6. Install [WezTerm](https://github.com/wezterm/wezterm)
7. Install Python 3

## How to use

Steps to configure picos:
1. [Identify pico serial numer](print_serial)
2. Flash pico with [auto-bootsel binary](auto-bootsel/bin) OR with [pico-debug](https://github.com/raspberrypi/debugprobe/releases) for a debug probe
3. Configure [project template](project_template) for your setup
4. Keep pico connected to your machine via USB

Usage: execute [run.sh](project_template/run.sh)
Type 'stop' in main tab to finish.

**WARNING!** If you forcibly close the WezTerm window while the board is stopped at a breakpoint, the board may hang, requiring you to unplug it and manually flash the [auto-bootsel binary](auto-bootsel/bin) while holding the BOOTSEL button. To avoid this, before finishing, make sure to clear all breakpoints and resume program execution. If your program is halted at a breakpoint, the board may freeze unless you re-flash or reconnect it to power source. In all active GDB prompts, execute 'f' to delete breakpoints and continue.

Notice:
1. Flashing with [auto-bootsel binary](auto-bootsel/bin) should be performed only once per each pico
2. CmakeLists.txt must follow [the template](cmakelists_template/CMakeLists.txt)
3. Main function has to start with *stdio_init_all()*
4. If pico happened to freeze unexpectedly, flash it with [auto-bootsel binary](auto-bootsel/bin) or try reconnecting it to power source
5. Try clearing the build folder if you encounter errors during the build process
6. WezTerm integration requires that it **NOT** be used as the primary terminal emulator. You should avoid running [run.sh](project_template/run.sh) directly through WezTerm.
7. If a boards freezes or turns to manual BOOTSEL on 'picotool load' execution, try to experiment with *PICO_RELOAD_TIMEOUT*, *PICOTOOL_LOAD_TIMEOUT*, *OPENOCD_INIT_TIMEOUT* parameters in [project.py](project_template/project.py)

See [examples](examples).
