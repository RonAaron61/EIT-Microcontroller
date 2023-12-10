from machine import Pin, SoftI2C, SoftSPI
from time import sleep
from ad9833 import *
from ADS1115 import *


class AD9833_get:
    def __init__(self, freq,  sspin, mode=MODE_SINE, phase=0):
        self.freq = freq
        self.mode = mode
        self.phase = phase
        self.sspin = sspin

        self.spi = SoftSPI(baudrate=100000, polarity=1, phase=0, sck=Pin(36), mosi=Pin(35), miso=Pin(37))
        self.spi.init(baudrate=200000) # set the baudrate
        self.ssel = Pin(self.sspin, Pin.OUT, value=1) # use /ss

        self.gen = AD9833(self.spi, self.ssel)

        # Suspend Output
        self.gen.reset = True

        self.gen.select_register(0)
        self.gen.mode = self.mode
        self.gen.freq = self.freq
        self.gen.phase = self.phase

        # Activate output on Freq0
        self.gen.select_register(0)

    """def initialize(self):
        self.spi = SoftSPI(baudrate=100000, polarity=1, phase=0, sck=Pin(36), mosi=Pin(35), miso=Pin(37))
        self.spi.init(baudrate=200000) # set the baudrate
        self.ssel = Pin(self.sspin, Pin.OUT, value=1) # use /ss

        self.gen = AD9833(self.spi, self.ssel)

        # Suspend Output
        self.gen.reset = True

        self.gen.select_register(0)
        self.gen.mode = self.mode
        self.gen.freq = self.freq
        self.gen.phase = self.phase

        # Activate output on Freq0
        self.gen.select_register(0)
    """
    def start(self):
        # Release signal to the output
        self.gen.reset = False
    
    def stop(self):
        self.gen.reset = True


class ADS1115_get:
    def __init__(self, address = 0x48):
        self.ADS1115_ADDRESS = address

        self.i2c = SoftI2C(scl=Pin(9), sda=Pin(8), freq=100000)
        self.i2c.scan()

        self.adc = ADS1115(self.ADS1115_ADDRESS, i2c = self.i2c)
        self.adc.setVoltageRange_mV(ADS1115_RANGE_6144) #Maks 6144 mV tapi jaga dibawahaa Vin sadja biar aman
        self.adc.setConvRate(ADS1115_128_SPS)
        self.adc.setMeasureMode(ADS1115_CONTINUOUS) 

    """def initialize(self):
        self.i2c = SoftI2C(scl=Pin(9), sda=Pin(10), freq=100000)
        self.i2c.scan()

        self.adc = ADS1115(self.ADS1115_ADDRESS, i2c = self.i2c)
        self.adc.setVoltageRange_mV(ADS1115_RANGE_6144) #Maks 6144 mV tapi jaga dibawahaa Vin sadja biar aman
        self.adc.setConvRate(ADS1115_128_SPS)
        self.adc.setMeasureMode(ADS1115_CONTINUOUS) """

    def readChannel(self, channel = ADS1115_COMP_0_GND, range=ADS1115_RANGE_6144):
        self.channel = channel
        self.adc.setVoltageRange_mV(range)
        self.adc.setCompareChannels(self.channel)
        self.voltage = self.adc.getResult_V()
        return self.voltage


