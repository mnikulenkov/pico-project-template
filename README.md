Requirements:
1. Clone [pico sdk](https://github.com/raspberrypi/pico-sdk)
2. Build and install [picotool](https://github.com/raspberrypi/picotool)
3. Build and install [openocd](https://github.com/majbthrd/pico-debug/blob/master/howto/openocd.md)
4. Install [WezTerm](https://github.com/wezterm/wezterm)

Steps to configure picos:
1. [Identify pico serial numer](print_serial)
2. Flash pico with [binary](no_unplug) OR with [pico-debug](https://github.com/majbthrd/pico-debug) (rp2040 only) for a debug probe
3. Configure [project template](project_template/README.md) for your setup

Usage: execute [run.sh](project_template/run.sh)

Notice:
1. Flashing with no_unplug_BOARD.uf2 should be performed only once per each pico
2. CmakeLists.txt must follow [the template](cmakelists_template/CMakeLists.txt)
3. Main function must start with stdio_init_all()

See [examples](examples/README.md).
