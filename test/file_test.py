#!/usr/bin/env python
#-*- coding: utf-8 -*-
#PROJECT_NAME: F:\code\easyofd\test
#CREATE_TIME: 2023-10-18 
#E_MAIL: renoyuan@foxmail.com
#AUTHOR: reno 
#note:  
from PIL import Image
import io
import base64
import numpy as np
text ="MIIBBgYKKoEcz1UGAQQCAqCB9zCB9AIBATEOMAwGCCqBHM9VAYMRBQAwDAYKKoEcz1UGAQQCATGB0DCBzQIBATBjMFgxCzAJBgNVBAYTAkNOMRswGQYDVQQLDBLlm73lrrbnqI7liqHmgLvlsYAxLDAqBgNVBAMMI+eojuWKoeeUteWtkOivgeS5pueuoeeQhuS4reW/gyhTTTIpAgcwAwAACMj3MAwGCCqBHM9VAYMRBQAwDAYIKoEcz1UBg3UFAARHMEUCIB7MZfURfTmw49WUAbrC+YohpCyEofFosJGr3Jew4E/2AiEAwdbxk3GIkvD7jJJ1oX87aRZgwWSOI96C2e5WpHvoabg="
file_p = r"F:\code\easyofd\test\增值税电子专票5\Doc_0\Signs\Sign_0\SignedValue.dat"
# 读取.dat文件中的二进制数据
# with open(file_p, 'rb') as file:
#     binary_data = file.read()

# 假设数据是PNG格式的，解码为图像
# image = Image.open(io.BytesIO(binary_data))

# 显示图像（可选）
# image.show()

# 将解码后的数据保存为图像文件
# image.save('output_image.png')

with open("text.png", 'wb') as file:
    file.write(base64.b64decode(text))
