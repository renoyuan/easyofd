#!/usr/bin/env python
#-*- coding: utf-8 -*-
#PROJECT_NAME: /home/reno/idp_ocr/test
#CREATE_TIME: 2023-12-06 
#E_MAIL: renoyuan@foxmail.com
#AUTHOR: reno 
#note:  pdf draw

from reportlab.pdfgen import canvas
def hello(c):
    c.drawString(100,100,"Hello World")
    # c.line(x1,y1,x2,y2)
    c.line(99,99,150,99)
c = canvas.Canvas("hello.pdf")
hello(c)
c.showPage()
c.save()
