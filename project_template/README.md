## Project config parameters

[Project config template](config_template.json)

Config has "devices" and "programs" lists: a program is attached to a device, each of them is configured independently.

DEVICE_NAME
BOARD_TYPE (pico/pico_w/pico2/pico2_w)
SERIAL - pico's [serial number](../print_serial)

PROGRAM_NAME
BUILD_TYPE (debug/release) - sets CMAKE_BUILD_TYPE in CMakeLists.txt.
SRC_PATH - path to directory with CMakeLists.txt.
TARGET_DEVICE_NAME - DEVICE_NAME of a pico to be flashed.
DEBUG_DEVICE_NAME - DEVICE_NAME of debug probe connected to target device.
GDB_PORT
TCL_PORT
TELNET_PORT

BEHAVIOUR (run/build_only) - "run" to build and flash target devices; "build_only" to just write binaries to BUILD_PATH.
BUILD_PATH
BUILD_NPROC - sets "make -jN" argument.
PICO_SDK_PATH - path to sdk folder.
GDB_DEBUG (on/of) - to run GDB debugging via WezTerm.
OPENOCD_OUTPUT (on/of) - to show OpenOCD tabs along with GDB in WezTerm.
PICOTOOL_LISTEN (on/of) - to build programs which make pico listen to BOOTSEL command so picotool can load them without unplugging. Setting PICOTOOL_LISTEN to "off" will disable this feature and you will have to manually flash pico with [BOOTSEL-friendly binary](../auto-bootsel) to use this project template for autoflashing.
GDB_COMMANDS_PATH - path to list of GDB commands to be executed per program.

## Executing GDB commands

Fill list of [GDB commads](gdb_commands.json) to be executed per program before GDB starts.
