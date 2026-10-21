#pragma once

#include "esphome/core/component.h"
#include "esphome/components/i2c/i2c.h"
#include "esphome/components/time/real_time_clock.h"

namespace esphome {
namespace rx8025 {

// Epson RX-8025SA/NB (I2C 0x32). The register number goes in the high nibble of the address byte
// (low nibble = transfer mode 0). Time registers 0-6: sec, min, hour, weekday (0-6), day, month, year (BCD).
// The RTC is kept in UTC; call write_time() after a network time sync.
class RX8025Component : public time::RealTimeClock, public i2c::I2CDevice {
 public:
  void setup() override;
  void update() override;
  void dump_config() override;
  float get_setup_priority() const override { return setup_priority::DATA; }
  // Sync system time from the RTC
  void read_time();
  // Store system time in the RTC
  void write_time();
  // Read the RTC without touching system time. Returns false on I2C error.
  // lost: power-on reset or oscillator stop, so the time is not valid. low_voltage: VDET flag.
  bool read_rtc(ESPTime &t, bool &lost, bool &low_voltage);
};

}  // namespace rx8025
}  // namespace esphome
