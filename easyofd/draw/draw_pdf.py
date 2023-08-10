#!/usr/bin/env python
#-*- coding: utf-8 -*-
#PROJECT_NAME: E:\code\easyofd\easyofd\draw
#CREATE_TIME: 2023-08-10 
#E_MAIL: renoyuan@foxmail.com
#AUTHOR: reno 
#NOTE:  绘制pdf
import traceback
import base64
import logging
import PIL
from io import BytesIO

from reportlab import platypus
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import mm,inch
from reportlab.platypus import SimpleDocTemplate, Image
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase.ttfonts import TTFont




class DrawPDF():
    """
    ofd 解析结果 绘制pdf
    OP ofd 单位转换
    """
    def __init__(self,data,*args, **kwargs):
        assert data,"未输入ofd解析结果"
        self.data = data
        self.OP = 200/25.4
        self.name = self.data[0]["pdf_name"]
    
    def gen_empty_pdf(self,json_list=None, gen_pdf_path="",need_image=False):
        c = canvas.Canvas(gen_pdf_path)
        c.setPageSize(A4)
        c.setFont('宋体', 20)
        c.drawString(0,210,"ofd 格式错误,不支持解析", mode=1  )
        c.save()
        
    def draw_pdf(self):
       
        c = canvas.Canvas(self.pdf_name)
     
        c.setAuthor("renoyuan")

        for doc_id,doc in enumerate(self.data)  :
            
            for page in doc.get("page_info"):        
                page_size= page.get("page_size")
                fonts = page.get("fonts")
                images = page.get("images")
                line_dict = page.get("line_dict")
                FontFilePath = page.get("FontFilePath")
                c.setPageSize((page_size[2]*self.OP, page_size[3]*self.OP))

                # 写入图片
                for image in images:
                    imgbyte = base64.b64decode(image.get('b64img'))
                    img = Image.open(BytesIO(imgbyte))
                    imgReade  = ImageReader(img)
                    CTM = image.get('CTM')
                    x_offset = 0
                    y_offset = 0
          
                    wrap_pos = image.get("wrap_pos")
                    
                        
                    x = (image.get('pos')[0]+x_offset)*self.OP
                    y = (page_size[3] - (image.get('pos')[1]+y_offset))*self.OP
                    if wrap_pos:
                        x = x+(wrap_pos[0]*self.OP)
                        y = y-(wrap_pos[1]*self.OP)
                
                        
                    
                    w =   image.get('pos')[2]*self.OP
                    h =  -image.get('pos')[3]*self.OP
                   
                    c.drawImage( imgReade,x,y ,w, h, 'auto')
                # c.drawInlineImage(img_path, 0, 0, width, height)

                # 循环写文本到图片
                # print(json_list)
                try:
                    # font_img_info = [] # 图片任务
                    for line_dict in page.get("page_info"):
                        # print("line_dict",line_dict)
                        # print(FONTS)
                        # "FontName":i.get("@FontName"),
                                                #    "FamilyName":i.get("@FamilyName"),     
                        # print(fonts.get(line_dict.get("font"),{}).get("FontName"),)
                        # print(fonts.get(line_dict.get("font"),{}).get("FamilyName"),)
                        font = fonts.get(line_dict.get("font"),{}).get("FontName",'STSong-Light')
                        font = self.juge_font(font)
                        # font =  font if font in FONTS else fonts.get(line_dict.get("font"),{}).get("FamilyName",'STSong-Light')
                        font_f = font
                        # if font == "BWSimKai-KaiTi-0":
                        #     print(font)
                        #     print(line_dict.get("text"))
                        # if font not in FONTS:
                        #     # print("font----------------：",font)
                        #     font = '宋体'
                        # print(font)
                        # print("font",font)
                        c.setFont(font, line_dict["size"]*Op)
                        # 原点在页面的左下角 
                        # 原点在页面的左下角
                        color = line_dict.get("color",[0,0,0])
                        # print("color",color)
                        c.setFillColorRGB(int(color[0])/255,int(color[1])/255, int(color[2])/255)
                        c.setStrokeColorRGB(int(color[0])/255,int(color[1])/255, int(color[2])/255)
                        # 按每个字写入精确到每个字的坐标
                        text = line_dict.get("text")
                        # print(text)
                        DeltaX = line_dict.get("DeltaX","")
                        DeltaY = line_dict.get("DeltaY","")
                        X = line_dict.get("X","")
                        Y = line_dict.get("Y","")
                        CTM = line_dict.get("CTM","") # 因为ofd 的傻逼 增加这个字符缩放
                        resizeX =1
                        resizeY =1
                        if CTM :
                            # print(CTM)
                            resizeX = float(CTM.split(" ")[0])
                            resizeY = float(CTM.split(" ")[3])
                    
                        x_list = self.cmp_offset(line_dict.get("pos")[0],X,DeltaX,text,resizeX)
                        y_list = self.cmp_offset(line_dict.get("pos")[1],Y,DeltaY,text,resizeY)
                        
                        # 对于自定义字体 写入字形 drawPath
                        
                        if line_dict.get("Glyphs_d") and  FontFilePath.get(line_dict["font"])  and font_f not in FONTS:
                            # continue
                            # print(line_dict.get("Glyphs_d"))
                            
                            # d_obj = []
                            # try:
                            Glyphs = [int(i) for i in line_dict.get("Glyphs_d").get("Glyphs").split(" ")]
                            for idx,Glyph_id in enumerate(Glyphs):
                                # print(FontFilePath.get(line_dict["font"]))
                                _cahr_x= float(x_list[idx])*Op
                                _cahr_y= (float(page_size[3])-(float(y_list[idx])))*Op
                                imageFile = draw_Glyph( FontFilePath.get(line_dict["font"]), Glyph_id,text[idx])
                                # print("size",line_dict["size"]*Op*2)
                                
                                # font_img_info.append((FontFilePath.get(line_dict["font"]), Glyph_id,text[idx],_cahr_x,_cahr_y,-line_dict["size"]*Op*2,line_dict["size"]*Op*2))
                                c.drawImage(imageFile,_cahr_x,_cahr_y,-line_dict["size"]*Op*2,line_dict["size"]*Op*2  )
                            
                            # except Exception as e:
                            #     print(e)
                                
                        else:
                            
                            if len(text) > len(x_list) or len(text) > len(y_list) :
                                text = re.sub("[^\u4e00-\u9fa5]","",text)  
                            try:
                                # 按行写入
                                if y_list[-1]*Op > page_size[3]*Op or x_list[-1]*Op >page_size[2]*Op or x_list[-1]<0 or y_list[-1]<0:
                                    # c.drawString( float(line_dict.get("pos")[0])*Op,  (float(page_size[3])-(float(line_dict.get("pos")[1])))*Op, text, mode=0) # mode=3 文字不可见 0可見
                                    # x_p = abs(float(line_dict.get("pos")[0])+float(X) )*Op
                                    x_p = abs(float(X) )*Op
                                    # y_p = abs(float(page_size[3])-(float(line_dict.get("pos")[1])+float(Y)))*Op
                                    y_p = abs(float(page_size[3])-(float(Y)))*Op
                                    c.drawString( x_p,  y_p, text, mode=0) # mode=3 文字不可见 0可見
                                    X = line_dict.get("X","")
                                    Y = line_dict.get("Y","")
                                    # print(x_p,  y_p, text)
                                # 按字符写入
                                else:
                                    for cahr_id, _cahr_ in enumerate(text) :
                                        _cahr_x= float(x_list[cahr_id])*Op
                                        _cahr_y= (float(page_size[3])-(float(y_list[cahr_id])))*Op
                                        # print(page_size)
                                        # print((page_size[2]*Op,page_size[3]*Op))
                                        # print(_cahr_x,  _cahr_y, _cahr_)
                                        
                                        c.drawString( _cahr_x,  _cahr_y, _cahr_, mode=0) # mode=3 文字不可见 0可見
                                    # print(text)
                                # 如果字符坐标异常超过按行写入
                                
                            except Exception as e:
                                # print("len(text)",len(text))
                                # print("cahr_id",cahr_id)
                                # print("x_list",x_list)
                                # print("text",text)
                                traceback.print_exc()
                                print(e)
                                
                   
                    # 按行写入
                    #c.drawString( float(line_dict.get("pos")[0])*Op,  (float(page_size[3])-(float(line_dict.get("pos")[1])))*Op, text, mode=0) # mode=3 文字不可见 0可見
                   

               
                
               
                except Exception as e:
                    traceback.print_exc()
                    logger.info("genpdf2 error")
                if idx+1 <= len(json_list):
                    c.showPage()  
            c.save()
    def __call__(self):
        pass