class get_Data:
    def __init__(self, n_elec = 16):
        self.n_elec = n_elec

        #<- def initialize(self):
        #MUX 1
        self.p1 = Pin(1, Pin.OUT)
        self.p2 = Pin(2, Pin.OUT)
        self.p3 = Pin(3, Pin.OUT)
        self.p4 = Pin(4, Pin.OUT)

        #MUX 2
        self.p5 = Pin(5, Pin.OUT)
        self.p6 = Pin(6, Pin.OUT)
        self.p7 = Pin(7, Pin.OUT)
        self.p8 = Pin(10, Pin.OUT)

        #MUX 3
        self.p9 = Pin(11, Pin.OUT)
        self.p10 = Pin(12, Pin.OUT)
        self.p11 = Pin(13, Pin.OUT)
        self.p12 = Pin(14, Pin.OUT)

        #MUX 4
        self.p13 = Pin(16, Pin.OUT)
        self.p14 = Pin(17, Pin.OUT)
        self.p15 = Pin(18, Pin.OUT)
        self.p16 = Pin(21, Pin.OUT)

        #LED
        self.LED1 = Pin(39, Pin.OUT)
        self.LED2 = Pin(40, Pin.OUT)
        self.LED_BuIn = Pin(15, Pin.OUT)

        self.mux = [[0,0,0,0], [0,0,0,1], [0,0,1,0], [0,0,1,1], [0,1,0,0], [0,1,0,1], [0,1,1,0], [0,1,1,1], 
        [1,0,0,0], [1,0,0,1], [1,0,1,0], [1,0,1,1], [1,1,0,0], [1,1,0,1], [1,1,1,0], [1,1,1,1]]

        try:
            self.ads1115 = ADS1115_get(address=0x48)
            #self.ads1115.initialize()
        except:
            print("_Stat-ADS1115 error")
        else:
            print("_Stat-ADS1115 good")


    def start(self):
        self.value = []    #Store Data

        sleep(1)
      
        self.LED1.value(1)  #Data get on

        for i in range(self.n_elec):
            self.a = i+1
            if (self.a > self.n_elec-1):
                self.a -= self.n_elec

            self.p1.value(self.mux[i][0])
            self.p2.value(self.mux[i][1])
            self.p3.value(self.mux[i][2])
            self.p4.value(self.mux[i][3])

            self.p5.value(self.mux[self.a][0])
            self.p6.value(self.mux[self.a][1])
            self.p7.value(self.mux[self.a][2])
            self.p8.value(self.mux[self.a][3])

            for j in range(self.n_elec):
                self.b = j+1
                if (self.b > self.n_elec-1):
                    self.b -= self.n_elec

                if j == i or j == self.a or self.b == i:    #PyEIT hanya menerima 208 data saja
                    continue

                self.p9.value(self.mux[j][0])
                self.p10.value(self.mux[j][1])
                self.p11.value(self.mux[j][2])
                self.p12.value(self.mux[j][3])


                self.p13.value(self.mux[self.b][0])
                self.p14.value(self.mux[self.b][1])
                self.p15.value(self.mux[self.b][2])
                self.p16.value(self.mux[self.b][3])

                self.LED_BuIn.value(self.mux[j][3]) #LED kedip selama pengambilan data

                sleep(0.5)

                """self.val = self.ads1115.readChannel(channel=ADS1115_COMP_0_GND)

                #If Volt is lower than 512 mV use 8x Gain 
                if self.val < 0.512:
                    self.value.append(self.ads1115.readChannel(channel=ADS1115_COMP_0_GND, range=ADS1115_RANGE_0512))
                    
                elif self.val > 0.480:
                    self.value.append(self.ads1115.readChannel(channel=ADS1115_COMP_0_GND, range=ADS1115_RANGE_6144))"""
                    
                self.value.append(self.ads1115.readChannel(channel=ADS1115_COMP_0_GND,  range=ADS1115_RANGE_6144))

        self.LED1.value(0)        
        return self.value

    def tester(self):
        """try:
            self.ads1115 = ADS1115_get(address=0x48)
            #self.ads1115.initialize()
        except:
            print("ADS1115 error")"""

        self.a, self.b, self.c, self.d = 0,1,2,3

        self.p1.value(self.mux[self.a][0])
        self.p2.value(self.mux[self.a][1])
        self.p3.value(self.mux[self.a][2])
        self.p4.value(self.mux[self.a][3])

        self.p5.value(self.mux[self.b][0])
        self.p6.value(self.mux[self.b][1])
        self.p7.value(self.mux[self.b][2])
        self.p8.value(self.mux[self.b][3])

        self.p9.value(self.mux[self.c][0])
        self.p10.value(self.mux[self.c][1])
        self.p11.value(self.mux[self.c][2])
        self.p12.value(self.mux[self.c][3])

        self.p13.value(self.mux[self.d][0])
        self.p14.value(self.mux[self.d][1])
        self.p15.value(self.mux[self.d][2])
        self.p16.value(self.mux[self.d][3])

        return self.ads1115.readChannel(channel=ADS1115_COMP_0_GND)


if __name__ == '__main__':
    try:
        ad9833 = AD9833_get(freq = 10000, mode=MODE_SINE, phase=0, sspin=15)
    except:
        print("_Stat-AD9833 Error")
    else:
        print("_Stat-AD9833 Good")

    ad9833.start()

    Get_data = get_Data(n_elec= 16)
    #get_data.initialize()
      
    sleep(1)
    data = Get_data.start()
    print(data)
    sleep(1)

    ad9833.stop()