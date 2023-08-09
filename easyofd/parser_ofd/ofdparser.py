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
    

FONTS = [ "Microsoft","MicrosoftYaHei","MicrosoftYaHei-Bold","微软简楷体","Arial",'宋体',"SWPMEH+SimSun",'SimSun',"SimKai",'KaiTi','楷体',"SWLCQE+KaiTi",
         "Courier",'Courier New','STSong-Light',"CourierNew","SWANVV+CourierNewPSMT","CourierNewPSMT","BWSimKai","hei","黑体","SimHei","SWDKON+SimSun","SWCRMF+CourierNewPSMT","SWHGME+KaiTi"]
         
pdfmetrics.registerFont(TTFont('宋体', 'simsun.ttc'))
pdfmetrics.registerFont(TTFont('SWPMEH+SimSun', 'simsun.ttc'))
pdfmetrics.registerFont(TTFont('SimSun', 'simsun.ttc'))
pdfmetrics.registerFont(TTFont('SWDKON+SimSun', 'simsun.ttc'))
pdfmetrics.registerFont(TTFont('KaiTi', 'simkai.ttf'))
pdfmetrics.registerFont(TTFont('SimKai', 'simkai.ttf'))
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
pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
pdfmetrics.registerFont(TTFont('微软简楷体', 'micross.ttf'))
pdfmetrics.registerFont(TTFont('Microsoft', 'micross.ttf'))
pdfmetrics.registerFont(TTFont('MicrosoftYaHei', 'msjh.ttc'))
pdfmetrics.registerFont(TTFont('MicrosoftYaHei-Bold', 'msjhbd.ttc'))

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
    imageFile = "images"+"/"+str(index)+".png"
    if  os.path.exists(imageFile):
        return imageFile
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
    # print(dir(g))
    w, h = g.width, g.width
    # if w >200 or h>200:
    #     w = 200
    #     h = 200
    #     g.width = 200
    # print(w, h)
    g = Group(pen.path)
    g.translate(0, 0)
    d = Drawing(w, h)
    d.add(g)
    
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
        
        # print(i)


