import winreg
from ctypes import Structure, c_int, POINTER, windll, byref, sizeof, cast
from ctypes.wintypes import DWORD, HWND, UINT, RECT, LPARAM, MSG, LPRECT
from enum import Enum
from sys import getwindowsversion
import platform

import win32api
import win32con
import win32gui


from PyQt6.QtCore import Qt, QTimer, QPointF, QSize, QEasingCurve, QPropertyAnimation, QAbstractAnimation
from PyQt6.QtGui import QGuiApplication, QPainter, QPen, QPainterPath, QIcon, QCursor
from PyQt6.QtWidgets import QWidget, QToolButton, QLabel, QHBoxLayout, QMainWindow, QDialog, QFrame, QMessageBox, QGraphicsOpacityEffect

from win32comext.shell import shellcon

from .window_effects import WindowsEffects

is_win11 = getwindowsversion().build >= 22000
# is_win11 = False
# is_win11 = True

class APPBARDATA(Structure):
    _fields_ = [
        ('cbSize', DWORD),
        ('hWnd', HWND),
        ('uCallbackMessage', UINT),
        ('uEdge', UINT),
        ('rc', RECT),
        ('lParam', LPARAM)
    ]


class PWINDOWPOS(Structure):
    _fields_ = [
        ('hWnd', HWND),
        ('hwndInsertAfter', HWND),
        ('x', c_int),
        ('y', c_int),
        ('cx', c_int),
        ('cy', c_int),
        ('flags', UINT)
    ]


class NCCALCSIZE_PARAMS(Structure):
    _fields_ = [
        ('rgrc', RECT * 3),
        ('lppos', POINTER(PWINDOWPOS))
    ]


LPNCCALCSIZE_PARAMS = POINTER(NCCALCSIZE_PARAMS)

def is_maximized(h_wnd):
    win_placement = win32gui.GetWindowPlacement(h_wnd)
    if win_placement:
        return win_placement[1] == win32con.SW_MAXIMIZE
    return False


def get_monitor_info(h_wnd, dw_flags):
    monitor = win32api.MonitorFromWindow(h_wnd, dw_flags)
    if monitor:
        return win32api.GetMonitorInfo(monitor)

def is_full_screen(h_wnd):
    if not h_wnd:
        return False
    h_wnd = int(h_wnd)

    win_rect = win32gui.GetWindowRect(h_wnd)
    if not win_rect:
        return False

    monitor_info = get_monitor_info(h_wnd, win32con.MONITOR_DEFAULTTOPRIMARY)
    if not monitor_info:
        return False

    monitor_rect = monitor_info['Monitor']
    return all(i == j for i, j in zip(win_rect, monitor_rect))


def find_window(h_wnd):
    if not h_wnd:
        return

    windows = QGuiApplication.topLevelWindows()
    if not windows:
        return

    for window in windows:
        if window and int(window.winId()) == int(h_wnd):
            return window


def get_resize_border_thickness(h_wnd):
    window = find_window(h_wnd)
    if not window:
        return 0

    result = win32api.GetSystemMetrics(
        win32con.SM_CXSIZEFRAME) + win32api.GetSystemMetrics(92)

    if result > 0:
        return result

    b_result = c_int(0)
    windll.dwmapi.DwmIsCompositionEnabled(byref(b_result))
    thickness = 8 if bool(b_result.value) else 4
    return round(thickness * window.devicePixelRatio())


class Taskbar:
    LEFT = 0
    TOP = 1
    RIGHT = 2
    BOTTOM = 3
    NO_POSITION = 4

    AUTO_HIDE_THICKNESS = 2

    @staticmethod
    def is_auto_hide():
        appbar_data = APPBARDATA(
            sizeof(APPBARDATA), 0, 0, 0, RECT(0, 0, 0, 0), 0)
        taskbar_state = windll.shell32.SHAppBarMessage(
            shellcon.ABM_GETSTATE, byref(appbar_data))
        return taskbar_state == shellcon.ABS_AUTOHIDE

    @classmethod
    def get_position(cls, h_wnd):
        monitor_info = get_monitor_info(
            h_wnd, win32con.MONITOR_DEFAULTTONEAREST)
        if not monitor_info:
            return cls.NO_POSITION

        monitor = RECT(*monitor_info['Monitor'])
        appbar_data = APPBARDATA(sizeof(APPBARDATA), 0, 0, 0, monitor, 0)
        for position in (cls.LEFT, cls.TOP, cls.RIGHT, cls.BOTTOM):
            appbar_data.uEdge = position
            if windll.shell32.SHAppBarMessage(11, byref(appbar_data)):
                return position

        return cls.NO_POSITION

