# LongSmart Lịch Vạn Niên V2.0 (LS-LVN-P510) - pinout from firmware v2.18 (v218_5k.bin)

Source: Ghidra decompile of app1 (active OTA slot) from full flash dump; v218_5k.bin downloaded from
sv.lscloud.in/fw/clockrgb/update is byte-identical (md5 ffafbff3de2ebfb14f5c4cfcfc3b3d40).
Arduino-ESP32 1.0.6 (IDF v3.3.5), HUB75 via ESP32-HUB75-MatrixPanel-I2S-DMA.

## HUB75 (14-byte i2s_pins table @0x3f403b9f, memcpy'd into HUB75_I2S_CFG)
R1=2  G1=26 B1=27  R2=14 G2=12 B2=13
A=23  B=19  C=5    D=17  E=-1 (GPIO18 when panel type 4 = 128x64)
LAT=4 OE=15 CLK=16
Panel types (setting byte): 1,2 -> 128x16; 3 -> 256x8; 4 -> 128x64 (E=18); other -> 64x32 (ours)

## Other I/O
KEY button   GPIO0  (pinMode INPUT, digitalRead) - also the boot strap, so holding KEY at power-on = download mode
Buzzer       GPIO25 passive, LEDC ch1 (ledcAttachPin(25,1) + ledcWriteTone); this is why R1 moved off 25
Status LED   GPIO33 (OUTPUT, toggled once a second in the 1 ms ticker when licensed)
I2C RTC Epson RX-8025SA (0x32, reg<<4 addressing, Ctrl1 0xE0=0x20 24h, Ctrl2 0xF0), Wire.begin() defaults SDA=21 SCL=22
NTC          GPIO35 analogRead (Steinhart/log math)
CDS (LDR)    GPIO34 analogRead (auto brightness)
DHT21        GPIO32 (DHT(32, DHT21, 6)), "SEN" header; selectable instead of NTC in setup page
