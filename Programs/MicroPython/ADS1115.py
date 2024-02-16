#https://github.com/wollewald/ADS1115_mpy/tree/main

#!/usr/bin/python
from time import sleep_ms
__ADS1115_CONV_REG      = 0x00     #Conversion Register
__ADS1115_CONFIG_REG    = 0x01     #Configuration Register
__ADS1115_LO_THRESH_REG = 0x02     #Low Threshold Register
__ADS1115_HI_THRESH_REG = 0x03     #High Threshold Register

__ADS1115_DEFAULT_ADDR  = 0x48
__ADS1115_REG_RESET_VAL = 0x8583
__ADS1115_REG_FACTOR    = 0x7FFF

__ADS1115_BUSY          = 0x0000
__ADS1115_START_ISREADY = 0x8000

__ADS1115_COMP_INC = 0x1000

ADS1115_RANGE_6144 = 6144
ADS1115_RANGE_4096 = 4096
ADS1115_RANGE_2048 = 2048
ADS1115_RANGE_1024 = 1024
ADS1115_RANGE_512  = 512
ADS1115_RANGE_256  = 256

ADS1115_ASSERT_AFTER_1 = 0x0000
ADS1115_ASSERT_AFTER_2 = 0x0001
ADS1115_ASSERT_AFTER_4 = 0x0002
ADS1115_DISABLE_ALERT  = 0x0003

ADS1115_LATCH_DISABLED = 0x0000
ADS1115_LATCH_ENABLED  = 0x0004

ADS1115_ACT_LOW  = 0x0000
ADS1115_ACT_HIGH = 0x0008

ADS1115_MAX_LIMIT = 0x0000
ADS1115_WINDOW    = 0x0010

ADS1115_8_SPS   = 0x0000
ADS1115_16_SPS  = 0x0020
ADS1115_32_SPS  = 0x0040
ADS1115_64_SPS  = 0x0060
ADS1115_128_SPS = 0x0080
ADS1115_250_SPS = 0x00A0
ADS1115_475_SPS = 0x00C0
ADS1115_860_SPS = 0x00E0

ADS1115_RANGE_6144  = 0x0000
ADS1115_RANGE_4096  = 0x0200
ADS1115_RANGE_2048  = 0x0400
ADS1115_RANGE_1024  = 0x0600
ADS1115_RANGE_0512  = 0x0800
ADS1115_RANGE_0256  = 0x0A00

ADS1115_COMP_0_1   = 0x0000
ADS1115_COMP_0_3   = 0x1000
ADS1115_COMP_1_3   = 0x2000
ADS1115_COMP_2_3   = 0x3000
ADS1115_COMP_0_GND = 0x4000
ADS1115_COMP_1_GND = 0x5000
ADS1115_COMP_2_GND = 0x6000
ADS1115_COMP_3_GND = 0x7000

ADS1115_CONTINUOUS = 0x0000 
ADS1115_SINGLE     = 0x0100


