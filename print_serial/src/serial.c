#include <stdio.h>
#include "pico/stdlib.h"
#include "pico/unique_id.h"

int main() {
    stdio_init_all();
    while (!stdio_usb_connected()) {
        sleep_ms(100);
    }
    pico_unique_board_id_t id;
    pico_get_unique_board_id(&id);
    while (true) {
        for (int len = 0; len < 8; len++) {
            printf("%02X", id.id[len]);
        }
        printf("\n");
        sleep_ms(2000);
    }
}
