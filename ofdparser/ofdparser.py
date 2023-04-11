#!/usr/bin/env python
#-*- coding: utf-8 -*-
#PROJECT_NAME: /home/azx_fp/forecaest_new/app_ocr/utils
#CREATE_TIME: 2023-02-23 
#E_MAIL: renoyuan@foxmail.com
#AUTHOR: reno 

# encoding: utf-8
from __future__ import print_function, division, absolute_import
from fontTools.ttLib import TTFont as ttLib_TTFont
from fontTools.pens.basePen import BasePen
from reportlab.graphics.shapes import Path
from reportlab.lib import colors
from reportlab.graphics import renderPM
from reportlab.graphics.shapes import Group, Drawing, scale

import time
import re
import json
import base64
import zipfile
import os
import shutil
import logging
from io import BytesIO,StringIO 
import string
from uuid import uuid1
import random
import traceback
import logging
import numpy as np
import tempfile
import xmltodict
from reportlab import platypus
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import mm,inch
from reportlab.platypus import SimpleDocTemplate, Image
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase.ttfonts import TTFont
from concurrent.futures import ThreadPoolExecutor
import threading
import multiprocessing
import PIL



try:
    import cv2
except :
    logging.warning("缺少cv2 若需要处理图片文件必不可少")
    

FONTS = ['宋体',"SWPMEH+SimSun",'SimSun','KaiTi','楷体',"SWLCQE+KaiTi",'Courier New','STSong-Light',"CourierNew","SWANVV+CourierNewPSMT","CourierNewPSMT","BWSimKai","hei","黑体","SimHei","SWDKON+SimSun","SWCRMF+CourierNewPSMT","SWHGME+KaiTi"]
pdfmetrics.registerFont(TTFont('宋体', 'simsun.ttc'))
pdfmetrics.registerFont(TTFont('SWPMEH+SimSun', 'simsun.ttc'))
pdfmetrics.registerFont(TTFont('SimSun', 'simsun.ttc'))
pdfmetrics.registerFont(TTFont('SWDKON+SimSun', 'simsun.ttc'))
pdfmetrics.registerFont(TTFont('KaiTi', 'simkai.ttf'))
pdfmetrics.registerFont(TTFont('楷体', 'simkai.ttf'))
pdfmetrics.registerFont(TTFont('SWLCQE+KaiTi', 'simkai.ttf'))
pdfmetrics.registerFont(TTFont('SWHGME+KaiTi', 'simkai.ttf'))
pdfmetrics.registerFont(TTFont('BWSimKai', 'simkai.ttf'))
pdfmetrics.registerFont(TTFont('SWCRMF+CourierNewPSMT', 'COURI.TTF'))
pdfmetrics.registerFont(TTFont('SWANVV+CourierNewPSMT', 'COURI.TTF'))
pdfmetrics.registerFont(TTFont('CourierNew', 'COURI.TTF'))
pdfmetrics.registerFont(TTFont('CourierNewPSMT', 'COURI.TTF'))
pdfmetrics.registerFont(TTFont('Courier New', 'COURI.TTF'))
pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
pdfmetrics.registerFont(TTFont('SimHei', 'simhei.ttf'))
pdfmetrics.registerFont(TTFont('hei', 'simhei.ttf'))
pdfmetrics.registerFont(TTFont('黑体', 'simhei.ttf'))

import copy
logger = logging.getLogger("root")


def _genShortId(length=12):
        """
        :params length: 默认随机生成的uuid长度
        """
        uuid = str(uuid1()).replace('-', '')
        result = ''
        for i in range(0, 8):
            sub = uuid[i * 4: i * 4 + 4]
            x = int(sub, 16)
            uuidChars = tuple(list(string.ascii_letters) + list(range(10)))
            result += str(uuidChars[x % 0x3E])
        return result + ''.join(random.sample(uuid, length - 8))

class ReportLabPen(BasePen):
 
    """A pen for drawing onto a reportlab.graphics.shapes.Path object."""
 
    def __init__(self, glyphSet, path=None):
        BasePen.__init__(self, glyphSet)
        if path is None:
            path = Path()
        self.path = path
 
    def _moveTo(self, p):
        (x,y) = p
        self.path.moveTo(x,y)
 
    def _lineTo(self, p):
        (x,y) = p
        self.path.lineTo(x,y)
 
    def _curveToOne(self, p1, p2, p3):
        (x1,y1) = p1
        (x2,y2) = p2
        (x3,y3) = p3
        self.path.curveTo(x1, y1, x2, y2, x3, y3)
 
    def _closePath(self):
        self.path.closePath()


def draw_Glyph(fontName,index,char_):
    font = ttLib_TTFont(fontName)
    gs = font.getGlyphSet()
    glyphset = font.getGlyphSet()
    # print(dir(gs))
    # font_id = font.getGlyphID(char_)
    char_aa = font.getGlyphOrder()[index]
    # char_aa = 
    # print("aa",aa)
    # print("char_",char_)
    # print("font_id",font_id)
    # glyphNames = font.getGlyphNames()
    # g = gs['cmap'][char_]
    g = gs[char_aa]
    pen = ReportLabPen(gs, Path(fillColor=colors.black, strokeWidth=5))
    g.draw(pen)
    w, h = g.width, g.width
    g = Group(pen.path)
    g.translate(0, 0)
    d = Drawing(w, h)
    d.add(g)
    imageFile = "images"+"/"+str(index)+".png"
    if not os.path.exists(imageFile):
        renderPM.drawToFile(d, imageFile, "png")
    return imageFile
        