class ADS1115(object):
    __autoRangeMode = False
    __voltageRange = 2048
    __measureMode = ADS1115_SINGLE
    
    def __init__(self, address = __ADS1115_DEFAULT_ADDR, i2c = None):
        self.__address = address
        if i2c is None:
            try:
                i2c = I2C(0)
            except:
                i2c = I2C()
        self.__i2c = i2c
        try:
            self.reset()
        except:
            raise ValueError("Can't connect to the ADS1115. Check wiring, address, etc.")
        
        self.setVoltageRange_mV(ADS1115_RANGE_2048)
        self.__writeADS1115(__ADS1115_LO_THRESH_REG, 0x8000)
        self.__writeADS1115(__ADS1115_HI_THRESH_REG, 0x7FFF)
        self.__measureMode = ADS1115_SINGLE
        self.__autoRangeMode = False
        
    def setAlertPinMode(self, mode):
        currentConfReg = self.__getConfReg()
        currentConfReg &= ~(0x8003)    
        currentConfReg |= mode
        self.__setConfReg(currentConfReg)

    def setAlertLatch(self, latch):
        currentConfReg = self.__getConfReg()
        currentConfReg &= ~(0x8004)    
        currentConfReg |= latch
        self.__setConfReg(currentConfReg)
        
    def setAlertPol(self, polarity):
        currentConfReg = self.__getConfReg()
        currentConfReg &= ~(0x8008)    
        currentConfReg |= polarity
        self.__setConfReg(currentConfReg)

    def setAlertModeAndLimit_V(self, mode, hiThres, loThres):
        currentConfReg = self.__getConfReg()
        currentConfReg &= ~(0x8010)    
        currentConfReg |= mode
        self.__setConfReg(currentConfReg)
        alertLimit = self.__calcLimit(hiThres)
        self.__writeADS1115(__ADS1115_HI_THRESH_REG, alertLimit)
        alertLimit = self.__calcLimit(loThres)
        self.__writeADS1115(__ADS1115_LO_THRESH_REG, alertLimit)
        
    def __calcLimit(self, rawLimit):
        limit = int((rawLimit * __ADS1115_REG_FACTOR / self.__voltageRange) * 1000)
        if limit > 32767:                       
            limit -= 65536
        return limit
        
    def reset(self):
        return self.__setConfReg(__ADS1115_REG_RESET_VAL)
        
    def setVoltageRange_mV(self, newRange):
        currentVoltageRange = self.__voltageRange
        currentConfReg = self.__getConfReg()
        currentRange = (currentConfReg >> 9) & 7
        currentAlertPinMode = currentConfReg & 3
        
        self.setMeasureMode(ADS1115_SINGLE)
       
        if newRange == ADS1115_RANGE_6144:
            self.__voltageRange = 6144;
        elif newRange == ADS1115_RANGE_4096:
             self.__voltageRange = 4096;
        elif newRange == ADS1115_RANGE_2048:
            self.__voltageRange = 2048;
        elif newRange == ADS1115_RANGE_1024:
            self.__voltageRange = 1024;
        elif newRange == ADS1115_RANGE_0512:
            self.__voltageRange = 512;
        elif newRange == ADS1115_RANGE_0256:
            self.__voltageRange = 256;
 
        if (currentRange != newRange) and (currentAlertPinMode != ADS1115_DISABLE_ALERT):
            alertLimit = self.__readADS1115(__ADS1115_HI_THRESH_REG)
            alertLimit = alertLimit * (currentVoltageRange / self.__voltageRange)
            self.__writeADS1115(__ADS1115_HI_THRESH_REG, alertLimit)
            alertLimit = self.__readADS1115(__ADS1115_LO_THRESH_REG)
            alertLimit = alertLimit * (currentVoltageRange / self.__voltageRange)
            self.__writeADS1115(__ADS1115_LO_THRESH_REG, alertLimit)   
     
        currentConfReg &= ~(0x8E00)    
        currentConfReg |= newRange
        self.__setConfReg(currentConfReg)
        rate = self.__getConvRate()
        self.__delayAccToRate(rate)
        
    def setAutoRange(self):
        currentConfReg = self.__getConfReg()
        self.setVoltageRange_mV(ADS1115_RANGE_6144)
        
        if self.__measureMode == ADS1115_SINGLE:
            self.setMeasureMode(ADS1115_CONTINUOUS)
            convRate = self.__getConvRate()
            self.__delayAccToRate(convRate) 
        
        rawResult = abs(self.__getConvReg())        
        optRange = ADS1115_RANGE_6144
        
        if rawResult < 1093:
            optRange = ADS1115_RANGE_0256
        elif rawResult < 2185:
            optRange = ADS1115_RANGE_0512
        elif rawResult < 4370:
            optRange = ADS1115_RANGE_1024
        elif rawResult < 8738:
            optRange = ADS1115_RANGE_2048
        elif rawResult < 17476:
            optRange = ADS1115_RANGE_4096
            
        self.__setConfReg(currentConfReg)
        self.setVoltageRange_mV(optRange)
        
    def setPermanentAutoRangeMode(self, autoMode):
        if autoMode:
            self.__autoRangeMode = True
        else:
            self.__autoRangeMode = False
                   
    def setMeasureMode(self, mMode):
        currentConfReg = self.__getConfReg()
        self.__measureMode = mMode
        currentConfReg &= ~(0x8100)    
        currentConfReg |= mMode
        self.__setConfReg(currentConfReg)
        
    def setCompareChannels(self, compChannels):
        currentConfReg = self.__getConfReg()
        currentConfReg &= ~(0xF000)    
        currentConfReg |= compChannels
        self.__setConfReg(currentConfReg)
        
        if not (currentConfReg & 0x0100):  # if not single shot mode
            convRate = self.__getConvRate()
            for i in range(2):
                self.__delayAccToRate(convRate)
            
    def setSingleChannel(self, channel):
        if channel >= 4:
            return
        self.setCompareChannels((ADS1115_COMP_0_GND + ADS1115_COMP_INC) * channel)
        
    def isBusy(self):
        currentConfReg = self.__getConfReg()
        return not((currentConfReg>>15) & 1)
    
    def startSingleMeasurement(self):
        currentConfReg = self.__getConfReg()
        currentConfReg |= (1 << 15)
        self.__setConfReg(currentConfReg)
        
    def getResult_V(self):
        return self.getResult_mV()/1000

    def getResult_mV(self):
        rawResult = self.getRawResult()
        return rawResult * self.__voltageRange / __ADS1115_REG_FACTOR

    def getRawResult(self):
        rawResult = self.__getConvReg()
                
        if self.__autoRangeMode:
            if (abs(rawResult) > 26214) and (self.__voltageRange != 6144): # 80%
                self.setAutoRange()
                rawResult = self.__getConvReg()
            elif (abs(rawResult) < 9800) and (self.__voltageRange != 256):  # 30%
                self.setAutoRange()
                rawResult = self.__getConvReg()
                
        return rawResult
    
    def __getConvReg(self):
        rawResult = self.__readADS1115(__ADS1115_CONV_REG)
        if rawResult > 32767:
            rawResult -= 65536
        return rawResult
    
    def getResultWithRange(self, minLimit, maxLimit):
        rawResult = self.getRawResult()
        result = rawResult * (maxLimit - minLimit) / 65536
        return result

    def getResultWithRangeAndMaxVolt(self, minLimit, maxLimit, maxMillivolt):
        result = self.getResultWithRange(minLimit, maxLimit)
        result = result * self.__voltageRange / maxMillivolt
        return result

    def getVoltageRange_mV(self):
        return self.__voltageRange

    def setAlertPinToConversionReady(self):
        self.__writeADS1115(__ADS1115_LO_THRESH_REG, (0<<15))
        self.__writeADS1115(__ADS1115_HI_THRESH_REG, (1<<15))

    def clearAlert(self):
        self.__readADS1115(__ADS1115_CONV_REG)    
    
    def __setConfReg(self, regVal):
        self.__writeADS1115(__ADS1115_CONFIG_REG, regVal)
    
    def __getConfReg(self):
        return self.__readADS1115(__ADS1115_CONFIG_REG)
        
    def __getConvRate(self):
        currentConfReg = self.__getConfReg()
        return (currentConfReg & 0xE0)
    
    def setConvRate(self, rate):
        currentConfReg = self.__getConfReg()
        currentConfReg &= ~(0x80E0)
        currentConfReg |= rate
        self.__setConfReg(currentConfReg)
    
    def __delayAccToRate(self, rate):
        if rate == ADS1115_8_SPS:
            sleep_ms(130)
        elif rate == ADS1115_16_SPS:
            sleep_ms(65)
        elif rate == ADS1115_32_SPS:
            sleep_ms(32)
        elif rate == ADS1115_64_SPS:
            sleep_ms(16)
        elif rate == ADS1115_128_SPS:
            sleep_ms(8)
        elif rate == ADS1115_250_SPS:
            sleep_ms(4)
        elif rate == ADS1115_475_SPS:
            sleep_ms(3)
        elif rate == ADS1115_860_SPS:
            sleep_ms(2)
    
    def __writeADS1115(self, reg, val):
        self.__i2c.writeto_mem(self.__address, reg, self.__toBytearray(val))
        
    def __readADS1115(self, reg):
        regVal = self.__i2c.readfrom_mem(self.__address, reg, 2)
        return self.__bytesToInt(regVal)
    
    def __toBytearray(self, intVal):
        return bytearray(intVal.to_bytes(2, 'big'))
    
    def __bytesToInt(self, bytesToConvert):
        intVal = int.from_bytes(bytesToConvert, 'big') # "big" = MSB at beginning
        return intVal
        
        

   