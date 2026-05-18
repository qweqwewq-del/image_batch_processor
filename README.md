# 图片批量处理工具

批量调整尺寸 / 添加水印 / 格式转换 / 批量重命名 / 图片压缩，电商卖家、自媒体运营者必备工具。

---

## 功能特性

| 功能 | 说明 | 命令 |
|------|------|------|
| 调整尺寸 | 批量修改图片宽高，支持保持宽高比或居中裁剪 | `resize` |
| 添加水印 | 支持自定义文字水印，5 种位置，可调透明度和字号 | `watermark` |
| 格式转换 | 在 jpg / png / webp / bmp / tiff 之间互转 | `convert` |
| 批量重命名 | 统一编号命名，如 `img_0001.jpg` | `rename` |
| 图片压缩 | 压缩文件体积，适合上传网站/发送微信 | `compress` |
| 信息预览 | 查看文件夹内所有图片的尺寸、格式、大小 | `info` |

---

## 环境要求

- Python 3.8+
- Pillow>=10.0.0

---

## 使用方法

### 1. 调整尺寸

```bash
# 调整为 800x600，保持宽高比居中裁剪
python main.py resize ./photos -W 800 -H 600

# 强制拉伸到指定尺寸（不保持宽高比）
python main.py resize ./photos -W 1920 -H 1080 --no-keep-aspect

# 缩小适配（不裁剪，图片完整显示在目标尺寸内）
python main.py resize ./photos -W 400 -H 300 --fit inside
```

### 2. 添加水印

```bash
# 右下角水印（默认）
python main.py watermark ./photos "我的店铺" -o 加水印

# 居中水印
python main.py watermark ./photos "© 张三摄影" -p center -o 居中水印

# 低透明度水印
python main.py watermark ./photos "SAMPLE" --opacity 60 -o 淡印
```

### 3. 格式转换

```bash
# 全部转为 PNG
python main.py convert ./photos -t png -o 转PNG

# 转为 WebP（网页友好格式，体积小）
python main.py convert ./photos -t webp -q 85 -o 转WebP

# 转为 JPEG 并调整质量
python main.py convert ./photos -t jpg -q 95 -o 转JPG
```

### 4. 批量重命名

```bash
# 重命名为 photo_0001.jpg, photo_0002.jpg ...
python main.py rename ./photos --prefix photo --start 1 --digits 4
```

### 5. 图片压缩

```bash
# 压缩到质量 60（推荐，体积与画质平衡）
python main.py compress ./photos -q 60 -o 压缩版

# 最大压缩（质量 20，体积极小）
python main.py compress ./photos -q 20 -o 极限压缩
```

### 6. 查看图片信息

```bash
python main.py info ./photos
```

输出示例：

```
文件名                           格式      尺寸              大小
---------------------------------------------------------------
IMG_001.JPG                      JPEG      4032x3024        2,048.0KB
IMG_002.PNG                      PNG       1920x1080           56.0KB
IMG_003.WEBP                     WEBP       800x600            12.5KB
---------------------------------------------------------------
共 3 个文件                                                   2,116.5KB
```

---

## 示例场景

### 场景一：电商批量处理商品图

```bash
# 1. 统一缩放到 800x800
python main.py resize ./原图 -W 800 -H 800 -o 统一尺寸
# 2. 加上店铺水印
python main.py watermark ./统一尺寸 "XX店铺" -p bottom-right -o 带水印
# 3. 压缩到质量 60 以提升网站加载速度
python main.py compress ./带水印 -q 60 -o 最终版
```

### 场景二：摄影作品整理

```bash
# 1. 批量重命名
python main.py rename ./raw_photos --prefix travel --start 1
# 2. 转为 WebP 发朋友圈
python main.py convert ./raw_photos -t webp -q 90 -o 朋友圈版
```

### 场景三：扫描件存档

```bash
# 将扫描的 TIFF 转为 PDF 兼容的 JPEG
python main.py convert ./扫描件 -t jpg -q 95 -o 归档版
```

---

## 文件结构

```
image_batch_processor/
├── main.py                 # 主程序（包含全部功能）
├── requirements.txt        # Python 依赖（仅 Pillow）
├── README.md               # 使用文档
├── meta.json               # 工具元信息
└── example/                # 示例文件夹
    ├── sample_photo.jpg    # 示例图片
    └── run_example.bat     # 一键运行示例
```

---

## 注意事项

- 水印功能支持中文，Windows 下会自动使用微软雅黑字体
- 原图不会被修改，所有操作输出到独立的文件夹
- 批量重命名不可逆，建议先备份
- 本工具由 AI 辅助生成，使用前请测试确认符合需求
