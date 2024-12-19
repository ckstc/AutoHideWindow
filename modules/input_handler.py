import threading
import time
import win32api
import win32gui
from pynput import keyboard
from .window_manager import WindowManager
from .animation_controller import AnimationController

class InputHandler:
    def __init__(self, window_manager: WindowManager, animation_controller: AnimationController):
        self.window_manager = window_manager
        self.animation_controller = animation_controller
        self.running = True
        self.shift_pressed = False
        self.edge_trigger_size = 5
        
        # 用于鼠标监控的状态
        self.shown_windows = set()
        self.window_positions = {}
        
        # 启动键盘监听
        self.keyboard_listener = keyboard.Listener(
            on_press=self.on_key_press,
            on_release=self.on_key_release)
        
        # 启动鼠标监控线程
        self.mouse_thread = threading.Thread(target=self.monitor_mouse, daemon=True)

    def start(self):
        """启动输入监听"""
        self.keyboard_listener.start()
        self.mouse_thread.start()

    def stop(self):
        """停止输入监听"""
        self.running = False
        if hasattr(self, 'keyboard_listener'):
            self.keyboard_listener.stop()

    def on_key_press(self, key):
        """处理按键事件"""
        try:
            if key == keyboard.Key.shift:
                self.shift_pressed = True
                return
            
            if self.shift_pressed and hasattr(key, 'name'):
                direction_map = {
                    'left': 'left',
                    'right': 'right',
                    'up': 'top',
                    'down': 'bottom'
                }
                
                if key.name in direction_map:
                    direction = direction_map[key.name]
                    hidden_windows = self.window_manager.get_hidden_windows()
                    if hidden_windows[direction]:
                        self.show_hidden_window(direction)
                    else:
                        self.hide_active_window(direction)
        except Exception as e:
            print(f"Error in key handling: {e}")

    def on_key_release(self, key):
        """处理按键释放事件"""
        if key == keyboard.Key.shift:
            self.shift_pressed = False

    def hide_active_window(self, direction):
        """隐藏当前活动窗口"""
        try:
            hwnd = self.window_manager.user32.GetForegroundWindow()
            hidden_windows = self.window_manager.get_hidden_windows()
            
            if hidden_windows[direction]:
                return
            
            title = win32gui.GetWindowText(hwnd)
            if not title:
                return
                
            rect = self.window_manager.get_window_rect(hwnd)
            self.window_manager.original_positions[hwnd] = (rect['x'], rect['y'])
            
            end_x, end_y = self.window_manager.calculate_hidden_position(direction, rect)
            if self.animation_controller.animation_enabled:
                self.animation_controller.animate_window(hwnd, rect['x'], rect['y'], end_x, end_y)
            else:
                self.window_manager.set_window_pos(hwnd, end_x, end_y)
            
            self.window_manager.set_hidden_window(direction, (hwnd, title))
            
        except Exception as e:
            print(f"Error hiding window: {e}")

    def show_hidden_window(self, direction):
        """显示指定方向的窗口"""
        try:
            hidden_windows = self.window_manager.get_hidden_windows()
            if not hidden_windows[direction]:
                return
                
            hwnd = hidden_windows[direction][0]
            rect = self.window_manager.get_window_rect(hwnd)
            
            if hwnd in self.window_manager.original_positions:
                end_x, end_y = self.window_manager.original_positions[hwnd]
                del self.window_manager.original_positions[hwnd]
            else:
                width, height = rect['width'], rect['height']
                end_x = (self.window_manager.screen_width - width) // 2
                end_y = (self.window_manager.screen_height - height) // 2
            
            self.window_manager.force_foreground_window(hwnd)
            if self.animation_controller.animation_enabled:
                self.animation_controller.animate_window(hwnd, rect['x'], rect['y'], end_x, end_y)
            else:
                self.window_manager.set_window_pos(hwnd, end_x, end_y)
            self.window_manager.set_hidden_window(direction, None)
            
        except Exception as e:
            print(f"Error showing window: {e}")

    def monitor_mouse(self):
        """监控鼠标位置"""
        while self.running:
            try:
                x, y = win32api.GetCursorPos()
                hidden_windows = self.window_manager.get_hidden_windows()
                
                for direction, window_info in list(hidden_windows.items()):
                    if window_info is None:
                        continue
                        
                    hwnd = window_info[0]
                    
                    if not self.window_manager.is_window_valid(hwnd):
                        self.cleanup_window(direction, hwnd)
                        continue
                    
                    try:
                        rect = self.window_manager.get_window_rect(hwnd)
                        
                        if hwnd in self.shown_windows:
                            if self.check_window_moved(hwnd, rect):
                                continue
                        
                        if self.should_show_window(direction, x, y):
                            self.show_window_temp(direction, hwnd, rect)
                        elif hwnd in self.shown_windows:
                            self.hide_window_temp(direction, hwnd, rect, x, y)
                            
                    except Exception:
                        self.cleanup_window(direction, hwnd)
                        
            except Exception as e:
                if self.running:
                    print(f"Error in mouse monitoring: {e}")
                
            time.sleep(0.1)

    def cleanup_window(self, direction, hwnd):
        """清理窗口相关数据"""
        self.window_manager.set_hidden_window(direction, None)
        self.shown_windows.discard(hwnd)
        self.window_positions.pop(hwnd, None)

    def check_window_moved(self, hwnd, rect):
        """检查窗口是否被手动移动"""
        original_pos = self.window_positions.get(hwnd)
        if original_pos:
            dx = abs(original_pos[0] - rect['x'])
            dy = abs(original_pos[1] - rect['y'])
            if dx > 20 or dy > 20:
                # 找到对应的方向
                hidden_windows = self.window_manager.get_hidden_windows()
                direction = next(k for k, v in hidden_windows.items() if v and v[0] == hwnd)
                self.cleanup_window(direction, hwnd)
                return True
        return False

    def should_show_window(self, direction, x, y):
        """判断是否应该显示窗口"""
        if direction == 'left':
            return x < self.edge_trigger_size
        elif direction == 'right':
            return x >= self.window_manager.screen_width - self.edge_trigger_size
        elif direction == 'top':
            return y < self.edge_trigger_size
        else:  # bottom
            return y >= self.window_manager.screen_height - self.edge_trigger_size

    def show_window_temp(self, direction, hwnd, rect):
        """临时显示窗口"""
        if hwnd not in self.shown_windows and self.window_manager.is_window_valid(hwnd):
            end_x, end_y = self.get_temp_show_position(direction, rect)
            self.window_manager.force_foreground_window(hwnd)
            if self.animation_controller.animation_enabled:
                self.animation_controller.animate_window(hwnd, rect['x'], rect['y'], end_x, end_y)
            else:
                self.window_manager.set_window_pos(hwnd, end_x, end_y)
            self.shown_windows.add(hwnd)
            self.window_positions[hwnd] = (end_x, end_y)

    def hide_window_temp(self, direction, hwnd, rect, mouse_x, mouse_y):
        """临时隐藏窗口"""
        if not (rect['x'] <= mouse_x <= rect['x'] + rect['width'] and 
                rect['y'] <= mouse_y <= rect['y'] + rect['height']):
            end_x, end_y = self.window_manager.calculate_hidden_position(direction, rect)
            
            if self.window_manager.is_window_valid(hwnd):
                if self.animation_controller.animation_enabled:
                    self.animation_controller.animate_window(hwnd, rect['x'], rect['y'], end_x, end_y)
                else:
                    self.window_manager.set_window_pos(hwnd, end_x, end_y)
                
                if self.animation_controller.verify_window_hidden(
                    hwnd, direction, rect['x'], rect['y'], end_x, end_y):
                    self.shown_windows.remove(hwnd)
                    self.window_positions.pop(hwnd, None)
                else:
                    print(f"窗口 {win32gui.GetWindowText(hwnd)} 隐藏失败")
                    self.cleanup_window(direction, hwnd)

    def get_temp_show_position(self, direction, rect):
        """获取临时显示位置"""
        if direction == 'left':
            return 0, rect['y']
        elif direction == 'right':
            return self.window_manager.screen_width - rect['width'], rect['y']
        elif direction == 'top':
            return rect['x'], 0
        else:  # bottom
            return rect['x'], self.window_manager.screen_height - rect['height']