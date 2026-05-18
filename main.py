"""
图片批量处理工具 — 调整尺寸 / 添加水印 / 格式转换 / 批量重命名 / 压缩

支持的格式：jpg, jpeg, png, bmp, gif, webp, tiff
"""
import os
import sys
import glob
import argparse
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
except ImportError:
    os.system(f"{sys.executable} -m pip install Pillow -q")
    from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance


# ───────────────────────── 常量 ─────────────────────────

SUPPORTED_EXT = (".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp", ".tiff", ".tif")
FORMAT_MAP = {
    "jpg": "JPEG", "jpeg": "JPEG",
    "png": "PNG",
    "bmp": "BMP",
    "gif": "GIF",
    "webp": "WEBP",
    "tiff": "TIFF", "tif": "TIFF",
}


# ───────────────────────── 工具函数 ─────────────────────────

def get_image_files(input_dir_or_glob):
    """获取输入路径下的所有图片文件，支持通配符"""
    if os.path.isdir(input_dir_or_glob):
        files = []
        for ext in SUPPORTED_EXT:
            files.extend(glob.glob(os.path.join(input_dir_or_glob, f"*{ext}")))
            files.extend(glob.glob(os.path.join(input_dir_or_glob, f"*{ext.upper()}")))
    else:
        files = glob.glob(input_dir_or_glob)
    return sorted(set(f.lower() for f in files))


# ───────────────────────── 核心功能 ─────────────────────────

def resize_images(input_path, output_dir, width, height, keep_aspect=True, fit="cover"):
    """
    批量调整图片尺寸。

    参数:
        keep_aspect (bool): 是否保持宽高比
        fit (str): "cover" 裁剪适配 / "inside" 缩小适配（keep_aspect=True 时有效）
    """
    files = get_image_files(input_path)
    if not files:
        print("未找到图片文件"); return

    os.makedirs(output_dir, exist_ok=True)
    count = 0
    for fpath in files:
        try:
            img = Image.open(fpath)
            if keep_aspect:
                if fit == "cover":
                    img.thumbnail((width, height), Image.LANCZOS)
                    # 居中裁剪到目标尺寸
                    new_img = Image.new(img.mode, (width, height), (255, 255, 255))
                    x = (width - img.size[0]) // 2
                    y = (height - img.size[1]) // 2
                    new_img.paste(img, (x, y))
                    img = new_img
                else:  # inside
                    img.thumbnail((width, height), Image.LANCZOS)
            else:
                img = img.resize((width, height), Image.LANCZOS)

            name = os.path.basename(fpath)
            out_path = os.path.join(output_dir, f"resized_{name}")
            img.save(out_path)
            count += 1
        except Exception as e:
            print(f"  跳过 {os.path.basename(fpath)}: {e}")

    print(f"调整尺寸完成：{count} 张图片 → {output_dir}")


