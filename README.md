# EIT-Microcontroller
Electrical Impedance Tomography using ESP32 S2 microcontroller with MicroPython

Creating an Electrical Impedance Tomography device using ESP32-S2 as the microcontroller and AD9833 as the function generator

---

## List of Content

- [Abstract](#Absract)
- [Component](#Component)
- [Design](#Design)
- [Programs](#Programs)
- [Result](#Result)

---

## Abstract

Abstract

---

## Component

### Positive to Negative Converter

Positive to Negative Converter


### AD9833

AD9833


### Non-Inverting Amplifier

Non-Inverting Amplifier


### VCCS

VCCS


### ADS1115

ADS1115

### Multi/Demultiplexer

Multi/Demultiplexer


### Electrode

Electroda

---

## Design

Schematic :

<img src="assets/image/Sheet_1.png" align="center"/>
<img src="assets/image/Sheet_2.png" align="center"/>
<img src="assets/image/Sheet_3.png" align="center"/>

PCB Model :

<img src="assets/image/PCB_2D.png" width=700></img>

---

## Programs

The program is divided into 2 parts, for the microcontroller to get the data, and to process the data into an image. For the microcontroller I use Micropython simply because I just want to learn
Micropython, and for the image reconstruction I use the PyEIT library for python.

### Micropython

The IDE I'm using is [Arduino Lab for Micropython](https://labs.arduino.cc/en/labs/micropython)

The Libray for the module that I use:

- AD9833 : [AD9833-mchobby](https://github.com/mchobby/esp8266-upy/tree/master/ad9833)
- ADS1115 : [ADS1115_mpy-wollewald](https://github.com/wollewald/ADS1115_mpy/tree/main)

### PyEIT

[PyEIT Github](https://github.com/eitcom/pyEIT) for more info

PyEIT

---

## Result

Result
