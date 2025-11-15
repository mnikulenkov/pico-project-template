## Description

A template for Raspberry Pi Pico CMake projects with multiple devices. It streamlines the build process, eliminates the need to unplug boards for reprogramming, and integrates WezTerm for managing multiple GDB instances.

## How to use

Requirements:
1. Clone [pico sdk](https://github.com/raspberrypi/pico-sdk)
2. Build and install [picotool](https://github.com/raspberrypi/picotool)
3. Build and install [openocd](https://github.com/majbthrd/pico-debug/blob/master/howto/openocd.md)
4. Install [WezTerm](https://github.com/wezterm/wezterm)
5. Install Python 3

Steps to configure picos:
1. [Identify pico serial numer](print_serial)
2. Flash pico with [auto-bootsel binary](auto-bootsel/bin) OR with [pico-debug](https://github.com/majbthrd/pico-debug) (rp2040 only) for a debug probe
3. Configure [project template](project_template) for your setup

Usage: execute [run.sh](project_template/run.sh)

Notice:
1. Flashing with no_unplug_BOARD.uf2 should be performed only once per each pico
2. CmakeLists.txt must follow [the template](cmakelists_template/CMakeLists.txt)
3. Main function has to start with stdio_init_all()

See [examples](examples).
