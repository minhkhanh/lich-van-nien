# Lịch vạn niên clock (ESPHome)

LongSmart "LICH VAN NIEN V2.0" (LS-LVN-P510): ESP32-WROOM-32 (ESP32-D0WDQ6, 4 MB) on a P5 HUB75 64x32 panel,
at `192.168.100.202`, MAC `D4:D4:DA:40:88:F0`. Stock closed firmware v2.18 was replaced with ESPHome on 2026-10-20.
In HA: ESPHome device "Lunar Calendar Clock" (`*.lunar_calendar_clock_*`).

## Layout

| Path | What |
|---|---|
| `lich-van-nien.yaml` | ESPHome config (also deployed to `/config/esphome/` on HA) |
| `components/rx8025/` | Time platform for the Epson RX-8025SA RTC (not in ESPHome) |
| `packages/alarm.yaml` | One alarm's entities (copy to `/config/esphome/packages/` too) |
| `includes/amlich.h` | Vietnamese lunar calendar (Ho Ngoc Duc's algorithm) |
| `fonts/5x8-prop.bdf` | Data-page font: X11 5x8 made proportional by `tools/propbdf.py` (copy to `/config/esphome/fonts/` too) |
| `fonts/seg7-5x8.bdf`, `fonts/seg7-6x8-bold.bdf` | Square seven-segment digits for the bottom line, thin and bold, 8 rows like the text capitals, from `tools/seg7bdf.py [--bold] --height=8` (copy to HA too) |
| `fonts/lvn-hour16-N[-small].bdf`, `fonts/lvn-hour22-N.bdf` | Stock clock digits (4 styles, 16 and 22 rows, plus small seconds) from `tools/extract_hourfonts.py` (vendor's) |
| `fonts/lvn-stock.bdf`, `fonts/lvn-stock-bold.bdf` | Text font (bottom line, messages, events) taken from the stock firmware by `tools/extract_stockfont.py` (vendor's font), and a bold copy (`tools/propbdf.py --vi --bold --space=4`) |
| `secrets.yaml` | Credentials (not for git) |
| `firmware/` | Last built `factory.bin` (serial, offset 0) and `ota.bin` |
| `clock-backup/` | Stock firmware: `v218_5k.bin` (OTA image from the vendor server, sha256 2675cea4…1dd6), `PINOUT.md`; the full 4 MB dump stays local (Wi-Fi credentials in NVS) |
| `analysis/` | Stock app as ELF and its Ghidra decompile (where the pinout came from) |
| `tools/` | `mkelf.py` (ESP32 image to ELF), `pinscan.py`, `DumpAll.java` (Ghidra headless), `sim.py` + `layout.py` (64x32 layout preview) |

`secrets.yaml` (mode 600) holds the credentials: Wi-Fi, `clock_web_password` (web login), `clock_api_key`
(api + OTA encryption). It is a copy of `/config/esphome/secrets.yaml` on HA, which the other ESPHome devices
share; change secrets there and copy the file back. `.gitignore` keeps it, `firmware/`, `clock-backup/`, the
saved stock web page and `.esphome/` out of git, since all of them contain credentials.

## Screen

Top: HH:MM, the colon blinking with the seconds (`Show seconds` adds small seconds and shrinks the time a
size). Bottom: one line, pages rotating every `Page duration` s (switches turn pages 1-4 off; digits use the seven-segment font):

0. Sun icon + weekday and date (no year)
1. Moon icon + lunar day/month, no year (`Show lunar date`)
2. Indoor PM2.5 and CO2 (PTH9BW) with a dust icon and a "CO2" label, values coloured by level; the dust icon hides when CO2 >= 1000 leaves no room (`Show air quality`)
3. Temperature and humidity from the PTH9BW, behind thermometer and droplet icons; the temperature falls
   back to the clock's own sensor while the PTH9BW is away (`Show temperature`)
4. Events (`Show events`): today's holidays from `includes/events.h` (the stock list plus Mùng 1 / Rằm of
   every lunar month), scrolled once with Vietnamese letters; also in HA as `Today event`

`Time color`: Orange, Per digit or Rainbow. `Night mode`: between `Night start` and `Night end` (hours) the
brightness is `Night brightness` (0 = panel off) instead of the normal/auto value.

`Time font`: the stock digits, Round / Segment / Outline / Italic at 22 rows or Round / Segment / Square /
Bold round at 16 rows. The 22-row digits leave no room for seconds or the marquee, so the same style's
16-row digits stand in while `Show seconds` is on or text scrolls. `Font` picks Bold (default) or Thin for all text below the time: the stock font and the seven-segment digits.

## Alarms

Three alarms (`packages/alarm.yaml`, included once per alarm with `n` and a default time): `Alarm N` on/off,
`Alarm N time`, `Alarm N days` (Every day / Mon-Fri / Mon-Sat / Sat-Sun) and `Alarm N tone`. They run on the
clock itself, so they ring without HA. An alarm repeats its tone for `Alarm duration` s and scrolls
"Báo thức HH:MM"; KEY or the `Stop alarm` button stops it, `Alarm ringing` shows it. `Hourly chime` plays a
tone at every full hour, except in the night mode window and while an alarm rings. Picking a tone plays it once.

The three tones are the stock firmware's (table at `0x3ffbdc30` in `analysis/app1.elf`, played from a 1 ms timer),
converted to RTTTL in `clock_util::stock_tone()`: Tone 1 C6-D6-G6, Tone 2 D6-G6-E6, Tone 3 E6-E6-D6.

The `Message` text entity (or action `esphome.lich_van_nien_show_message`) beeps and scrolls a message with
Vietnamese letters three times, then clears it. KEY: stop sound, else clear message, else display on/off.
HA entity IDs for the pages are substitutions at the top of the YAML. Preview layouts with `tools/sim.py`.

## Hardware (from the stock firmware)

- HUB75: R1=2 G1=26 B1=27 R2=14 G2=12 B2=13 A=23 B=19 C=5 D=17 LAT=4 OE=15 CLK=16 (no E)
- Buzzer GPIO25 (passive, LEDC), status LED GPIO33, KEY GPIO0 (also the boot strap)
- RTC RX-8025SA on I2C SDA=21 SCL=22, address 0x32
- NTC 5k@25°C on GPIO35 (10k divider in practice), CDS on GPIO34, DHT21 header on GPIO32 (not fitted)

## Build and flash

Build in this directory (the build cache lives in `.esphome/`). The corporate TLS proxy on the Mac needs a CA
bundle for downloads (fonts, toolchains):

```sh
security find-certificate -a -p /System/Library/Keychains/SystemRootCertificates.keychain \
  /Library/Keychains/System.keychain > /tmp/ca.pem
export REQUESTS_CA_BUNDLE=/tmp/ca.pem SSL_CERT_FILE=/tmp/ca.pem
uvx --native-tls esphome@2026.9.1 compile lich-van-nien.yaml
uvx --native-tls esphome@2026.9.1 upload lich-van-nien.yaml --device 192.168.100.202
```

Away from home, tunnel through the router (its host key is stored under `192.168.100.1`):

```sh
ssh -f -N -o HostKeyAlias=192.168.100.1 -L 3232:192.168.100.202:3232 -L 18080:192.168.100.202:80 openwrt
uvx --native-tls esphome@2026.9.1 upload lich-van-nien.yaml --device 127.0.0.1
```

After changing the YAML or components, copy them to `/config/esphome/` on HA too.

If the clock stays down after an OTA (only port 3232 answers, no API or web UI), the new firmware is in
safe mode after a boot loop. Known cause: esp-hub75 0.3.5 crashes at boot when the second DMA buffer
(`double_buffer`) can't be allocated, which depends on how much RAM a build leaves. `bit_depth: 6` keeps the
buffers small; watch `Heap largest block`. Unplug and replug it: OTA rollback is on, so a firmware that never
reached "Boot seems successful" (1 min) is replaced by the previous one. Check which one runs with the
`Firmware` sensor (build time) and `Reset reason`, then flash again while watching `esphome logs`.

OTA uploads are encrypted with the api key (no OTA password). The web UI and its `/update` need a login:
user `admin`, password `clock_web_password` in `/config/esphome/secrets.yaml` (digest auth, e.g.
`curl --digest -u admin:… http://192.168.100.202/sensor/Temperature`). The web `/update` upload is the
fallback if `esphome upload` ever fails.

Serial (first flash or recovery): CP2102 on TX/RX/GND only, hold KEY (IO0 low) while powering on, then
`esptool.py -p /dev/cu.usbserial-0001 --before no_reset write_flash 0 firmware/esphome-lich-van-nien.factory.bin`.
Erase first (`erase_flash`) when coming from the stock firmware, or its otadata boots the wrong slot.

## Restore the stock firmware

```sh
esptool.py -p /dev/cu.usbserial-0001 --before no_reset write_flash 0 clock-backup/lichvannien_v2.18_full.bin
```

The dump contains the Wi-Fi credentials in NVS, so keep it private.
