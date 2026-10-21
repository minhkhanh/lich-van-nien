# Stock firmware v2.18 features

Sources: the saved web UI (`LỊCH VẠN NIÊN LS.html`), strings and decompile of `v218_5k.bin`, and the vendor video
"ĐỒNG HỒ LỊCH VẠN NIÊN LS WIFI - HƯỚNG DẪN CÀI ĐẶT" (ĐIỆN TỬ LONGSMART, 2023-11-24, https://youtu.be/mGdeDIRQfzs;
frames and transcript in `video/`).

## Screen (from the video)

- Top half: large HH:MM (about 16 rows). Each digit can have its own colour or a rainbow / colour shift.
  AM/PM (green) and seconds (`.07`) in small type on the right.
- Bottom half: a scrolling line about 16 rows high, **with Vietnamese diacritics**, cycling through items such as
  "Chủ nhật", "19/11/2023", "Âm lịch: …", "Nh.độ: 29.5 °C", "Độ ẩm: …", "Địa chỉ IP: …", events and custom text.
  Each item has a title colour and a value colour.
- Boot: "Đồng Hồ Lịch Vạn Niên WiFi", AP password hint, "Khôi phục về mặc định", Wi-Fi result, IP.

## Web UI (5 tabs)

1. **Display**: theme 1-4 (theme 0 has no seconds bar or second colour; themes 1-3 force the solar date;
   theme 2 has no 12/24h option), hour font 1-4, background effect (off, fireworks, snow, flying hearts,
   falling flowers, random) with effect speed and colour-mix sliders, toggles for seconds bar, 24h mode,
   solar date, lunar date, temperature, humidity, IP, scrolling text; brightness.
2. **Colours**: hour and minute modes (single, multi 1-3, rainbow 1-3, colour shift 1-2) plus a colour picker;
   seconds and event text (single, multi, rainbow); AM/PM; title + value colours for solar date, lunar date,
   temperature, humidity and IP.
3. **Text / image / alarm**
   - Annual events on/off and scroll speed. About 50 built-in days with greetings: Tết Dương lịch,
     Mùng 1-3 Tết, Ông Táo, Giỗ Tổ Hùng Vương, Đoan Ngọ, Trung Thu (lunar), and solar days such as 3/2, 8/3,
     30/4, 1/5, 19/5, 1/6, 27/7, 2/9, 20/10, 20/11, 22/12, Giáng Sinh, Valentine.
   - Up to 5 custom texts: 3 segments each with colour (single/multi/rainbow), optional "on date".
   - Image: the browser scales any picture to 64x32 on a canvas and POSTs a PNG to `/upload` (SPIFFS);
     show image on/off and display time (0-30 s).
   - 5 alarms: on/off, time, tone (3), ring duration (s), repeat interval, weekdays, text + colour.
     A "Báo thức đang báo! Tắt" dialog and the KEY button stop it.
4. **Date/time**: manual time and date (with "seconds = 0"), Wi-Fi SSID/password + test (for NTP).
   Other: temperature offset (-10..10 °C), timezone, AP on/off (SSID "Lịch Vạn Niên…", password 123456789,
   address 9.9.9.9), language VI/EN, hourly chime (off / tone 1-3), brightness by schedule (2 time slots with
   brightness %) instead of the light sensor.
5. **Info**: maker LS TECH, IP, version 2.18 (04/10/2024), online update (`sv.lscloud.in`) or `.bin` upload.

Hidden pages: `/setup` / `/cauhinh` (LED type: P5 indoor 16S, P5 outdoor 8S, 4x P10 indoor 8S, 4x P10 outdoor
4S, ...; sensor NTC or DHT21), `/dir` and `/spiffs` (file list). The device registers with
`/fw/clockrgb/reg` at boot and only runs the display when licensed.

## HTTP API

GET `loaddata`, `config?…`, `color?…`, `settxt?…`, `loadtxt?id=|act=add|edit|del`, `setimg?en=…`,
`alarm?id=|act=…|data=`, `sound?run=N|off=1`, `datetime?time=&date=&sec=`, `wifi?data=`, `setting?…`,
`app/checkversion`, `app/update`; POST `/upload` (image), `/update` (firmware).

## ESPHome port status

| Feature | Status / plan |
|---|---|
| Time, solar date, lunar date + year name, temperature | Done (8-row text, no diacritics) |
| Auto brightness from the light sensor | Done (min/max numbers) |
| Buzzer, KEY button | Done (rtttl, `play_rtttl` action) |
| Stock layout: 16-row scrolling bottom line with diacritics | Partly: rotating 2-line pages (Tiny5, no marks); 13 px marquee with diacritics for messages |
| Per-digit colours, rainbow, colour shift | To do (lambda) |
| Annual events (solar + lunar) with greetings | To do (table in a header, lunar dates via amlich.h) |
| Custom scrolling text | Done: `Message` text entity / `show_message` action |
| Alarms, hourly chime | Done on the device: 3 alarms + chime with the 3 stock tones |
| Brightness schedule | HA automation on the brightness number, or keep auto |
| Image (64x32) | Possible with `online_image` from HA |
| Background effects | Low priority |
| Wi-Fi/AP setup, NTP, timezone, OTA, language | Replaced by ESPHome / HA |

## New in the ESPHome version (not in the stock firmware)

- Air quality page (outdoor AQI/PM2.5, indoor PM2.5/CO2), power page (W, AC circuit, monthly kWh, EVN bill),
  weather page, all from HA
- Power alert: power page pinned and red above the HA threshold
- Messages from HA automations, with beep
- Entities in HA: temperature, ambient light, RTC time, lunar date, brightness controls, button
