#!/usr/bin/env python
#-*- coding: utf-8 -*-
#PROJECT_NAME: E:\code\easyofd\easyofd\draw
#CREATE_TIME: 2023-08-10 
#E_MAIL: renoyuan@foxmail.com
#AUTHOR: reno 
#NOTE:  绘制pdf
import os
import re
import traceback
import base64
import logging
from PIL import Image as PILImage
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
from reportlab.lib import fonts as reportlab_fonts

from draw.font_tools import FontTool
logger = logging.getLogger("root")

print(reportlab_fonts)
class DrawPDF():
    """
    ofd 解析结果 绘制pdf
    OP ofd 单位转换
    """
    def __init__(self,data,*args, **kwargs):
        assert data,"未输入ofd解析结果"
        self.data = data
        self.author = "renoyuan"
        self.OP = 200/25.4
        self.pdf_uuid_name=self.data[0]["pdf_name"]
        self.pdf_io = BytesIO() 
        self.SupportImgType = ("JPG","IPEG","PNG")
        self.init_font = "宋体"
        self.font_tool = FontTool()
    
    def gen_empty_pdf(self):
        c = canvas.Canvas(self.pdf_io)
        c.setPageSize(A4)
        c.setFont(self.init_font, 20)
        c.drawString(0,210,"ofd 格式错误,不支持解析", mode=1  )
        c.save()
    
    # 单个字符偏移量计算
    def cmp_offset(self,pos,offset,DeltaRule,text,resize=1)->list:
        """
        pos 文本框x|y 坐标
        offset 初始偏移量
        DeltaRule 偏移量规则
        
        """

        char_pos = float(pos if pos else 0 ) + float(offset if offset else 0 )
        pos_list = []
        pos_list.append(char_pos)
        offsets = [i for i in DeltaRule.split(" ")]

        if "g" in   DeltaRule:  
            g_no = None
            for _no, offset_i in enumerate(offsets) :
            
                if offset_i == "g":
                    g_no = _no
                    for j in range(int(offsets[(g_no+1)])):
                        char_pos += float(offsets[(g_no+2)]) 
                        pos_list.append(char_pos)
                    
                elif offset_i != "g" :
                    if g_no == None:
                        char_pos += float(offset_i) * resize
                        pos_list.append(char_pos)
                    elif  (int(_no) > int(g_no+2)) and g_no!=None:
                      
                        char_pos += float(offset_i)  * resize
                        pos_list.append(char_pos)
                    
        elif not DeltaRule:
            pos_list = []
            for i in range(len(text)):
                pos_list.append(char_pos)
        else:
            for i in offsets:
                if not i:
                    char_pos += 0
                else:
                    char_pos += float(i)  * resize
                pos_list.append(char_pos)
                
        return pos_list
        
          
    def draw_pdf(self):
       
        c = canvas.Canvas(self.pdf_io)
        c.setAuthor(self.author)

        for doc_id,doc in enumerate(self.data,start=1)  :
            fonts = doc.get("fonts")
            images = doc.get("images")
            page_size= doc.get("page_size")
            
            # 注册字体
            for font_id,font_v in fonts.items():    
                file_name = font_v.get("FontFile")
                font_b64 = font_v.get("font_b64")
                if font_b64:
                    self.font_tool.register_font(os.path.split(file_name)[1],font_v.get("@FontName"),font_b64)
                       
            for page_id,page in doc.get("page_info").items():     
                text_list = page.get("text_list")
                img_list = page.get("img_list")
              
                c.setPageSize((page_size[2]*self.OP, page_size[3]*self.OP))

                # 写入图片
                for img_d in img_list:
                    image = images.get(img_d["ResourceID"])
                    
                    if image.get("suffix").upper() not in self.SupportImgType:
                        continue
                    
                    imgbyte = base64.b64decode(image.get('b64img'))
                    img = PILImage.open(BytesIO(imgbyte))
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
                    c.drawImage(imgReade,x,y ,w, h, 'auto')

                # 写入文本
                for line_dict in text_list:
                    # 默认整行写入 也可以按字符写入
                    text = line_dict.get("text")
                    font_info = fonts.get(line_dict.get("font"),{})
                    if font_info:
                        font_name = font_info.get("FontName","")
                        # TODO 判断是否通用已有字体 否则匹配相近字体使用
                    else:
                        font_name = self.init_font
                    font=font_name

                    c.setFont(font, line_dict["size"]*self.OP)
                    # 原点在页面的左下角 
                    color = line_dict.get("color",[0,0,0])
                    c.setFillColorRGB(int(color[0])/255,int(color[1])/255, int(color[2])/255)
                    c.setStrokeColorRGB(int(color[0])/255,int(color[1])/255, int(color[2])/255)
                    
                    DeltaX = line_dict.get("DeltaX","")
                    DeltaY = line_dict.get("DeltaY","")
                    X = line_dict.get("X","")
                    Y = line_dict.get("Y","")
                    CTM = line_dict.get("CTM","") # 因为ofd 的傻逼 增加这个字符缩放
                    resizeX =1
                    resizeY =1
                    if CTM :
                        resizeX = float(CTM.split(" ")[0])
                        resizeY = float(CTM.split(" ")[3])
                
                    x_list = self.cmp_offset(line_dict.get("pos")[0],X,DeltaX,text,resizeX)
                    y_list = self.cmp_offset(line_dict.get("pos")[1],Y,DeltaY,text,resizeY)
                    

                    # if line_dict.get("Glyphs_d") and  FontFilePath.get(line_dict["font"])  and font_f not in FONTS:
                    if False: # 对于自定义字体 写入字形 drawPath 性能差暂时作废
                        Glyphs = [int(i) for i in line_dict.get("Glyphs_d").get("Glyphs").split(" ")]
                        for idx,Glyph_id in enumerate(Glyphs):
                            _cahr_x= float(x_list[idx])*self.OP
                            _cahr_y= (float(page_size[3])-(float(y_list[idx])))*self.OP
                            imageFile = draw_Glyph( FontFilePath.get(line_dict["font"]), Glyph_id,text[idx])
                            
                            # font_img_info.append((FontFilePath.get(line_dict["font"]), Glyph_id,text[idx],_cahr_x,_cahr_y,-line_dict["size"]*Op*2,line_dict["size"]*Op*2))
                            c.drawImage(imageFile,_cahr_x,_cahr_y,-line_dict["size"]*self.OP*2,line_dict["size"]*self.OP*2  )
                            
                    else:
                        if len(text) > len(x_list) or len(text) > len(y_list) :
                            text = re.sub("[^\u4e00-\u9fa5]","",text)  
                        try:
                            # 按行写入
                            if y_list[-1]*self.OP > page_size[3]*self.OP or x_list[-1]*self.OP >page_size[2]*self.OP or x_list[-1]<0 or y_list[-1]<0 :
                                x_p = abs(float(X) )*self.OP
                                y_p = abs(float(page_size[3])-(float(Y)))*self.OP
                                c.drawString( x_p,  y_p, text, mode=0) # mode=3 文字不可见 0可見
                                X = line_dict.get("X","")
                                Y = line_dict.get("Y","")

                            # 按字符写入
                            else:
                                for cahr_id, _cahr_ in enumerate(text) :
                                    _cahr_x= float(x_list[cahr_id])*self.OP
                                    _cahr_y= (float(page_size[3])-(float(y_list[cahr_id])))*self.OP                                        
                                    c.drawString( _cahr_x,  _cahr_y, _cahr_, mode=0) # mode=3 文字不可见 0可見
                                
                      
                            
                        except Exception as e:
                            logger.error(f"{e}")
                            traceback.print_exc()
            
                if page_id != len(doc.get("page_info"))-1  and doc_id != len(self.data): 
                    c.showPage()  
        c.save()
        
    def __call__(self):
        try:
            self.draw_pdf()
            pdfbytes  = self.pdf_io.getvalue()
        except Exception as e:
            logger.error(f"{e}")
            logger.error(f"ofd解析失败")
            traceback.print_exc()
            self.gen_empty_pdf()
            pdfbytes  = self.pdf_io.getvalue()
        return pdfbytes
