# -*- coding: utf-8 -*-

"""
# @Time    : 2022/11/14 0014 16:11
# @Author  : Silva
# @File    : pdf_parse_nice.py
"""

import os
import re
import json
import time
import copy
import string
import random
from uuid import uuid1
from decimal import Decimal
from collections import OrderedDict
# 第三方包
import fitz
from PIL import Image
# import pdfplumber

__ALL__ = ['pdf_ocr',"DPFParser"]

class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return str(obj)
        elif isinstance(obj, Decimal):
            return float(obj)
        return json.JSONEncoder.default(self, obj)

class DPFParser(object):
    def __init__(self, ):
        pass
    def to_img(self,buffer_pdf):
        pix_list = []
        pdfDoc = fitz.open(stream=buffer_pdf)
        for pg in range(pdfDoc.page_count):
            page = pdfDoc[pg]
            rotate = int(0)
            # 每个尺寸的缩放系数为1.3，这将为我们生成分辨率提高2.6的图像。
            # 此处若是不做设置，默认图片大小为：792X612, dpi=96
            zoom_x = 1.33333333 #(1.33333333-->1056x816)   (2-->1584x1224)
            zoom_y = 1.33333333
            # zoom_x,zoom_y = (1,1)
            mat = fitz.Matrix(zoom_x, zoom_y).prerotate(rotate)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            pix_list.append(pix)
        return pix_list
           
            
            
    def get_size(self):
        pass
    
def coast_time(func):
    '''
    计算对象执行耗时
    '''
    def fun(*agrs, **kwargs):
        t = time.perf_counter()
        result = func(*agrs, **kwargs)
        print(f'function {func.__name__} coast time: {time.perf_counter() - t:.8f} s')
        return result
    return fun


class BaseInit:
    '''
    解析pdf所需的基本信息
    '''

    def __init__(self, pdf_path, output_path):

        self.file_path = pdf_path
        self.output_path = output_path
        # file_name
        self.file_name = os.path.basename(self.file_path)
        # file_type
        self.fileType = os.path.splitext(self.file_path)[-1]
        # no suffix
        self.file_no_suffix = self.file_name[:-len(self.fileType)]
        self.uuidChars = tuple(list(string.ascii_letters) + list(range(10)))
        # 表格占位、分割符
        self.divide = ':'
        self.solid = ''
        # 初始化整个过程需要创建的中间目录
        # iou 占比
        self.iou_rate = 0.001
        self.init_file()

    def init_file(self):
        """
        初始化项目过程中需要创建的文件夹
        """
        self.image_folder_path = os.path.join(self.output_path, 'pdf_img_save')
        self.json_folder_path = os.path.join(self.output_path, 'json')
        self.ocr_result_path = os.path.join(self.json_folder_path, self.file_no_suffix + '.json')
        # 后面还有txt..., 目前的流程先需要5个
        for path in [self.image_folder_path, self.json_folder_path]:
            if not os.path.exists(path):
                os.makedirs(path)

    def genShortId(self, length=12):
        """
        :params length: 默认随机生成的uuid长度
        """
        uuid = str(uuid1()).replace('-', '')
        result = ''
        for i in range(0, 8):
            sub = uuid[i * 4: i * 4 + 4]
            x = int(sub, 16)
            result += str(self.uuidChars[x % 0x3E])
        return result + ''.join(random.sample(uuid, length - 8))


class PageInfo(BaseInit):
    '''
    记录每页中的 图片和表格信息
    '''
    __page_image = {}
    __page_table = {}

    @classmethod
    def add_image(cls, page_num, image):
        if not cls.__page_image.get(page_num):
            cls.__page_image[page_num] = []
        cls.__page_image[page_num].append(image)

    @classmethod
    def add_table(cls, page_num, table):
        if not cls.__page_table.get(page_num):
            cls.__page_table[page_num] = []
        cls.__page_table[page_num].append(table)

    @classmethod
    def get_image(cls, page_num):
        return cls.__page_image.get(page_num, [])

    @classmethod
    def get_table(cls, page_num):
        return cls.__page_table.get(page_num, [])

    @classmethod
    def save_image(cls, output_path, file):
        '''
        保存图片至本地
        :param output:
        :return:
        '''
        file = file.split('.')[0]
        for images in cls.__page_image.values():
            for image in images:
                iamge_content = image['objContent']
                name = image['name']
                img_dir = os.path.join(output_path, 'page_img_save')
                img_path = os.path.join(img_dir, file + '_' + name + '.jpg')
                if not os.path.exists(img_dir):
                    os.mkdir(img_dir)
                with open(img_path, 'wb') as fp:
                    fp.write(iamge_content)


