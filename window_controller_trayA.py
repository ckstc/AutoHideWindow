import tkinter as tk
import os
from modules import WindowManager, AnimationController, InputHandler, TrayIcon

class WindowController:
    def __init__(self):
        # 初始化运行标志
        self.running = True
        
        # 初始化各个模块
        self.window_manager = WindowManager()
        self.animation_controller = AnimationController(self.window_manager)
        self.input_handler = InputHandler(self.window_manager, self.animation_controller)
        self.tray_icon = TrayIcon(self.animation_controller, self.quit_app)
        
        # 启动输入监听
        self.input_handler.start()
        
        # 启动系统托盘
        self.tray_icon.run()

    def quit_app(self, icon=None, item=None):
        """退出应用程序"""
        try:
            # 设置退出标志
            self.running = False
            
            # 停止输入监听
            self.input_handler.stop()
            
            # 停止系统托盘
            self.tray_icon.stop()
            
            # 强制退出程序
            os._exit(0)
            
        except Exception as e:
            print(f"Error during quit: {e}")
            os._exit(1)

    def run(self):
        """运行程序"""
        try:
            # 创建一个隐藏的tkinter窗口来保持程序运行
            root = tk.Tk()
            root.withdraw()
            root.mainloop()
        except Exception as e:
            print(f"Error in main loop: {e}")
        finally:
            self.quit_app()

if __name__ == "__main__":
    try:
        app = WindowController()
        app.run()
    except Exception as e:
        print(f"Program error: {e}")
        os._exit(1)  # 直接退出程序不等待用户输入