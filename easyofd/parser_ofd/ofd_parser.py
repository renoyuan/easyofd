#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PROJECT_NAME: D:\code\easyofd\easyofd\parser
# CREATE_TIME: 2023-07-27
# E_MAIL: renoyuan@foxmail.com
# AUTHOR: reno
# NOTE: ofd 解析主流程

import os
import sys
import traceback
import base64
import re
import io
from typing import Any, Dict, List, Optional, Tuple

from PIL import Image
from PIL.Image import Image as ImageClass
from loguru import logger

from .img_deal import DealImg
from .file_deal import FileRead
from .file_ofd_parser import OFDFileParser
from .file_doc_parser import DocumentFileParser
from .file_docres_parser import DocumentResFileParser
from .file_content_parser import ContentFileParser
from .file_annotation_parser import AnnotationFileParser, AnnotationsParser
from .file_publicres_parser import PublicResFileParser
from .file_signature_parser import SignaturesFileParser, SignatureFileParser
from .path_parser import PathParser


class OFDParserError(Exception):
    """OFD 解析异常"""
    pass


class OFDParser(object):
    """
    OFD 解析器

    解析流程:
    1. 解压文件，创建文件映射表
    2. 逐级解析 xml，收集文本、图片、资源
    3. 注册字体

    图层顺序: tlp > content > annotation
    """

    def __init__(self, ofdb64: Optional[str]) -> None:
        self.img_deal = DealImg()
        self.ofdb64: Optional[str] = ofdb64
        self.file_tree: Optional[Dict[str, Any]] = None
        self.jbig2dec_path: str = r"C:/msys64/mingw64/bin/jbig2dec.exe"

    # ════════════════════════════════════════════
    #  图片转 data（用于 jpg2ofd 场景）
    # ════════════════════════════════════════════

    def img2data(self, imglist: List[ImageClass]) -> List[dict]:
        """
        将图片列表转为 ofd data 结构

        Args:
            imglist: PIL Image 列表

        Returns:
            ofd data 列表（每个元素对应一个 document）
        """
        OP = 200 / 25.4
        img_info: Dict[str, dict] = {}
        page_info_d: Dict[int, dict] = {}

        for idx, img_pil in enumerate(imglist):
            w, h = img_pil.size
            img_bytes = self.img_deal.pil2bytes(img_pil)
            imgb64 = str(base64.b64encode(img_bytes), encoding="utf-8")

            img_info[str(idx)] = {
                "format": "jpg",
                "wrap_pos": "",
                "type": "IMG",
                "suffix": "jpg",
                "fileName": f"{idx}.jpg",
                "imgb64": imgb64,
            }

            img_d = {
                "CTM": "",
                "ID": str(idx),
                "ResourceID": str(idx),
                "pos": [0, 0, w / OP, h / OP],
            }
            page_size = [0, 0, w / OP, h / OP]

            page_info_d[idx] = {
                "text_list": [],
                "img_list": [img_d],
            }

        return [{
            "pdf_name": "demo.pdf",
            "doc_no": "0",
            "images": img_info,
            "page_size": page_size,
            "fonts": {},
            "page_info": page_info_d,
        }]

    # ════════════════════════════════════════════
    #  文件树查询
    # ════════════════════════════════════════════

    def get_xml_obj(self, label: str) -> Any:
        """
        根据文件路径标签从文件树中获取 xml 对象或 base64 内容

        Args:
            label: 文件路径，如 "Doc_0/Document.xml"

        Returns:
            xml 字典 / base64 字符串，未找到时返回空字符串
        """
        if not label:
            return ""

        if self.file_tree is None:
            return ""

        label = label.lstrip('./')
        label_compare = label.replace("\\\\", "-").replace("//", "-").replace("\\", "-").replace("/", "-")

        for abs_p in self.file_tree:
            abs_p_compare = abs_p.replace("\\\\", "-").replace("//", "-").replace("\\", "-").replace("/", "-")
            if label_compare in abs_p_compare:
                return self.file_tree[abs_p]

        return ""

    # ════════════════════════════════════════════
    #  图片格式转换
    # ════════════════════════════════════════════

    def _safe_img_convert(self, img_d: dict, suffix: str, convert_func_name: str) -> None:
        """安全执行图片格式转换，失败不影响主流程"""
        try:
            convert_func = getattr(self, convert_func_name, None)
            if convert_func:
                convert_func(img_d)
        except Exception as e:
            logger.warning(f"图片格式转换失败 ({suffix}→jpg): {img_d.get('fileName')}, {e}")

    def jb22png(self, img_d: dict) -> None:
        """jb2 转 png（依赖外部 jbig2dec）"""
        if not os.path.exists(self.jbig2dec_path):
            logger.warning(f"未安装 jbig2dec，无法处理 jb2 文件: {img_d.get('fileName')}")
            return

        fileName = img_d.get("fileName")
        if not fileName:
            return

        new_fileName = fileName.replace(".jb2", ".png")
        try:
            with open(fileName, "wb") as f:
                f.write(base64.b64decode(img_d.get("imgb64", "")))

            command = f"{self.jbig2dec_path} -o {new_fileName} {fileName}"
            res = os.system(command)

            if res != 0:
                logger.warning(f"jbig2dec 处理失败: {fileName}")
                return

            if os.path.exists(new_fileName):
                logger.info(f"jb2→png 处理成功: {fileName} -> {new_fileName}")
                img_d["fileName"] = new_fileName
                img_d["suffix"] = "png"
                img_d["format"] = "png"
                with open(new_fileName, "rb") as f:
                    img_d["imgb64"] = str(base64.b64encode(f.read()), encoding="utf-8")
                os.remove(new_fileName)
        except Exception as e:
            logger.warning(f"jb2 转换异常: {e}")
        finally:
            if os.path.exists(fileName):
                os.remove(fileName)

    def bmp2jpg(self, img_d: dict) -> None:
        """bmp 转 jpg"""
        fileName = img_d.get("fileName", "")
        if not fileName:
            return
        new_fileName = fileName.replace(".bmp", ".jpg")
        try:
            b64_nmp = self.get_xml_obj(fileName)
            if not b64_nmp:
                return
            image_data = base64.b64decode(b64_nmp)
            image = Image.open(io.BytesIO(image_data))
            rgb_image = image.convert("RGB")
            output_buffer = io.BytesIO()
            rgb_image.save(output_buffer, format="JPEG")
            image.close()
            b64_jpeg = base64.b64encode(output_buffer.getvalue()).decode('utf-8')
            output_buffer.close()
            if b64_jpeg:
                img_d["fileName"] = new_fileName
                img_d["suffix"] = "jpg"
                img_d["format"] = "jpg"
                img_d["imgb64"] = b64_jpeg
                logger.info(f"bmp→jpg 处理成功: {fileName}")
        except Exception as e:
            logger.warning(f"bmp→jpg 失败: {e}")

    def tif2jpg(self, img_d: dict) -> None:
        """tif 转 jpg"""
        fileName = img_d.get("fileName", "")
        if not fileName:
            return
        new_fileName = fileName.replace(".tif", ".jpg")
        try:
            tif_nmp = self.get_xml_obj(fileName)
            if not tif_nmp:
                return
            image_data = base64.b64decode(tif_nmp)
            image = Image.open(io.BytesIO(image_data))
            if image.mode in ("RGBA", "LA") or (image.mode == "P" and "transparency" in image.info):
                image = image.convert("RGB")
            output_buffer = io.BytesIO()
            image.save(output_buffer, format="JPEG", quality=95)
            image.close()
            b64_jpeg = base64.b64encode(output_buffer.getvalue()).decode('utf-8')
            output_buffer.close()
            if b64_jpeg:
                img_d["fileName"] = new_fileName
                img_d["suffix"] = "jpg"
                img_d["format"] = "jpg"
                img_d["imgb64"] = b64_jpeg
                logger.info(f"tif→jpg 处理成功: {fileName}")
        except Exception as e:
            logger.warning(f"tif→jpg 失败: {e}")

    def gif2jpg(self, img_d: dict) -> None:
        """gif 转 jpg"""
        fileName = img_d.get("fileName", "")
        if not fileName:
            return
        new_fileName = fileName.replace(".gif", ".jpg")
        try:
            b64_gif = self.get_xml_obj(fileName)
            if not b64_gif:
                return
            image_data = base64.b64decode(b64_gif)
            image = Image.open(io.BytesIO(image_data))
            if image.mode != "RGB":
                image = image.convert("RGB")
            output_buffer = io.BytesIO()
            image.save(output_buffer, format="JPEG", quality=95)
            image.close()
            b64_jpeg = base64.b64encode(output_buffer.getvalue()).decode('utf-8')
            output_buffer.close()
            if b64_jpeg:
                img_d["fileName"] = new_fileName
                img_d["suffix"] = "jpg"
                img_d["format"] = "jpg"
                img_d["imgb64"] = b64_jpeg
                logger.info(f"gif→jpg 处理成功: {fileName}")
        except Exception as e:
            logger.warning(f"gif→jpg 失败: {e}")

    # ════════════════════════════════════════════
    #  字体解析
    # ════════════════════════════════════════════

    def _resolve_font(self, text_obj: Any, text: str) -> str:
        """
        字体 fallback 解析

        Args:
            text_obj: 文本对象（dict 或类似结构）
            text: 文本内容

        Returns:
            字体名称，中文 fallback 到 SimSun，英文到 Helvetica
        """
        font_name = ""
        if isinstance(text_obj, dict):
            font_name = text_obj.get("@Font", "")

        # 如果有 font_tool，优先使用
        if hasattr(self, "font_tool") and font_name in getattr(self.font_tool, "FONTS", []):
            return self.font_tool.normalize_font_name(font_name)

        # fallback
        if any('\u4e00' <= c <= '\u9fff' for c in text):
            return "SimSun"
        return "Helvetica"

    # ════════════════════════════════════════════
    #  核心解析
    # ════════════════════════════════════════════

    def _parse_page_size(self, page_xml_obj: Any) -> Optional[List[float]]:
        """安全解析页面尺寸"""
        try:
            if not isinstance(page_xml_obj, dict):
                return None
            page = page_xml_obj.get('ofd:Page', page_xml_obj)
            if not isinstance(page, dict):
                return None
            area = page.get("ofd:Area", {})
            if not isinstance(area, dict):
                return None
            physical_box = area.get("ofd:PhysicalBox", "")
            parts = [float(x) for x in str(physical_box).split() if re.match(r"[\d\.]", x)]
            return parts if len(parts) >= 2 else None
        except Exception:
            return None

    def _parse_font_info(self, public_res_name: list) -> Tuple[Dict, Dict]:
        """解析字体信息和 DrawParam 信息"""
        font_info: Dict = {}
        draw_param_info: Dict = {}
        if not public_res_name:
            return font_info, draw_param_info

        try:
            public_xml_obj = self.get_xml_obj(public_res_name[0])
            if not public_xml_obj:
                return font_info, draw_param_info

            parser = PublicResFileParser(public_xml_obj)()
            font_info = parser.get("font", {})
            draw_param_info = parser.get("drawparams", {})

            # 注册字体二进制内容
            for font_v in font_info.values():
                file_name = font_v.get("FontFile")
                if file_name:
                    font_b64 = self.get_xml_obj(file_name)
                    if font_b64:
                        font_v["font_b64"] = font_b64
        except Exception as e:
            logger.warning(f"字体解析失败: {e}")

        return font_info, draw_param_info

    def _parse_images(self, document_res_name: list) -> Dict:
        """解析图片资源"""
        img_info: Dict = {}
        if not document_res_name:
            return img_info

        try:
            document_res_xml_obj = self.get_xml_obj(document_res_name[0])
            if not document_res_xml_obj:
                return img_info

            img_info = DocumentResFileParser(document_res_xml_obj)()

            # 获取图片 base64 数据并格式转换
            for img_v in img_info.values():
                img_v["imgb64"] = self.get_xml_obj(img_v.get("fileName", ""))
                suffix = img_v.get("suffix", "")
                if suffix == 'jb2':
                    self.jb22png(img_v)
                elif suffix == 'bmp':
                    self.bmp2jpg(img_v)
                elif suffix == 'tif':
                    self.tif2jpg(img_v)
                elif suffix == 'gif':
                    self.gif2jpg(img_v)
        except Exception as e:
            logger.warning(f"图片资源解析失败: {e}")

        return img_info

    def _parse_signatures(self, signatures: list, page_id_map: dict) -> Dict:
        """解析签章信息"""
        signatures_page_id: Dict = {}
        if not signatures:
            return signatures_page_id

        try:
            signatures_xml_obj = self.get_xml_obj(signatures[0])
            if not signatures_xml_obj:
                return signatures_page_id

            signatures_info = SignaturesFileParser(signatures_xml_obj)()
            if not signatures_info:
                return signatures_page_id

            for _, signatures_cell in signatures_info.items():
                BaseLoc = signatures_cell.get("BaseLoc")
                if not BaseLoc:
                    continue
                signature_xml_obj = self.get_xml_obj(BaseLoc)
                if not signature_xml_obj:
                    continue

                prefix = BaseLoc.split("/")[0]
                sig_info = SignatureFileParser(signature_xml_obj)(prefix=prefix)
                PageRef = sig_info.get("PageRef")
                Boundary = sig_info.get("Boundary")
                SignedValue = sig_info.get("SignedValue")
                sing_page_no = page_id_map.get(PageRef)

                sig_data = {
                    "sing_page_no": sing_page_no,
                    "PageRef": PageRef,
                    "Boundary": Boundary,
                    "SignedValue": self.get_xml_obj(SignedValue) if SignedValue else None,
                }

                if sing_page_no in signatures_page_id:
                    signatures_page_id[sing_page_no].append(sig_data)
                else:
                    signatures_page_id[sing_page_no] = [sig_data]
        except Exception as e:
            logger.warning(f"签章解析失败: {e}")

        return signatures_page_id

    def _parse_annotations(self, annotations_name: list) -> Dict:
        """解析注释信息"""
        annotation_info: Dict = {}
        if not annotations_name:
            return annotation_info

        try:
            annotations_xml_obj = self.get_xml_obj(annotations_name[0])
            if not annotations_xml_obj:
                return annotation_info

            annotations_info = AnnotationsParser(annotations_xml_obj)()
            if not annotations_info:
                return annotation_info

            for page_id, annotations_cell in annotations_info.items():
                file_loc = annotations_cell.get("FileLoc")
                anno_page_no = annotations_cell.get("pageNo")
                if file_loc:
                    annotation_xml_obj = self.get_xml_obj(file_loc)
                    if annotation_xml_obj:
                        annotation_info[anno_page_no] = AnnotationFileParser(annotation_xml_obj)()
        except Exception as e:
            logger.warning(f"注释解析失败: {e}")

        return annotation_info

    def _parse_pages(self, page_name: list) -> Tuple[Dict[int, dict], List[list]]:
        """解析页面内容"""
        page_info_d: Dict[int, dict] = {}
        page_size_details: List[list] = []

        if not page_name:
            return page_info_d, page_size_details

        for index, _page in enumerate(page_name):
            page_xml_obj = self.get_xml_obj(_page)
            if not page_xml_obj:
                page_size_details.append([])
                continue

            # 解析页面尺寸
            ps = self._parse_page_size(page_xml_obj)
            page_size_details.append(ps if ps else [])

            # 解析页面内容
            try:
                page_info = ContentFileParser(page_xml_obj)()
            except Exception as e:
                logger.warning(f"页面 {_page} 内容解析失败: {e}")
                page_info = {"text_list": [], "img_list": [], "line_list": []}

            pg_no_match = re.search(r"\d+", _page)
            pg_no = int(pg_no_match.group()) if pg_no_match else index
            page_info_d[pg_no] = page_info

        return page_info_d, page_size_details

    def _parse_tpls(self, tpls_name: list, page_info_d: Dict[int, dict]) -> None:
        """解析模板页并合并到对应页面（直接修改 page_info_d）"""
        if not tpls_name:
            return

        for index, _tpl in enumerate(tpls_name):
            try:
                tpl_xml_obj = self.get_xml_obj(_tpl)
                if not tpl_xml_obj:
                    continue

                tpl_info = ContentFileParser(tpl_xml_obj)()
                tpl_no_match = re.search(r"\d+", _tpl)
                tpl_no = int(tpl_no_match.group()) if tpl_no_match else index

                if tpl_no in page_info_d:
                    # 合并到已有页面
                    target = page_info_d[tpl_no]
                    for key in ["text_list", "img_list", "line_list"]:
                        tpl_items = tpl_info.get(key, [])
                        if tpl_items:
                            if key not in target:
                                target[key] = []
                            target[key].extend(tpl_items)
                            target[key].sort(
                                key=lambda x: (float(x.get("pos", [0, 0])[1]), float(x.get("pos", [0, 0])[0]))
                            )
                else:
                    # 新增模板页
                    page_info_d[tpl_no] = tpl_info
            except Exception as e:
                logger.warning(f"模板页 {_tpl} 解析失败: {e}")

    def parser(self) -> List[dict]:
        """
        执行完整的 OFD 解析流程

        文档结构:
        OFD.xml > Document.xml > [DocumentRes.xml, PublicRes.xml, Signatures.xml, Annotations.xml]

        Returns:
            doc_list: 解析后的文档数据列表
        """
        if self.file_tree is None:
            raise OFDParserError("文件树未初始化，请先执行 __call__")

        doc_list: List[dict] = []
        default_page_size: list = []
        page_size_details: list = []

        # ── 1. 解析根节点 OFD.xml ──
        ofd_xml_obj = self.get_xml_obj(self.file_tree.get("root_doc", ""))
        if ofd_xml_obj:
            try:
                ofd_obj_res = OFDFileParser(ofd_xml_obj)()
                doc_root_name = ofd_obj_res.get("doc_root", ["Doc_0/Document.xml"])
                signatures = ofd_obj_res.get("signatures", ["Doc_0/Signs/Signatures.xml"])
            except Exception as e:
                logger.warning(f"OFD.xml 解析失败: {e}")
                doc_root_name = ["Doc_0/Document.xml"]
                signatures = ["Doc_0/Signs/Signatures.xml"]
        else:
            doc_root_name = ["Doc_0/Document.xml"]
            signatures = ["Doc_0/Signs/Signatures.xml"]

        # ── 2. 解析 Document.xml ──
        doc_root_xml_obj = self.get_xml_obj(doc_root_name[0])
        if not doc_root_xml_obj:
            raise OFDParserError(f"Document.xml 未找到: {doc_root_name[0]}")

        doc_root_info = DocumentFileParser(doc_root_xml_obj)()

        # 默认页面尺寸
        doc_size = doc_root_info.get("size", "")
        if doc_size:
            try:
                default_page_size = [float(x) for x in str(doc_size).split() if re.match(r"[\d\.]", x)]
            except Exception:
                default_page_size = []

        # ── 3. 解析公共资源（字体、DrawParam） ──
        font_info, draw_param_info = self._parse_font_info(doc_root_info.get("public_res", []))

        # ── 4. 解析图片资源 ──
        img_info = self._parse_images(doc_root_info.get("document_res", []))

        # ── 5. 页面 ID 映射 ──
        page_id_map: dict = doc_root_info.get("page_id_map", {})

        # ── 6. 解析签章 ──
        signatures_page_id = self._parse_signatures(signatures, page_id_map)

        # ── 7. 解析注释 ──
        annotation_info = self._parse_annotations(doc_root_info.get("Annotations", []))

        # ── 8. 解析页码内容 ──
        page_info_d, page_size_details = self._parse_pages(doc_root_info.get("page", []))

        # ── 9. 解析模板并合并 ──
        self._parse_tpls(doc_root_info.get("tpls", []), page_info_d)

        # ── 10. 组装结果 ──
        doc_no = 0
        doc_list.append({
            "default_page_size": default_page_size,
            "page_size": page_size_details,
            "pdf_name": self.file_tree.get("pdf_name", "unknown.pdf"),
            "doc_no": doc_no,
            "images": img_info,
            "signatures_page_id": signatures_page_id,
            "annotation_info": annotation_info,
            "page_id_map": page_id_map,
            "fonts": font_info,
            "drawparams": draw_param_info,
            "page_info": page_info_d,
            "page_tpl_info": page_info_d,
            "page_content_info": page_info_d,
        })

        return doc_list

    def __call__(self, *args: Any, **kwargs: Any) -> List[dict]:
        """
        执行完整的 OFD 解析流程

        Args:
            save_xml: 是否保存解压的 xml 到独立目录（调试用）
            xml_name: 保存 xml 的目录名

        Returns:
            解析后的文档数据列表

        Raises:
            OFDParserError: 解析过程中发生严重错误
            FileReadError: OFD 文件读取失败
        """
        save_xml = kwargs.get("save_xml", False)
        xml_name = kwargs.get("xml_name")

        try:
            reader = FileRead(self.ofdb64)
            self.file_tree = reader(save_xml=save_xml, xml_name=xml_name)
            return self.parser()
        except Exception as e:
            logger.error(f"OFD 解析失败: {e}")
            raise


if __name__ == "__main__":
    with open(r"E:\code\easyofd\test\增值税电子专票5.ofd", "rb") as f:
        ofdb64 = str(base64.b64encode(f.read()), "utf-8")
    print(OFDParser(ofdb64)())