class ParseFile(PageInfo):

    def __init__(self, pdf_path, output_path, table_type='v2', is_save=True):
        super().__init__(pdf_path, output_path)
        print('初始化 pdf 对象：{}'.format(self.file_path))
        self.is_save = is_save
        self.table_type = table_type
        # 第一版结果列表： 行 表分开
        self.page_result_list = []
        # 第二版结果列表： 行表合并
        self.combine_page_result_list = []

    @coast_time
    def get_result(self):
        self.load_pdf()
        result = self.parse_pdf()
        self.ocr_result = result
        print(f'解析完成：共 {len(result)} 页  表格类型： {self.table_type}')
        return result

    def load_pdf(self):
        self.fitz_doc = fitz.open(self.file_path, filetype='pdf')
        # self.pdfplum_doc_pages = pdfplumber.open(self.file_path).pages
        # assert len(self.fitz_doc) == len(self.pdfplum_doc_pages)

    def parse_pdf(self):
        for page_no, fitz_doc in enumerate(self.fitz_doc):
            # 测试
            # if page_no != 25:
            #     continue
            self.height = fitz_doc.get_text('dict')['height']
            self.width = fitz_doc.get_text('dict')['width']
            # 聚合fitz页面解析的字符, 行, 块信息
            line_list = self.group_block(page_no, fitz_doc)
            # 获取页面表格信息
            table_list = self.extract_table(page_no, self.pdfplum_doc_pages[page_no])
            # 计算表格行列合并信息
            table_list = list(CalcTableRL(table_list).run())
            # 获取页面图片信息
            image_list = self.get_image(page_no)
            # 构造每页最终返回结果，
            page_result = self.construct_final_result(line_list, page_no, image_list, table_list)

            if self.table_type == 'v2':
                # 合并成ocr所需格式：表格合并至行列表
                combine_page_result_list = self.combine_table_v2(page_result)
                page_result = self.construct_final_result(combine_page_result_list, page_no, image_list, table_list)

            self.page_result_list.append(page_result)
            if page_no and  page_no % 10 == 0:
                print(f'解析前 {page_no} 页完成')
        final_result_list = copy.deepcopy(self.page_result_list)
        # 转换为符合ocr解析格式
        if self.table_type == 'v2':
            final_result_list = self.reform_ocr_result(final_result_list)
        # 2023/09/26 保存之前加入 contIndex 给后续 抽取模型使用
        for page_num, page in enumerate(final_result_list):
            if not page.get('lineList'):
                break
            contIndex = {}
            for line in page['lineList']:
                line_bak = dict(copy.copy(line))
                line_bak["objType_postpreprocess"] = f"{line_bak.get('objType','textLine')}_postpreprocess"
                contIndex[line_bak["lineId"]] = line_bak
            
            page["contIndex"] = contIndex
            for line in page['lineList']:
                print(page_num, line['objType'], line['objContent'])
        # 保存至本地
        if self.is_save:
            self.save_result(final_result_list)
        for page_num, page in enumerate(final_result_list):
            for line in page['lineList']:
                print(page_num, line['objType'], line['objContent'])
        return final_result_list

    def combine_table_v2(self, page_result):
        lineList = page_result['lineList']
        table_list = page_result['table_list']
        # 先进行表格行、非表格行划分 减少后续操作的时间杂度
        __notable_lines, __all_table_lines = self.filter_table_line(lineList, table_list)
        notable_lines, all_table_lines = copy.deepcopy(__notable_lines), copy.deepcopy(__all_table_lines)
        del __notable_lines, __all_table_lines, lineList
        # 整合
        combine_page_result_list = self.combine_table_with_line(notable_lines, all_table_lines, table_list)
        return combine_page_result_list

    def filter_table_line(self, lineList, table_list):
        '''
        筛选出属于表格的行、在 __notable_lines 属于表格的位置插庄 方便后续补全
        __notable_lines： 非表格的行
        __all_table_lines：属于表格的行
        '''
        __notable_lines = []
        __all_table_lines = []
        for table_info in table_list:
            table_bbox = table_info['objPos']
            # 属于当前表格的所有行
            __sub_table_lines = []
            is_iter_table = False
            while lineList:
                line = lineList.pop(0)
                line_bbox = line['objPos']
                # 空表格误判：行Y坐标已经超过表范围导致后续全都识别不到
                table_y, line_y = table_bbox[3], line_bbox[1]
                if line_y >= table_y:
                    lineList.insert(0, line)
                    break
                iou = self.count_iou(table_bbox, line_bbox)
                # 非表格区域
                if iou > 0:
                    __sub_table_lines.append(line)
                    # 首次匹配到表格行
                    if not is_iter_table:
                        is_iter_table = True
                        # 插入标记
                        __notable_lines.append('table')
                elif iou <= 0 and not is_iter_table:
                    __notable_lines.append(line)
                # 当前表格判断结束
                elif iou <= 0 and is_iter_table:
                    lineList.insert(0, line)
                    line_index, flag = self.more_judge(table_bbox, lineList)
                    if flag:
                        # 跳至index位置继续后续判断
                        # more_lines = copy.deepcopy()
                        __notable_lines.extend(lineList[:line_index])
                        lineList = lineList[line_index:]
                    else:
                        break
            __all_table_lines.append(__sub_table_lines)
        # 表格遍历替换完毕, 合并剩下的 page_words
        if lineList:
            __notable_lines.extend(lineList)
        return __notable_lines, __all_table_lines

    def more_judge(self, table_bbox, lineList, max_judge=6):
        '''
        判断后续行列表是否还存在属于当前表格的行
        对于表格、行界限不明显的额外判断 如： 页面分栏、表格不全
        :return 是否存在 True | False
        '''
        # 往后多判断 max_judge 行
        if len(lineList) < max_judge:
            judge_lines = lineList
        else:
            judge_lines = lineList[:max_judge]
        for index, line in enumerate(judge_lines):
            line_bbox = line['objPos']
            iou = self.count_iou(table_bbox, line_bbox)
            if iou > 0:
                return index, True
        return index, False


    def combine_table_with_line(self, notable_lines, all_table_lines, table_list):
        '''
        将行、字符合并至对应的表格行、cell
        '''
        for table_id, table in enumerate(table_list):
            new_table_lines = []
            for table_line in table['lineList']:
                is_iter_table = False
                table_line_bbox = table_line['objPos']
                # 遍历每一行：全局匹配
                for __line in all_table_lines[table_id]:
                    line = copy.deepcopy(__line)
                    line_bbox = line['objPos']
                    iou = self.count_iou(table_line_bbox, line_bbox)
                    # 首次识别到表格， 将文本行的文本、坐标替换为表格行文本、坐标，文本行的其他信息不变
                    if iou > self.iou_rate and not is_iter_table:
                        is_iter_table = True
                        line['objContent'] = table_line['objContent']
                        line['objPos'] = table_line['objPos']
                        line['objType'] = 'table'
                        line['tableId'] = table_id
                        self.combine_cell_with_span(table_line, line)
                        line['cells'] = table_line['cells']
                        new_table_lines.append(line)
                    elif iou > self.iou_rate and is_iter_table:
                        self.combine_cell_with_span(table_line, line)
                    else:
                        pass
            if 'table' not in notable_lines or not new_table_lines:
                # FIX ERROR: 'table' is not in list
                # 处理大表格内识别到小表格的情况
                # 有可能的bug：如果此时有多个大表格嵌套会导致行分配和插庄个数不对等
                continue
            # 将表格行new_table_lines替换之前插庄table位置并展开
            table_index = notable_lines.index('table')
            new_notable_lines = notable_lines[:table_index]
            new_notable_lines.extend(new_table_lines)
            notable_lines = new_notable_lines + notable_lines[table_index+1:]
        return notable_lines

    def combine_cell_with_span(self,table_line , text_line):
        '''
        将表格的cell内加上对应span的chars信息：解决表格合并时cell有多行导致chars顺序错乱的问题
        '''
        del_list = []
        for index, cell in enumerate(table_line['cells']):
            if not cell.get('chars'):
                cell['chars'] = []
            cell_bbox = cell['objPos']
            if cell_bbox is None:
                del_list.append(index)
                continue
            for span in  text_line['span']:
                span_bbox = span['bbox']
                iou = self.count_iou(cell_bbox, span_bbox)
                if iou < self.iou_rate:
                    continue
                # 为了解决一些 span 和 cell 长度不一致问题 将循环细分到每个字符chars
                for char in span['chars']:
                    char_bbox = char['bbox']
                    iou = self.count_iou(cell_bbox, char_bbox)
                    if iou > self.iou_rate:
                        cell['chars'].append(char)
                    else:
                        pass
        # 清除无效的span
        if len(del_list):
            for index, index_del in enumerate(del_list):
                index_del -= index
                del table_line['cells'][index_del]

    def group_block(self, page_num, fitz_doc):
        """
        组合两个方法的block信息, 使每一个span内具有其每一个字符信息
        参考官方文档：https://pymupdf.readthedocs.io/en/latest/textpage.html#textpagedict
        :param fitz_doc:
        :return: total_info
        """
        line_count = 0
        total_line_list = []
        # char_blocks 最小粒度为每一个字符
        char_blocks = fitz_doc.get_text('rawdict')['blocks']
        # block_blocks 最小粒度为每行中的span
        block_blocks = fitz_doc.get_text('dict')['blocks']
        # 先进行文本块排序
        char_blocks.sort(key=lambda x: [int(x['bbox'][1]), int(x['bbox'][0])])
        block_blocks.sort(key=lambda x: [int(x['bbox'][1]), int(x['bbox'][0])])
        # 分组聚合
        group_blocks = zip(block_blocks, char_blocks)
        for span_blocks, char_block in group_blocks:
            if span_blocks['type'] == 1:
                # 保存其中的图片
                img_attrs = self.deal_image(page_num, line_count, span_blocks)
                self.add_image(page_num, img_attrs)
                continue
            for line_index, line in enumerate(span_blocks['lines']):
                line['text'] = ''
                line['chars'] = []
                line['span'] = []
                # 减少时间复杂度，在此处合并每一行
                # 合并每一行，并附上行内每一个字符的信息
                for span_index, span in enumerate(line['spans']):
                    span['text'] = span['text'].replace(' ', '').strip()
                    if not span['text']:
                        continue
                    # 给span_blocks中的span加上char_block的chars信息
                    span_chars = char_block['lines'][line_index]['spans'][span_index]['chars']
                    span_chars = [char for char in span_chars if char['c'].strip()]
                    line['text'] += span['text']
                    line['chars'].extend(span_chars)
                    line['span'].append({'bbox': span['bbox'], 'chars': span_chars,'text': span['text']})
                if not line['text']:
                    continue
                # 构造每行内部的数据结构
                line_info = self.construct_line_info(line['text'], line['bbox'], line['span'], line['chars'],
                                                     line_count, page_num)
                total_line_list.append(line_info)
                line_count += 1
        return total_line_list

    def extract_table(self, page_no, plum_page):
        '''
        提取页面所有表格
        :param page_no:
        :param plum_page:
        :return:
        '''
        table_list = []
        for table in plum_page.find_tables():
            # 获取当前表格的边界定位
            table_line_list = self.merge_table_row(table)
            if not table_line_list:
                continue
            table_info = self.deal_table(page_no, table.bbox, table_line_list)
            table_list.append(table_info)
            # 将表格信息加入全局变量 | 此处有点有点冗余
            self.add_table(page_no, table_info)
        return table_list

    def merge_table_row(self, table):
        '''
        表格cell 按行合并
        :param table:
        :return: [({line_text}, {line_bbox}), ...]
        '''
        table_line_list = []
        for item, row in zip(table.extract(), table.rows):
            # 表格每行预处理
            table_line = self.divide.join([self.clear_text(txt) for txt in item])
            # 判断当前行是否为空
            __line = self.clear_text(table_line).replace(' ', '')
            if not __line:
                continue
            table_line_list.append((table_line, row.bbox, zip(item, row.cells)))
        return table_line_list

    def clear_text(self, txt, retrans=False):

        if retrans:
            txt = txt.replace(self.solid, '').replace(self.divide, '')
        else:
            # 空列替换为占位符
            txt = txt if txt else self.solid
        return str(txt).replace('\n', '').replace(' ', '')

    def deal_table(self, page_no, table_bbox, table_line_list):
        '''
        对表格做结构转换
        :param page_no:
        :param table_bbox:
        :param table_line_list:
        :return:
        '''
        table_first_line = self.clear_text(table_line_list[0][0], retrans=True)
        table_id = '{0}_{1}_'.format(page_no, table_first_line) + self.genShortId()
        lineList = [{
            'objContent': line[0],
            'objPos': line[1],
            'cells': self.deal_table_cell(line[2])
        } for line in table_line_list]
        table_info = {
            'tableId': table_id,
            'name': table_id,
            'objPos': table_bbox,
            'lineList': lineList,
        }
        return table_info

    def deal_table_cell(self, cells):
        return [{"objContent": self.clear_text(text), "objPos": box} for text, box in cells]

    def deal_image(self, page_num, name, img_attrs):
        '''
        对image做结构转换
        :param page_num:
        :param name:
        :param img_attrs:
        :return:
        '''
        image_id = '{0}_{1}_'.format(page_num, name) + self.genShortId()
        img_info = {
            'imageId': image_id,
            'name': image_id,  # 暂时以图片所在页面的行数命名
            'objPos': img_attrs['bbox'],
            'ext': img_attrs['ext'],
            'objContent': img_attrs['image'],
            'size': img_attrs['size']
        }
        return img_info

    def deal_chars(self, line_num, lineId, chars):
        '''
        对chars做结构转换
        :param line_num:
        :param lineId:
        :param chars:
        :return:
        '''
        num_count = 0
        char_list = []
        for char in chars:
            if not char['c'].strip():
                continue
            char_dict = {
                'lineId': lineId,
                'charId': 'char_' + str(line_num) + '_' + str(num_count) + '_' + self.genShortId(),
                'objContent': char['c'],
                'objPos': char['bbox']
            }
            char_list.append(char_dict)
            num_count += 1
        return char_list

    def construct_line_info(self, text, rect, span, chars, count, pageNo, objType='textLine'):
        '''
        对每行做结构转换
        # x, y, h, w = rect[0], rect[1], rect[3] - rect[1], rect[2] - rect[0]
        '''
        lineId = 'line_' + str(pageNo) + '_' + str(count) + '_' + self.genShortId()
        chars = self.deal_chars(count, lineId, chars)
        return OrderedDict({
            'lineNo': count,
            'lineId': lineId,
            'objType': objType,
            'objContent': re.sub(r'\s', '', text),
            'chars': chars,
            'objPos': rect,
            'span': span
        })

    @staticmethod
    def rect_format(bbox):
        '''
        数据坐标转换 x1, y1, x2, y2 >> y1, x1 h, w
        :param rect: [x1, y1, x2, y2]
        :return: [y, x, h, w]
        '''
        y, x, h, w = bbox[1], bbox[0], bbox[3] - bbox[1], bbox[2] - bbox[0]
        return [y, x, h, w]

    def count_iou(self, RecA, RecB):
        '''
        计算边框交并比
        左上边界坐标为Ax0, Ay0, Bx0, By0
        右下边界坐标为Ax1, Ay1, Bx1, By1
        交集面积计算为：
            M = min(Ax1, Bx1) - max(Ax0, Bx0)
            H = min(Ay1, By1) - max(Ay0, By0)
        # 当前表格的边界信息
        left_x, top_y, right_x, botm_y： table_box_info[0], table_box_info[1], table_box_info[2], table_box_info[3]
        '''
        M = min(RecB[2], RecA[2]) - max(RecB[0], RecA[0])
        H = min(RecB[3], RecA[3]) - max(RecB[1], RecA[1])

        # 计算交集部分面积
        interArea = max(0, M) * max(0, H)

        # 计算两个边框的面积
        RecA_Area = (RecA[2] - RecA[0]) * (RecA[3] - RecA[1])
        RecB_Area = (RecB[2] - RecB[0]) * (RecB[3] - RecB[1])
        # 计算IOU
        iou = interArea / float(RecA_Area + RecB_Area - interArea)
        return iou

    def construct_final_result(self, line_list, pageNo, image_list=[], table_list=[]):
        '''
        每页转换为最终数据结构
        :param line_list: ocr每行结果
        :param pageNo: 页码
        :param image_list:
        :param table_list:
        :return: type: Dict
        '''
        document_id = 'v1' + '_' + self.file_no_suffix + '_' + self.genShortId()
        return OrderedDict({
            'pageNo': pageNo,
            'docID': document_id,
            'page_info':{'size': [self.width, self.height]},
            'lineList': line_list,
            'image_list': image_list if image_list else [],
            'table_list': table_list if table_list else []
        })

    def save_result(self, final_result_list):
        '''
        保存结果数据至本地
        '''
        if self.table_type == 'v2':
            with open(self.ocr_result_path, 'w', encoding='utf-8') as f:
                json.dump(final_result_list, f, indent=4, ensure_ascii=False)
        else:
            with open(self.ocr_result_path, 'w', encoding='utf-8') as f:
                json.dump(self.page_result_list, f, cls=MyEncoder, indent=4, ensure_ascii=False)

    def reform_ocr_result(self, final_result_list):
        """
        对返回的结果最最终处理 并 重新定义行号排序
        :param final_result_list: 本地解析和ocr解析的合并结果
        """
        for result_list in final_result_list:
            del result_list['image_list']
            del result_list['table_list']
            lineList = result_list['lineList']
            for num, line in enumerate(lineList):
                # 重写行号和行ID
                line['lineNo'] = str(num)
                line_split = line['lineId'].split('_')
                line_split[-2] = str(num)
                line['lineId'] = '_'.join(line_split)
                # 转换坐标格式
                obj_type = line['objType']
                # 计算每一个字相对于当前行想x，y 的偏移量
                offset_x_list, offset_y_list = self.coord_offset(line, obj_type)
                line['objPos'] = self.rect_format(line['objPos'])
                line['objPos'].append(offset_x_list)
                line['chars_offset'] = [offset_x_list, offset_y_list]
                if line.get('chars'):
                    del line['chars']
                if obj_type == 'table' and line.get('span'):
                    del line['span']
        return final_result_list

    def coord_offset(self, line, obj_type='textLine'):
        '''
        计算每个字符的左上角 相对行左上角位置的偏移量
        @obj_type: textLine | table
        '''
        offset_x_list = []
        offset_y_list = []
        line_x, line_y = line['objPos'][0], line['objPos'][1]
        if obj_type == 'textLine':
            for span in line['span']:
                self.all_rect_format(span)
                for char in span['chars']:
                    char_x, char_y = char['bbox'][0], char['bbox'][1]
                    offset_x_list.append(char_x - line_x)
                    offset_y_list.append(char_y - line_y)
                    self.all_rect_format(char)
        else:
            __cells = []
            for num, _cell in enumerate(line['cells']):
                cell = copy.deepcopy(_cell)
                self.all_rect_format(cell)
                for char in cell['chars']:
                    char_x, char_y = char['bbox'][0], char['bbox'][1]
                    offset_x_list.append(char_x - line_x)
                    offset_y_list.append(char_y - line_y)
                    self.all_rect_format(char)
                __cells.append(cell)
            line['cells'] = __cells
        return offset_x_list, offset_y_list

    def all_rect_format(self, obj):
        '''
        将所有格式转换为ocr所需格式
        '''
        if 'chars' in obj:
            if obj.get('text'):
                obj['objContent'] = obj['text']
                del obj['text']
            if obj.get('objPos'):
                obj['objPos'] = self.rect_format(obj['objPos'])
            elif obj.get('bbox'):
                obj['objPos'] = self.rect_format(obj['bbox'])
                del obj['bbox']
        else:
            obj['objContent'] = obj['c']
            obj['objPos'] = self.rect_format(obj['bbox'])
            del obj['c']
            del obj['bbox']