def ttfToImage(fontName,imagePath,fmt="png"):
    font = ttLib_TTFont(fontName)
    gs = font.getGlyphSet()
    glyphNames = font.getGlyphNames()
    dict_={}
    for i in glyphNames:
        if i[0] == '.':#跳过'.notdef', '.null'
            continue
        
        g = gs[i]
        pen = ReportLabPen(gs, Path(fillColor=colors.black, strokeWidth=5))
        g.draw(pen)
        w, h = g.width, g.width
        g = Group(pen.path)
        g.translate(0, 0)
        # g.translate(w, h)
        
        d = Drawing(w, h)
        d.add(g)
        imageFile = imagePath+"/"+i+".png"
        renderPM.drawToFile(d, imageFile, fmt)
        
        print(i)


class OfdParser(object):
    def __init__(self,ofdb64,zip_path="",dpi=200) -> None:
        self.zip_path = ""
        self.dpi = dpi
        self.ofdbyte = base64.b64decode(ofdb64) 
        if not zip_path:
            pid=os.getpid()
            zip_path = f"{os.getcwd()}/{pid}_{str(uuid1())}.ofd"
        self.zip_path = zip_path
        # fp = tempfile.TemporaryFile()
        # fp.write(ofdbyte)
        
        # self.zip_path_fp = fp
        # self.zip_path = fp.name
        
        

    # 解压odf
    def unzip_file(self,zip_path="", unzip_path=None):
        """
        :param zip_path: ofd格式文件路径
        :param unzip_path: 解压后的文件存放目录
        :return: unzip_path
        """
        # if not zip_path:
        zip_path = self.zip_path
        # unzip_path_fp = tempfile.TemporaryDirectory()
        # unzip_path = unzip_path_fp.name
       
        if not unzip_path:
            unzip_path = zip_path.split('.')[0]
        with zipfile.ZipFile(zip_path, 'r') as f:
            for file in f.namelist():
                f.extract(file, path=unzip_path)
        
        return unzip_path

    def readjb2(self,jb2path,pbmpath) :
    
        """
        imput jb2path pbmpath
        output cv2_obj
        """
        res = os.system(f"jbig2dec -o {pbmpath} {jb2path}")
        if res == 0:
            print(res,"执行成功")
        else:
            raise Exception("jb2转换失败,检查参数")
        pbm_content =  cv2.imread(f"{pbmpath}")
        if os.path.exists(pbmpath):
            os.remove(pbmpath)
            
        return pbm_content

    # 解析Xml正文
    def parserContntXml(self,path:str)->list:
        """
        输入xml 文件地址
        输出主体坐标和文字信息 cell_list
        [{"pos":row['@Boundary'].split(" "),
                    "text":row['ofd:TextCode'].get('#text'),
                    "font":row['@Font'],
                    "size":row['@Size'],}]
        
        
        """
        
        cell_list = []
        try:
            with open(f"{path}" , "r", encoding="utf-8") as f:
                _text = f.read()
                tree = xmltodict.parse(_text)  # xml 对象
                TextObjectLayer = tree.get('ofd:Page',{}).get('ofd:Content',{}).get('ofd:Layer',{})
                
                TextObjectList = []
                
                
                        
                # 判断ofd标签格式
                if isinstance(TextObjectLayer,list):
                    for i in TextObjectLayer: 
                        if i.get('ofd:TextObject',[]):
                            TextObjectList.extend(i.get('ofd:TextObject',[]))
                elif TextObjectLayer.get("ofd:PageBlock",{}).get("ofd:PageBlock",{}).get("ofd:TextObject",{}) :
                    TextObjectList_new = TextObjectLayer.get("ofd:PageBlock").get("ofd:PageBlock").get("ofd:TextObject")
                    if isinstance(TextObjectList_new,list):
                        TextObjectList.extend(TextObjectList_new)
                else:
                    TextObjectList = tree.get('ofd:Page',{}).get('ofd:Content',{}).get('ofd:Layer',{}).get('ofd:TextObject',[])
                
            
                # print(TextObjectList)
                for row in TextObjectList:
                    # print(row)
            
                    if not row.get('ofd:TextCode',{}).get('#text'):
                        continue
                    cell_d = {}
                    if row.get("ofd:CGTransform"):
                        Glyphs_d = {
                            "Glyphs":row.get("ofd:CGTransform").get("ofd:Glyphs"),
                            "GlyphCount":row.get("ofd:CGTransform").get("@GlyphCount"),
                            "CodeCount":row.get("ofd:CGTransform").get("@CodeCount"),
                            "CodePosition":row.get("ofd:CGTransform").get("@CodePosition")
                            }
                        cell_d["Glyphs_d"] = Glyphs_d
                    
                    cell_d ["pos"] = [float(pos_i) for pos_i in row['@Boundary'].split(" ")]
                    if row.get('ofd:Clips',{}).get('ofd:Clip',{}).get('ofd:Area',{}).get('ofd:Path',{}):
                        cell_d ["pos"] = [float(pos_i) for pos_i in row.get('ofd:Clips',{}).get('ofd:Clip',{}).get('ofd:Area',{}).get('ofd:Path',{}).get('@Boundary',"").split(" ")]
                    cell_d ["text"] = str(row['ofd:TextCode'].get('#text'))
                    cell_d ["font"] = row['@Font'] # 字体
                    cell_d ["size"] = float(row['@Size']) # 字号
                    
                    color = row.get("ofd:FillColor",{}).get("@Value","0 0 0")
                    
                    
                    cell_d ["color"] = tuple(color.split(" "))  # 颜色
                    cell_d ["DeltaY"] = row.get("ofd:TextCode",{}).get("@DeltaY","") # y 轴偏移量 竖版文字表示方法之一
                    cell_d ["DeltaX"] = row.get("ofd:TextCode",{}).get("@DeltaX","") # x 轴偏移量 
                    cell_d ["CTM"] = row.get("@CTM","") # 平移矩阵换 
                    
                    cell_d ["X"] = row.get("ofd:TextCode",{}).get("@X","") # X 文本之与文本框距离
                    cell_d ["Y"] = row.get("ofd:TextCode",{}).get("@Y","") # Y 文本之与文本框距离

                    cell_list.append(cell_d)
                    
        except Exception as e:
            traceback.print_exc()
            print(e)
                
        return cell_list
    
    # 解析提取图片 
    def parserImageXml(self,path:str,_org_images:dict)->dict:
        """
        path: 解析文件路径 文件对象不同解析结构不同
        _org_images: 图片基本信息
        return b64 格式 & img type
        [{'ResourceID': '89', 'pos': [0.0, 0.0, 30.0, 20.0], 'CTM': '30 0 0 20 0 0', format ,'b64img':
        
        """
        img_list = []
        try:
            with open(f"{path}" , "r", encoding="utf-8") as f:
                _text = f.read()
                tree = xmltodict.parse(_text)  # xml 对象
                
                

            ImageObjectList = [] # 图片资源xml对象
            
            
            if path.endswith("Annotation.xml"):
                Annot =  tree.get('ofd:PageAnnot',{}).get('ofd:Annot',{})
                # print("Annot",Annot)
                if isinstance(Annot,dict):
                    Annot = [Annot]
                for Annot_cell in Annot:
                    Appearance = Annot_cell.get('ofd:Appearance',{})
                    AppearanceBoundary = Appearance.get("@Boundary","")
                    if AppearanceBoundary:
                        AppearanceBoundary = [float(i) for i in AppearanceBoundary.split(" ")]
                    
                    # print("AppearanceBoundary",AppearanceBoundary)
                    if  isinstance(Appearance,dict):
                        Appearance = [Appearance]
                    # print("Appearance",Appearance)
                    for i in Appearance :
                        if i.get('ofd:ImageObject',{}) and isinstance(i,list):
                            ImageObjectL = i.get('ofd:ImageObject',{})
                            for ImageObject_cell in  ImageObjectL:
                                ImageObject_cell["@wrap_pos"] = AppearanceBoundary
                            ImageObjectList.extend(ImageObjectL)
                            
                        elif i.get('ofd:ImageObject',{}) and isinstance(i,dict):
                            ImageObject = copy.deepcopy(i.get('ofd:ImageObject',{})) 
                            ImageObject["@wrap_pos"] = AppearanceBoundary
                            ImageObjectList.extend(
                                [ImageObject]
                                )
                # print("ImageObjectList",ImageObjectList)
                
            elif path.endswith("Content.xml"):
                ImageObjectLayer = tree.get('ofd:Page',{}).get('ofd:Content',{}).get('ofd:Layer',{})
                
                if isinstance(ImageObjectLayer,list):
                    for i in ImageObjectLayer:
                        if i.get('ofd:ImageObject',[]):
                            ImageObjectList.extend(i.get('ofd:ImageObject',[]))

                else:
                    ImageObjectList = tree.get('ofd:Page',{}).get('ofd:Content',{}).get('ofd:Layer',{}).get('ofd:ImageObject',[])
                
                
                if isinstance(ImageObjectList,dict):
                    ImageObjectList = [ImageObjectList]
                    
            # print(ImageObjectList)
            for row in ImageObjectList:
                # print(row)
                if row.get("@ResourceID") in _org_images:
                    f = open(_org_images.get(row.get("@ResourceID")).get("Path"),"rb")
                    b64img_b =  f.read()
                    f.close()
                    b64img = str( base64.b64encode(b64img_b) ,encoding="utf-8")
                    img_list.append(
                        
                        {
                            "ResourceID":row.get("@ResourceID"), #ID
                            "pos":[float(pos_i) for pos_i in row['@Boundary'].split(" ")],  #POS
                            "CTM":row.get("@CTM","") ,# 平移矩阵换 
                            "format":   _org_images[row.get("@ResourceID")]["format"] , 
                            "b64img":   b64img , # b64 
                            "wrap_pos" :row.get("@wrap_pos","")
                            
                            }
                        
                    )
                
        except Exception as e:
            traceback.print_exc()
            print(e)       
          
                
                
        # print(img_list)
        return img_list
        
    
    def get_xml_path(self,file_path,root_path):
        """
        获取关键xml 路径
        
        
        """
         # contentPath&tplsPath
        with open(f"{file_path}/{root_path}" , "r", encoding="utf-8") as f:
                _text = f.read()
                tree = xmltodict.parse(_text)
                # print(tree['ofd:Document']['ofd:Pages'])
                content_label = tree['ofd:Document']['ofd:Pages']['ofd:Page']
                
                if isinstance(content_label,list) :
                    contentPath_l = [f"{file_path}/{root_path.split('/')[0]}/{i.get('@BaseLoc')}" for i in  content_label]
                    # contentPath = f"{file_path}/{root_path.split('/')[0]}/{tree['ofd:Document']['ofd:Pages']['ofd:Page'][0]['@BaseLoc']}"
                else:
                    # contentPath = f"{file_path}/{root_path.split('/')[0]}/{tree['ofd:Document']['ofd:Pages']['ofd:Page']['@BaseLoc']}"
                    contentPath_l = [f"{file_path}/{root_path.split('/')[0]}/{tree['ofd:Document']['ofd:Pages']['ofd:Page']['@BaseLoc']}"]
                # print("contentPath",contentPath)
                 # AnnotstplsPath
                try:
                    tpls_label = tree['ofd:Document']['ofd:CommonData']['ofd:TemplatePage']
                    if isinstance(tpls_label,list) :
                        tplsPath_l = [f"{file_path}/{root_path.split('/')[0]}/{i.get('@BaseLoc')}" for i in  tpls_label]
                    else:
                        tplsPath_l = [f"{file_path}/{root_path.split('/')[0]}/{tree['ofd:Document']['ofd:CommonData']['ofd:TemplatePage']['@BaseLoc']}"]
                    # tplsPath = f"{file_path}/{root_path.split('/')[0]}/{tree['ofd:Document']['ofd:CommonData']['ofd:TemplatePage']['@BaseLoc']}"
                
                except :
                    tplsPath_l = []
                try:
                    AnnotationsPath = f"{file_path}/{root_path.split('/')[0]}/{tree['ofd:Document']['ofd:Annotations']}"
                except :
                    AnnotationsPath = ""
                if AnnotationsPath:
                    AnnotFileLocPath =  xmltodict.parse(open(f"{AnnotationsPath}" , "r", encoding="utf-8").read()).get("ofd:Annotations",{}).get("ofd:Page").get("ofd:FileLoc","")
                    AnnotFileLocPath = os.path.join( os.path.abspath(os.path.dirname(AnnotationsPath)) , AnnotFileLocPath) 
                else:
                    AnnotFileLocPath = ""
                    
        path_tree = {
            "PublicRes" :f"{file_path}/{root_path.split('/')[0]}/PublicRes.xml",
            "DocumentRes" :f"{file_path}/{root_path.split('/')[0]}/DocumentRes.xml",
            "contentPath" : contentPath_l,
            "tplsPath" : tplsPath_l,
            "AnnotationsPath" : AnnotationsPath,
            
        }
        return path_tree
        
    # 提取主要文本内容 结构更改，加入 页码，每页大小，字体，字号，颜色, 图片 兼容一些不规范的文件
    def parse_ofd(self, path) ->list:
        """
        :param content: ofd文件字节内容
        :param path: ofd文件存取路径
        """

        # with open(path, "wb") as f:
            # f.write(content)
        # file_path = unzip_file("path")
        file_path = self.unzip_file(path)
        xml_path = f"{file_path}/OFD.xml" 
        data_dict = {}
        rootPath = ""
        page_list = []
        # read ROOTPATAH
        with open(xml_path, "r", encoding="utf-8") as f:
            _text = f.read()
            tree = xmltodict.parse(_text)
            rootPath = tree['ofd:OFD']['ofd:DocBody']['ofd:DocRoot']
            
            # print(type(rootPath),rootPath)
        
        
        if isinstance(rootPath,str):
            rootPath = [rootPath]
        
    
        _img_format = ("png","jpg","jpeg")
        
        page_ID = 0
        for page,root_path in enumerate(rootPath) :
            
            _org_images = {}
            contentPath_l = []
            tplsPath_l = []
            # font  PublicRes
            fonts = {}
            FontFilePath_dict = {}
            path_tree = self.get_xml_path(file_path,root_path)
            # "PublicRes" :f"{file_path}/{root_path.split('/')[0]}/PublicRes.xml",
            # "DocumentRes" :f"{file_path}/{root_path.split('/')[0]}/DocumentRes.xml",
            # "contentPath" : contentPath_l,
            # "tplsPath" : tplsPath_l,
            # "AnnotationsPath" : AnnotationsPath,
            if os.path.exists(path_tree.get("PublicRes")):
                with open(f"{file_path}/{root_path.split('/')[0]}/PublicRes.xml" , "r", encoding="utf-8") as f:
                    _text = f.read()
                    tree = xmltodict.parse(_text)
                    fonts_obj = tree["ofd:Res"]["ofd:Fonts"]["ofd:Font"]
                    for i in fonts_obj:
                        fonts[i.get("@ID")] = { 
                                               "FontName":i.get("@FontName"),
                                               "FamilyName":i.get("@FamilyName"),          
                            } 
                        # fonts[i.get("@ID")] = i.get("@FontName")
                        if i.get("@FontName") not in FONTS and i.get("ofd:FontFile"):
                            
                            FontFilePath = f"{file_path}/{root_path.split('/')[0]}/Res/{i.get('ofd:FontFile')}"
                            if os.path.exists(FontFilePath):
                                FontFilePath_dict[i.get("@ID")] = FontFilePath
                                FONTS.append(i.get("@FontName"))
                                # print(FONTS)
                                pdfmetrics.registerFont(TTFont(i.get("@FontName"), FontFilePath))
                                # print(FontFilePath)
                    
            # image DocumentRes
            with open(path_tree.get("DocumentRes") , "r", encoding="utf-8") as f:
                _text = f.read()
                tree = xmltodict.parse(_text)
                MutiMedias_obj = tree.get("ofd:Res",{}).get("ofd:MultiMedias",{}).get("ofd:MultiMedia",{})
                if MutiMedias_obj and isinstance(MutiMedias_obj,list) :
              
                    for Media_obj in MutiMedias_obj:
                        if Media_obj.get("@Type") == "Image" and Media_obj.get("@Format","").lower() in _img_format:
                            name = Media_obj.get("ofd:MediaFile","")
                      
                            _org_images[Media_obj.get("@ID")] = {
                                "format":Media_obj.get("@Format",""),
                                "fileName":name,
                                "Path":f"{file_path}/{root_path.split('/')[0]}/Res/{name}"
                            }
                        
                            # print(f"{file_path}/{root_path.split('/')[0]}/Res/{name}")
                            # print(Media_obj.get("ofd:MediaFile",""))
            
            # contentPath&tplsPath
            with open(f"{file_path}/{root_path}" , "r", encoding="utf-8") as f:
                _text = f.read()
                tree = xmltodict.parse(_text)
                # print(tree['ofd:Document']['ofd:Pages'])
                content_label = tree['ofd:Document']['ofd:Pages']['ofd:Page']
                if isinstance(content_label,list) :
                    contentPath_l = [f"{file_path}/{root_path.split('/')[0]}/{i.get('@BaseLoc')}" for i in  content_label]
                    # contentPath = f"{file_path}/{root_path.split('/')[0]}/{tree['ofd:Document']['ofd:Pages']['ofd:Page'][0]['@BaseLoc']}"
                else:
                    # contentPath = f"{file_path}/{root_path.split('/')[0]}/{tree['ofd:Document']['ofd:Pages']['ofd:Page']['@BaseLoc']}"
                    contentPath_l = [f"{file_path}/{root_path.split('/')[0]}/{tree['ofd:Document']['ofd:Pages']['ofd:Page']['@BaseLoc']}"]
                # print("contentPath",contentPath)
                 # AnnotstplsPath
                try:
                    tpls_label = tree['ofd:Document']['ofd:CommonData']['ofd:TemplatePage']
                    if isinstance(tpls_label,list) :
                        tplsPath_l = [f"{file_path}/{root_path.split('/')[0]}/{i.get('@BaseLoc')}" for i in  tpls_label]
                    else:
                        tplsPath_l = [f"{file_path}/{root_path.split('/')[0]}/{tree['ofd:Document']['ofd:CommonData']['ofd:TemplatePage']['@BaseLoc']}"]
                    # tplsPath = f"{file_path}/{root_path.split('/')[0]}/{tree['ofd:Document']['ofd:CommonData']['ofd:TemplatePage']['@BaseLoc']}"
                
                except :
                    tplsPath = ""
                try:
                    AnnotationsPath = f"{file_path}/{root_path.split('/')[0]}/{tree['ofd:Document']['ofd:Annotations']}"
                except :
                    AnnotationsPath = ""
                if AnnotationsPath:
                    AnnotFileLocPath =  xmltodict.parse(open(f"{AnnotationsPath}" , "r", encoding="utf-8").read()).get("ofd:Annotations",{}).get("ofd:Page").get("ofd:FileLoc","")
                    AnnotFileLocPath = os.path.join( os.path.abspath(os.path.dirname(AnnotationsPath)) , AnnotFileLocPath) 
                else:
                    AnnotFileLocPath = ""
                    # print(AnnotFileLocPath)

                
                
                # print(contentPath)
                # print(tplsPath)
                page_size = []
                try:
                    page_size = [float(pos_i) for pos_i in tree.get('ofd:Document',{}).get("ofd:CommonData",{}).get("ofd:PageArea",{}).get("ofd:PhysicalBox","").split(" ") if re.match("[\d\.]",pos_i)] 
                except:
                    traceback.print_exc()
                    
                # print("page_size",page_size)

            
            cell_list = [] 
            _images = []
            # _images = self.parserImageXml(contentPath,_org_images)
           
            # if AnnotFileLocPath:
            #     _images2 = self.parserImageXml(AnnotFileLocPath,_org_images)
            # else:
            #     _images2 = []
            # _images.extend(_images2)
            # print(_images)
            contentPathL = path_tree.get("contentPath")
            tplsPathL = path_tree.get("tplsPath")
          
            for idx,contentPath in enumerate(contentPathL) :
                try:
                    cell_list = self.parserContntXml(contentPath)
                except Exception as e:
                    cell_list = []
                    traceback.print_exc()
                    print(e)
                # print(cell_list)
                tpls_cellS = []
                if len(contentPathL) == len(tplsPathL):
                    tplsPath = tplsPathL[idx]
                else:
                    tplsPath = ""
                if tplsPath :
                    tpls_cellS = self.parserContntXml(tplsPath)
            
                cell_list.extend(tpls_cellS)
                cell_list.sort(key=lambda pos_text:  (float(pos_text.get("pos")[1]),float(pos_text.get("pos")[0])))
                
                # 重新获取页面size
                with open(contentPath, "r", encoding="utf-8") as f:
                    _text = f.read()
                    tree = xmltodict.parse(_text)
                    try:
                        page_size_new = [float(pos_i) for pos_i in tree.get('ofd:Page',{}).get("ofd:Area",{}).get("ofd:PhysicalBox","").split(" ") if re.match("[\d\.]",pos_i)] 
                        # print(page_size)
                        if page_size_new and len(page_size_new)>=2 :
                            page_size = page_size_new
                            # print("page_size",page_size)
                    except Exception as e:
                        
                        traceback.print_exc()
                        print(e)
                
                # _images = ""
                page_list.append({
                    "page":page_ID,
                    "images":_images,
                    "page_size":page_size,
                    "fonts":fonts,
                    "FontFilePath":FontFilePath_dict,
                    "page_info":cell_list        
                                })
                page_ID +=1
            # print(cell_list)
        
        # json.dump(page_list,open("a.josn","w",encoding="utf-8"),indent=4,ensure_ascii=False)
        return page_list

    # 转json格式
    def odf2json(self, page_list:list) ->dict:
        """
        坐标默认为毫米单位 
        dpi 有则转化为px
        """
        Op = 1 # 转换算子单位
        
        dpi = self.dpi # 200
        if dpi:
            Op = dpi/25.4
        
        # 行信息构建
        for paga in page_list:
            
            document_id = 'v1' + '_' + _genShortId()
            pageList = []
            pageInfo = {}
            pageInfo["pageNo"] = 0
            pageInfo["pageNo"] = 0
            pageInfo["docID"] = document_id
            size = paga.get("page_size")
            if size:
                size = [size[2],size[3]]
            else:
                size = [0,0]
            pageInfo["imageQuality"] = {
                "size": [size[0]*Op, size[1]*Op]
            }
            pageInfo["lineList"] = []
            
            images = paga.get("images",[])
            if images:
                for iamge in images:
                    pos = iamge.get('pos')
                    wrap_pos = iamge.get('wrap_pos')
                    
                    if wrap_pos:
                        pos = [pos[0]+wrap_pos[0], pos[1]+wrap_pos[2],pos[2],pos[3]]
                    objPos = [pos[1]*Op,pos[0]*Op,pos[3]*Op ,pos[2]*Op,[pos[2]*Op]]
                    iamge["objPos"] = objPos
                        
                    
            pageInfo["images"] = paga.get("images",[])
            
            
            for lineNo,values in enumerate(paga.get("page_info")):
                line = {}
                pos = []
                line["lineId"] = 'line_' + str(0) + '_' + str(lineNo) + '_' + _genShortId()
                line["lineNo"] = lineNo
                line["sortNo"] = lineNo
                line["rowNo"] = lineNo
                line["objType_postpreprocess"] = "text_postpreprocess"
                
            
                
                # print(values)
                text = values.get("text")
                line['objContent'] = text
                pos = values.get("pos")
                
                offset = float(pos[3])*Op
                
                DeltaX = values.get("DeltaX","")
                DeltaY = values.get("DeltaY","")
                X = values.get("X","")
                Y = values.get("Y","")
                CTM = values.get("CTM","") # 因为ofd 的傻逼 增加这个字符缩放
                resizeX =1
                resizeY =1
                if CTM :
                    # print(CTM)
                    resizeX = float(CTM.split(" ")[0])
                    resizeY = float(CTM.split(" ")[3])
                
                x_list = self.cmp_offset(values.get("pos")[0],X,DeltaX,text,resizeX)
                y_list = self.cmp_offset(values.get("pos")[1],Y,DeltaY,text,resizeY)
                # print("x_list",x_list,Op,CTM)
                # print("pos",pos,float(X),float(x_list[-1]))
                w = (float(x_list[-1])- float(X)-float(pos[0]))*Op
                # print(text,w)
                if w == 0:
                    
                    w = (float(x_list[-1])- float(X))*Op
                # pos = [float(pos[1])*Op, float(pos[0])*Op,float(pos[3])*Op,float(pos[2])*Op]
                pos = [float(y_list[0])*Op, float(x_list[0])*Op,float(pos[3])*Op,w]
                offsetPost = [offset*(i+1) for i in range(len(values.get("text")))]
                pos.append(offsetPost)
                line['objPos'] = pos
            
                line['objType'] = 'text'
                pageInfo["lineList"].append(line)
            
            contIndex = {}
            lineList = pageInfo.get("lineList")
            if lineList:
                for cell in lineList:
                    contIndex[cell.get("lineId")] = {
                    "lineNo": cell.get("lineNo"),
                    "lineId": cell.get("lineId"),
                    "objType":cell.get("objType"),
                    "objContent": cell.get("objContent"),
                    "objPos":  cell.get("objPos"),
                    "sortNo": cell.get("lineNo"),
                    "rowNo": cell.get("lineNo"),
                    "objType_postpreprocess": "table_postpreprocess"
                    
                    }
            pageInfo["contIndex"] = contIndex
            pageList.append(pageInfo)
        return pageList
    
    def sort_x(self,lineList):
        lineList_bak = copy.deepcopy(lineList)
        for idx,line in enumerate(lineList) :
            for line2 in lineList_bak[idx:]:
                if abs(line.get("objPos")[0] - line2.get("objPos")[0]) < 3 :
                    line.get("objPos")[0] = line2.get("objPos")[0]
                    
        lineList.sort(key=lambda line:(line.get("objPos")[0],line.get("objPos")[1]))
        return lineList
    
    # 合并行 并重排序 排除竖版块
    def merge_line_pipeline(self, page_list):
        page_list_new = []
        for page_info in  page_list:
            lineList = page_info.get("lineList")
            lineList = self.sort_x(lineList)
            page_list_new.append(
                {
                "pageNo": page_info.get("pageNo"),
                "docID": page_info.get("docID"),
                "imageQuality": page_info.get("imageQuality"),
                
                "lineList":self.merge_line(lineList),
                "images": page_info.get("images"),
                "contIndex": page_info.get("contIndex"),
                
                }
                   
               )
           
        
        return page_list_new
    
    # 合并行  
    def merge_line(self,lineList):
        
        lineList_new = []
        non_id = []
        for idx,line_info in enumerate(lineList) :
            objPos = line_info.get("objPos")
            if objPos[2]/objPos[3] >1: # 排除竖版块
                if line_info and line_info.get("lineId") not in non_id:
                    lineList_new.append(line_info)
                    # print("line_info",line_info)
                non_id.append(line_info.get("lineId"))
                continue
            
            else:
                # 找是否有符合条件的，有则合并无则返回
                line_new = None
                for line_info2 in lineList[idx:]:
                    objPos2 = line_info2.get("objPos")
                    if objPos == objPos2:
                        line_new = line_info2
                    if objPos[2]/objPos[3] >1 :
                        # print("合并行")
                        continue
                    # print(line_info.get("objContent"))
                    # print("objPos","objPos2")
                    # print(objPos,objPos2)
                    if objPos2[1] > objPos[1] and abs(objPos2[0] - objPos[0])<objPos[2]/2 and 0 < abs(objPos2[1] - objPos[1] - objPos[3]) < objPos[2]:
                        # print("合并")
                        # print(line_info.get("objContent") +  line_info2.get("objContent") )
                        non_id.append(line_info2.get("lineId"))
                        new_objContent = line_info.get("objContent") +  line_info2.get("objContent")
                        # print("new_objContent",new_objContent)
                        new_objPos = self.merge_pos (line_info.get("objPos"),line_info2.get("objPos"))
                        
                        line_new = {
                            "lineId":line_info.get("lineId"),
                            "lineNo":line_info.get("lineNo"),
                            "objType_postpreprocess":line_info.get("objType_postpreprocess"),
                            "objContent": new_objContent ,
                            "objPos": new_objPos,
                            "objType":line_info.get("objType") 
                        }
                        # print(line_new)
                        # print(line_info.get("objContent") ,  line_info2.get("objContent"))
                        
                    
                if line_new and line_new.get("lineId") not in non_id:
                    # print(line_new)
                    lineList_new.append(line_new)
                    non_id.append(line_new.get("lineId"))
                else:
                    
                    # print("banline_new",line_new)
                    pass
        
        # print("non_id",non_id)
        return lineList_new
        
    def merge_pos(self,pos1,pos2):
        # print(pos1,pos2)
        y = min(pos1[0],pos2[0])
        x = min(pos1[1],pos2[1]) 
        bottom = max( (pos1[2]),(pos2[0]+pos2[2]))
        top = max( (pos1[1]+pos1[3]),(pos2[1]+pos2[3]))
        h = bottom -y
        w = top -x
        offset_l = pos1[4]
        offset = (pos2[1] - (pos1[1]+pos1[3]) )+ pos1[4][-1]
        if len(pos2) == 4:
            
            for i in pos2[4]:
                offset_l.append(offset+i)
        pos = [y,x,h,w,offset_l]
        
        return pos
        
    # ofd2json流程
    def parserodf2json(self):
        try:
            zip_path = self.zip_path
            with open(zip_path,"wb") as f:
                f.write(self.ofdbyte)
            unzip_path = self.unzip_file(self.zip_path)
            page_list = self.parse_ofd(unzip_path)
            page_list_new = self.odf2json(page_list)
            #  结果后处理合并接近的块
            page_list_new = self.merge_line_pipeline(page_list_new)
            
            
           
        finally:
             # 删除文件
            if os.path.exists(unzip_path):
                shutil.rmtree(unzip_path)
            if os.path.exists(self.zip_path):
                os.remove(self.zip_path)
        return page_list_new
    
    # task 
    @staticmethod
    def draw_task(c,parms):
        
        font_path,Glyph_id,char_,_cahr_x,_cahr_y,w,h = parms
        imageFile = draw_Glyph(font_path,Glyph_id,char_)
        # print("写入")
        c.drawImage(imageFile,_cahr_x,_cahr_y,w,h)
        return "写入成功"
        
    # 单个字符偏移量计算
    def cmp_offset(self,pos,offset,DeltaRule,text,resize=1)->list:
        """
        pos 文本框x|y 坐标
        offset 初始偏移量
        DeltaRule 偏移量规则
        
        """
        # print("DeltaRule",DeltaRule)
        char_pos = float(pos if pos else 0 ) + float(offset if offset else 0 )
        pos_list = []
        pos_list.append(char_pos)
        offsets = [i for i in DeltaRule.split(" ")]
        # print(offsets)
        if "g" in   DeltaRule:  
            g_no = None
            for _no, offset_i in enumerate(offsets) :
                # print(f"_no: {_no}",f"offset_i: {offset_i} g_no: {g_no}")
                
                
                if offset_i == "g":
                    g_no = _no
                    for j in range(int(offsets[(g_no+1)])):
                        char_pos += float(offsets[(g_no+2)]) 
                        pos_list.append(char_pos)
                    
                elif offset_i != "g" :
                    # print("offset_i",offset_i)
                    if g_no == None:
                        char_pos += float(offset_i) * resize
                        pos_list.append(char_pos)
                    elif  (int(_no) > int(g_no+2)) and g_no!=None:
                        # print("非g offset")
                        
                        char_pos += float(offset_i)  * resize
                        pos_list.append(char_pos)
                    
                # print("len(pos_list)",len(pos_list))
        elif not DeltaRule:
            pos_list = []
            for i in range(len(text)):
                pos_list.append(char_pos)
        else:
            for i in offsets:
                # print(i,char_pos)
                if not i:
                    char_pos += 0
                else:
                    char_pos += float(i)  * resize
                pos_list.append(char_pos)
                
        return pos_list
        
    def gen_pdf(self,json_list=None, gen_pdf_path="",need_image=False):
        '''
        input：
        
            json_list-- 文本和坐标
            gen_pdf2_path：图片和json文件生成的双层PDF所在文件夹路径
        '''

        # 读取json
        # json_list = json.load(open(json_path, 'r', encoding='utf-8'))
        
        #v (210*mm,140*mm)
    
        Op = 200/25.4
       
        c = canvas.Canvas(gen_pdf_path)
        # c = canvas.Canvas(gen_pdf_path,(page_size[2]*Op,page_size[3]*Op))
        c.setAuthor("reno")
        # print("gen_pdf_path",gen_pdf_path)    
        # print(len(json_list))
        for idx,page in enumerate(json_list)  :
            
                        
            # 写入 文本
            page_size= page.get("page_size")
            # print("page_size",page_size)
            fonts = page.get("fonts")
            images = page.get("images")
            line_dict = page.get("line_dict")
            FontFilePath = page.get("FontFilePath")
            
            # print("page_size",page_size)
            
            c.setPageSize((page_size[2]*Op, page_size[3]*Op))
            
            # c.setPageSize = ((page_size[2]*Op,page_size[3]*Op))

            # 图片
            if need_image:
                for image in images:
                    # print(image.get('b64img'))
                    
                    imgbyte = base64.b64decode(image.get('b64img'))
                    
                    
                    img = cv2.imdecode(np.frombuffer(imgbyte, np.uint8), cv2.IMREAD_COLOR)
                    rgb_img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                    img = PIL.Image.fromarray(rgb_img)
                    imgReade  = ImageReader(img)
                    CTM = image.get('CTM')
                    x_offset = 0
                    y_offset = 0
                    # if CTM:
                    #     CTM = [float(i) for i in CTM.split(" ")]
                    #     x_offset  = CTM[0]
                    #     y_offset  = CTM[3]
                    wrap_pos = image.get("wrap_pos")
                    # print("wrap_pos",wrap_pos)
                        
                    x = (image.get('pos')[0]+x_offset)*Op
                    y = (page_size[3] - (image.get('pos')[1]+y_offset))*Op
                    if wrap_pos:
                        x = x+(wrap_pos[0]*Op)
                        y = y-(wrap_pos[1]*Op)
                   
                        
                    # print(x,y)
                    w =   image.get('pos')[2]*Op
                    h =  -image.get('pos')[3]*Op
                    # print(w,h)
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
                    font =  font if font in FONTS else fonts.get(line_dict.get("font"),{}).get("FamilyName",'STSong-Light')
                    font_f = font
                    # if font == "BWSimKai-KaiTi-0":
                    #     print(font)
                    #     print(line_dict.get("text"))
                    if font not in FONTS:
                        # print("font----------------：",font)
                        font = '宋体'
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

    def gen_empty_pdf(self,json_list=None, gen_pdf_path="",need_image=False):
        c = canvas.Canvas(gen_pdf_path)
        c.setPageSize(A4)
        c.setFont('宋体', 20)
        c.drawString(0,210,"ofd 格式错误,不支持解析", mode=1  )
        c.save()
    
    # ofd2pdf流程
    def ofd2pdf(self,need_image=False)->bytes:
        
        try:
            
            zip_path = ""
            unzip_path = ""
            zip_path = self.zip_path
            with open(zip_path,"wb") as f:
                f.write(self.ofdbyte)
            # zip_path_fp = self.zip_path_fp
            images_path = "images"
            if not os.path.exists(images_path):
                os.mkdir(images_path)
            pdfname=BytesIO()
            
            unzip_path = self.unzip_file(zip_path=zip_path)
            # print("unzip_path",unzip_path)
            page_list = self.parse_ofd(unzip_path)
            # print(page_list)
            self.gen_pdf(page_list,pdfname,need_image=need_image)
            # 删除文件
            # raise Exception("异常")
            pdfbytes  = None
            pdfbytes  = pdfname.getvalue()
        except Exception as e:
            print(e)
            traceback.print_exc()
            time.sleep(10)
            print("ofd格式不兼容文件")
            self.gen_empty_pdf(None,pdfname,need_image=need_image)
            pdfbytes  = None
            pdfbytes  = pdfname.getvalue()
        finally:
            # zip_path_fp.close()
            
            if os.path.exists(images_path):
                shutil.rmtree(images_path)
            if os.path.exists(unzip_path):
                shutil.rmtree(unzip_path)
            # print("zip_path",zip_path)
            if os.path.exists(zip_path):
                os.remove(zip_path)
           
        # with open("test.pdf","wb") as f:
            # f.write(pdfbytes)
        return pdfbytes



