#pragma once
// Helpers for the HA data pages: colour scales, EVN bill estimate, weather names; alarm tones and days.
#include <cmath>
#include <string>
#include "esphome/core/color.h"

namespace clock_util {

using esphome::Color;

static const Color GREEN(0, 228, 0), YELLOW(255, 220, 0), ORANGE(255, 126, 0), RED(255, 0, 0),
    PURPLE(160, 60, 200), MAROON(160, 0, 40), GREY(120, 120, 120);

// Vietnam AQI (VN_AQI) and US AQI share the same breakpoints and colours
inline Color aqi_color(float v) {
  if (std::isnan(v)) return GREY;
  if (v <= 50) return GREEN;
  if (v <= 100) return YELLOW;
  if (v <= 150) return ORANGE;
  if (v <= 200) return RED;
  if (v <= 300) return PURPLE;
  return MAROON;
}

// PM2.5 in µg/m³ (US EPA 24h breakpoints)
inline Color pm25_color(float v) {
  if (std::isnan(v)) return GREY;
  if (v <= 12) return GREEN;
  if (v <= 35.4f) return YELLOW;
  if (v <= 55.4f) return ORANGE;
  if (v <= 150.4f) return RED;
  if (v <= 250.4f) return PURPLE;
  return MAROON;
}

inline Color co2_color(float v) {
  if (std::isnan(v)) return GREY;
  if (v < 800) return GREEN;
  if (v < 1000) return YELLOW;
  if (v < 1500) return ORANGE;
  return RED;
}

// Whole-house power in W; alert is the HA threshold (input_number.power_alert_total)
inline Color power_color(float w, float alert) {
  if (std::isnan(w)) return GREY;
  if (!std::isnan(alert) && w >= alert) return RED;
  if (w < 1000) return GREEN;
  if (w < 2500) return YELLOW;
  return ORANGE;
}

// EVN residential tariff, same tiers and VAT as scripts/energy_dashboard.py (QĐ 1279/QĐ-BCT, VAT 8%)
inline float evn_bill(float kwh) {
  static const float SIZE[] = {50, 50, 100, 100, 100, 1e9f};
  static const float PRICE[] = {1984, 2050, 2380, 2998, 3350, 3460};
  float left = kwh, sum = 0;
  for (int i = 0; i < 6 && left > 0; i++) {
    float q = left < SIZE[i] ? left : SIZE[i];
    sum += q * PRICE[i];
    left -= q;
  }
  return sum * 1.08f;
}

// HA weather condition -> short Vietnamese text without diacritics (the small font has none)
inline const char *weather_vn(const std::string &c) {
  if (c == "sunny") return "Nang";
  if (c == "clear-night") return "Troi quang";
  if (c == "partlycloudy") return "Co may";
  if (c == "cloudy") return "Nhieu may";
  if (c == "rainy") return "Mua";
  if (c == "pouring") return "Mua to";
  if (c == "lightning") return "Dong set";
  if (c == "lightning-rainy") return "Mua dong";
  if (c == "fog") return "Suong mu";
  if (c == "hail") return "Mua da";
  if (c == "windy" || c == "windy-variant") return "Gio manh";
  if (c == "snowy" || c == "snowy-rainy") return "Tuyet";
  return c.c_str();
}

// Alarm / hourly chime tones of the stock firmware v2.18 (table at 0x3ffbdc30: {tick ms - 1, then
// (600/duration, Hz) pairs}, played from a 1 ms timer), as RTTTL. Stock lengths in ms are in the comments.
inline const char *stock_tone(int i) {
  static const char *const TONES[] = {
      "tone1:d=16,o=6,b=100:c,d,4g,8p.",       // C6 164, D6 164, G6 604, rest 484
      "tone2:d=16,o=6,b=100:d,g,8e.,8p.",      // D6 164, G6 164, E6 404, rest 484
      "tone3:d=16,o=6,b=160:e,p,e,p,8d,4p",    // E6 93, rest 93, E6 93, rest 93, D6 183, rest 363
  };
  return TONES[i >= 0 && i < 3 ? i : 0];
}

// Alarm "days" option: 0 every day, 1 Mon-Fri, 2 Mon-Sat, 3 Sat-Sun. dow is ESPTime's (1 = Sunday).
inline bool alarm_day(int sel, int dow) {
  switch (sel) {
    case 1: return dow >= 2 && dow <= 6;
    case 2: return dow >= 2;
    case 3: return dow == 1 || dow == 7;
    default: return true;
  }
}

// Hour window [start, end), may wrap past midnight
inline bool in_hours(int hour, int start, int end) {
  return start <= end ? (hour >= start && hour < end) : (hour >= start || hour < end);
}

}  // namespace clock_util