class CalcTableRL:
    '''
    还原表格虚线 计算表格行列合并信息
    输入目标表格结构信息：必须包含所有的cell坐标
    在目标表格结构cell上加上row_start_end, col_start_end属性
    '''
    def __init__(self, table_info):
        self.table_info = table_info

    def run(self):
        if isinstance(self.table_info, list):
            for table_info in self.table_info:
                table_info = self.add_table_property(table_info)
                yield table_info
        else:
            table_info = self.add_table_property(self.table_info)
            yield table_info
    def add_table_property(self, table_info):
        '''
        表格结构增加行列合并信息:
        cell['col_start_end'] = (col_start, col_end)
        cell['row_start_end'] = (row_start, row_end)
        '''
        # 分别得到所有排序好的行列坐标
        set_x, set_y = self.collect_table_coord(table_info)
        # 排序 后的set_x，set_y 坐标集合就是最小粒度表格
        list_x, list_y = sorted(set_x), sorted(set_y)
        for line in table_info['lineList']:
            for cell in line['cells']:
                if cell['objPos'] == None:
                    continue
                x1, y1, x2, y2 = cell['objPos']
                # 查找坐标点在虚线表格中对应的位置
                col_start = list_x.index(x1)
                col_end = list_x.index(x2)
                row_start = list_y.index(y1)
                row_end = list_y.index(y2)
                cell['col_start_end'] = (col_start, col_end)
                cell['row_start_end'] = (row_start, row_end)
                # print(f"{cell['objContent']} 属于行：{cell['row_start_end']} 属于列：{cell['col_start_end']}")
        return table_info

    def collect_table_coord(self, table_info):
        '''
        获取所有x, y坐标点
        传入单个表格信息，提取出其中所有cell的x1, y1, x2, y2坐标点 去重
        :param table_info:
        :return: set(x), set(y)
        '''
        set_x = set()
        set_y = set()
        for line in table_info['lineList']:
            for cell in line['cells']:
                if cell['objPos'] == None:
                    continue
                x1, y1, x2, y2 = cell['objPos']
                set_x.add(x1)
                set_x.add(x2)
                set_y.add(y1)
                set_y.add(y2)
        return set_x, set_y



