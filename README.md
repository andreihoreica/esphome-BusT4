# Nice Bus-T4 ESPHome Component

ESPHome component for integrating **Nice gate and garage door automation** into Home Assistant via the Bus-T4 protocol.

> This is an updated version after https://github.com/makstech/esphome-BusT4 for using with an LilyGO T-CAN485 board.

## Features

- 🏠 **Home Assistant** - Native ESPHome integration
- 🔒 **Local control** - No cloud, no internet required
- 🚪 **Full gate control** - Open, close, stop, and partial opening commands
- 📊 **Real-time status** - Opening, closing, stopped, fully open/closed states
- 📏 **Position tracking** - Time-based estimation with encoder priority when available
- 🧠 **Auto-learning** - Automatically learns and re-learns your gate's open/close timing
- ⚙️ **Motor configuration** - Control auto-close, standby, peak mode, and more via SET commands
- 📡 **OXI receiver logging** - Remote control button presses are logged for debugging

## Required Hardware

### - LilyGO T-CAN485 (XY_32_CAN+RS485) v1.1  (Used for testing)
### - IBT4N module from Nice
### - Buck Converter DC-DC (Step-Down) from 32-40V to 5V
### - Splitter adapter 1 M to 2F RJ11 6P4C
### - Cable RJ11 6P4C
### - Wifi antenna with conector I-PEX (u.FL).
**⚠️ Please be carefull to use an Buck Converter DC-DC (Step-Down) because the LilyGO board needs 5V and the gate offers 24v.⚠️

Tested with:
- Nice Robus RBS600
- connected in parallel with IT4WIFI module

Should work with any Nice controller that has a Bus-T4 port.


#### Step 1: Backup Original Firmware

  **⚠️ Important:** Before flashing, backup the original firmware so you can restore it if needed.

#### Step 2: Install driver for LilyGo board for PC/Mac/etc.

  Download and install driver from here: [Link oficial LilyGO/Drivers](https://github.com/Xinyuan-LilyGO/CH9102_Driver).

#### Step 3: Connect for Flashing

  I used ESP Builder from Home Assistant and you can use directly the code from "nice final.yaml".

  Or you can use https://web.esphome.io/ to connect to the LilyGO board and install the .bin file generated with ESP Builder.

  NOTE: Please make sure you make changes in the next section with your information:

```yaml
wifi:
  ssid: "wifi_ssid"
  password: "wifi_password"
  fast_connect: true
  power_save_mode: NONE
  #  IP static 
  manual_ip:
    static_ip: 192.168.0.13 # Exemplu
    gateway: 192.168.0.1 #conform setarilor retelei
    subnet: 255.255.255.0 #conform setarilor retelei
```

#### Step 4: Making wiring connections to Nice motor

  A. identify the pins from BusT4

<img width="989" height="454" alt="image" src="https://github.com/user-attachments/assets/8007d6f7-58a2-4da9-9ce2-adbacced4d0a" />


Pin RJ11	Nice BusT4	- Please test with an multimeter for 24V to identify the corect wiring. 

Usually there are like below:
  - Pin 1	Black	Terminal GND
  - Pin 3	Red	Terminal A	
  - Pin 4	Green	Terminal B
  - Pin 1	Yellow	Terminal +24V	
  
 I've used an RJ11 6P4C cable cut in two and an splitter adapter 1 M to 2F RJ11 6P4C for connecting in parallel with Nice IT4WIFI.

  B. Connect the GND and +24V pins to the Buck Converter and set 5V for Output.

  C. Make connection to the Canbus: GND on the middle and Red/Green on the left/right. If the gate is unresponsive you can try changing the Red and Green wires in the canbus connector.

  D. Attach the antenna to LilyGo board and all the setup should be recognised by the motor. If not, press and hold for a few secconds the Open+Stop Buttons from the motor till L1 and L2 start flashing.

I've made my setup like in the photos below:

![WhatsApp Image 2026-04-09 at 13 14 53](https://github.com/user-attachments/assets/b9f1f214-4b69-4931-9e47-8f04436466c9)
![WhatsApp Image 2026-04-09 at 13 14 53 (1)](https://github.com/user-attachments/assets/7eae83ec-1426-430f-9e53-43dcd903cdc1)
![WhatsApp Image 2026-04-09 at 13 14 53 (2)](https://github.com/user-attachments/assets/af846eb0-8560-425f-9744-0d566d2df9cf)
![WhatsApp Image 2026-04-09 at 13 14 53 (3)](https://github.com/user-attachments/assets/5cd814d8-0ca1-4b29-84a1-94ba8af4b053)



For more information please refer to https://github.com/makstech/esphome-BusT4.

### Many thanks to Max Slotov [@makstech]!!!

## Credits

- Original Bus-T4 work by [@pruwait](https://github.com/pruwait/Nice_BusT4)
- BiDi-WiFi firmware by [@gashtaan](https://github.com/gashtaan/nice-bidiwifi-firmware)
- Initial ESPHome ESP32 PoC by [@andrein](https://github.com/andrein/esphome-BusT4)
- Latest esphome-BusT4 by Max Slotov [@makstech] (https://github.com/makstech/esphome-BusT4)



