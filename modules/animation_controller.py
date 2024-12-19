import time
from .window_manager import WindowManager

class AnimationController:
    def __init__(self, window_manager: WindowManager):
        self.window_manager = window_manager
        # 动画开关，默认关闭
        self.animation_enabled = False
        # 动画速度（倍率）
        self.animation_speed = 1.0
        # 动画步数（越大越平滑，但可能更耗性能）
        self.animation_steps = 30
        # 每步时间间隔（毫秒）
        self.animation_interval = 8
        # 动画曲线类型
        self.animation_curve = 'ease'  # 'linear', 'ease', 'ease-in', 'ease-out'
        
    def set_animation_enabled(self, enabled):
        """设置动画开关"""
        self.animation_enabled = enabled

    def set_animation_speed(self, speed):
        """设置动画速度"""
        self.animation_speed = speed

    def set_animation_quality(self, steps, interval):
        """设置动画质量
        
        Args:
            steps: 动画步数（10-60）
            interval: 每步时间间隔（1-20毫秒）
        """
        self.animation_steps = max(10, min(60, steps))
        self.animation_interval = max(1, min(20, interval))

    def set_animation_curve(self, curve_type):
        """设置动画曲线类型"""
        if curve_type in ['linear', 'ease', 'ease-in', 'ease-out']:
            self.animation_curve = curve_type

    def get_curve_value(self, progress):
        """根据动画曲线类型计算插值
        
        Args:
            progress: 动画进度（0-1）
        Returns:
            插值后的进度值（0-1）
        """
        if self.animation_curve == 'linear':
            return progress
        elif self.animation_curve == 'ease':
            # 使用三次贝塞尔曲线
            return progress * progress * (3 - 2 * progress)
        elif self.animation_curve == 'ease-in':
            # 缓入
            return progress * progress
        elif self.animation_curve == 'ease-out':
            # 缓出
            return 1 - (1 - progress) * (1 - progress)
        return progress

    def animate_window(self, hwnd, start_x, start_y, end_x, end_y):
        """使用动画移动窗口"""
        if not self.animation_enabled:
            # 如果动画被禁用，直接移动到目标位置
            self.window_manager.set_window_pos(hwnd, end_x, end_y)
            return
            
        interval = self.animation_interval / self.animation_speed
        
        for i in range(self.animation_steps + 1):
            progress = i / self.animation_steps
            eased_progress = self.get_curve_value(progress)
            
            x = int(start_x + (end_x - start_x) * eased_progress)
            y = int(start_y + (end_y - start_y) * eased_progress)
            
            self.window_manager.set_window_pos(hwnd, x, y)
            time.sleep(interval / 1000)  # 转换为秒

    def verify_window_hidden(self, hwnd, direction, start_x, start_y, end_x, end_y, retries=3):
        """验证窗口是否成功隐藏，如果没有则重试"""
        for _ in range(retries):
            try:
                rect = self.window_manager.get_window_rect(hwnd)
                current_x, current_y = rect['x'], rect['y']
                
                # 检查窗口位置是否符合预期的隐藏位置（允许5像素误差）
                if abs(current_x - end_x) <= 5 and abs(current_y - end_y) <= 5:
                    return True
                    
                # 如果位置不对，重新尝试隐藏
                if self.animation_enabled:
                    self.animate_window(hwnd, current_x, current_y, end_x, end_y)
                    time.sleep(0.1)  # 等待动画完成
                else:
                    self.window_manager.set_window_pos(hwnd, end_x, end_y)
                
            except Exception as e:
                print(f"验证窗口隐藏时出错: {e}")
                return False
                
        return False 