#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PROJECT_NAME: E:\code\easyofd\easyofd\draw
# CREATE_TIME: 2023-08-10
# E_MAIL: renoyuan@foxmail.com
# AUTHOR: reno
# NOTE:  绘制pdf
import base64
import os
import re
import traceback
from io import BytesIO

from PIL import Image as PILImage
from loguru import logger
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from easyofd.draw.font_tools import FontTool
from .find_seal_img import SealExtract


# print(reportlab_fonts)
class DrawPDF():
    """
    ofd 解析结果 绘制pdf
    OP ofd 单位转换
    """

    def __init__(self, data, *args, **kwargs):
        assert data, "未输入ofd解析结果"
        self.data = data
        self.author = "renoyuan"
        self.OP = 200 / 25.4
        # self.OP = 1
        self.pdf_uuid_name = self.data[0]["pdf_name"]
        self.pdf_io = BytesIO()
        self.SupportImgType = ("JPG", "JPEG", "PNG")
        self.init_font = "宋体"
        self.font_tool = FontTool()

    def draw_lines(my_canvas):
        """
        draw_line
        """
        my_canvas.setLineWidth(.3)

        start_y = 710
        my_canvas.line(30, start_y, 580, start_y)

        for x in range(10):
            start_y -= 10
            my_canvas.line(30, start_y, 580, start_y)

    def gen_empty_pdf(self):
        """
        """
        c = canvas.Canvas(self.pdf_io)
        c.setPageSize(A4)
        c.setFont(self.init_font, 20)
        c.drawString(0, 210, "ofd 格式错误,不支持解析", mode=1)
        c.save()

    # 单个字符偏移量计算
    def cmp_offset(self, pos, offset, DeltaRule, text, CTM_info, dire="X") -> list:
        """
        pos 文本框x|y 坐标 
        offset 第一个字符的X|Y 
        DeltaRule 偏移量规则
        resize 字符坐标缩放
        返回 x|y  字符位置list 
        """
        if CTM_info and dire == "X":
            resize = CTM_info.get("resizeX")
            rotate = CTM_info.get("rotateX")
            move= CTM_info.get("moveX")
        elif CTM_info and dire == "Y":
            resize = CTM_info.get("resizeY")
            rotate = CTM_info.get("rotateY")
            move = CTM_info.get("moveY")
        else:
            resize = 1
            rotate = 0
            move = 0

        # print(f"resize is {resize}")
        char_pos = float(pos if pos else 0) + (float(offset if offset else 0) + move) * resize
        pos_list = []
        pos_list.append(char_pos)  # 放入第一个字符
        offsets = [i for i in DeltaRule.split(" ")]

        if "g" in DeltaRule:  # g 代表多个元素
            g_no = None
            for _no, offset_i in enumerate(offsets):

                if offset_i == "g":
                    g_no = _no
                    for j in range(int(offsets[(g_no + 1)])):
                        char_pos += float(offsets[(g_no + 2)])
                        pos_list.append(char_pos)

                elif offset_i and offset_i != "g" :
                    if g_no == None:
                        char_pos += float(offset_i) * resize
                        pos_list.append(char_pos)
                    elif (int(_no) > int(g_no + 2)) and g_no != None:
                        # print(f"offset_i is {offset_i}")
                        char_pos += float(offset_i) * resize
                        pos_list.append(char_pos)

        elif not DeltaRule:  # 没有字符偏移量 一般单字符
            pos_list = []
            for i in range(len(text)):
                pos_list.append(char_pos)
        else:  # 有字符偏移量
            for i in offsets:
                if not i:
                    char_pos += 0
                else:
                    char_pos += float(i) * resize
                pos_list.append(char_pos)

        return pos_list

    def draw_chars(self, canvas, text_list, fonts, page_size):
        """写入字符"""
        c = canvas
        for line_dict in text_list:
            # TODO 写入前对于正文内容整体序列化一次 方便 查看最后输入值 对于最终 格式先
            text = line_dict.get("text")
            font_info = fonts.get(line_dict.get("font"), {})
            if font_info:
                font_name = font_info.get("FontName", "")
            else:
                font_name = self.init_font
            # print(f"font_name:{font_name}")

            # TODO 判断是否通用已有字体 否则匹配相近字体使用
            if font_name not in self.font_tool.FONTS:
                font_name = self.font_tool.FONTS[0]

            font = self.font_tool.normalize_font_name(font_name)
            # print(f"font_name:{font_name} font:{font}")

            try:
                c.setFont(font, line_dict["size"] * self.OP)
            except KeyError as key_error:
                logger.error(f"{key_error}")
                font =  self.font_tool.FONTS[0]
                c.setFont(font, line_dict["size"] * self.OP)
            # 原点在页面的左下角 
            color = line_dict.get("color", [0, 0, 0])
            if len(color) < 3:
                color = [0, 0, 0]

            c.setFillColorRGB(int(color[0]) / 255, int(color[1]) / 255, int(color[2]) / 255)
            c.setStrokeColorRGB(int(color[0]) / 255, int(color[1]) / 255, int(color[2]) / 255)

            DeltaX = line_dict.get("DeltaX", "")
            DeltaY = line_dict.get("DeltaY", "")
            # print("DeltaX",DeltaX)
            X = line_dict.get("X", "")
            Y = line_dict.get("Y", "")
            CTM = line_dict.get("CTM", "")  # 因为ofd 增加这个字符缩放
            resizeX = 1
            resizeY = 1
            # CTM =None # 有的数据不使用这个CTM
            if CTM and (CTMS:=CTM.split(" ")) and len(CTMS) == 6:
                CTM_info = {
                    "resizeX": float(CTMS[0]),
                    "rotateX": float(CTMS[1]),
                    "rotateY": float(CTMS[2]),
                    "resizeY": float(CTMS[3]),
                    "moveX": float(CTMS[4]),
                    "moveY": float(CTMS[5]),

                }

            else:
                CTM_info ={}
            x_list = self.cmp_offset(line_dict.get("pos")[0], X, DeltaX, text, CTM_info, dire="X")
            y_list = self.cmp_offset(line_dict.get("pos")[1], Y, DeltaY, text, CTM_info, dire="Y")

            # print("x_list",x_list)
            # print("y_list",y_list)
            # print("Y",page_size[3])
            # print("x",page_size[2])
            # if line_dict.get("Glyphs_d") and  FontFilePath.get(line_dict["font"])  and font_f not in FONTS:
            if False:  # 对于自定义字体 写入字形 drawPath 性能差暂时作废
                Glyphs = [int(i) for i in line_dict.get("Glyphs_d").get("Glyphs").split(" ")]
                for idx, Glyph_id in enumerate(Glyphs):
                    _cahr_x = float(x_list[idx]) * self.OP
                    _cahr_y = (float(page_size[3]) - (float(y_list[idx]))) * self.OP
                    imageFile = draw_Glyph(FontFilePath.get(line_dict["font"]), Glyph_id, text[idx])

                    # font_img_info.append((FontFilePath.get(line_dict["font"]), Glyph_id,text[idx],_cahr_x,_cahr_y,-line_dict["size"]*Op*2,line_dict["size"]*Op*2))
                    c.drawImage(imageFile, _cahr_x, _cahr_y, -line_dict["size"] * self.OP * 2,
                                line_dict["size"] * self.OP * 2)
            else:
                if len(text) > len(x_list) or len(text) > len(y_list):
                    text = re.sub("[^\u4e00-\u9fa5]", "", text)
                try:
                    # 按行写入  最后一个字符y  算出来大于 y轴  最后一个字符x  算出来大于 x轴 
                    if y_list[-1] * self.OP > page_size[3] * self.OP or x_list[-1] * self.OP > page_size[2] * self.OP or \
                            x_list[-1] < 0 or y_list[-1] < 0:
                        # print("line wtite")
                        x_p = abs(float(X)) * self.OP
                        y_p = abs(float(page_size[3]) - (float(Y))) * self.OP
                        c.drawString(x_p, y_p, text, mode=0)  # mode=3 文字不可见 0可見

                        # text_write.append((x_p,  y_p, text))
                    # 按字符写入
                    else:
                        for cahr_id, _cahr_ in enumerate(text):
                            if len(x_list)>cahr_id:
                                # print("char wtite")
                                c.setFont(font, line_dict["size"] * self.OP * resizeX)
                                _cahr_x = float(x_list[cahr_id]) * self.OP
                                _cahr_y = (float(page_size[3]) - (float(y_list[cahr_id]))) * self.OP
                                # print(_cahr_x,  _cahr_y, _cahr_)
                                c.drawString(_cahr_x, _cahr_y, _cahr_, mode=0)  # mode=3 文字不可见 0可見
                            else:
                                logger.debug(f"match {_cahr_} pos error \n{text} \n{x_list}")
                            # text_write.append((_cahr_x,  _cahr_y, _cahr_))
                except Exception as e:
                    logger.error(f"{e}")
                    traceback.print_exc()

    def compute_ctm(self, CTM,x1, y1, img_width, img_height):
        """待定方法"""
        a,b,c,d,e,f = CTM.split(" ")
        a, b, c, d, e, f = float(a), float(b), float(c), float(d),float(e), float(f)
        # 定义变换矩阵的元素

        # 计算原始矩形的宽和高
        x2 = x1 + img_width
        y2 = y1 + img_height
        print(f"ori x1 {x1} y1 {y1} x2 {x2} y2 {y2} img_width {img_width} img_height {img_height}")
        a = a/10
        d = d/10
        # 对左上角和右下角点进行变换
        x1_new = a * x1 + c * y1 + (e )
        y1_new = b * x1 + d * y1 + (f)
        x2_new = a * x2 + c * y2 + (e)
        y2_new = b * x2 + d * y2 + (f)
        print(f"x1_new {x1_new} y1_new {y1_new} x2_new {x2_new} y2_new {y2_new}")
        # 计算变换后矩形的宽和高
        w_new = x2_new - x1_new
        h_new = y2_new - y1_new

        print(f"原始矩形宽度: {img_width}, 高度: {img_height}")
        print(f"变换后矩形宽度: {w_new}, 高度: {h_new}")
        return x1_new, y1_new, w_new, h_new

    def draw_img(self, canvas, img_list, images, page_size):
        """写入图片"""
        c = canvas
        for img_d in img_list:
            image = images.get(img_d["ResourceID"])

            if not image or image.get("suffix").upper() not in self.SupportImgType:
                continue

            imgbyte = base64.b64decode(image.get('imgb64'))
            if not imgbyte:
                logger.error(f"{image['fileName']} is null")
                continue

            img = PILImage.open(BytesIO(imgbyte))
            img_width, img_height = img.size
            # img_width = img_width / self.OP *25.4
            # img_height = img_height / self.OP *25.4
            info = img.info
            # print( f"ing info dpi {info.get('dpi')}")
            # print(img_width, img_height)
            imgReade = ImageReader(img)
            CTM = img_d.get('CTM')
            # print("CTM", CTM)

            wrap_pos = img_d.get("wrap_pos")
            # wrap_pos = img_d.get("wrap_pos")
            pos = img_d.get('pos')
            print("pos", pos,"wrap_pos", wrap_pos,"CTM", CTM)
            # CTM =None
            if CTM and not wrap_pos and page_size == pos:
                x1_new, y1_new, w_new, h_new = self.compute_ctm(CTM, 0, 0, img_width, img_height)
                pdf_pos = [pos[0] * self.OP, pos[1] * self.OP, pos[2] * self.OP, pos[3] * self.OP]
                print(f"pos: {pos} pdf_pos: {pdf_pos}")

                x1_new = (pos[0] + x1_new) * self.OP
                y1_new = (page_size[3] - y1_new) * self.OP
                if w_new >pdf_pos[2]:
                    w_new = pdf_pos[2]
                if h_new >pdf_pos[3]:
                    h_new = pdf_pos[3]
                print(f"写入 {x1_new} {y1_new} {w_new} {-h_new}")
                c.drawImage(imgReade, x1_new, y1_new, w_new, -h_new, 'auto')
            else:
                x_offset = 0
                y_offset = 0

                x = (pos[0] + x_offset) * self.OP
                y = (page_size[3] - (pos[1] + y_offset)) * self.OP
                if wrap_pos:
                    x = x + (wrap_pos[0] * self.OP)
                    y = y - (wrap_pos[1] * self.OP)
                    w = img_d.get('pos')[2] * self.OP
                    h = -img_d.get('pos')[3] * self.OP

                    # print(x, y, w, h)
                    c.drawImage(imgReade, x, y, w, h, 'auto')
                elif pos:
                    print(f"page_size == pos :{page_size == pos} ")
                    x = pos[0] * self.OP
                    y = (page_size[3] - pos[1]) * self.OP
                    w = pos[2] * self.OP
                    h = -pos[3] * self.OP

                    # print(x, y, w, h)
                    # print("pos",pos[0],pos[1],pos[2]* self.OP,pos[3]* self.OP)
                    # print(x2_new, -y2_new, w_new, h_new,)

                    c.drawImage(imgReade, x, y, w, h, 'auto')
                    # c.drawImage(imgReade,x2_new, -y2_new, w_new, h_new, 'auto')

    def draw_signature(self, canvas, signatures_page_list, page_size):
        """
        写入签章
            {
            "sing_page_no": sing_page_no,
            "PageRef": PageRef,
            "Boundary": Boundary,
            "SignedValue": self.file_tree(SignedValue),
                            }
        """
        c = canvas
        try:
            if signatures_page_list:
                # print("signatures_page_list",signatures_page_list)
                for signature_info in signatures_page_list:
                    image = SealExtract()(b64=signature_info.get("SignedValue"))
                    if not image:
                        logger.info(f"提取不到签章图片")
                        continue
                    else:
                        image_pil = image[0]

                    pos = [float(i) for i in signature_info.get("Boundary").split(" ")]

                    imgReade = ImageReader(image_pil)

                    x = pos[0] * self.OP
                    y = (page_size[3] - pos[1]) * self.OP

                    w = pos[2] * self.OP
                    h = -pos[3] * self.OP
                    c.drawImage(imgReade, x, y, w, h, 'auto')
                    print(f"签章写入成功")
            else:
                # 无签章
                pass
        except Exception as e:
            print(f"签章写入失败 {e}")
            traceback.print_exc()

    def draw_line_old(self, canvas, line_list, page_size):
        """绘制线条"""

        # print("绘制",line_list)

        def match_mode(Abbr: list):
            """
            解析AbbreviatedData
            匹配各种线条模式
            S 定义起始 坐标 x, y
            M 移动到指定坐标 x, y
            L 从当前点移动到指定点 x, y
            Q x1 y1 x2 y2 二次贝塞尔曲线
            B x1 y1 x2 y2 x3 y3 三次贝塞尔曲线
            A 到 x,y 的圆弧 并移动到 x,y  rx 长轴 ry 短轴 angle 旋转角度 large为1表示 大于180 的弧 为0时表示小于180的弧 swcpp 为1 表示顺时针旋转 0 表示逆时针旋转
            C 当前点和SubPath自动闭合
            """
            relu_list = []
            mode = ""
            modes = ["S", "M", "L", "Q", "B", "A", "C"]
            mode_dict = {}
            for idx, i in enumerate(Abbr):
                if i in modes:
                    mode = i
                    if mode_dict:
                        relu_list.append(mode_dict)
                    mode_dict = {"mode": i, "points": []}

                else:
                    mode_dict["points"].append(i)

                if idx + 1 == len(Abbr):
                    relu_list.append(mode_dict)
            return relu_list

        def assemble(relu_list: list):
            start_point = {}
            acticon = []
            for i in relu_list:
                if i.get("mode") == "M":
                    start_point = i
                elif i.get("mode") in ['B', "Q", 'L']:
                    acticon.append({"start_point": start_point,
                                    "end_point": i
                                    })
            return acticon

        def convert_coord(p_list, direction, page_size, pos):
            """坐标转换ofd2pdf"""
            new_p_l = []
            for p in p_list:
                if direction == "x":

                    new_p = (float(pos[0]) + float(p)) * self.OP
                else:
                    new_p = (float(page_size[3]) - float(pos[1]) - float(p)) * self.OP
                new_p_l.append(new_p)
            return new_p_l

        for line in line_list:
            Abbr = line.get("AbbreviatedData").split(" ")  # AbbreviatedData 
            color = line.get("FillColor", [0, 0, 0])

            relu_list = match_mode(Abbr)
            # TODO 组合 relu_list 1 M L 直线 2 M B*n 三次贝塞尔线 3 M Q*n 二次贝塞尔线

            # print(relu_list)

            acticons = assemble(relu_list)
            pos = line.get("pos")
            # print(color)
            if len(color) < 3:
                color = [0, 0, 0]
            canvas.setStrokeColorRGB(*(int(color[0]) / 255, int(color[1]) / 255, int(color[2]) / 255))  # 颜色

            # 设置线条宽度
            try:
                LineWidth = (float(line.get("LineWidth", "0.25").replace(" ", "")) if \
                                 line.get("LineWidth", "0.25").replace(" ", "") else 0.25) * self.OP
            except Exception as e:
                logger.error(f"{e}")
                LineWidth = 0.25 * self.OP

            canvas.setLineWidth(LineWidth)  # 单位为点，2 表示 2 点

            for acticon in acticons:
                if acticon.get("end_point").get("mode") == 'L':  # 直线
                    x1, y1, x2, y2 = *acticon.get("start_point").get("points"), *acticon.get("end_point").get("points")
                    x1, x2 = convert_coord([x1, x2], "x", page_size, pos)
                    y1, y2 = convert_coord([y1, y2], "y", page_size, pos)
                    # 绘制一条线 x1 y1 x2 y2
                    canvas.line(x1, y1, x2, y2)

                elif acticon.get("end_point").get("mode") == 'B':  # 三次贝塞尔线
                    continue
                    x1, y1, x2, y2, x3, y3, x4, y4 = *acticon.get("start_point").get("points"), *acticon.get(
                        "end_point").get("points")
                    x1, x2, x3, x4 = convert_coord([x1, x2, x3, x4], "x", page_size, pos)
                    y1, y2, y3, y4 = convert_coord([y1, y2, y3, y4], "y", page_size, pos)
                    # print(x1, y1, x2, y2, x3, y3, x4, y4)

                    # 绘制三次贝塞尔线
                    canvas.bezier(x1, y1, x2, y2, x3, y3, x4, y4)

                elif acticon.get("end_point").get("mode") == 'Q':  # 二次贝塞尔线
                    pass
                else:
                    continue

    def draw_line(self, canvas, line_list, page_size):
        def match_mode(Abbr: list):
            """
            解析AbbreviatedData
            匹配各种线条模式
            S 定义起始 坐标 x, y
            M 移动到指定坐标 x, y
            L 从当前点移动到指定点 x, y
            Q x1 y1 x2 y2 二次贝塞尔曲线 从当前点连接一条到点(x2,y2)的二次贝塞尔曲线，并将当前点移动到点(x2,y2)，此贝塞尔曲线使用点(x1,y1)作为其控制点。
            B x1 y1 x2 y2 x3 y3 三次贝塞尔曲线 从当前点连接一条到点(x3,y3)的三次贝塞尔曲线，并将当前点移动到点(x3,y3)，此贝塞尔曲线使用点(x1,y1)和点(x2,y2)作为其控制点。
            A Are 操作数为rx ry angle large sweep x y，从当前点连接一条到点(x,y)的圆弧，并将当前点移动到点(x,y)。
            其中，rx表示椭圆的长轴长度，ry表示椭圆的短轴长度，angle表示椭圆在当前坐标系下旋转的角度，正值为顺时针，
            负值为逆时针，large为 1 时表示对应度数大于 180° 的弧，为 0 时表示对应度数小于 180° 的弧，
            sweep为 1 时表示由圆弧起始点到结束点是顺时针旋转，为 0 时表示由圆弧起始点到结束点是逆时针旋转。
            C 无操作数，其作用是SubPath自动闭合，表示将当前点和SubPath的起始点用线段直接连接。
            """
            relu_list = []
            mode = ""
            modes = ["S", "M", "L", "Q", "B", "A", "C"]
            mode_dict = {}
            for idx, i in enumerate(Abbr):
                if i in modes:
                    mode = i
                    if mode_dict:
                        relu_list.append(mode_dict)
                    mode_dict = {"mode": i, "points": []}

                else:
                    mode_dict["points"].append(i)

                if idx + 1 == len(Abbr):
                    relu_list.append(mode_dict)
            return relu_list

        def assemble(relu_list: list):
            start_point = {}
            acticon = []

            for i in relu_list:
                if i.get("mode") == "M":
                    if not start_point:
                        start_point = i
                    acticon.append({
                        "start_point": start_point,"end_point": i})

                elif i.get("mode") in ['B', "Q", 'L']:
                    acticon.append({"start_point": start_point,
                                    "end_point": i
                                    })
                elif i.get("mode") == "C":
                    acticon.append({"start_point": start_point,
                                    "end_point": i
                                    })
                elif i.get("mode") == "A":
                    acticon.append({"start_point": start_point,
                                    "end_point": i
                                    })
                elif i.get("mode") == "S":
                    start_point = i

            return acticon

        def convert_coord(p_list, direction, page_size, pos):
            """坐标转换ofd2pdf"""
            new_p_l = []
            # print("p_list", p_list)
            for p in p_list:
                if direction == "x":
                    new_p = (float(pos[0]) + float(p)) * self.OP
                else:
                    new_p = (float(page_size[3]) - float(pos[1]) - float(p)) * self.OP
                new_p_l.append(new_p)
            # print("new_p_l", new_p_l)
            return new_p_l

        for line in line_list:
            path = canvas.beginPath()
            Abbr = line.get("AbbreviatedData").split(" ")  # AbbreviatedData
            color = line.get("FillColor", [0, 0, 0])

            relu_list = match_mode(Abbr)
            # TODO 组合 relu_list 1 M L 直线 2 M B*n 三次贝塞尔线 3 M Q*n 二次贝塞尔线

            # print(relu_list)

            acticons = assemble(relu_list)
            pos = line.get("pos")
            # print(color)
            if len(color) < 3:
                color = [0, 0, 0]
            canvas.setStrokeColorRGB(*(int(color[0]) / 255, int(color[1]) / 255, int(color[2]) / 255))  # 颜色

            # 设置线条宽度
            try:
                LineWidth = (float(line.get("LineWidth", "0.25").replace(" ", "")) if \
                                 line.get("LineWidth", "0.25").replace(" ", "") else 0.25) * self.OP
            except Exception as e:
                logger.error(f"{e}")
                LineWidth = 0.25 * self.OP

            canvas.setLineWidth(LineWidth)  # 单位为点，2 表示 2 点
            cur_point = []
            for acticon in acticons:
                if acticon.get("end_point").get("mode") == 'M':
                    x, y = acticon.get("end_point").get("points")
                    x = convert_coord([x], "x", page_size, pos)[0]
                    y = convert_coord([y], "y", page_size, pos)[0]
                    cur_point = [x, y]
                    path.moveTo(x, y)

                elif acticon.get("end_point").get("mode") == 'L':  # 直线
                    x, y = acticon.get("end_point").get("points")
                    x = convert_coord([x], "x", page_size, pos)[0]
                    y = convert_coord([y], "y", page_size, pos)[0]
                    path.lineTo(x, y)


                elif acticon.get("end_point").get("mode") == 'B':  # 三次贝塞尔线
                    x1, y1, x2, y2, x3, y3 = acticon.get("end_point").get("points")
                    # print(x1, y1, x2, y2, x3, y3)
                    x1, x2,x3 = convert_coord([x1, x2,x3], "x", page_size, pos)
                    y1, y2,y3 = convert_coord([y1, y2,y3], "y", page_size, pos)
                    cur_point = [x2, y2]
                    path.curveTo(x1, y1, x2, y2, x3, y3)
                    path.moveTo(x3, y3)

                elif acticon.get("end_point").get("mode") == 'Q':  # 二次贝塞尔线
                    x1, y1, x2, y2 = acticon.get("end_point").get("points")
                    x1, x2 = convert_coord([x1, x2], "x", page_size, pos)
                    y1, y2 = convert_coord([y1, y2], "y", page_size, pos)
                    cur_point = [x2, y2]
                    path.curveTo(x1, y1, x2, y2, x2, y2)
                    path.moveTo(x2, y2)
                elif acticon.get("end_point").get("mode") == 'A':  # 圆弧线
                    x1, y1 = acticon.get("start_point").get("points")
                    rx, ry, startAng, large_arc_flag, sweep_flag, x2, y2 = acticon.get("end_point").get("points")
                    rx_o = rx
                    ry_o = ry

                    x1,x2,rx = convert_coord([x1,x2,rx], "x", page_size, pos)
                    y1,y2,ry = convert_coord([y1,y2,ry], "y", page_size, pos)

                    cur_x,cur_y=cur_point

                    # 绘制圆弧 有问题
                    if rx_o==ry_o:
                        # path.circle(cur_x,cur_y, 20) # 圆
                        path.circle(rx,ry, 20) # 圆 # 莫名其妙的圆
                    else:
                        print(rx, ry, x2, y2, startAng, large_arc_flag, sweep_flag)
                        path.ellipse(rx, ry,20, 20, ) # 椭圆
                    # path.arc(rx, ry, x2, y2, startAng=int(startAng), extent=int(sweep_flag))
                    # path.ellipse(rx, ry,x2, y2, ) # 椭圆
                    # path.curveTo(rx, ry ,x2, y2, startAng=int(startAng), extent=int(sweep_flag))
                    path.moveTo(x2, y2)
                    cur_point = [x2,y2]

                elif acticon.get("end_point").get("mode") == 'C':
                    # canvas.drawPath(path)
                    path.close()
            canvas.drawPath(path)

    def draw_annotation(self, canvas, annota_info, images, page_size):
        """
        写入注释 暂只看到签章图片 有其他的再加入
        """
        img_list = []
        for key, annotation in annota_info.items():
            if annotation.get("AnnoType").get("type") == "Stamp":
                pos = annotation.get("ImgageObject").get("Boundary","").split(" ")
                pos = [float(i) for i in pos] if pos else []
                wrap_pos = annotation.get("Appearance").get("Boundary","").split(" ")
                wrap_pos = [float(i) for i in wrap_pos] if wrap_pos else []
                CTM = annotation.get("ImgageObject").get("CTM","").split(" ")
                CTM = [float(i) for i in CTM] if CTM else []
                img_list.append({
                    "wrap_pos": wrap_pos,
                    "pos": pos,
                    "CTM": CTM,
                    "ResourceID": annotation.get("ImgageObject").get("ResourceID",""),
                })
        self.draw_img( canvas, img_list, images, page_size)
        
    def draw_pdf(self):

        c = canvas.Canvas(self.pdf_io)
        c.setAuthor(self.author)

        for doc_id, doc in enumerate(self.data, start=0):
            # print(1)
            fonts = doc.get("fonts")
            images = doc.get("images")
            default_page_size = doc.get("default_page_size")
            page_size_details = doc.get("page_size")
            print("page_size_details", page_size_details)
            signatures_page_id = doc.get("signatures_page_id")  # 签证信息
            annotation_info = doc.get("annotation_info")  # 注释信息

            # 注册字体
            for font_id, font_v in fonts.items():
                file_name = font_v.get("FontFile")
                font_b64 = font_v.get("font_b64")
                if font_b64:
                    self.font_tool.register_font(os.path.split(file_name)[1], font_v.get("@FontName"), font_b64)
            # text_write = []
            # print("doc.get(page_info)", len(doc.get("page_info")))
            for pg_no, page in doc.get("page_info").items():
                print(f"pg_no: {pg_no} page_size_details: {page_size_details}")
                if len(page_size_details) > pg_no and page_size_details[pg_no]:
                    page_size = page_size_details[pg_no]
                else:
                    page_size = default_page_size
                # logger.info(f"page_id {page_id} page_size {page_size}")
                text_list = page.get("text_list")
                img_list = page.get("img_list")
                line_list = page.get("line_list")
                # print("img_list",img_list)

                c.setPageSize((page_size[2] * self.OP, page_size[3] * self.OP))

                # 写入图片
                if img_list:
                    self.draw_img(c, img_list, images, page_size)

                # 写入文本
                if text_list:

                    self.draw_chars(c, text_list, fonts, page_size)

                # 绘制线条
                if line_list:
                    self.draw_line(c, line_list, page_size)

                # 绘制签章
                if signatures_page_id:
                    self.draw_signature(c, signatures_page_id.get(pg_no), page_size)
                # 绘制注释
                if annotation_info and pg_no in annotation_info:
                    self.draw_annotation(c, annotation_info.get(pg_no),images, page_size)
                
                # 页码判断逻辑 # print(doc_id,len(self.data))
                if pg_no != len(doc.get("page_info")) - 1 and doc_id != len(self.data):
                    # print("写入")
                    c.showPage()
                    # json.dump(text_write,open("text_write.json","w",encoding="utf-8"),ensure_ascii=False)

        c.save()

    def __call__(self):
        try:
            self.draw_pdf()
            pdfbytes = self.pdf_io.getvalue()
        except Exception as e:
            logger.error(f"{e}")
            logger.error(f"ofd解析失败")
            traceback.print_exc()
            self.gen_empty_pdf()
            pdfbytes = self.pdf_io.getvalue()
        return pdfbytes