def pdf_ocr(pdf_path, output_path, table_type='v2', is_save=True):
    '''
    简单封装, 方便调用和多线程
    '''
    pdf = ParseFile(pdf_path, output_path, table_type, is_save)
    pdf.get_result()
    return pdf

# ---------------------------以下是测试案列-----------------------------------

@coast_time
def test_dir():
    for root in os.walk(r'E:\workplace\cjhx_test\创金和信\pdf2json\input\all_test'):
        dir, files = root[0], root[2]
        for file in files:
            if 'test.pdf' not in file:
                continue
            file_path = os.path.join(dir, file)
            output_dir = r'E:\workplace\cjhx_test\创金和信\pdf2json\file_data\all_test'
            pdf_ocr_result = pdf_ocr(file_path, output_dir)

@coast_time
def test_single():
    # file_path = r'E:\workplace\daily_work\pdf2json\input\all_test\测试足够复杂的表格解析.pdf'
    file_path = r'/home/yhocr/extractor/3f195fba-0916-4d74-b956-bf3bcadc77f2/20220913-浙江省贰号职业年金计划银华资产组合2022年二季度管理费用支付指令.pdf'
    # file_path = r'E:\workplace\daily_work\pdf2json\input\all_test\公开募集基金销售支付结算机构名录(2022年9月)(1).pdf'
    # file_path = r'C:\Users\Administrator\Documents\WeChat Files\wxid_x36dhycno4s121\FileStorage\File\2022-11\20210928-ZL001-西部利得天添鑫货币B-申购5000万-确认书.pdf'
    # file_path = r'E:\workplace\daily_work\pdf2json\input\all_test\2-信息系统部2021年大数据平台系统维护服务--工作记录表和考核表2021Q3-原版.pdf'
    output_dir = r'/home/yhocr/extractor/3f195fba-0916-4d74-b956-bf3bcadc77f2/电子解析'
    pdf = pdf_ocr(file_path, output_dir, table_type='v2')
    # print(pdf.ocr_result)

