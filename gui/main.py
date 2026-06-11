#!/usr/bin/env python
# -*- coding: utf-8 -*-
# E_MAIL: renoyuan@foxmail.com
# AUTHOR: reno
# NOTE: EasyOFD GUI - OFD/PDF/图片 格式互转

import os
import sys
import base64
import traceback
from pathlib import Path

lib_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, lib_path)

from PIL import Image

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QLineEdit, QPushButton, QRadioButton,
    QCheckBox, QTextEdit, QStatusBar, QFileDialog, QMessageBox,
    QFrame, QButtonGroup, QProgressBar,
)
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QAction, QIcon, QFont, QTextCursor

from easyofd import OFD


# ──────────────────────────────────────────────
#  常量定义
# ──────────────────────────────────────────────

APP_NAME = "EasyOFD"
APP_TITLE = "EasyOFD - OFD文档处理工具"
ICON_PATH = Path(__file__).parent / "ico" / "reno.ico"

MODE_GROUP = [
    ("ofd2pdf", "OFD → PDF"),
    ("ofd2img", "OFD → 图片"),
    ("pdf2ofd", "PDF → OFD"),
    ("pdf2img", "PDF → 图片"),
    ("img2ofd", "图片 → OFD"),
    ("img2pdf", "图片 → PDF"),
]

MODE_EXT_MAP = {
    "ofd2pdf": ".ofd",
    "ofd2img": ".ofd",
    "pdf2ofd": ".pdf",
    "pdf2img": ".pdf",
    "img2ofd": (".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"),
    "img2pdf": (".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"),
}

MODE_FILTER_MAP = {
    "ofd2pdf": ("选择 OFD 文件", "OFD (*.ofd)"),
    "ofd2img": ("选择 OFD 文件", "OFD (*.ofd)"),
    "pdf2ofd": ("选择 PDF 文件", "PDF (*.pdf)"),
    "pdf2img": ("选择 PDF 文件", "PDF (*.pdf)"),
    "img2ofd": ("选择图片", "图片 (*.jpg *.jpeg *.png *.bmp *.tif *.tiff)"),
    "img2pdf": ("选择图片", "图片 (*.jpg *.jpeg *.png *.bmp *.tif *.tiff)"),
}

STYLE_SHEET = """
    QMainWindow { background: #F5F5F5; }
    QPushButton#btn_start {
        background: #4A90D9; color: white; border: none;
        border-radius: 4px; padding: 6px 16px;
        font-size: 13px; font-weight: bold;
    }
    QPushButton#btn_start:hover { background: #357ABD; }
    QPushButton#btn_start:disabled { background: #C0C0C0; color: #808080; }
"""

ABOUT_TEXT = (
    "<h3>EasyOFD</h3>"
    "<p>版本: 20260427</p>"
    "<p>作者: renoyuan</p>"
    "<hr><p>OFD/PDF/图片 格式互转</p>"
    '<p><a href="https://github.com/renoyuan/easyofd">github.com/renoyuan/easyofd</a></p>'
)


# ──────────────────────────────────────────────
#  工作线程
# ──────────────────────────────────────────────

