## Description

A template for Raspberry Pi Pico CMake projects with multiple devices. It streamlines the build process, eliminates the need to unplug boards for reprogramming, and integrates WezTerm for managing multiple GDB instances.

## Installation

1. Clone [pico SDK](https://github.com/raspberrypi/pico-sdk)
2. Navigate to pico SDK folder and execute: git submodule update --init 
3. Build and install [picotool](https://github.com/raspberrypi/picotool)
4. Build and install openocd:
```
$ sudo apt install automake autoconf build-essential texinfo libtool libhidapi-dev libusb-1.0-0-dev
$ git clone git://git.code.sf.net/p/openocd/code openocd
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

Usage: execute [run.sh](project_template/run.sh)

Notice:
1. Flashing with [auto-bootsel binary](auto-bootsel/bin) should be performed only once per each pico
2. CmakeLists.txt must follow [the template](cmakelists_template/CMakeLists.txt)
3. Main function has to start with stdio_init_all()
4. If pico happened to freeze unexpectedly, flash it with [auto-bootsel binary](auto-bootsel/bin)
5. Try clearing the build folder if you encounter errors during the build process

See [examples](examples).
