import threading
import tkinter as tk
import pystray
from PIL import Image, ImageDraw
import winreg
import os
import sys
from .animation_controller import AnimationController

class TrayIcon:
    def __init__(self, animation_controller: AnimationController, quit_callback):
        self.animation_controller = animation_controller
        self.quit_callback = quit_callback
        self.create_tray_icon()
        self.startup_reg_name = "WindowControllerA"
        self.app_path = os.path.abspath(sys.argv[0])

    def create_tray_icon(self):
        """创建系统托盘图标"""
        menu = (
            pystray.MenuItem("使用说明", self.show_instructions),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("动画设置", 
                pystray.Menu(
                    pystray.MenuItem(
                        "启用动画",
                        lambda: self.set_animation_enabled(True),
                        checked=lambda item: self.animation_controller.animation_enabled
                    ),
                    pystray.MenuItem(
                        "关闭动画",
                        lambda: self.set_animation_enabled(False),
                        checked=lambda item: not self.animation_controller.animation_enabled
                    ),
                    pystray.Menu.SEPARATOR,
                    pystray.MenuItem("动画速度", 
                        pystray.Menu(
                            pystray.MenuItem("0.5x (慢速)", lambda: self.set_speed(0.5)),
                            pystray.MenuItem("1.0x (标准)", lambda: self.set_speed(1.0)),
                            pystray.MenuItem("1.5x (快速)", lambda: self.set_speed(1.5)),
                            pystray.MenuItem("2.0x (极速)", lambda: self.set_speed(2.0))
                        )
                    ),
                    pystray.MenuItem("动画效果",
                        pystray.Menu(
                            pystray.MenuItem("线性", lambda: self.set_curve('linear')),
                            pystray.MenuItem("平滑", lambda: self.set_curve('ease')),
                            pystray.MenuItem("缓入", lambda: self.set_curve('ease-in')),
                            pystray.MenuItem("缓出", lambda: self.set_curve('ease-out'))
                        )
                    ),
                    pystray.MenuItem("动画质量",
                        pystray.Menu(
                            pystray.MenuItem("流畅 (60步)", lambda: self.set_quality(60, 8)),
                            pystray.MenuItem("标准 (30步)", lambda: self.set_quality(30, 8)),
                            pystray.MenuItem("省电 (15步)", lambda: self.set_quality(15, 12))
                        )
                    )
                )
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "开机启动",
                self.toggle_startup,
                checked=lambda item: self.is_startup_enabled()
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("退出", self.quit_callback)
        )
        
        # 创建水字形状的图标
        image = self.create_water_icon()
        
        # 创建系统托盘图标
        self.tray_icon = pystray.Icon(
            "window_controller",
            image,
            "窗口控制器",
            menu
        )

    def is_startup_enabled(self):
        """检查是否已设置开机启动"""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_READ
            )
            try:
                value, _ = winreg.QueryValueEx(key, self.startup_reg_name)
                return value == f'"{self.app_path}"'
            except WindowsError:
                return False
            finally:
                winreg.CloseKey(key)
        except WindowsError:
            return False

    def toggle_startup(self, icon, item):
        """切换开机启动状态"""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_SET_VALUE | winreg.KEY_READ
            )
            
            if self.is_startup_enabled():
                # 删除开机启动项
                winreg.DeleteValue(key, self.startup_reg_name)
                print("已禁用开机启动")
            else:
                # 添加开机启动项
                winreg.SetValueEx(
                    key,
                    self.startup_reg_name,
                    0,
                    winreg.REG_SZ,
                    f'"{self.app_path}"'
                )
                print("已启用开机启动")
                
            winreg.CloseKey(key)
        except Exception as e:
            print(f"设置开机启动时出错: {e}")

    def create_water_icon(self):
        """创建水字形状的图标"""
        image = Image.new('RGBA', (64, 64), color=(255, 255, 255, 0))
        draw = ImageDraw.Draw(image)
        
        # 绘制类似甲骨文中"水"字的图形
        # 主体部分
        points = [
            (32, 10),  # 顶部中心
            (15, 25),  # 左上
            (20, 32),  # 左中
            (15, 40),  # 左下
            (32, 50),  # 底部中心
            (49, 40),  # 右下
            (44, 32),  # 右中
            (49, 25),  # 右上
            (32, 10)   # 回到顶部中心
        ]
        
        # 绘制外边框（白色）
        draw.line(points, fill=(255, 255, 255), width=3)
        
        # 绘制内部波浪线（白色）
        wave_points = [
            (25, 28),
            (32, 33),
            (39, 28),
            (32, 38),
            (25, 33)
        ]
        draw.line(wave_points, fill=(255, 255, 255), width=2)
        
        return image

    def show_instructions(self, icon, item):
        """显示使用说明"""
        instruction_window = tk.Tk()
        instruction_window.title("使用说明")
        instruction_window.geometry("400x450")
        
        instructions = """
        使用说明：
        
        1. 快捷键操作：
           - Shift + 方向键：隐藏当前窗口到对应方向
           - 再次 Shift + 方向键：显示该方向的隐藏窗口
        
        2. 鼠标触发：
           - 将鼠标移动到屏幕边缘可显示隐藏的窗口
           - 鼠标离开窗口区域后窗口自动隐藏
        
        3. 动画设置：
           - 启用/关闭动画：完全开启或关闭动画效果
           - 动画速度：
             * 0.5x：慢速移动
             * 1.0x：标准速度
             * 1.5x：快速移动
             * 2.0x：极速移动
           - 动画效果：
             * 线性：匀速移动
             * 平滑：渐入渐出
             * 缓入：开始慢后来快
             * 缓出：开始快后来慢
           - 动画质量：
             * 流畅：最高质量 (60步)
             * 标准：平衡性能 (30步)
             * 省电：性能优先 (15步)
        
        4. 开机启动：
           - 勾选"开机启动"选项即可设置开机自动运行
        
        5. 退出程序：
           - 右键点击托盘图标，选择"退出"即可
        """
        
        text = tk.Text(instruction_window, wrap=tk.WORD, padx=10, pady=10)
        text.insert("1.0", instructions)
        text.config(state=tk.DISABLED)
        text.pack(fill=tk.BOTH, expand=True)
        
        instruction_window.mainloop()

    def set_animation_enabled(self, enabled):
        """设置动画开关"""
        self.animation_controller.set_animation_enabled(enabled)

    def set_speed(self, speed):
        """设置动画速度"""
        self.animation_controller.set_animation_speed(speed)

    def set_quality(self, steps, interval):
        """设置动画质量"""
        self.animation_controller.set_animation_quality(steps, interval)

    def set_curve(self, curve_type):
        """设置动画曲线"""
        self.animation_controller.set_animation_curve(curve_type)

    def run(self):
        """运行系统托盘"""
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def stop(self):
        """停止系统托盘"""
        if hasattr(self, 'tray_icon'):
            try:
                self.tray_icon.visible = False
                self.tray_icon.stop()
            except:
                pass 