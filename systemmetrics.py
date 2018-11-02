"""
ToDo:
    - Implement remaining SystemMetrics
"""
import win32api
import win32con

class SystemMetrics():
    """Wrapper Class for win32api.GetSystemMetrics
    """
    screen_width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
    screen_height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)