def watermark_images(input_path, output_dir, text, position="bottom-right",
                     opacity=128, font_size_ratio=25):
    """
    批量添加文字水印。

    参数:
        position (str): "bottom-right" / "center" / "top-left"
        opacity (int): 透明度 0-255
        font_size_ratio (int): 字号相对于图片长边的分母
    """
    files = get_image_files(input_path)
    if not files:
        print("未找到图片文件"); return

    os.makedirs(output_dir, exist_ok=True)
    count = 0
    for fpath in files:
        try:
            img = Image.open(fpath).convert("RGBA")
            overlay = Image.new("RGBA", img.size, (255, 255, 255, 0))
            draw = ImageDraw.Draw(overlay)

            font_size = max(img.size) // font_size_ratio
            try:
                font = ImageFont.truetype("simhei.ttf", font_size)
            except (IOError, OSError):
                try:
                    # Windows 系统字体路径
                    font_path = "C:/Windows/Fonts/msyh.ttc"
                    if os.path.exists(font_path):
                        font = ImageFont.truetype(font_path, font_size)
                    else:
                        font = ImageFont.load_default()
                except Exception:
                    font = ImageFont.load_default()

            bbox = draw.textbbox((0, 0), text, font=font)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
            margin = 20

            pos_map = {
                "bottom-right": (img.size[0] - tw - margin, img.size[1] - th - margin),
                "center":       ((img.size[0] - tw) // 2, (img.size[1] - th) // 2),
                "top-left":     (margin, margin),
                "top-right":    (img.size[0] - tw - margin, margin),
                "bottom-left":  (margin, img.size[1] - th - margin),
            }
            pos = pos_map.get(position, pos_map["bottom-right"])

            draw.text(pos, text, font=font, fill=(255, 255, 255, opacity))
            result = Image.alpha_composite(img, overlay)
            result = result.convert("RGB")

            name = os.path.basename(fpath)
            out_path = os.path.join(output_dir, f"wm_{name}")
            # 如果输入是 png，保持 png 输出（否则 jpg 不支持透明）
            if fpath.lower().endswith(".png"):
                out_path = os.path.join(output_dir, f"wm_{os.path.splitext(name)[0]}.png")
                result = Image.alpha_composite(img, overlay)

            result.save(out_path)
            count += 1
        except Exception as e:
            print(f"  跳过 {os.path.basename(fpath)}: {e}")

    print(f"水印添加完成：{count} 张图片 → {output_dir}")


def convert_format(input_path, output_dir, target_format="png", quality=90):
    """
    批量转换图片格式。

    参数:
        target_format (str): 目标格式 jpg/png/webp/bmp/tiff
        quality (int): JPEG/WebP 压缩质量 1-100
    """
    files = get_image_files(input_path)
    if not files:
        print("未找到图片文件"); return

    os.makedirs(output_dir, exist_ok=True)
    target = target_format.lower()
    fmt = FORMAT_MAP.get(target)
    if not fmt:
        print(f"不支持的目标格式: {target}"); return

    count = 0
    for fpath in files:
        try:
            img = Image.open(fpath)
            # 转换 RGBA -> RGB 用于 JPEG
            if fmt == "JPEG" and img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            name = os.path.splitext(os.path.basename(fpath))[0]
            out_path = os.path.join(output_dir, f"{name}.{target}")
            img.save(out_path, fmt, quality=quality)
            count += 1
        except Exception as e:
            print(f"  跳过 {os.path.basename(fpath)}: {e}")

    print(f"格式转换完成：{count} 张图片 → {output_dir}（.{target}）")


def rename_batch(input_path, prefix="img", start_num=1, digits=4):
    """
    批量重命名图片为统一格式。

    示例：img_0001.jpg, img_0002.jpg ...
    """
    files = get_image_files(input_path)
    if not files:
        print("未找到图片文件"); return

    count = 0
    for i, fpath in enumerate(files):
        try:
            ext = os.path.splitext(fpath)[1].lower()
            new_name = f"{prefix}_{(start_num + i):0{digits}d}{ext}"
            new_path = os.path.join(os.path.dirname(fpath), new_name)
            os.rename(fpath, new_path)
            print(f"  {os.path.basename(fpath)} → {new_name}")
            count += 1
        except Exception as e:
            print(f"  跳过 {os.path.basename(fpath)}: {e}")

    print(f"重命名完成：{count} 张图片")


def compress_images(input_path, output_dir, quality=60):
    """
    批量压缩图片（减小文件体积）。

    参数:
        quality (int): 压缩质量 1-100（越低体积越小）
    """
    files = get_image_files(input_path)
    if not files:
        print("未找到图片文件"); return

    os.makedirs(output_dir, exist_ok=True)
    total_orig = 0
    total_new = 0
    count = 0

    for fpath in files:
        try:
            img = Image.open(fpath)
            name = os.path.basename(fpath)
            out_path = os.path.join(output_dir, f"compressed_{name}")
            ext = os.path.splitext(fpath)[1].lower()

            save_kw = {"quality": quality, "optimize": True}
            if ext in (".jpg", ".jpeg"):
                img.save(out_path, "JPEG", **save_kw)
            elif ext == ".png":
                img.save(out_path, "PNG", optimize=True)
            elif ext == ".webp":
                img.save(out_path, "WEBP", **save_kw)
            else:
                img.save(out_path)

            orig_size = os.path.getsize(fpath)
            new_size = os.path.getsize(out_path)
            total_orig += orig_size
            total_new += new_size
            ratio = (1 - new_size / orig_size) * 100
            print(f"  {name}: {orig_size/1024:.1f}KB → {new_size/1024:.1f}KB ({ratio:.0f}%)")
            count += 1
        except Exception as e:
            print(f"  跳过 {os.path.basename(fpath)}: {e}")

    if count > 0:
        total_ratio = (1 - total_new / total_orig) * 100
        print(f"\n压缩完成：{count} 张图片，总体积减少 {total_ratio:.0f}% → {output_dir}")


def images_info(input_path):
    """输出文件夹内所有图片的尺寸、格式、大小信息"""
    files = get_image_files(input_path)
    if not files:
        print("未找到图片文件"); return

    print(f"\n{'文件名':30s} {'格式':8s} {'尺寸':16s} {'大小':10s}")
    print("-" * 66)
    total_size = 0
    for fpath in files:
        try:
            img = Image.open(fpath)
            size_str = f"{img.size[0]}x{img.size[1]}"
            fsize = os.path.getsize(fpath)
            total_size += fsize
            print(f"{os.path.basename(fpath):30s} {img.format:8s} {size_str:16s} {fsize/1024:>8.1f}KB")
        except Exception as e:
            print(f"{os.path.basename(fpath):30s} {'ERROR':8s} {str(e):16s}")

    print("-" * 66)
    print(f"{'共 ' + str(len(files)) + ' 个文件':30s} {'':8s} {'':16s} {total_size/1024:>8.1f}KB")


# ───────────────────────── CLI 入口 ─────────────────────────

def main():
    p = argparse.ArgumentParser(
        description="图片批量处理工具 —— 调整尺寸 / 水印 / 格式转换 / 重命名 / 压缩",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "示例:\n"
            "  python main.py resize ./photos -W 800 -H 600\n"
            "  python main.py watermark ./photos '水印文字' -p center\n"
            "  python main.py convert ./photos -t webp -q 85\n"
            "  python main.py rename ./photos --prefix photo --start 1\n"
            "  python main.py compress ./photos -q 50\n"
            "  python main.py info ./photos\n"
        )
    )
    sub = p.add_subparsers(dest="cmd", help="子命令")

    # resize
    r = sub.add_parser("resize", help="批量调整尺寸")
    r.add_argument("input", help="图片文件夹路径")
    r.add_argument("-o", "--output", default="resized", help="输出文件夹")
    r.add_argument("-W", "--width", type=int, default=800, help="目标宽度")
    r.add_argument("-H", "--height", type=int, default=600, help="目标高度")
    r.add_argument("--keep-aspect", action="store_true", default=True, help="保持宽高比（默认）")
    r.add_argument("--no-keep-aspect", action="store_false", dest="keep_aspect", help="强制拉伸到目标尺寸")
    r.add_argument("--fit", default="cover", choices=["cover", "inside"], help="适配方式")

    # watermark
    w = sub.add_parser("watermark", help="批量添加水印")
    w.add_argument("input", help="图片文件夹路径")
    w.add_argument("text", help="水印文字内容")
    w.add_argument("-o", "--output", default="watermarked", help="输出文件夹")
    w.add_argument("-p", "--position", default="bottom-right",
                   choices=["bottom-right", "center", "top-left", "top-right", "bottom-left"],
                   help="水印位置")
    w.add_argument("--opacity", type=int, default=128, help="透明度 0-255（默认 128）")
    w.add_argument("--font-size-ratio", type=int, default=25, help="字号分母（默认 25）")

    # convert
    c = sub.add_parser("convert", help="批量格式转换")
    c.add_argument("input", help="图片文件夹路径")
    c.add_argument("-o", "--output", default="converted", help="输出文件夹")
    c.add_argument("-t", "--target", default="png", choices=["jpg", "png", "webp", "bmp", "tiff"], help="目标格式")
    c.add_argument("-q", "--quality", type=int, default=90, help="压缩质量 1-100")

    # rename
    rn = sub.add_parser("rename", help="批量重命名")
    rn.add_argument("input", help="图片文件夹路径")
    rn.add_argument("--prefix", default="img", help="文件名前缀（默认 img）")
    rn.add_argument("--start", type=int, default=1, help="起始编号（默认 1）")
    rn.add_argument("--digits", type=int, default=4, help="编号位数（默认 4）")

    # compress
    cp = sub.add_parser("compress", help="批量压缩")
    cp.add_argument("input", help="图片文件夹路径")
    cp.add_argument("-o", "--output", default="compressed", help="输出文件夹")
    cp.add_argument("-q", "--quality", type=int, default=60, help="压缩质量 1-100")

    # info
    info = sub.add_parser("info", help="查看图片信息")
    info.add_argument("input", help="图片文件夹路径")

    args = p.parse_args()
    if args.cmd is None:
        p.print_help()
        return

    cmds = {
        "resize":    lambda: resize_images(args.input, args.output, args.width, args.height, args.keep_aspect, args.fit),
        "watermark": lambda: watermark_images(args.input, args.output, args.text, args.position, args.opacity, args.font_size_ratio),
        "convert":   lambda: convert_format(args.input, args.output, args.target, args.quality),
        "rename":    lambda: rename_batch(args.input, args.prefix, args.start, args.digits),
        "compress":  lambda: compress_images(args.input, args.output, args.quality),
        "info":      lambda: images_info(args.input),
    }
    cmds[args.cmd]()


if __name__ == "__main__":
    main()
