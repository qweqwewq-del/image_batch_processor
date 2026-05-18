@echo off
chcp 65001 >nul
echo === 生成示例图片 ===
python create_sample_data.py
echo.
echo === 1. 调整尺寸为 400x300 ===
python ..\main.py resize . -W 400 -H 300 -o resized
echo.
echo === 2. 添加水印 ===
python ..\main.py watermark . "Sample Watermark" -p bottom-right -o watermarked
echo.
echo === 3. 转换为 WebP ===
python ..\main.py convert . -t webp -q 85 -o converted
echo.
echo === 4. 压缩图片 ===
python ..\main.py compress . -q 50 -o compressed
echo.
echo === 5. 查看图片信息 ===
python ..\main.py info .
echo.
echo 全部完成！检查 resized/ watermarked/ converted/ compressed/ 目录
pause