def invert_color(color):
    inverted_color = ''
    for i in range(0, 5, 2):
        channel = int(color[i:i + 2], base=16)
        inverted_color += hex(round(channel / 6))[2:].upper().zfill(2)
    inverted_color += color[-2:]
    return inverted_color


class CustomBase(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent

        self.effect_enabled = False
        self._effect_timer = None
# 
        self.win_effects = WindowsEffects()      

        self.setWindowFlags(Qt.WindowType.Window | 
                            Qt.WindowType.FramelessWindowHint |
                            Qt.WindowType.WindowSystemMenuHint |
                            Qt.WindowType.WindowMinimizeButtonHint |
                            Qt.WindowType.WindowMaximizeButtonHint |
                            Qt.WindowType.WindowCloseButtonHint) 
        
        self.win_effects.add_window_animation(self.winId())
        self.set_effect(True)

        if is_win11:
            self.win_effects.add_blur_behind_window(self.winId())
            self.win_effects.add_shadow_effect(self.winId())
        
        self._effect_timer = QTimer(self)
        self._effect_timer.setInterval(10)
        self._effect_timer.setSingleShot(True)
        self._effect_timer.timeout.connect(self.set_effect)
        self.animate()

    def animate(self, reverse=False):
        # animate startup
        effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(effect)
        animation = QPropertyAnimation(self)
        animation.setPropertyName(bytes("opacity", "utf-8"))
        animation.setTargetObject(effect)
        animation.setDuration(450)
        animation.setStartValue(0)
        animation.setEndValue(1)

        if reverse:
            animation.setStartValue(1)
            animation.setEndValue(0)
            animation.setDuration(200)
        
        animation.setEasingCurve(QEasingCurve.Type.OutInCubic)
        animation.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
        animation.finished.connect(lambda: self.setGraphicsEffect(None))

    def set_effect(self, enable=True):
        if self.effect_enabled == enable:
            return
        
        if enable and is_win11:
            self.win_effects.add_mica_effect(self.winId())
        else:
            self.win_effects.remove_background_effect(self.winId())

        self.effect_enabled = enable
        self.update()

    def _temporary_disable_effect(self):
        self.set_effect(False)
        self._effect_timer.start()

    def moveEvent(self, event):
        if is_win11 or not self._effect_timer:
            return super().moveEvent(event)
        self._temporary_disable_effect()

    def paintEvent(self, event):
        if self.effect_enabled:
            return super().paintEvent(event)

    def nativeEvent(self, event_type, message):
        msg = MSG.from_address(int(message))
        if not msg.hWnd:
            return False, 0
        if msg.message == win32con.WM_NCCALCSIZE:
            if msg.wParam:
                rect = cast(msg.lParam, LPNCCALCSIZE_PARAMS).contents.rgrc[0]
            else:
                rect = cast(msg.lParam, LPRECT).contents

            is_max = is_maximized(msg.hWnd)
            is_full = is_full_screen(msg.hWnd)

            # Adjust the size of client rect
            if is_max and not is_full:
                thickness = get_resize_border_thickness(msg.hWnd)
                rect.top += thickness
                rect.left += thickness
                rect.right -= thickness
                rect.bottom -= thickness

            # Handle the situation that an auto-hide taskbar is enabled
            if (is_max or is_full) and Taskbar.is_auto_hide():
                position = Taskbar.get_position(msg.hWnd)
                if position == Taskbar.LEFT:
                    rect.top += Taskbar.AUTO_HIDE_THICKNESS
                elif position == Taskbar.BOTTOM:
                    rect.bottom -= Taskbar.AUTO_HIDE_THICKNESS
                elif position == Taskbar.LEFT:
                    rect.left += Taskbar.AUTO_HIDE_THICKNESS
                elif position == Taskbar.RIGHT:
                    rect.right -= Taskbar.AUTO_HIDE_THICKNESS

            res = 0 if not msg.wParam else win32con.WVR_REDRAW
            return True, res

        return False, 0

class CustomWindow(CustomBase):
    BORDER_WIDTH = 4
    max_btn_hovered = False
    title_bar = None

    def __init__(self, parent=None):
        self.parent = parent
        CustomBase.__init__(self, parent=parent)

    def resizeEvent(self, event):
        if not self.title_bar:  # if not initialized
            return
        self.title_bar.setFixedWidth(self.width())

        super().resizeEvent(event)

    def nativeEvent(self, event_type, message):

        msg = MSG.from_address(int(message))
        if not msg.hWnd:
            return False, 0
        
        if msg.message == win32con.WM_NCHITTEST:
            super().nativeEvent(event_type, message)

            pos = QCursor.pos()
            x = pos.x() - self.x()
            y = pos.y() - self.y()
            
            if is_win11 and self.title_bar and self.title_bar.childAt(
                    pos - self.geometry().topLeft()) is self.title_bar.max_btn:
                self.max_btn_hovered = True
                self.title_bar.max_btn.set_state(TitleBarButtonState.HOVER)
                return True, win32con.HTMAXBUTTON

            lx = x < self.BORDER_WIDTH
            rx = x > self.width() - self.BORDER_WIDTH
            ty = y < self.BORDER_WIDTH
            by = y > self.height() - self.BORDER_WIDTH
            if rx and by:
                return True, win32con.HTBOTTOMRIGHT
            elif rx and ty:
                return True, win32con.HTTOPRIGHT
            elif lx and by:
                return True, win32con.HTBOTTOMLEFT
            elif lx and ty:
                return True, win32con.HTTOPLEFT
            elif rx:
                return True, win32con.HTRIGHT
            elif by:
                return True, win32con.HTBOTTOM
            elif lx:
                return True, win32con.HTLEFT
            elif ty:
                return True, win32con.HTTOP

        elif is_win11 and self.max_btn_hovered:
            if msg.message == win32con.WM_NCLBUTTONDOWN:
                self.title_bar.max_btn.set_state(TitleBarButtonState.PRESSED)
                return True, 0
            elif msg.message in [win32con.WM_NCLBUTTONUP,
                                 win32con.WM_NCRBUTTONUP]:
                self.title_bar.max_btn.click()
            elif msg.message in [0x2A2, win32con.WM_MOUSELEAVE] \
                    and self.title_bar.max_btn.get_state() != 0:
                self.max_btn_hovered = False
                self.title_bar.max_btn.set_state(TitleBarButtonState.NORMAL)

        return super().nativeEvent(event_type, message)


class CustomMainWindow(QMainWindow, CustomWindow):
    def __init__(self, parent=None):
        self.parent=parent
        CustomWindow.__init__(self, parent=parent)


class CustomDialog(QDialog, CustomWindow):
    def __init__(self, parent=None):
        self.parent=parent
        CustomWindow.__init__(self, parent=parent)


class TitleBarButtonState(Enum):
    NORMAL = 0
    HOVER = 1
    PRESSED = 2

class TitleBarButton(QToolButton):
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.parent=parent
        self._state = TitleBarButtonState.NORMAL
        self._style = "border: none; margin: 0px;"
        self.colors = ["transparent", "", ""]

        self.set_state(TitleBarButtonState.NORMAL)
        
        self.setFixedSize(46, 32)

    def get_state(self):
        return self._state

    def set_state(self, state):
        self._state = state
        self.setStyleSheet(
            f"background-color: {self.colors[state.value]};\n{self._style}")

    def enterEvent(self, e):
        self.set_state(TitleBarButtonState.HOVER)
        super().enterEvent(e)

    def leaveEvent(self, e):
        self.set_state(TitleBarButtonState.NORMAL)
        super().leaveEvent(e)

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self.set_state(TitleBarButtonState.PRESSED)
        super().mousePressEvent(e)

    def mouseReleaseEvent(self, e):
        self.set_state(TitleBarButtonState.HOVER)
        super().mouseReleaseEvent(e)

class MinimizeButton(TitleBarButton):
    def __init__(self, parent):
        super().__init__(parent)

class MaximizeButton(TitleBarButton):
    def __init__(self, parent):
        super().__init__(parent)

class CloseButton(TitleBarButton):
    def __init__(self, parent):
        super().__init__(parent)
        self.colors = "transparent", "#C42B1C", "#C83C30"
        self.set_state(TitleBarButtonState.NORMAL)
        

