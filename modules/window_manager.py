import win32gui
import win32con
import win32api
import ctypes
from ctypes import wintypes, POINTER
import threading
import time
import win32process

class WindowManager:
    def __init__(self):
        self.user32 = ctypes.windll.user32
        self.screen_width = win32api.GetSystemMetrics(0)
        self.screen_height = win32api.GetSystemMetrics(1)
        
        # 维护隐藏窗口字典
        self.hidden_windows = {
            'left': None,
            'right': None,
            'top': None,
            'bottom': None
        }
        self.original_positions = {}
        self.visible_part = 10
        
        # 初始化临时显示窗口的集合和位置字典
        self.shown_windows = set()
        self.window_positions = {}

    def is_window_valid(self, hwnd):
        """检查窗口是否有效"""
        try:
            return win32gui.IsWindow(hwnd)
        except:
            return False

    def force_foreground_window(self, hwnd):
        """强制将窗口设置为前台窗口"""
        try:
            # 获取当前前台窗口信息
            foreground_hwnd = self.user32.GetForegroundWindow()
            foreground_thread = self.user32.GetWindowThreadProcessId(foreground_hwnd, None)
            target_thread = self.user32.GetWindowThreadProcessId(hwnd, None)
            current_thread = win32api.GetCurrentThreadId()
            
            # 将线程输入状态关联
            self.user32.AttachThreadInput(target_thread, foreground_thread, True)
            self.user32.AttachThreadInput(current_thread, foreground_thread, True)
            
            # 激活窗口
            self.user32.ShowWindow(hwnd, win32con.SW_RESTORE)
            self.user32.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, 
                                   win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW)
            self.user32.SetForegroundWindow(hwnd)
            self.user32.BringWindowToTop(hwnd)
            
            # 恢复窗口Z序
            self.user32.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0,
                                   win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW)
            
            # 解除线程输入状态关联
            self.user32.AttachThreadInput(current_thread, foreground_thread, False)
            self.user32.AttachThreadInput(target_thread, foreground_thread, False)
            
        except Exception as e:
            print(f"Error forcing foreground window: {e}")

    def get_window_rect(self, hwnd):
        """获取窗口位置和大小"""
        rect = win32gui.GetWindowRect(hwnd)
        return {
            'x': rect[0],
            'y': rect[1],
            'width': rect[2] - rect[0],
            'height': rect[3] - rect[1]
        }

    def set_window_pos(self, hwnd, x, y):
        """设置窗口位置"""
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, x, y, 
                            0, 0, win32con.SWP_NOSIZE)

    def calculate_hidden_position(self, direction, rect):
        """计算窗口隐藏位置"""
        if direction == 'right':
            return self.screen_width - self.visible_part, rect['y']
        elif direction == 'left':
            return -rect['width'] + self.visible_part, rect['y']
        elif direction == 'top':
            return rect['x'], -rect['height'] + self.visible_part
        else:  # bottom
            return rect['x'], self.screen_height - self.visible_part

    def get_hidden_windows(self):
        """获取隐藏窗口"""
        return self.hidden_windows

    def set_hidden_window(self, direction, window_info):
        """设置隐藏窗口"""
        self.hidden_windows[direction] = window_info

    def show_window_temp(self, direction, hwnd, rect):
        """临时显示窗口"""
        if hwnd not in self.shown_windows and self.is_window_valid(hwnd):
            end_x, end_y = self.get_temp_show_position(direction, rect)
            
            # 先设置窗口位置
            self.set_window_pos(hwnd, end_x, end_y)
            
            # 确保窗口可见
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            
            # 强制激活窗口
            self.force_foreground_window(hwnd)
            
            self.shown_windows.add(hwnd)
            self.window_positions[hwnd] = (end_x, end_y)

    def hide_window_temp(self, direction, hwnd, rect, mouse_x, mouse_y):
        """临时隐藏窗口"""
        if not (rect['x'] <= mouse_x <= rect['x'] + rect['width'] and 
                rect['y'] <= mouse_y <= rect['y'] + rect['height']):
            end_x, end_y = self.calculate_hidden_position(direction, rect)
            
            if self.is_window_valid(hwnd):
                # 先设置窗口位置
                self.set_window_pos(hwnd, end_x, end_y)
                
                # 验证窗口是否成功隐藏
                new_rect = self.get_window_rect(hwnd)
                if abs(new_rect['x'] - end_x) <= 5 and abs(new_rect['y'] - end_y) <= 5:
                    self.shown_windows.remove(hwnd)
                    self.window_positions.pop(hwnd, None)
                else:
                    print(f"窗口 {win32gui.GetWindowText(hwnd)} 隐藏失败")
                    self.cleanup_window(direction, hwnd)

    def cleanup_window(self, direction, hwnd):
        """清理窗口相关数据"""
        self.hidden_windows[direction] = None
        self.shown_windows.discard(hwnd)
        self.window_positions.pop(hwnd, None)

    def get_temp_show_position(self, direction, rect):
        """获取临时显示位置"""
        if direction == 'left':
            return 0, rect['y']
        elif direction == 'right':
            return self.screen_width - rect['width'], rect['y']
        elif direction == 'top':
            return rect['x'], 0
        else:  # bottom
            return rect['x'], self.screen_height - rect['height']