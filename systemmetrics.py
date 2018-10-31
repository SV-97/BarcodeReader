import win32api
import win32con

class SystemMetrics():
    screen_width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
    screen_height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)

if __name__=="__main__":
    print(f"{SystemMetrics.screen_width}x{SystemMetrics.screen_height}")