class ConvertWorker(QThread):
    """后台转换工作线程"""

    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal(bool, str)
    file_signal = pyqtSignal(str, int, int)

    def __init__(self, mode: str, input_path: str, output_path: str, recursive: bool = False):
        super().__init__()
        self.mode = mode
        self.input_path = input_path
        self.output_path = output_path
        self.recursive = recursive
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def run(self):
        try:
            ofd = OFD()
            files = self._collect_files()
            if not files:
                self.finished_signal.emit(False, "未找到符合条件的输入文件")
                return

            total = len(files)
            self.log_signal.emit(f"找到 {total} 个文件，开始转换...")
            self.progress_signal.emit(0)

            for idx, fp in enumerate(files):
                if self._cancelled:
                    self.finished_signal.emit(False, "用户取消")
                    return
                name = os.path.basename(fp)
                self.file_signal.emit(name, idx + 1, total)
                self.log_signal.emit(f"[{idx + 1}/{total}] {name}")
                self._process_one(ofd, fp)
                self.progress_signal.emit(int((idx + 1) / total * 100))

            ofd.del_data()
            self.finished_signal.emit(True, f"完成，共 {total} 个文件")
        except Exception as e:
            self.log_signal.emit(traceback.format_exc())
            self.finished_signal.emit(False, str(e))

    def _collect_files(self) -> list[str]:
        exts = MODE_EXT_MAP.get(self.mode, ".ofd")
        p = Path(self.input_path)
        if p.is_file():
            return [str(p)]
        walk = p.rglob if self.recursive else p.iterdir
        if not isinstance(exts, tuple):
            exts = (exts,)
        return sorted(
            str(f) for f in walk()
            if f.is_file() and f.suffix.lower() in exts
        )

    @staticmethod
    def _ensure_bytes(data):
        return data if isinstance(data, bytes) else data[0]

    def _process_one(self, ofd: OFD, fp: str):
        base = os.path.splitext(os.path.basename(fp))[0]

        if self.mode in ("ofd2pdf", "ofd2img"):
            with open(fp, "rb") as f:
                b64_data = str(base64.b64encode(f.read()), "utf-8")
            ofd.read(b64_data)

        if self.mode == "ofd2pdf":
            pdf = ofd.to_pdf()
            with open(os.path.join(self.output_path, f"{base}.pdf"), "wb") as f:
                f.write(self._ensure_bytes(pdf))

        elif self.mode == "ofd2img":
            for i, img in enumerate(ofd.to_jpg()):
                img.save(os.path.join(self.output_path, f"{base}_{i}.jpg"))

        elif self.mode == "pdf2ofd":
            with open(fp, "rb") as f:
                b = ofd.pdf2ofd(f.read())
            with open(os.path.join(self.output_path, f"{base}.ofd"), "wb") as f:
                f.write(self._ensure_bytes(b))

        elif self.mode == "pdf2img":
            with open(fp, "rb") as f:
                for i, img in enumerate(ofd.pdf2img(f.read())):
                    img.save(os.path.join(self.output_path, f"{base}_{i}.jpg"))

        elif self.mode == "img2ofd":
            b = ofd.jpg2ofd([Image.open(fp)])
            with open(os.path.join(self.output_path, f"{base}.ofd"), "wb") as f:
                f.write(self._ensure_bytes(b))

        elif self.mode == "img2pdf":
            ofd.del_data()
            b = ofd.jpg2pfd([Image.open(fp)])
            with open(os.path.join(self.output_path, f"{base}.pdf"), "wb") as f:
                f.write(self._ensure_bytes(b))

        ofd.del_data()
        self.log_signal.emit(f"  OK {base}")


