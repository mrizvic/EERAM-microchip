### MICROCHIP EERAM manipulation library

perform software EEPROM store/recall commands
manipulate various CONTROL REGISTER bits
hexdump SRAM portions
read/write single byte
read/write null terminated strings

I have MICROCHIP 47C16 serial EERAM hooked up to RPI via I2C pins therefore smbusDevice=1. Pins A1 and A2 are grounded so address is 0. Also capacitor is hooked between Vcap and GND in order perform copy SRAM to EEPROM in case of power outage. Note that ASE bit has to be set in order to enable this feature. See wiring and example usage below.

### WIRING DIAGRAM
![rpi-eeram-wiring](https://github.com/mrizvic/EERAM-microchip/blob/master/rpi-eeram-wiring.png)

### USAGE:
```
$ pip3 install smbus2
$ python3
Python 3.7.3 (default, Jul 25 2020, 13:03:44)
[GCC 8.3.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import EERAM
>>> size = 16384
>>> smbuSdevice = 1
>>> address = 0
>>> debug = 0
>>> e=EERAM.EERAM(size, smbusDevice, address, debug)
```
or without arguments but with same defaults
```
>>> e=EERAM.EERAM()
```

hexdump, memset
```
>>> e.hexdump(0,64)
0x0000  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
0x0010  48 49 21 00 4f 20 57 4f  52 4c 44 21 00 00 00 00  |HI!.O WORLD!....|
0x0020  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
0x0030  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
>>> e.memset(0,0,32)
True
>>> e.hexdump(0,64)
0x0000  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
0x0010  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
0x0020  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
0x0030  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
```

read various CONTROL REGISTER bits
```
>>> e.readEVENT()
False
>>> e.readAM()
True
```

execute software store command
```
>>> e.eepromRecall()
True
>>> e.hexdump(0,64)
0x0000  41 42 45 43 45 44 41 52  49 4a 41 00 00 00 00 00  |ABECEDARIJA.....|
0x0010  48 49 21 00 4f 20 57 4f  52 4c 44 21 00 00 00 00  |HI!.O WORLD!....|
0x0020  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
0x0030  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
```

read/write null terminated strings
```
>>> e.readstring(0x0000)
'ABECEDARIJA'
>>> e.readstring(0x0010)
'HI!'
>>> e.readstring(0x0014)
'O WORLD!'
>>> e.memset(0,0xff,32)
True
>>> e.hexdump(0,64)
0x0000  ff ff ff ff ff ff ff ff  ff ff ff ff ff ff ff ff  |................|
0x0010  ff ff ff ff ff ff ff ff  ff ff ff ff ff ff ff ff  |................|
0x0020  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
0x0030  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
>>> e.readconfig()
130
>>> bytes([e.readconfig()])
b'\x82'
>>> e.writestring(0x10, "HELLO WORLD!")
True
>>> e.readstring(0x10)
'HELLO WORLD!'
>>> e.readstring(0x15)
' WORLD!'
-
>>> e.readstring(0)
'ÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿHELLO WORLD!'
>>>
>>>
```

read chunk of bytes and possibly convert it to string
```
>>> e.readchunk(0x00,32)
[255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 72, 69, 76, 76, 79, 32, 87, 79, 82, 76, 68, 33, 0, 255, 255, 255]
>>> e.toString(e.readchunk(0x00,32))
'ÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿHELLO WORLD!\x00ÿÿÿ'
```

manipulate with single byte
>>> e.hexdump(0,16)
0x0000  ff ff ff ff ff ff ff ff  ff ff ff ff ff ff ff ff  |................|
>>> e.readbyte(0)
255
>>> e.writebyte(0,0)
True
>>> e.readbyte(0)
0
>>> e.hexdump(0,16)
0x0000  00 ff ff ff ff ff ff ff  ff ff ff ff ff ff ff ff  |................|
>>>
