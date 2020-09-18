from smbus2 import SMBus, i2c_msg, SMBusWrapper

class EERAM(object):

    def __init__(self, size=16384, smbusDevice=1, address=0, debug=0):
        self._EERAM_SIZE = int(size / 8)
        self._SMBUS_DEVICE = smbusDevice
        self._DEBUG = debug
        self._EERAM_CONTROL_ADDRESS  = 0x18
        self._EERAM_CONTROL_REGISTER = 0x00
        self._EERAM_SRAM_ADDRESS     = 0x50
        self._EERAM_COMMAND_REGISTER = 0x55
        self._EERAM_EXEC_SW_STORE    = 0b00110011
        self._EERAM_EXEC_SW_RECALL   = 0b11011101
        self._EERAM_EVENT_BIT        = 0b00000001
        self._EERAM_ASE_BIT          = 0b00000010
        self._EERAM_BP0_BIT          = 0b00000100
        self._EERAM_BP1_BIT          = 0b00001000
        self._EERAM_BP2_BIT          = 0b00010000
        self._EERAM_AM_BIT           = 0b10000000
        self._ADDRESS = address

    def size(self):
        '''
        return EERAM size
        '''
        return self._EERAM_SIZE

    def readconfig(self):
        '''
        Read from CONTROL register (0x18)
        '''
        write = i2c_msg.write(self._EERAM_CONTROL_ADDRESS | ((self._ADDRESS & 0x03) << 1), [0])
        read = i2c_msg.read(self._EERAM_CONTROL_ADDRESS, 1)
        with SMBusWrapper(self._SMBUS_DEVICE) as bus:
            bus.i2c_rdwr(write, read)
            return int.from_bytes(read.buf[0], 'big')

    def writeconfig(self, value):
        '''
        Write value to CONTROL register
        '''
        write = i2c_msg.write(self._EERAM_CONTROL_ADDRESS | ((self._ADDRESS & 0x03) << 1), [self._EERAM_CONTROL_REGISTER, value])
        with SMBusWrapper(self._SMBUS_DEVICE) as bus:
            bus.i2c_rdwr(write)
            return True

    def writecmd(self, value):
        '''
        Write value to COMMAND register
        Note that COMMAND register is write only.
        '''
        write = i2c_msg.write(self._EERAM_CONTROL_ADDRESS | ((self._ADDRESS & 0x03) << 1), [self._EERAM_COMMAND_REGISTER, value])
        with SMBusWrapper(self._SMBUS_DEVICE) as bus:
            bus.i2c_rdwr(write)
            return True


    def eepromRecall(self):
        '''
         Executes a Software Recall command
        '''
        return self.writecmd(self._EERAM_EXEC_SW_RECALL)


    def eepromStore(self):
        '''
        Executes a Software Store command
        '''
        return self.writecmd(self._EERAM_EXEC_SW_STORE)


    def enableASE(self):
        '''
        Enable AUto-Store feature
        '''
        status = self.readconfig()
        return self.writeconfig(status | self._EERAM_ASE_BIT)


    def disableASE(self):
        '''
        Disable AUto-Store feature
        '''
        status = self.readconfig()
        return self.writeconfig(status & ~(self._EERAM_ASE_BIT))


    def readEVENT(self):
        '''
        Returns True if event was detected on HS pin
        '''
        status = self.readconfig()
        return status & self._EERAM_EVENT_BIT > 0


    def readAM(self):
        '''
        Returns True if SRAM array has been modified
        '''
        status = self.readconfig()
        return status & self._EERAM_AM_BIT > 0


    def readbyte(self, address):
        '''
        >>> e.readbyte(0)
        255
        '''
        self._checkOverflow(address)
        HI_addr = address >> 8
        LO_addr = address & 0xff
        self._debug("address={0:02X}{1:02X}".format(HI_addr, LO_addr)),
        write = i2c_msg.write(self._EERAM_SRAM_ADDRESS | ((self._ADDRESS & 0x03) << 1), [HI_addr, LO_addr])
        read = i2c_msg.read(self._EERAM_SRAM_ADDRESS, 1)
        with SMBusWrapper(self._SMBUS_DEVICE) as bus:
            bus.i2c_rdwr(write, read)
            ### return BYTES, INTEGERS, CHARS?
            return ord(read.buf[0])


    def readchunk(self, address, size):
        '''
         >>> e.readchunk(0x00,32)
        [255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 72, 69, 76, 76, 79, 32, 87, 79, 82, 76, 68, 33, 0, 255, 255, 255]
        '''
        chunk = []
        for i in range(0, size):
            chunk.append(self.readbyte(address + i))
        return chunk


    def readstring(self, address):
        '''
        >>> e.readstring(0x10)
        'HELLO WORLD!'
        '''
        terminator = 0
        chunk = []
        for i in range(0, self._EERAM_SIZE):
            byte = self.readbyte(address + i)
            if byte == terminator:
                break
            else:
                chunk.append(byte)
        return self.toString(chunk)


    def writebyte(self, address, value):
        '''
        >>> e.writebyte(0,0)
        True
        '''

        self._checkOverflow(address)
        HI_addr = address >> 8
        LO_addr = address & 0xff
        self._debug("address={0:02X}{1:02X} byte={2:02X}".format(HI_addr, LO_addr, value)),
        write = i2c_msg.write(self._EERAM_SRAM_ADDRESS | ((self._ADDRESS & 0x03) << 1), [HI_addr, LO_addr, value])
        with SMBusWrapper(self._SMBUS_DEVICE) as bus:
            bus.i2c_rdwr(write)
            ### KAJ BI BLO SMISELNO TLE VRACAT?
            return True


    def writestring(self, address, dataz):
        '''
        >>> e.writestring(0x10, "HELLO WORLD!")
        True
        '''
        dataLen = len(dataz)
        terminator = 0
        endAddr = address + dataLen
        self._checkOverflow(endAddr)
        for position in range(0, dataLen):
            self.writebyte(address + position, ord(dataz[position]))
        self.writebyte(address + position + 1, terminator)
        ### KAJ BI BLO SMISELNO TLE VRACAT?
        return True

    def memset(self, address, value, size):
        '''
        >>> e.memset(0,0,32)
        True
        '''
        self._checkOverflow(address + size)
        for position in range(0, size):
            self.writebyte(address + position, value)
        return True



    # def incr(self, address):
    #     '''
    #     TODO
    #     '''
    #     byte = self.readbyte(address)
    #     byte += 1 % 256
    #     self.writebyte(address, byte)




    # def decr(self, address):
    #     '''
    #     TODO
    #     '''
    #     byte = self.readbyte(address)
    #     byte -= 1
    #     if byte == -1:
    #         byte = 255
    #     self.writebyte(address, byte)


    def toString(self, list):
        '''
        >>> e.toString(e.readchunk(0x00,32))
        'ÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿHELLO WORLD!\x00ÿÿÿ'
        '''
        return ''.join([chr(b) for b in list])


    def hexdump(self, start, stop):
        '''
        >>> e.hexdump(0, e.size())
        0x0000  ff ff ff ff ff ff ff ff  ff ff ff ff ff ff ff ff  |................|
        0x0010  48 45 4c 4c 4f 20 57 4f  52 4c 44 21 00 ff ff ff  |HELLO WORLD!....|
        0x0020  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
        ...snip...
        0x07e0  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
        0x07f0  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
        '''
        step=16
        for i in range(start, stop, step):
            b=bytes(self.readchunk(i, step))
            s1 = " ".join([f"{i:02x}" for i in b])
            s1 = s1[0:23] + " " + s1[23:]
            s2 = "".join([chr(i) if 32 <= i <= 127 else "." for i in b])
            print(f"0x{i:04x}  {s1:<48}  |{s2}|")


    def _checkOverflow(self, lastAddr):
        if lastAddr > self._EERAM_SIZE:
            raise ValueError("lastAddr > EERAM_SIZE")


    def _debug(self, message):
        if self._DEBUG:
            print("DEBUG: {0}".format(message))