@coast_time
def test_thread():
    # 多进程
    from concurrent.futures import ProcessPoolExecutor
    pool = ProcessPoolExecutor(max_workers=8)
    # 多线程
    # from concurrent.futures import ThreadPoolExecutor
    # pool = ThreadPoolExecutor(max_workers=8)
    for root in os.walk(r'E:\workplace\daily_work\pdf2json\input\签字模板二'):
        dir, files = root[0], root[2]
        for file in files:
            file_path = os.path.join(dir, file)
            output_dir = r'E:\workplace\daily_work\pdf2json\output\签字模板二'
            ret = pool.submit(pdf_ocr, file_path, output_dir, table_type='v2')
            ret.add_done_callback(print_callback)
    pool.shutdown()

def print_callback(ret):
    # print('ret:', ret.result())
    pass

if __name__ == '__main__':
    # test_dir()
    # test_thread()
    # test_single()
    pdf_obj = DPFParser()
    with open(r"F:\code\easyofd\test\test.pdf","rb") as f:
        pdf_bytes = f.read()

    img_list = pdf_obj.to_img(pdf_bytes)
    pil_img_list = []
    for _img in img_list:
        print(_img.width,_img.height)
        img = Image.frombytes("RGB", [_img.width, _img.height], _img.samples)
        print(type(img))
        img.save('output_image.png')
      
    