if __name__ == "__main__":
    import time
    import json
    import base64

    dirPath = "/home/data/0305data/OFD数据总"
    # dir_ = os.listdir(dirPath)
    t_t = time.time()
    dir_ = []
    for root, dirs, files in os.walk(dirPath):
        for file in files:
            file_path = os.path.join(root, file)
            dir_.append(file_path)

    
    f_path = f"/home/data/0305data/ofd数据收集/0404/e20b0612-9807-481b-81b4-2ce57ace833c.ofd"
    f_path = f"/home/data/0305data/OFD数据总/增值税电子专票4.ofd"
    f = open(f_path,"rb")
    ofdb64 = str(base64.b64encode(f.read()),"utf-8")
    OfdParser(ofdb64,f_path).unzip_file(f"{f_path}","增值税电子专票4")
    # pdfbytes = OfdParser(ofdb64).ofd2pdf(need_image=True) # 插入图片 支持jpg ,jpeg ，png 
    # pdfbytes = OfdParser(ofdb64).ofd2pdf() # 不插入图片
    json_ =json.dump( OfdParser(ofdb64).parserodf2json(), open(f"json/增值税电子专票4.json","w",encoding="utf-8"), indent=4, ensure_ascii=False)
    # print(pdfbytes)
    # ocr_json = OfdParser(ofdb64).parserodf2json() #
    # print(ocr_json)
    # with open(f"test.pdf","wb") as f:
    #         f.write(pdfbytes)
    # 批量调
    count = 0
    for i in dir_:
        name =  i.split("/")[-1]
        break
        if i.split(".")[-1].lower() != "ofd":
            continue
        # f = open("增值税电子专票5.ofd","rb")
        f = open(f"{i}","rb")
        print(i)
        count += 1
        # 传入b64 字符串
        ofdb64 = str(base64.b64encode(f.read()),"utf-8")
        # print(ofdb64)
        f.close
        t = time.time()
        

        # # 转pdf输出
        # pdfbytes = OfdParser(ofdb64).ofd2pdf()
        # with open(f"pdfs/{name}.pdf","wb") as f:
        #     f.write(pdfbytes)
            
        # 转json输出
        json_ =json.dump( OfdParser(ofdb64).parserodf2json(), open(f"json/{name}.json","w",encoding="utf-8"), indent=4, ensure_ascii=False)
       
       
        print(f"ofd解析耗时{(time.time()-t)*1000}/ms")	
        # json.dump(data_dict,open("data_dict.json","w",encoding="utf-8"),ensure_ascii=False,indent=4)
        # pbmpath = "image_80.pbm"
        # jb2path = "增值税电子专票5/Doc_0/Res/image_80.jb2"
        # pdfbytes = OfdParser(ofdb64).readjb2(jb2path,pbmpath)
    print(f"ofd解析 文件 {count} -------------- 总耗时{(time.time()-t_t)*1000}/ms")
    
