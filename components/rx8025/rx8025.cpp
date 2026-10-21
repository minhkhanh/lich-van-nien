#include "rx8025.h"
#include "esphome/core/log.h"

namespace esphome {
namespace rx8025 {

static const char *const TAG = "rx8025";

static const uint8_t REG_TIME = 0x00;
static const uint8_t REG_CTRL1 = 0xE0;
static const uint8_t REG_CTRL2 = 0xF0;
static const uint8_t CTRL1_24H = 0x20;
static const uint8_t CTRL2_VDET = 0x40;  // supply voltage dropped
static const uint8_t CTRL2_XST = 0x20;   // 0 = oscillator stopped
static const uint8_t CTRL2_PON = 0x10;   // power-on reset

static uint8_t bcd2dec(uint8_t v) { return (v >> 4) * 10 + (v & 0x0F); }
static uint8_t dec2bcd(uint8_t v) { return ((v / 10) << 4) | (v % 10); }

void RX8025Component::setup() {
  uint8_t ctrl1;
  if (!this->read_byte(REG_CTRL1, &ctrl1)) {
    this->mark_failed();
    return;
  }
  // The hour register is only BCD 0-23 in 24-hour mode (the stock firmware also sets this)
  if (!(ctrl1 & CTRL1_24H))
    this->write_byte(REG_CTRL1, ctrl1 | CTRL1_24H);
  this->read_time();
}

void RX8025Component::update() { this->read_time(); }

void RX8025Component::dump_config() {
  ESP_LOGCONFIG(TAG, "RX8025:");
  LOG_I2C_DEVICE(this);
  if (this->is_failed()) {
    ESP_LOGE(TAG, "Communication failed");
  }
  RealTimeClock::dump_config();
}

bool RX8025Component::read_rtc(ESPTime &t, bool &lost, bool &low_voltage) {
  uint8_t ctrl2;
  uint8_t r[7];
  if (!this->read_byte(REG_CTRL2, &ctrl2) || !this->read_bytes(REG_TIME, r, sizeof(r)))
    return false;
  lost = (ctrl2 & CTRL2_PON) || !(ctrl2 & CTRL2_XST);
  low_voltage = ctrl2 & CTRL2_VDET;
  t = ESPTime{};
  t.second = bcd2dec(r[0] & 0x7F);
  t.minute = bcd2dec(r[1] & 0x7F);
  t.hour = bcd2dec(r[2] & 0x3F);
  t.day_of_week = (r[3] & 0x07) + 1;
  t.day_of_month = bcd2dec(r[4] & 0x3F);
  t.day_of_year = 1;  // recalc_timestamp_utc() does not use it
  t.month = bcd2dec(r[5] & 0x1F);
  t.year = bcd2dec(r[6]) + 2000;
  t.recalc_timestamp_utc(false);
  return true;
}

void RX8025Component::read_time() {
  ESPTime t;
  bool lost, low_voltage;
  if (!this->read_rtc(t, lost, low_voltage)) {
    ESP_LOGE(TAG, "Read failed");
    return;
  }
  if (low_voltage)
    ESP_LOGW(TAG, "Low voltage detected (VDET), check the backup battery");
  if (lost) {
    ESP_LOGW(TAG, "Power-on reset or oscillator stop, time not valid");
    return;
  }
  if (!t.is_valid()) {
    ESP_LOGW(TAG, "Invalid time %04u-%02u-%02u %02u:%02u:%02u", t.year, t.month, t.day_of_month, t.hour,
             t.minute, t.second);
    return;
  }
  ESP_LOGD(TAG, "Read UTC %04u-%02u-%02u %02u:%02u:%02u", t.year, t.month, t.day_of_month, t.hour, t.minute,
           t.second);
  this->synchronize_epoch_(t.timestamp);
}

void RX8025Component::write_time() {
  ESPTime now = this->utcnow();
  if (!now.is_valid()) {
    ESP_LOGE(TAG, "System time not valid, not writing");
    return;
  }
  uint8_t r[7] = {
      dec2bcd(now.second),
      dec2bcd(now.minute),
      dec2bcd(now.hour),
      static_cast<uint8_t>(now.day_of_week - 1),
      dec2bcd(now.day_of_month),
      dec2bcd(now.month),
      dec2bcd(now.year % 100),
  };
  // Then clear PON/VDET and the alarm flags, and set XST to re-arm oscillator stop detection
  if (!this->write_bytes(REG_TIME, r, sizeof(r)) || !this->write_byte(REG_CTRL2, CTRL2_XST)) {
    ESP_LOGE(TAG, "Write failed");
    return;
  }
  ESP_LOGD(TAG, "Wrote UTC %04u-%02u-%02u %02u:%02u:%02u", now.year, now.month, now.day_of_month, now.hour,
           now.minute, now.second);
}

}  // namespace rx8025
}  // namespace esphome
