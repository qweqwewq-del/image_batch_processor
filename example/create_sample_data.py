"""
生成示例图片文件，用于测试图片批量处理工具。
"""
from PIL import Image, ImageDraw, ImageFont
import os


def create_sample_image(filename, width, height, color, text):
    """创建带颜色的示例图片"""
    img = Image.new("RGB", (width, height), color)
    draw = ImageDraw.Draw(img)
    # 添加文字
    try:
        font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 40)
    except Exception:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((width - tw) // 2, (height - th) // 2), text, fill="white", font=font)
    img.save(filename)
    print(f"已生成: {filename} ({width}x{height})")


create_sample_image("sample_photo_01.jpg", 1920, 1080, (70, 130, 180), "Photo 01")
create_sample_image("sample_photo_02.png", 800, 600, (60, 179, 113), "Photo 02")
create_sample_image("sample_photo_03.jpg", 1200, 1600, (220, 100, 100), "Photo 03")

print("\n示例文件生成完毕！运行以下命令测试：")
print("  1. resize:    python ..\\main.py resize . -W 400 -H 300 -o resized")
print("  2. watermark: python ..\\main.py watermark . 'Sample' -o watermarked")
print("  3. convert:   python ..\\main.py convert . -t webp -q 85 -o converted")
print("  4. info:      python ..\\main.py info .")
print("  5. compress:  python ..\\main.py compress . -q 50 -o compressed")
