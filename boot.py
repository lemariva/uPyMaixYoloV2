from fpioa_manager import *
import os, Maix, lcd, image
from Maix import FPIOA, GPIO

import sensor,image,lcd
import KPU as kpu
import network
import socket
from machine import UART

# wlan access
ssid_ = ""
wpa2_pass = ""

fm.register(board_info.WIFI_RX, fm.fpioa.UART2_TX)
fm.register(board_info.WIFI_TX, fm.fpioa.UART2_RX)
uart = UART(UART.UART2,115200,timeout=1000, read_buf_len=4096)
nic=network.ESP8285(uart)
nic.connect(ssid_,wpa2_pass)

nic.ifconfig()
nic.isconnected()

def http_get(url):
    _, _, host, path = url.split('/', 3)
    addr = socket.getaddrinfo(host, 80)[0][-1]
    s = socket.socket()
    s.connect(addr)
    s.send(bytes('GET /%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (path, host), 'utf8'))
    s.close()

## Sensor
lcd.init()
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.set_windowing((224, 224))
sensor.set_vflip(0)
sensor.run(1)
classes = ["brio"]
task = kpu.load(0x300000)
anchor = (0.57273, 0.677385, 1.87446, 2.06253, 3.33843, 5.47434, 7.88282, 3.52778, 9.77052, 9.16828)
a = kpu.init_yolo2(task, 0.3, 0.5, 5, anchor)

while(True):
    img = sensor.snapshot()
    code = kpu.run_yolo2(task, img)
    if code:
        for i in code:
            a=img.draw_rectangle(i.rect(),color = (0, 255, 0))
            a = img.draw_string(i.x(),i.y(), classes[i.classid()], color=(255,0,0), scale=3)
            #http_get('http://192.168.178.29/train/1')
        a = lcd.display(img)
    else:
        a = lcd.display(img)
a = kpu.deinit(task)