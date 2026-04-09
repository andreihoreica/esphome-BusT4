#include "bus_t4.h"

namespace esphome::bus_t4 {

void BusT4Device::send_cmd(T4Command cmd) {
  // DEP packet structure: [device] [command] [cmd_value] [offset]
  uint8_t message[4] = { OVIEW, RUN, cmd, 0x64 };
  T4Packet packet(target_address_, parent_->get_address(), DEP, message, sizeof(message));
  write(&packet, 0);
}

void BusT4Device::send_info_request(T4Target target, T4InfoCommand command) {
  // DMP GET packet structure: [target] [command] [request_type] [offset] [length]
  uint8_t message[5] = { target, command, REQ_GET, 0x00, 0x00 };
  T4Packet packet(target_address_, parent_->get_address(), DMP, message, sizeof(message));
  write(&packet, 0);
}

//void BusT4Device::send_config_set(T4InfoCommand param, uint8_t value)
void BusT4Device::send_config_set(uint8_t param, uint8_t value) {
  // DMP SET packet structure: [target] [param] [request_type] [offset] [length] [value]
  uint8_t message[6] = { FOR_CU, param, REQ_SET, 0x00, 0x01, value };
  T4Packet packet(target_address_, parent_->get_address(), DMP, message, sizeof(message));
  write(&packet, 0);
}

void BusT4Device::send_it4_cmd(T4Command cmd) {
  // DEP packet structure: [device] [command] [cmd_value] [offset]
  // Folosim 0x02 în loc de OVIEW (0x01) pentru a fi recunoscuți ca IT4WIFI pentru securitate
  uint8_t message[4] = { 0x02, RUN, cmd, 0x64 };
  T4Packet packet(target_address_, parent_->get_address(), DEP, message, sizeof(message));
  write(&packet, 0);
}

void BusT4Device::send_it4_cmd(uint8_t cmd_value) {
  // DEP packet structure: [device=0x02] [command=RUN] [cmd_value] [offset=0x64]
  uint8_t message[4] = { 0x02, 0x82, cmd_value, 0x64 };
  T4Packet packet(target_address_, parent_->get_address(), (T4Protocol)0x01, message, sizeof(message));
  write(&packet, 0);
}

} // namespace esphome::bus_t4
