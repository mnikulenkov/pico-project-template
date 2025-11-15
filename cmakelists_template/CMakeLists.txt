cmake_minimum_required(VERSION 3.12)
include(${PICO_SDK_PATH}/external/pico_sdk_import.cmake)

set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

project(CPU C CXX ASM)

# this ensures you don't lose any debug output while USB is set up
if (CMAKE_BUILD_TYPE EQUAL "DEBUG")
    set(PICO_STDIO_USB_CONNECT_WAIT_TIMEOUT_MS 3000)
endif (CMAKE_BUILD_TYPE EQUAL "DEBUG")

if (NOT DEFINED PICO_STDIO_USB_CONNECT_WAIT_TIMEOUT_MS)
    set(PICO_STDIO_USB_CONNECT_WAIT_TIMEOUT_MS 3000)
endif()


# initialize the SDK
pico_sdk_init()

SET(SOURCES main.c)

add_executable(${PROJECT_NAME} ${SOURCES})



# pull in common dependencies
target_link_libraries(${PROJECT_NAME}
    pico_stdlib # core functionality
    #pico_cyw43_arch_none # to use LED on pico w
    )

#to enable usb debug output and use picotool load -f
pico_enable_stdio_usb(${PROJECT_NAME} 1)
pico_enable_stdio_uart(${PROJECT_NAME} 0)

# create map/bin/hex file etc.
pico_add_extra_outputs(${PROJECT_NAME})