# ──────────────────────────────────────────────
#  主窗口
# ──────────────────────────────────────────────

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.worker: ConvertWorker | None = None
        self.rbs: dict[str, QRadioButton] = {}
        self._init_ui()

    # ---------- UI 构建 ----------

    def _init_ui(self):
        self._setup_window()
        cw = QWidget()
        self.setCentralWidget(cw)
        layout = QVBoxLayout(cw)

        self._add_mode_section(layout)
        layout.addWidget(self._make_separator())
        self._add_path_section(layout)
        self._add_option_section(layout)
        self._add_button_section(layout)
        self._add_progress_bar(layout)
        self._add_log_area(layout)
        self._setup_menu()
        self._setup_statusbar()
        self._apply_style()

    def _setup_window(self):
        self.setWindowTitle(APP_TITLE)
        self.setMinimumSize(640, 480)
        self.resize(680, 520)
        if ICON_PATH.exists():
            self.setWindowIcon(QIcon(str(ICON_PATH)))

    def _add_mode_section(self, parent: QVBoxLayout):
        parent.addWidget(QLabel("转换模式"))
        hl = QHBoxLayout()
        group = QButtonGroup(self)
        for i, (key, text) in enumerate(MODE_GROUP):
            rb = QRadioButton(text)
            self.rbs[key] = rb
            group.addButton(rb)
            hl.addWidget(rb)
            if i == 0:
                rb.setChecked(True)
        parent.addLayout(hl)

    @staticmethod
    def _make_separator() -> QFrame:
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        return line

    def _add_path_section(self, parent: QVBoxLayout):
        grid = QGridLayout()

        grid.addWidget(QLabel("输入路径:"), 0, 0)
        self.input_path = QLineEdit()
        self.input_path.setPlaceholderText("选择输入文件或目录...")
        grid.addWidget(self.input_path, 0, 1)
        btn_in = QPushButton("浏览...")
        btn_in.setMaximumWidth(90)
        btn_in.clicked.connect(self._browse_input)
        grid.addWidget(btn_in, 0, 2)

        grid.addWidget(QLabel("输出路径:"), 1, 0)
        self.output_path = QLineEdit()
        self.output_path.setPlaceholderText("选择输出目录...")
        grid.addWidget(self.output_path, 1, 1)
        btn_out = QPushButton("浏览...")
        btn_out.setMaximumWidth(90)
        btn_out.clicked.connect(self._browse_output)
        grid.addWidget(btn_out, 1, 2)

        parent.addLayout(grid)

    def _add_option_section(self, parent: QVBoxLayout):
        ol = QHBoxLayout()
        self.check_recursive = QCheckBox("递归子目录")
        ol.addWidget(self.check_recursive)
        ol.addStretch()
        parent.addLayout(ol)

    def _add_button_section(self, parent: QVBoxLayout):
        bl = QHBoxLayout()
        self.btn_start = QPushButton("开始转换")
        self.btn_start.setMinimumSize(120, 36)
        self.btn_start.clicked.connect(self._start_convert)
        bl.addWidget(self.btn_start)
        btn_clear = QPushButton("清空日志")
        btn_clear.clicked.connect(lambda: self.log_area.clear())
        bl.addWidget(btn_clear)
        bl.addStretch()
        parent.addLayout(bl)

    def _add_progress_bar(self, parent: QVBoxLayout):
        self.progress = QProgressBar()
        self.progress.setTextVisible(True)
        self.progress.setValue(0)
        parent.addWidget(self.progress)

    def _add_log_area(self, parent: QVBoxLayout):
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setPlaceholderText("日志信息将在这里显示...")
        font = QFont("Consolas", 10)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.log_area.setFont(font)
        parent.addWidget(self.log_area)

    def _setup_menu(self):
        mb = self.menuBar()

        file_menu = mb.addMenu("文件")
        act_input = QAction("打开输入文件/目录...", self)
        act_input.triggered.connect(self._browse_input)
        file_menu.addAction(act_input)

        act_output = QAction("打开输出目录...", self)
        act_output.triggered.connect(self._browse_output)
        file_menu.addAction(act_output)

        file_menu.addSeparator()
        act_exit = QAction("退出", self)
        act_exit.triggered.connect(self.close)
        file_menu.addAction(act_exit)

        help_menu = mb.addMenu("帮助")
        act_about = QAction("关于 EasyOFD", self)
        act_about.triggered.connect(self._show_about)
        help_menu.addAction(act_about)

    def _setup_statusbar(self):
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("就绪")

    def _apply_style(self):
        self.setStyleSheet(STYLE_SHEET)
        self.btn_start.setObjectName("btn_start")

    # ---------- 逻辑 ----------

    def _get_mode(self) -> str:
        for key, rb in self.rbs.items():
            if rb.isChecked():
                return key
        return "ofd2pdf"

    def _browse_input(self):
        mode = self._get_mode()
        info = MODE_FILTER_MAP.get(mode)
        if info:
            title, filter_str = info
            p, _ = QFileDialog.getOpenFileName(self, title, "", filter_str)
        else:
            p = QFileDialog.getExistingDirectory(self, "选择输入目录")
        if p:
            self.input_path.setText(p)

    def _browse_output(self):
        p = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if p:
            self.output_path.setText(p)

    def _start_convert(self):
        if self.worker and self.worker.isRunning():
            QMessageBox.warning(self, "提示", "正在转换中...")
            return

        inp = self.input_path.text().strip()
        out = self.output_path.text().strip()

        if not inp or not out:
            QMessageBox.warning(self, "提示", "请选择输入和输出路径")
            return
        if not os.path.exists(inp):
            QMessageBox.warning(self, "提示", f"输入路径不存在: {inp}")
            return

        try:
            if not os.path.exists(out):
                os.makedirs(out)
        except Exception as e:
            QMessageBox.warning(self, "提示", f"无法创建输出目录: {e}")
            return

        mode = self._get_mode()
        recursive = self.check_recursive.isChecked()

        self.log_area.clear()
        self.progress.setValue(0)
        self.btn_start.setEnabled(False)
        self.btn_start.setText("转换中...")
        self.status.showMessage("正在转换...")

        self.log(f"模式: {mode}")
        self.log(f"输入: {inp}")
        self.log(f"输出: {out}")
        self.log(f"递归: {'是' if recursive else '否'}")
        self.log("-" * 50)

        self.worker = ConvertWorker(mode, inp, out, recursive)
        self.worker.log_signal.connect(self.log)
        self.worker.progress_signal.connect(self.progress.setValue)
        self.worker.file_signal.connect(
            lambda fn, ci, tt: self.status.showMessage(f"处理 [{ci}/{tt}]: {fn}")
        )
        self.worker.finished_signal.connect(self._on_finished)
        self.worker.start()

    def _on_finished(self, ok: bool, msg: str):
        self.btn_start.setEnabled(True)
        self.btn_start.setText("开始转换")
        self.progress.setValue(100 if ok else 0)
        self.status.showMessage("就绪" if ok else "失败")

        if ok:
            self.log("\n" + "=" * 50)
            self.log(f"OK {msg}")
            self.log("=" * 50)
            QMessageBox.information(self, "完成", msg)
        else:
            self.log(f"\nFAIL {msg}")

    def log(self, msg: str):
        self.log_area.append(msg)
        cursor = self.log_area.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.log_area.setTextCursor(cursor)

    def _show_about(self):
        QMessageBox.about(self, "关于 EasyOFD", ABOUT_TEXT)

    def closeEvent(self, event):
        if self.worker and self.worker.isRunning():
            reply = QMessageBox.question(
                self, "确认退出", "任务进行中，确定退出？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.worker.cancel()
                self.worker.wait(3000)
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


# ──────────────────────────────────────────────
#  入口
# ──────────────────────────────────────────────

def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
