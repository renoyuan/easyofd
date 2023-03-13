#!/usr/bin/env python
#-*- coding: utf-8 -*-
#PROJECT_NAME: /home/azx_fp/forecaest_new/app_ocr/utils
#CREATE_TIME: 2023-02-23 
#E_MAIL: renoyuan@foxmail.com
#AUTHOR: reno 

# encoding: utf-8
import time
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


import xmltodict
from reportlab import platypus
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import mm,inch
from reportlab.platypus import SimpleDocTemplate, Image
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase.ttfonts import TTFont





try:
    import cv2
except :
    logging.warning("缺少cv2 若需要处理图片文件必不可少")
    

FONTS = ('宋体',"SWPMEH+SimSun",'SimSun','KaiTi','楷体',"SWLCQE+KaiTi",'Courier New','STSong-Light',"CourierNew","SWANVV+CourierNewPSMT","CourierNewPSMT","BWSimKai","hei","黑体","SimHei","SWDKON+SimSun","SWCRMF+CourierNewPSMT","SWHGME+KaiTi")
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
    
class OfdParser(object):
    def __init__(self,ofdb64,zip_path="ofd.ofd") -> None:
        ofdbyte = base64.b64decode(ofdb64)
        zip_path = f"{str(_genShortId())}.ofd"
        with open(zip_path,"wb") as f:
            f.write(ofdbyte)
        self.zip_path = zip_path

    # 解压odf
    def unzip_file(self,zip_path="", unzip_path=None):
        """
        :param zip_path: ofd格式文件路径
        :param unzip_path: 解压后的文件存放目录
        :return: unzip_path
        """
        # if not zip_path:
        zip_path = self.zip_path
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

    # 解析Xml
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
        
        with open(f"{path}" , "r", encoding="utf-8") as f:
            _text = f.read()
            tree = xmltodict.parse(_text)  # xml 对象
            TextObjectLayer = tree.get('ofd:Page',{}).get('ofd:Content',{}).get('ofd:Layer',{})
            TextObjectList = []
            if isinstance(TextObjectLayer,list):
                for i in TextObjectLayer:
                    if i.get('ofd:TextObject',[]):
                        TextObjectList.extend(i.get('ofd:TextObject',[]))
            else:
                TextObjectList = tree.get('ofd:Page',{}).get('ofd:Content',{}).get('ofd:Layer',{}).get('ofd:TextObject',[])
            
            # print(TextObjectList)
            for row in TextObjectList:
                # print(row)
               
                if not row.get('ofd:TextCode',{}).get('#text'):
                    continue
                cell_d = {}
                
                cell_d ["pos"] = [float(pos_i) for pos_i in row['@Boundary'].split(" ")]
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
                
             
                
        return cell_list
    
    # 提取主要文本内容 结构更改，加入 页码，每页大小，字体，字号，颜色
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
        
        # read ROOTPATAH
        with open(xml_path, "r", encoding="utf-8") as f:
            _text = f.read()
            tree = xmltodict.parse(_text)
            rootPath = tree['ofd:OFD']['ofd:DocBody']['ofd:DocRoot']
            
            # print(type(rootPath),rootPath)
        
        
        if isinstance(rootPath,str):
            rootPath = [rootPath]
        
        page_list = []
        
        for page,root_path in enumerate(rootPath) :
            
            # font 
            fonts = {}
            with open(f"{file_path}/{root_path.split('/')[0]}/PublicRes.xml" , "r", encoding="utf-8") as f:
                _text = f.read()
                tree = xmltodict.parse(_text)
                fonts_obj = tree["ofd:Res"]["ofd:Fonts"]["ofd:Font"]
                for i in fonts_obj:
                    fonts[i.get("@ID")] = i.get("@FontName")
                
                
            # read contentPath&tplsPath
            with open(f"{file_path}/{root_path}" , "r", encoding="utf-8") as f:
                _text = f.read()
                tree = xmltodict.parse(_text)
                contentPath = f"{file_path}/{root_path.split('/')[0]}/{tree['ofd:Document']['ofd:Pages']['ofd:Page']['@BaseLoc']}"
                try:
                    tplsPath = f"{file_path}/{root_path.split('/')[0]}/{tree['ofd:Document']['ofd:CommonData']['ofd:TemplatePage']['@BaseLoc']}"
                except :
                    tplsPath = ""
                
                # print(contentPath)
                # print(tplsPath)
                page_size = [float(pos_i) for pos_i in tree['ofd:Document']['ofd:CommonData']['ofd:PageArea']['ofd:PhysicalBox'].split(" ")] 
                # print("page_size",page_size)

            
            cell_list = [] 
            cell_list = self.parserContntXml(contentPath)
            # print(cell_list)
            tpls_cellS = []
            if tplsPath :
                tpls_cellS = self.parserContntXml(tplsPath)
        
            cell_list.extend(tpls_cellS)
            cell_list.sort(key=lambda pos_text:  (float(pos_text.get("pos")[1]),float(pos_text.get("pos")[0])))
            # 重新获取页面size
            with open(contentPath, "r", encoding="utf-8") as f:
                _text = f.read()
                tree = xmltodict.parse(_text)
                try:
                    page_size = [float(pos_i) for pos_i in tree['ofd:Page']['ofd:Area']['ofd:PhysicalBox'].split(" ")] 
                    # print(page_size)
                except Exception as e:
                    print(e)
                    pass
            page_list.append({
                "page":page,
                "page_size":page_size,
                "fonts":fonts,
                "page_info":cell_list        
                              })
            # print(cell_list)
        
        
        return page_list

    # 转json格式
    def odf2json(self, ofd_date:list,dpi=200) ->dict:
        """
        坐标默认为毫米单位 
        dpi 有则转化为px
        """
        Op = 1 # 转换算子单位
        
        dpi = 200
        if dpi:
            Op = dpi/25.4
        
        # 行信息构建
        for paga in ofd_date:
            
            document_id = 'v1' + '_' + _genShortId()
            pageList = []
            pageInfo = {}
            pageInfo["pageNo"] = 0
            pageInfo["pageNo"] = 0
            pageInfo["docID"] = document_id
            pageInfo["imageQuality"] ={
                "size": [
                    0,
                    0
                ]
            }
            pageInfo["lineList"] = []
            
            
            for lineNo,values in enumerate(paga.get("page_info")):
                line = {}
                pos = []
                line["lineId"] = 'line_' + str(0) + '_' + str(lineNo) + '_' + _genShortId()
                line["lineNo"] = lineNo
                line["sortNo"] = lineNo
                line["rowNo"] = lineNo
                line["objType_postpreprocess"] = "text_postpreprocess"
                
            
                
                # print(values)
                line['objContent'] = values.get("text")
                pos = values.get("pos")
                
                offset = float(pos[3])*Op
                pos = [float(pos[1])*Op, float(pos[0])*Op,float(pos[3])*Op,float(pos[2])*Op]
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
        
    # ofd2json流程
    def parserodf2json(self):
        unzip_path = self.unzip_file(self.zip_path)
        cell_list = self.parse_ofd(unzip_path)
        dict = self.odf2json(cell_list,200)
        
        # 删除文件
        shutil.rmtree(unzip_path)
        if os.path.exists(self.zip_path):
            os.remove(self.zip_path)
        return dict

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
        
    def gen_pdf(self,json_list=None, gen_pdf_path=""):
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
        # print("gen_pdf_path",gen_pdf_path)
        

                    
        for page in json_list :
            
            page_size= page.get("page_size")
            fonts = page.get("fonts")
            
            # print(page_size)
            c = canvas.Canvas(gen_pdf_path,(page_size[2]*Op,page_size[3]*Op))
            c.setPageSize((page_size[2]*Op, page_size[3]*Op))
            # c.setPageSize = ((page_size[2]*Op,page_size[3]*Op))

            
            # c.drawInlineImage(img_path, 0, 0, width, height)

            # 循环写文本到图片
            # print(json_list)
            try:
            
                for line_dict in page.get("page_info"):
                    # print("line_dict",line_dict)
                    
                    font = fonts.get(line_dict["font"],'STSong-Light')
                    
                    if font not in FONTS:
                        print("font----------------：",font)
                        font = '宋体'
                    # print(font)
                    # print("font",font)
                    c.setFont(font, line_dict["size"]*Op)
                    # 原点在页面的左下角 
                    # 原点在页面的左下角
                    color = line_dict.get("color",[0,0,0])
                    # print(color)
                    c.setFillColorRGB(int(color[0])/255,int(color[1])/255, int(color[2])/255)
                    c.setStrokeColorRGB(int(color[0])/255,int(color[1])/255, int(color[2])/255)
                    # 按每个字写入精确到每个字的坐标
                    text = line_dict.get("text")
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
                            
                    
                        
                    # print ("text",text)
                    # print ("x_list",x_list)
                    # print ("y_list",y_list)
                    # print ("x_list",len(x_list))
                    # print ("y_list",len(y_list))
                    # print ("text",len(text))
                    
                    
                    # 按字符写入
                    for cahr_id, _cahr_ in enumerate(text) :
                        _cahr_x= float(x_list[cahr_id])*Op
                        _cahr_y= (float(page_size[3])-(float(y_list[cahr_id])))*Op
                        c.drawString( _cahr_x,  _cahr_y, _cahr_, mode=0) # mode=3 文字不可见 0可見
                    
                    # 按行写入
                    #c.drawString( float(line_dict.get("pos")[0])*Op,  (float(page_size[3])-(float(line_dict.get("pos")[1])))*Op, text, mode=0) # mode=3 文字不可见 0可見
                   

                c.showPage()
            except Exception as e:
                traceback.print_exc()
                logger.info("genpdf2 error")
        c.save()

    # ofd2pdf流程
    def ofd2pdf(self)->bytes:
        
        pdfname=BytesIO()
        
        unzip_path = self.unzip_file(self.zip_path)
        page_list = self.parse_ofd(unzip_path)
        self.gen_pdf(page_list,pdfname)
        # 删除文件
        pdfbytes  = None
     
        pdfbytes  = pdfname.getvalue()
        shutil.rmtree(unzip_path)
        if os.path.exists(self.zip_path):
            os.remove(self.zip_path)
        # with open("test.pdf","wb") as f:
            # f.write(pdfbytes)
        return pdfbytes



