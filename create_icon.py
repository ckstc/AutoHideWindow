from PIL import Image, ImageDraw

def create_water_icon():
    """创建水字形状的图标"""
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    images = []
    
    for size in sizes:
        image = Image.new('RGBA', size, color=(0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # 计算缩放比例
        scale = size[0] / 64.0
        
        # 绘制类似甲骨文中"水"字的图形
        # 主体部分
        points = [
            (int(32 * scale), int(10 * scale)),  # 顶部中心
            (int(15 * scale), int(25 * scale)),  # 左上
            (int(20 * scale), int(32 * scale)),  # 左中
            (int(15 * scale), int(40 * scale)),  # 左下
            (int(32 * scale), int(50 * scale)),  # 底部中心
            (int(49 * scale), int(40 * scale)),  # 右下
            (int(44 * scale), int(32 * scale)),  # 右中
            (int(49 * scale), int(25 * scale)),  # 右上
            (int(32 * scale), int(10 * scale))   # 回到顶部中心
        ]
        
        # 绘制外边框（白色）
        line_width = max(1, int(3 * scale))
        draw.line(points, fill=(255, 255, 255), width=line_width)
        
        # 绘制内部波浪线（白色）
        wave_points = [
            (int(25 * scale), int(28 * scale)),
            (int(32 * scale), int(33 * scale)),
            (int(39 * scale), int(28 * scale)),
            (int(32 * scale), int(38 * scale)),
            (int(25 * scale), int(33 * scale))
        ]
        wave_width = max(1, int(2 * scale))
        draw.line(wave_points, fill=(255, 255, 255), width=wave_width)
        
        images.append(image)
    
    # 保存为ICO文件
    images[0].save('icon.ico', format='ICO', sizes=sizes, append_images=images[1:])

if __name__ == '__main__':
    create_water_icon() 