class OfdParser(object):
    def __init__(self,ofdb64,zip_path="",dpi=200) -> None:
        self.zip_path = ""
        self.dpi = dpi
        self.ofdbyte = base64.b64decode(ofdb64) 
        if not zip_path:
            pid=os.getpid()
            zip_path = f"{os.getcwd()}/{pid}_{str(uuid1())}.ofd"
        self.zip_path = zip_path
        self.need_img_b64 = False # 解析结果中是否需要图片的b64 串默认不需要要
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
           
              
            tree = self.read_xml(path) # xml 对象
            TextObjectList = []
            text_key = "ofd:TextObject"
            self.recursion_ext(tree,TextObjectList,text_key)
            # print(TextObjectList)
            for row in TextObjectList:
                # print(row)
        
                if not row.get('ofd:TextCode',{}).get('#text'):
                    continue
                cell_d = {}
                
                # 字体字形信息
                if row.get("ofd:CGTransform"):
                    Glyphs_d = {
                        "Glyphs":row.get("ofd:CGTransform").get("ofd:Glyphs"),
                        "GlyphCount":row.get("ofd:CGTransform").get("@GlyphCount"),
                        "CodeCount":row.get("ofd:CGTransform").get("@CodeCount"),
                        "CodePosition":row.get("ofd:CGTransform").get("@CodePosition")
                        }
                    cell_d["Glyphs_d"] = Glyphs_d
                
                cell_d ["pos"] = [float(pos_i) for pos_i in row['@Boundary'].split(" ")] # 文本框
                if row.get('ofd:Clips',{}).get('ofd:Clip',{}).get('ofd:Area',{}).get('ofd:Path',{}):
                    cell_d ["clips_pos"] = [float(pos_i) for pos_i in row.get('ofd:Clips',{}).get('ofd:Clip',{}).get('ofd:Area',{}).get('ofd:Path',{}).get('@Boundary',"").split(" ")]
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
    
    # 解析提取图片信息包括 坐标 路径 b64-默认无
    def parserImageXml(self,path:str,_org_images:dict)->list:
        """
        path: 解析文件路径 文件对象不同解析结构不同
        _org_images: 图片基本信息
        return b64 格式 & img type
        [ {
                        "ResourceID":row.get("@ResourceID"), #ID
                        "pos":[float(pos_i) for pos_i in row['@Boundary'].split(" ")],  #POS
                        "CTM":row.get("@CTM","") ,# 平移矩阵换 
                        "Path":_org_images.get(row.get("@ResourceID")).get("Path") ,# 平移矩阵换 
                        "format":   _org_images[row.get("@ResourceID")]["format"] , 
                        "b64img":   b64img , # b64 默认不需要
                        "wrap_pos" :row.get("@wrap_pos","")
                        
                        }]
        """
        img_list = []
        
        tree = self.read_xml(path)
       
        ImageObjectList = [] # 图片资源xml对象
            
        if not tree:
            return img_list
        
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
            img_key = 'ofd:ImageObject'
            self.recursion_ext(tree,ImageObjectList,img_key)
            # ImageObjectLayer = tree.get('ofd:Page',{}).get('ofd:Content',{}).get('ofd:Layer',{})
            
            # if isinstance(ImageObjectLayer,list):
            #     for i in ImageObjectLayer:
            #         if i.get('ofd:ImageObject',[]):
            #             ImageObjectList.extend(i.get('ofd:ImageObject',[]))

            # else:
            #     ImageObjectList = tree.get('ofd:Page',{}).get('ofd:Content',{}).get('ofd:Layer',{}).get('ofd:ImageObject',[])
            
            
            # if isinstance(ImageObjectList,dict):
            #     ImageObjectList = [ImageObjectList]
                    
        # print(ImageObjectList)
        for row in ImageObjectList:
            # print(row)
            if row.get("@ResourceID") in _org_images:
                b64img = ""
                if self.need_img_b64:
                    with open(_org_images.get(row.get("@ResourceID")).get("Path"),"rb") as f:
                        b64img_b =  f.read()
                        b64img = str( base64.b64encode(b64img_b) ,encoding="utf-8")
                    
                
                img_list.append(
                    
                    {
                        "ResourceID":row.get("@ResourceID"), #ID
                        "pos":[float(pos_i) for pos_i in row['@Boundary'].split(" ")],  #POS
                        "CTM":row.get("@CTM","") ,# 平移矩阵换 
                        "Path":_org_images.get(row.get("@ResourceID")).get("Path") ,# 平移矩阵换 
                        "format":   _org_images[row.get("@ResourceID")]["format"] , 
                        "b64img":   b64img , # b64 默认不需要
                        "wrap_pos" :row.get("@wrap_pos","")
                        
                        }
                    
                )
                

        # print(img_list)
        return img_list
        
    
    def get_xml_path(self,file_path,root_path):
        """
        获取关键xml 路径
            "PublicRes" :f"{file_path}/{root_path.split('/')[0]}/PublicRes.xml",
            "DocumentRes" :f"{file_path}/{root_path.split('/')[0]}/DocumentRes.xml",
            "contentPath" : contentPath_l,
            "tplsPath" : tplsPath_l,
            "AnnotationsPath" : AnnotationsPath,
        
        """
         # contentPath&tplsPath
        
        doc_root_path = os.path.join(file_path,root_path) # doc 根节点绝对路径
        doc_dir_path = os.path.abspath(os.path.dirname(doc_root_path)) # doc 根节目录绝对路径
        # print("doc_root_path",doc_root_path)
        # print("doc_dir_path",doc_dir_path)
        if not os.path.exists(doc_dir_path) or not os.path.exists(doc_root_path):
            print("doc_root_path not exists",doc_root_path)
            return None
       
        
        tree = self.read_xml(doc_root_path) # doc 根tree
        if not tree:
            print("doc_root_path tree not exists",doc_root_path)
            return None
        
        # Content 正文节点收集
        content_label = tree.get("ofd:Document",{}).get("ofd:Pages",{}).get("ofd:Page") # 正文节点路径
        
        if isinstance(content_label,list) : # 正文多页情况
            contentPath_l = []
            for i in content_label:
                content_p = os.path.join(doc_dir_path,re.sub(r"[/]{0,1}Doc_[\d]{1,3}/","", i.get('@BaseLoc')) ) 
                if os.path.exists(content_p):
                    contentPath_l.append(content_p)
            
        elif not content_label:
            contentPath_l = []
        elif isinstance(content_label,dict):
            contentPath_l = []
           
            content_p = os.path.join(doc_dir_path,re.sub(r"[/]{0,1}Doc_[\d]{1,3}/","", content_label.get('@BaseLoc')) )
           
            if os.path.exists(content_p):
                contentPath_l.append(content_p) 

        else: # 正文单页情况
            
            contentPath_l = []
        
        
        # TemplatePage  Tpl 模板节点收集
        
        try:
            # tpls_label = tree.get("ofd:Document",{}).get("ofd:CommonData",{}).get("ofd:TemplatePage")
            tpls_label = []
            TemplatePage_key = "ofd:TemplatePage"
            self.recursion_ext(tree,tpls_label,TemplatePage_key)
            # print(tpls_label)
            tplsPath_l = []
            if tpls_label:
                for i in tpls_label:
                    tpls_p = os.path.join(doc_dir_path,re.sub(r"[/]{0,1}Doc_[\d]{1,3}/","", i.get('@BaseLoc')) ) 
                    if os.path.exists(tpls_p):
                        tplsPath_l.append(tpls_p)
                        
            

            elif not tplsPath_l:
                tplsPath_l = []
            elif isinstance(tplsPath_l,dict):
                tplsPath_l = []
                tpls_p = os.path.join(doc_dir_path,re.sub(r"[/]{0,1}Doc_[\d]{1,3}/","", i.get('@BaseLoc')) )
                if os.path.exists(tpls_p):
                        tplsPath_l.append(tpls_p)
            else:
                tplsPath_l = []

        
        except :
            tplsPath_l = []
            
            
        # AnnotationsPath  Annots 签注节点收集
        try:
            annots_label = tree.get("ofd:Document",{}).get("ofd:Annotations")
            if annots_label and isinstance(annots_label,str) :
                AnnotationsPath = os.path.join(doc_dir_path,annots_label)
                if not os.path.exists(AnnotationsPath):
                    AnnotationsPath = ""
            else:
                AnnotationsPath = ""
        except :
            AnnotationsPath = ""
        
        # PublicRes  公共资源节点路径收集
        try:
            public_label = tree.get("ofd:Document",{}).get("ofd:CommonData").get("ofd:PublicRes")
            if public_label and isinstance(public_label,str) :
                PublicResPath = os.path.join(doc_dir_path,public_label)
                if not os.path.exists(PublicResPath):
                    PublicResPath = ""
            else:
                PublicResPath = ""
        except :
            PublicResPath = ""
        
        # PublicRes  公共资源节点路径收集
        try:
            DocumentRes_label = tree.get("ofd:Document",{}).get("ofd:CommonData").get("ofd:DocumentRes")
            if DocumentRes_label and isinstance(DocumentRes_label,str) :
                DocumentResPath = os.path.join(doc_dir_path,DocumentRes_label)
                if not os.path.exists(DocumentResPath):
                    DocumentResPath = ""
            else:
                DocumentResPath = ""
        except :
            DocumentResPath = ""
        
        # AnnotFileLocPath AnnotsFile 签注文件收集  这个应该放在下一级别 不应该是是doc 级别解析
        if AnnotationsPath :
            AnnotFileLocPath_l = []
            AnnotationsTree = self.read_xml(AnnotationsPath)
            AnnotFileLocPath_lable =  AnnotationsTree.get("ofd:Annotations",{})
            if AnnotFileLocPath_lable and isinstance(AnnotFileLocPath_lable,list):
                for i in AnnotFileLocPath_lable:
                    AnnotFileLocP = i.get("ofd:Page").get("ofd:FileLoc","")
                    
                    if AnnotFileLocP.startswith("/"):
                        AnnotFileLocP = AnnotFileLocP[1:]
                    
                    AnnotFileLocP = os.path.join(os.path.abspath(os.path.dirname(AnnotationsPath)), AnnotFileLocP )
                    if  os.path.exists(AnnotationsPath):
                        AnnotFileLocPath_l.append(AnnotationsPath)
            
            elif AnnotFileLocPath_lable and isinstance(AnnotFileLocPath_lable,dict):
                AnnotFileLocP_Page = AnnotFileLocPath_lable.get("ofd:Page")
                if  isinstance(AnnotFileLocP_Page,list):
                    pass
                elif isinstance(AnnotFileLocP_Page,dict):
                    AnnotFileLocP = AnnotFileLocP_Page.get("ofd:FileLoc","")
                    if AnnotFileLocP.startswith("/"):
                        AnnotFileLocP = AnnotFileLocP[1:]
                    AnnotFileLocP = os.path.join(os.path.abspath(os.path.dirname(AnnotationsPath)), AnnotFileLocP )
                    if  os.path.exists(AnnotationsPath):
                        AnnotFileLocPath_l.append(AnnotationsPath)
              
            
           
            
        else:
            AnnotFileLocPath_l = []

        
        if not PublicResPath:
            PublicResPath = os.path.join(doc_dir_path,"PublicRes.xml")
        
        if not DocumentResPath:
            DocumentResPath = os.path.join(doc_dir_path,"DocumentRes.xml")
        
        page_size = []
        try:
           
            page_size = [float(pos_i) for pos_i in tree.get('ofd:Document',{}).get("ofd:CommonData",{}).get("ofd:PageArea",{}).get("ofd:PhysicalBox","").split(" ") if re.match("[\d\.]",pos_i)] 
        except:
            traceback.print_exc()
                
        path_tree = {
            "absdoc_dir_path":doc_dir_path,
            "PublicRes" : "" if not os.path.exists(PublicResPath) else PublicResPath,
            "DocumentRes" :"" if not os.path.exists(DocumentResPath) else DocumentResPath,
            "contentPath" : contentPath_l, #列表
            "tplsPath" : tplsPath_l,
            "AnnotationsPath" : AnnotFileLocPath_l,
            "page_size" : page_size,
            
        }
        return path_tree
    
    def read_xml(self,path):
        """
        读取一个xml 文件返回他的dom 文件不存在返回None
        """
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                _text = f.read()
                tree = xmltodict.parse(_text)
                return tree
        else:
            return None
        
    
    def get_root_path(self,file_path)->dict:
        """
        输入解压后目录路径输出主要节点的路径 返回一个树状结构 所有文件以绝对路径 且需要验证
        """
        RootPath = f"{file_path}/OFD.xml" # 根节点路径 所有文档必须要有
        RootPathtree = self.read_xml(RootPath)
        if RootPathtree:
            
            docrootPath = RootPathtree['ofd:OFD']['ofd:DocBody']['ofd:DocRoot']
        else:
            return None
        if isinstance(docrootPath,str): # 
            docrootPath = [docrootPath]
            
        
            
        resPath = {
            "RootPath":RootPath, # 根节点路径 所有文档必须要有
            "DOCRootPath":docrootPath, # 每个doc的根节点 是列表 
        }
        
        return resPath
        
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
        
        root_path = self.get_root_path(file_path)
        RootPath = root_path.get("RootPath")
        DOCRootPath = root_path.get("DOCRootPath")
       
        data_dict = {}
        rootPath = ""
        page_list = []
        # read ROOTPATAH
        
    
        _img_format = ("png","jpg","jpeg")
        
        page_ID = 0
        for page,root_path in enumerate(DOCRootPath) : # 子节点处理
            
            _org_images = {}
            contentPath_l = []
            tplsPath_l = []
            # font  PublicRes
            fonts = {}
            FontFilePath_dict = {}
            if root_path.startswith("/"):
                root_path = root_path[1:]
                
            # -------------------------------------------------    
            path_tree = self.get_xml_path(file_path,root_path) # 获取docroot 节点内的关键节点信息
            # print(path_tree)
            absdoc_dir_path = path_tree.get("absdoc_dir_path")
            
            # print(path_tree) # 获取公共信息 如字体
            if os.path.exists(path_tree.get("PublicRes")):
                
                PublicResTree = self.read_xml(path_tree.get("PublicRes"))
                if PublicResTree:
                    fonts_obj = []
                    Font_key = "ofd:Font"
                    self.recursion_ext(PublicResTree,fonts_obj,Font_key)
                    
                    if fonts_obj:
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
                                    
                                    # print(FONTS)
                                   
                                    if os.path.exists(FontFilePath):
                                        
                                        
                                        try:
                                            pdfmetrics.registerFont(TTFont(i.get("@FontName"), FontFilePath))
                                            FONTS.append(i.get("@FontName"))
                                        except :
                                            traceback.print_exc()
                                            print("registerFontEroor",i.get("@FontName"),FontFilePath)
                                            pass
                                       
                                          
                                                
                                           
                    
            # image DocumentRes 资源节点 可能为空 其中保存了图片资源
            DocumentResPath = path_tree.get("DocumentRes")
            DocumentResTree = None
            if DocumentResPath:
                DocumentResTree  = self.read_xml(DocumentResPath)
                
            if DocumentResTree:
               
                MutiMedias_obj_lable = DocumentResTree.get("ofd:Res",{}).get("ofd:MultiMedias",{})
                img_dir = DocumentResTree.get("ofd:Res",{}).get("@BaseLoc") # 图片资源dirname 默认为 Res
                img_dir = img_dir if img_dir else "Res"
                
                
                MutiMedias_obj_list = []
                # 抽取 
                Media_key = "ofd:MultiMedia"
                self.recursion_ext(DocumentResTree,MutiMedias_obj_list,Media_key)
                
                
                for Media_obj in MutiMedias_obj_list:
                   
                    name = Media_obj.get("ofd:MediaFile","")
                   
                    img_path =  os.path.join( os.path.join(absdoc_dir_path,img_dir) ,name)
                    _org_images[Media_obj.get("@ID")] = {
                        
                        "format":Media_obj.get("@Format",""),
                        "fileName":name,
                        
                        "Path":img_path
                    }
                        
                # print(_org_images)
            
            # contentPath&tplsPath
            
            # 从docroot 获取page_size 可能不是最终的 page_size
           
            page_size = path_tree.get("page_size")
            # print("page_size",page_size)

            
            cell_list = [] 
            _images = []
            
            
           
           
            # print(_images)
            contentPathL = path_tree.get("contentPath")
            tplsPathL = path_tree.get("tplsPath")
            # print("contentPathL",contentPathL)
            for idx,contentPath in enumerate(contentPathL) :
                _images2 = []
                _images2 = list(self.parserImageXml(contentPath,_org_images))
                _images.extend(_images2)  # 将图片信息放入正文中解析得到 图片信息和正文中图片坐标
                # print(_images)
                try:
                    cell_list = self.parserContntXml(contentPath)
                except Exception as e:
                    cell_list = []
                    traceback.print_exc()
                    print(e)
                # print(cell_list)
                tpls_cellS = []
                # print(tplsPathL)
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
                # resizeX =1
                # resizeY =1
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
    
    
    @staticmethod
    def draw_task(c,parms):
        
        font_path,Glyph_id,char_,_cahr_x,_cahr_y,w,h = parms
        imageFile = draw_Glyph(font_path,Glyph_id,char_)
        # print("写入")
        c.drawImage(imageFile,_cahr_x,_cahr_y,w,h)
        return "写入成功"
        
    # 单个字符偏移量计算
    def cmp_offset(self,pos,offset,DeltaRule,text,resize=1,line_dict_size=0,text_pos=None)->list:
        """
        pos 文本框x|y 坐标
        offset 初始偏移量
        DeltaRule 偏移量规则
        resize 坐标缩放
        
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
                    # char_pos += float(i) 
                pos_list.append(char_pos)
                
        return pos_list
    
    # 递归抽取需要xml要素
    def recursion_ext(self,need_ext_obj,ext_list,key):
        """
        need_ext_obj : xmltree
        ext_list: data container
        key: key
        """
        # print(type(need_ext_obj))
        if isinstance(need_ext_obj,dict):
            for k,v in  need_ext_obj.items():
                if k == key:
                    # print(key,v)
                    if isinstance(v,dict):
                        ext_list.append(v)
                    elif isinstance(v,list):
                        ext_list.extend(v)
                else:
                    # print(key,v)
                    if  isinstance(v,dict):
                        self.recursion_ext(v,ext_list,key)
                    elif isinstance(v,list):
                        for cell in v:
                            self.recursion_ext(cell,ext_list,key)
                    else:
                        # print(type(v))
                        pass
        else:
            print(type(need_ext_obj))
        
        
    # 生成pdf
    def gen_pdf(self,json_list=None, gen_pdf_path="",need_image=False):
        '''
        input：
        
            json_list-- 文本和坐标
            gen_pdf2_path：图片和json文件生成的
        '''

        #v (210*mm,140*mm)
    
        Op = 200/25.4
       
        c = canvas.Canvas(gen_pdf_path)
        # c = canvas.Canvas(gen_pdf_path,(page_size[2]*Op,page_size[3]*Op))
        c.setAuthor("reno")
        # print("gen_pdf_path",gen_pdf_path)    
        # print(len(json_list))
        # print(json_list)
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
            # c.setPageSize((215.89999*Op, 279.39999*Op))
            
            # c.setPageSize = ((page_size[2]*Op,page_size[3]*Op))

            
            
            for image in images: # 图片 图片插入规则修改超过1/2 则插入否则不插入
                
                # print(image.get('b64img'))
                
                # 流中读取
                # imgbyte = base64.b64decode(image.get('b64img'))
                # img = (np.frombuffer(imgbyte, np.uint8), cv2.IMREAD_COLOR)
                # rgb_img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                # img = PIL.Image.fromarray(rgb_img)
                
                img_pos = image.get("pos")
                img_w = float(img_pos[2]) - float(img_pos[0])
                img_h = float(img_pos[3]) - float(img_pos[1])
                imgPath = image.get("Path")
                
                if   os.path.exists(imgPath) and page_size[2]/2 <= img_w or  page_size[3]/2 <= img_w or  page_size[3]/2<img_h or page_size[2]/2<img_h:
                    
                    
                    img = PIL.Image.open(imgPath)
                    
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
           

            # 循环写文本到图片
            # print(json_list)
            try:
                
                for line_dict in page.get("page_info"):
                   
                    font = fonts.get(line_dict.get("font"),{}).get("FontName",'STSong-Light')
                    font_f = font
                    font =  font if font in FONTS else fonts.get(line_dict.get("font"),{}).get("FamilyName",'STSong-Light')
                    
                    
                    # if font_f:
                    #     if "SimSun" in font_f:
                    #         font_f = "SimSun"
                    #     elif "Courier" in font_f:
                    #         font_f = "Courier"
                    #     elif "KaiTi" in font_f:
                    #         font_f = "KaiTi"
                    #     elif "STSongti" in font_f:
                    #         font_f = "STSong-Light"
                        
                   
                    if font not in FONTS :
                        # print("font----------------：",font)
                        if font_f and "SimSun" in font_f:
                            font = "SimSun"
                        elif font_f and "Courier" in font_f:
                            font = "Courier"
                        elif font_f and "KaiTi" in font_f:
                            font = "KaiTi"
                        elif font_f and "STSongti" in font_f:
                            font = "STSong-Light"
                        else:  
                            font = '宋体'
                    # print(font)
                    # print("font",font)
                    CTM = line_dict.get("CTM","") # 因为ofd 的傻逼 增加这个字符缩放
                    resizeX =1
                    resizeY =1
                    if CTM :
                        # print(CTM)
                        resizeX = float(CTM.split(" ")[0])
                        resizeY = float(CTM.split(" ")[3])
                    
                    line_dict_size = line_dict["size"]
                    if line_dict_size == 1:
                        line_dict_size = 5
                    line_dict_size = line_dict_size
                    
                    c.setFont(font, line_dict_size*Op)
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
                    X = float(line_dict.get("X",""))
                    Y = float(line_dict.get("Y",""))
                    if float(X)<0:
                        X = 0
                    if float(Y)<0:
                        Y = 0
                    text_pos = line_dict.get("pos","")
                    # print("text_pos",text_pos)
                    pos_0 = float(text_pos[0])
                    pos_1 =float(text_pos[1])
                    if pos_0 < 0:
                        pos_0 = 0
                    if pos_1 < 0:
                        pos_1 = 0
                    x_list = self.cmp_offset(pos_0,X,DeltaX,text,resizeX,line_dict_size,text_pos)
                    y_list = self.cmp_offset(pos_1,Y,DeltaY,text,resizeY,line_dict_size,text_pos)
                    
                    # 对于自定义字体 写入字形 drawPath
                    if   font_f and line_dict.get("Glyphs_d") and  FontFilePath.get(line_dict["font"])  and font_f not in FONTS :
                        # continue
                        # print(line_dict.get("Glyphs_d"))
                        # print(font)
                        
                        
                        # d_obj = []
                        
                        Glyphs = [int(i) for i in line_dict.get("Glyphs_d").get("Glyphs").split(" ")]
                        for idx,Glyph_id in enumerate(Glyphs):
                            # print(FontFilePath.get(line_dict["font"]))
                            if len(x_list)<= idx or len(y_list)<= idx:
                                continue
                            _cahr_x= float(x_list[idx])*Op
                                
                            _cahr_y= (float(page_size[3])-(float(y_list[idx])))*Op
                            imageFile = draw_Glyph( FontFilePath.get(line_dict["font"]), Glyph_id,text[idx])
                            # print("size",line_dict["size"]*Op*2)
                            
                            # font_img_info.append((FontFilePath.get(line_dict["font"]), Glyph_id,text[idx],_cahr_x,_cahr_y,-line_dict["size"]*Op*2,line_dict["size"]*Op*2))
                            c.drawImage(imageFile,_cahr_x,_cahr_y,-line_dict["size"]*Op*2,line_dict["size"]*Op*2  )
      
                    else: # 写入文本
 
                         
                        try:
                            
                            if   y_list[-1]*Op > page_size[3]*Op or x_list[-1]*Op >page_size[2]*Op or x_list[-1]<0 or y_list[-1]<0: # 如果出现不合理的点坐标 按行写入# 按行写入
                                
                                x_p = abs(float(X) + pos_0)*Op
                                
                                y_p = abs(float(page_size[3])-(float(Y) + pos_1))*Op
                                c.drawString(x_p, y_p, text, mode=0) # mode=3 文字不可见 0可見
                              
                                # print(page_size[2]*Op, page_size[3]*Op)
                                # print(x_p,  y_p, text)
                                # print(pos_0,  pos_1)
                                
                            else: # 按字符写入
                                if len(text) > len(x_list) or len(text) > len(y_list) :
                                    print("调整字符")
                                    text = re.sub("[^\u4e00-\u9fa5]","",text) 
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
            except Exception as e:
                traceback.print_exc()
                logger.info("genpdf2 error")
            if idx+1 <= len(json_list):
                c.showPage()  
        c.save()

    # 生成空白pdf
    def gen_empty_pdf(self,json_list=None, gen_pdf_path="",need_image=False):
        c = canvas.Canvas(gen_pdf_path)
        c.setPageSize(A4)
        c.setFont('宋体', 20)
        c.drawString(0,210,"ofd 格式错误,不支持解析", mode=1  )
        c.save()
    
    # ofd2pdf流程
    def ofd2pdf(self,need_image=False,name="")->bytes:
        
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
            logging.error(traceback.format_exc())
            traceback.print_exc()
            print("ofd格式不兼容文件")
            
            # 排错使用
            # with open("error.txt","a+") as f:
            #     f.write(f"{name}\n")
            
            self.gen_empty_pdf(None,pdfname,need_image=need_image)
            
            pdfbytes  = None
            pdfbytes  = pdfname.getvalue()
        finally:
            # zip_path_fp.close()
            
            if os.path.exists(images_path):
                shutil.rmtree(images_path)
            if os.path.exists(unzip_path):
                shutil.rmtree(unzip_path)
           
            if os.path.exists(zip_path):
                os.remove(zip_path)
                
            # print("zip_path",zip_path)
           
        # with open("test.pdf","wb") as f:
            # f.write(pdfbytes)
        return pdfbytes



if __name__ == "__main__":
    import time
    import json
    import base64

    dirPath = "/home/data/0305data/OFD数据总"
    dirPath = "/home/ligang/0315测试数据/0427测试数据/test"
    # dirPath = "/home/data/0305data/ofd数据收集/0322"
    # dirPath = "/home/data/0305data/ofd数据收集/0426"
    # dir_ = os.listdir(dirPath)
    t_t = time.time()
    dir_ = []
    for root, dirs, files in os.walk(dirPath):
        for file in files:
            file_path = os.path.join(root, file)
            dir_.append(file_path)

    # 只跑错误文件
    # with open("error.txt") as f:
    #     path_c = f.read()
    # dir__ = path_c.split("\n")
    # dir_ = [ f"{dirPath}/{name.split('/')[-1]}"  for name in dir__ if name]
    
    # print(dir_)
    
  
    f_path = f"/home/data/0305data/ofd数据收集/0426/e119e065-b20b-48cf-8b07-6f9a68b52d70.ofd"
    # f_path = f"/home/data/0305data/OFD数据总/6c711357-2df6-4ffd-820d-5ca1c012aaee.ofd"
    f_path = f"/home/data/0305data/OFD数据总/15b814d4-476a-414d-b41e-616faded409b.ofd"

  
    f = open(f_path,"rb")
    ofdb64 = str(base64.b64encode(f.read()),"utf-8")

    # pdfbytes = OfdParser(ofdb64).ofd2pdf(need_image=True) # 插入图片 支持jpg ,jpeg ，png 
    pdfbytes = OfdParser(ofdb64).ofd2pdf() # 不插入图片
    # json_ =json.dump(OfdParser(ofdb64).parserodf2json(), open(f"json/增值税电子专票4.json","w",encoding="utf-8"), indent=4, ensure_ascii=False)
    # print(pdfbytes)
    # ocr_json = OfdParser(ofdb64).parserodf2json() #
    # print(ocr_json)
    with open(f"test.pdf","wb") as f:
            f.write(pdfbytes)
    # 批量调
    count = 0
    for i in dir_:
        name =  i.split("/")[-1]
        # break
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
        pdfbytes = OfdParser(ofdb64).ofd2pdf(name=name) # 派错使用
        ouputpath = "pdfs"
        ouputpath = "/home/data/0305data/ofd数据收集/0426ofd2pdf"
        ouputpath = "/home/ligang/0315测试数据/0427测试数据/0429ofd"
        # ouputpath = "/home/data/0305data/ofd数据收集/0322pdfs"
        with open(f"{ouputpath}/{name}.pdf","wb") as f:
            f.write(pdfbytes)
            
        # 转json输出
        # json_ =json.dump( OfdParser(ofdb64).parserodf2json(), open(f"json/{name}.json","w",encoding="utf-8"), indent=4, ensure_ascii=False)
       
       
        print(f"ofd解析耗时{(time.time()-t)*1000}/ms")	
        # json.dump(data_dict,open("data_dict.json","w",encoding="utf-8"),ensure_ascii=False,indent=4)
        # pbmpath = "image_80.pbm"
        # jb2path = "增值税电子专票5/Doc_0/Res/image_80.jb2"
        # pdfbytes = OfdParser(ofdb64).readjb2(jb2path,pbmpath)
    print(f"ofd解析 文件 {count} -------------- 总耗时{(time.time()-t_t)*1000}/ms")
    