if __name__ == "__main__":
    import time
    import json
    import base64
    dirPath = "/home/0305data/OFD数据"
    dirPath = "/home/data/调用成功但返回报错样本-0308"
    dir_ = os.listdir(dirPath)
    t_t = time.time()

    # OfdParser("").unzip_file("/home/data/调用成功但返回报错样本-0308/ff378288-00fa-47e5-a447-ed017a80ea8c.ofd","ff378288-00fa-47e5-a447-ed017a80ea8c")
    for i in dir_:
        # break
        if i.split(".")[-1].lower() != "ofd":
            continue
        # f = open("增值税电子专票5.ofd","rb")
        f = open(f"{dirPath}/{i}","rb")
        # print(i)
        ofdb64 = str(base64.b64encode(f.read()),"utf-8")
        
        f.close
        t = time.time()
        
        # 传入b64 字符串
        
        # 输出ocr 格式解析结果
        # data_dict = OfdParser(ofdb64).parserodf2json()
        
        # 转pdf输出
        pdfbytes = OfdParser(ofdb64).ofd2pdf()
        
        # print(data_dict)
        # print(pdfbytes)
        with open(f"pdfs/{i}.pdf","wb") as f:
            f.write(pdfbytes)
        print(f"ofd解析耗时{(time.time()-t)*1000}/ms")	
        # json.dump(data_dict,open("data_dict.json","w",encoding="utf-8"),ensure_ascii=False,indent=4)
        # pbmpath = "image_80.pbm"
        # jb2path = "增值税电子专票5/Doc_0/Res/image_80.jb2"
        # pdfbytes = OfdParser(ofdb64).readjb2(jb2path,pbmpath)
    print(f"ofd解析耗时{(time.time()-t_t)*1000}/ms")
    
