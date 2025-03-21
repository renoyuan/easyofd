import base64
import os
import easyofd

def export_to_image(ofd_path: str, output_dir: str):
    file_prefix = os.path.splitext(os.path.split(ofd_path)[1])[0]
    print(f"file_prefix: {file_prefix}")
    with open(ofd_path,"rb") as f:
        ofdb64 = str(base64.b64encode(f.read()),"utf-8")
    print(f"ofdb64: {len(ofdb64)}")
    ofd = easyofd.OFD()  # 初始化OFD 工具类
    ofd.read(ofdb64, save_xml=True, xml_name=f"{file_prefix}_xml")  # 读取ofdb64
    pdf_bytes = ofd.to_pdf()  # 转pdf
    img_np = ofd.to_jpg()  # 转图片
    ofd.del_data()
    print(f"pdf_bytes: {len(pdf_bytes)}")
    print(f"img_np: {len(img_np)}")
    with open(f"{file_prefix}.pdf", "wb") as f:
        f.write(pdf_bytes)
    
    for idx, img in enumerate(img_np):
        # im = Image.fromarray(img)
        img.save(f"{file_prefix}_{idx}.jpg")
            

if __name__ == "main":
    ofd_file_path = "data/fapiao.ofd"
    output_dir = "data"
    print(f"ofd_file_path: {ofd_file_path}")
    print(f"output_dir: {output_dir}")
    export_to_image(ofd_file_path, output_dir)