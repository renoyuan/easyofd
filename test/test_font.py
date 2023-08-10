
#!/usr/bin/env python
#-*- coding: utf-8 -*-
#PROJECT_NAME: E:\code\pyofdpaerser\test
#CREATE_TIME: 2023-03-28 
#E_MAIL: renoyuan@foxmail.com
#AUTHOR: reno 

from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.ttfonts import pdfmetrics

if __name__ == "__main__":
   pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))