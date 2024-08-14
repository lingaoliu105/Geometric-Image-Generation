from pdf2image import convert_from_path
import sys
# PDF 文件路径
pdf_path = sys.argv[1]

# 将 PDF 转换为图片
# dpi 参数控制图片的分辨率
images = convert_from_path(pdf_path, dpi=300)

# 保存每一页为图片
for j, image in enumerate(images):
    image.save(f'output_png/{pdf_path.split("/")[-1].split(".")[0]}.png', 'PNG')