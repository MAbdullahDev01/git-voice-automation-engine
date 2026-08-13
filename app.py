from __future__ import annotations

from datetime import datetime
import math
import sys

from utils.logger import get_logger
from PyQt6.QtCore import QEasingCurve, QPoint, QPointF, QPropertyAnimation, QRect, Qt, QThread, QTimer, pyqtProperty, pyqtSignal # type: ignore
from PyQt6.QtGui import QColor, QFont, QPainter, QPen, QBrush, QRadialGradient
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

logger = get_logger(__name__)

try:
    import speech_recognition as sr
except Exception:  # pragma: no cover - optional runtime dependency
    sr = None

try:
    import keyboard
except Exception:  # pragma: no cover - optional runtime dependency
    keyboard = None

BG_DARK = "#05070d"
BG_PANEL = "#0b1220"
BG_PANEL_ALT = "#111a2c"
BORDER = "#1e293b"
TEXT_PRIMARY = "#e2e8f0"
TEXT_MUTED = "#64748b"

ACCENT_CYAN = "#38bdf8"
ACCENT_TEAL = "#22d3ee"
ACCENT_AMBER = "#f59e0b"
ACCENT_GREEN = "#34d399"
ACCENT_RED = "#ef4444"

FONT_FAMILY = "Consolas, 'Courier New', monospace"
FONT_FAMILY_UI = "Segoe UI, Arial, sans-serif"

STATE_COLORS = {
    "idle": ACCENT_CYAN,
    "listening": ACCENT_TEAL,
    "processing": ACCENT_AMBER,
    "speaking": ACCENT_GREEN,
    "error": ACCENT_RED,
}

STATE_LABELS = {
    "idle": "STANDING BY",
    "listening": "LISTENING",
    "processing": "PROCESSING",
    "speaking": "RESPONDING",
    "error": "ERROR",
}

GLOBAL_QSS = f"""
QWidget {{
    background-color: transparent;
    color: {TEXT_PRIMARY};
    font-family: {FONT_FAMILY_UI};
}}

#RootFrame {{
    background-color: {BG_DARK};
    border: 1px solid {BORDER};
    border-radius: 14px;
}}

#TitleBar {{
    background-color: {BG_PANEL};
    border-top-left-radius: 14px;
    border-top-right-radius: 14px;
    border-bottom: 1px solid {BORDER};
}}

#TitleBarLabel {{
    color: {ACCENT_CYAN};
    font-family: {FONT_FAMILY};
    font-size: 13px;
    font-weight: bold;
    letter-spacing: 2px;
}}

#TitleBarBtn {{
    background-color: transparent;
    color: {TEXT_MUTED};
    border: none;
    font-size: 14px;
    font-weight: bold;
    border-radius: 6px;
}}
#TitleBarBtn:hover {{
    background-color: {BG_PANEL_ALT};
    color: {TEXT_PRIMARY};
}}
#CloseBtn:hover {{
    background-color: {ACCENT_RED};
    color: white;
}}

#SidePanel {{
    background-color: {BG_PANEL};
    border-right: 1px solid {BORDER};
}}

#StatusLabel {{
    font-family: {FONT_FAMILY};
    font-size: 13px;
    font-weight: bold;
    letter-spacing: 3px;
    qproperty-alignment: AlignCenter;
}}

#SubStatusLabel {{
    font-family: {FONT_FAMILY};
    font-size: 10px;
    color: {TEXT_MUTED};
    letter-spacing: 1px;
    qproperty-alignment: AlignCenter;
}}

#LogOutput {{
    background-color: {BG_PANEL_ALT};
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 12px;
    font-family: {FONT_FAMILY};
    font-size: 13px;
    selection-background-color: {ACCENT_CYAN};
}}

#InputField {{
    background-color: {BG_PANEL_ALT};
    border: 1px solid {BORDER};
    border-radius: 20px;
    padding: 10px 16px;
    font-size: 13px;
    color: {TEXT_PRIMARY};
}}
#InputField:focus {{
    border: 1px solid {ACCENT_CYAN};
}}

#SendBtn {{
    background-color: {ACCENT_CYAN};
    color: {BG_DARK};
    border: none;
    border-radius: 20px;
    font-weight: bold;
    font-size: 13px;
}}
#SendBtn:hover {{
    background-color: #7dd3fc;
}}
#SendBtn:pressed {{
    background-color: #0284c7;
}}

QScrollBar:vertical {{
    background: transparent;
    width: 8px;
    margin: 0px;
}}
QScrollBar::handle:vertical {{
    background: {BORDER};
    border-radius: 4px;
    min-height: 24px;
}}
QScrollBar::handle:vertical:hover {{
    background: {ACCENT_CYAN};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}
"""


class JarvisHUD(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(200, 200)
        self._rotation = 0.0
        self._pulse = 0.0
        self._state = "idle"

        self._rotation_timer = QTimer(self)
        self._rotation_timer.timeout.connect(self._advance_rotation)
        self._rotation_timer.start(16)

        self._pulse_anim = QPropertyAnimation(self, b"pulse")
        self._pulse_anim.setDuration(1400)
        self._pulse_anim.setStartValue(0.0)
        self._pulse_anim.setEndValue(1.0)
        self._pulse_anim.setEasingCurve(QEasingCurve.Type.InOutSine)
        self._pulse_anim.setLoopCount(-1)
        self._pulse_anim.start()

    def _get_pulse(self):
        return self._pulse

    def _set_pulse(self, value):
        self._pulse = value
        self.update()

    pulse = pyqtProperty(float, _get_pulse, _set_pulse)

    def set_state(self, state: str):
        if state not in STATE_COLORS:
            state = "idle"
        self._state = state
        self._rotation_timer.setInterval(6 if state == "processing" else 16)

    def _advance_rotation(self):
        speed = 2.2 if self._state == "processing" else 0.6
        self._rotation = (self._rotation + speed) % 360
        self.update()

    def paintEvent(self, _event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        cx, cy = w / 2, h / 2
        base_radius = min(w, h) / 2 - 22

        color = QColor(STATE_COLORS[self._state])

        glow_r = base_radius * (1.3 + self._pulse * 0.15)
        gradient = QRadialGradient(QPointF(cx, cy), glow_r)
        glow_color = QColor(color)
        glow_color.setAlpha(90)
        transparent = QColor(color)
        transparent.setAlpha(0)
        gradient.setColorAt(0.0, glow_color)
        gradient.setColorAt(1.0, transparent)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(gradient))
        painter.drawEllipse(QPointF(cx, cy), glow_r, glow_r)

        ref_pen = QPen(QColor(255, 255, 255, 18))
        ref_pen.setWidth(1)
        painter.setPen(ref_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPointF(cx, cy), base_radius + 10, base_radius + 10)

        outer_pen = QPen(color)
        outer_pen.setWidthF(3.0)
        outer_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(outer_pen)
        rect_outer = (cx - base_radius, cy - base_radius, base_radius * 2, base_radius * 2)
        painter.drawArc(*(int(v) for v in rect_outer), int(self._rotation * 16), int(110 * 16)) # type: ignore
        painter.drawArc(*(int(v) for v in rect_outer), int((self._rotation + 180) * 16), int(110 * 16)) # type: ignore

        inner_radius = base_radius - 18
        inner_color = color.lighter(140)
        inner_pen = QPen(inner_color)
        inner_pen.setWidthF(2.0)
        inner_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(inner_pen)
        rect_inner = (cx - inner_radius, cy - inner_radius, inner_radius * 2, inner_radius * 2)
        painter.drawArc(*(int(v) for v in rect_inner), int(-self._rotation * 22), int(70 * 16)) # type: ignore
        painter.drawArc(*(int(v) for v in rect_inner), int(-(self._rotation + 180) * 22), int(70 * 16)) # type: ignore

        tick_pen = QPen(QColor(255, 255, 255, 40))
        tick_pen.setWidth(1)
        painter.setPen(tick_pen)
        for i in range(24):
            angle = math.radians(i * 15)
            r1 = base_radius + 12
            r2 = base_radius + 17
            x1, y1 = cx + r1 * math.cos(angle), cy + r1 * math.sin(angle)
            x2, y2 = cx + r2 * math.cos(angle), cy + r2 * math.sin(angle)
            painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

        core_r = 26 + self._pulse * 6
        core_gradient = QRadialGradient(QPointF(cx, cy), core_r)
        bright = QColor(color).lighter(160)
        core_gradient.setColorAt(0.0, bright)
        core_gradient.setColorAt(0.6, color)
        core_gradient.setColorAt(1.0, QColor(color.red(), color.green(), color.blue(), 60))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(core_gradient))
        painter.drawEllipse(QPointF(cx, cy), core_r, core_r)

        painter.end()


class SpeechCaptureWorker(QThread):
    result_ready = pyqtSignal(str)
    error_ready = pyqtSignal(str)
    stopped = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._stop_requested = False

    def request_stop(self):
        self._stop_requested = True

    def run(self):
        if sr is None:
            self.error_ready.emit("Speech recognition dependency is unavailable.")
            self.stopped.emit()
            return

        try:
            recognizer = sr.Recognizer()
            mic = sr.Microphone()
            audio_chunks = []

            with mic as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.1)
                stream = mic.stream
                while not self._stop_requested:
                    try:
                        chunk = stream.read(source.CHUNK)
                        audio_chunks.append(chunk)
                    except IOError:
                        continue

            if not audio_chunks:
                self.result_ready.emit("")
                self.stopped.emit()
                return

            raw_audio = b"".join(audio_chunks)
            audio_data = sr.AudioData(raw_audio, source.SAMPLE_RATE, source.SAMPLE_WIDTH)
            try:
                text = recognizer.recognize_google(audio_data).strip()
            except sr.UnknownValueError:
                text = ""
            except sr.RequestError as exc:
                logger.error("Speech recognition service is unavailable: %s", exc)
                text = ""

            self.result_ready.emit(text)
        except Exception as exc:
            logger.error("Microphone capture failed: %s", exc)
            self.error_ready.emit(str(exc))
        finally:
            self.stopped.emit()


class PipelineWorker(QThread):
    finished = pyqtSignal(str)
    failed = pyqtSignal(str)
    shutdown_requested = pyqtSignal()
    chunk_received = pyqtSignal(str)

    def __init__(self, user_input: str):
        super().__init__()
        self.user_input = user_input

    def run(self):
        try:
            from main import EXIT_SIGNAL, process_pipeline

            result = process_pipeline(
                self.user_input,
                interactive=False,
                on_chunk=self.chunk_received.emit,
            )
            if result is EXIT_SIGNAL:
                self.shutdown_requested.emit()
                return
            if not isinstance(result, str) or not result.strip():
                result = f"Acknowledged. You said: \u201c{self.user_input}\u201d"
            self.finished.emit(result)
        except Exception as exc:
            logger.error("Pipeline processing failed: %s", exc)
            self.failed.emit(str(exc))


class JarvisMainWindow(QMainWindow):
    WINDOW_W, WINDOW_H = 920, 640
    RESIZE_MARGIN = 10

    def __init__(self):
        super().__init__()
        self._drag_pos = None
        self._worker = None
        self._speech_worker = None
        self._streaming_started = False
        self._typing_timer = QTimer(self)
        self._typing_timer.timeout.connect(self._type_next_chunk)
        self._typing_buffer = ""
        self._typing_index = 0
        self._resize_zone = None
        self._resize_start_geo = None
        self._is_resizing = False
        self._hotkey_enabled = False

        self._init_window()
        self._build_ui()
        self._set_state("idle")
        self._install_global_hotkey()

    def _init_window(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(self.WINDOW_W, self.WINDOW_H)
        self.setMinimumSize(620, 420)
        self.setStyleSheet(GLOBAL_QSS)

    def _build_ui(self):
        root = QFrame()
        root.setObjectName("RootFrame")
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        root_layout.addWidget(self._build_title_bar())

        body = QWidget()
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)
        body_layout.addWidget(self._build_side_panel(), 0)
        body_layout.addWidget(self._build_chat_panel(), 1)
        root_layout.addWidget(body)

        self.setCentralWidget(root)
        self._root_frame = root
        self._root_frame.setMouseTracking(True)
        self._root_frame.mousePressEvent = self._root_mouse_press  # type: ignore
        self._root_frame.mouseMoveEvent = self._root_mouse_move  # type: ignore
        self._root_frame.mouseReleaseEvent = self._root_mouse_release  # type: ignore
        self._root_frame.leaveEvent = self._root_leave_event  # type: ignore

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(40)
        shadow.setOffset(0, 0)
        shadow.setColor(QColor(0, 0, 0, 160))
        root.setGraphicsEffect(shadow)

    def _build_title_bar(self):
        bar = QFrame()
        bar.setObjectName("TitleBar")
        bar.setFixedHeight(44)
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(18, 0, 10, 0)

        title = QLabel("J . A . R . V . I . S")
        title.setObjectName("TitleBarLabel")
        layout.addWidget(title)
        layout.addStretch()

        min_btn = QPushButton("\u2013")
        min_btn.setObjectName("TitleBarBtn")
        min_btn.setFixedSize(30, 30)
        min_btn.clicked.connect(self.showMinimized)

        close_btn = QPushButton("\u2715")
        close_btn.setObjectName("TitleBarBtn")
        close_btn.setProperty("class", "close")
        close_btn.setFixedSize(30, 30)
        close_btn.clicked.connect(self.close)
        close_btn.setObjectName("CloseBtn")

        layout.addWidget(min_btn)
        layout.addWidget(close_btn)

        bar.mousePressEvent = self._title_mouse_press # type: ignore
        bar.mouseMoveEvent = self._title_mouse_move # type: ignore
        return bar

    def _title_mouse_press(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def _title_mouse_move(self, event):
        if self._drag_pos is not None and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def _resize_zone_for_pos(self, pos: QPoint):
        rect = self._root_frame.rect()
        if rect.isEmpty():
            return None

        margin = self.RESIZE_MARGIN
        x, y = pos.x(), pos.y()
        w, h = rect.width(), rect.height()

        if x <= margin and y <= margin:
            return "top-left"
        if x >= w - margin and y <= margin:
            return "top-right"
        if x <= margin and y >= h - margin:
            return "bottom-left"
        if x >= w - margin and y >= h - margin:
            return "bottom-right"
        if x <= margin:
            return "left"
        if x >= w - margin:
            return "right"
        if y <= margin:
            return "top"
        if y >= h - margin:
            return "bottom"
        return None

    def _cursor_for_resize_zone(self, zone):
        cursor_map = {
            "top": Qt.CursorShape.SizeVerCursor,
            "bottom": Qt.CursorShape.SizeVerCursor,
            "left": Qt.CursorShape.SizeHorCursor,
            "right": Qt.CursorShape.SizeHorCursor,
            "top-left": Qt.CursorShape.SizeFDiagCursor,
            "top-right": Qt.CursorShape.SizeBDiagCursor,
            "bottom-left": Qt.CursorShape.SizeBDiagCursor,
            "bottom-right": Qt.CursorShape.SizeFDiagCursor,
        }
        return cursor_map.get(zone, Qt.CursorShape.ArrowCursor)

    def _constrained_resize_geometry(self, width: int, height: int, zone: str):
        base = self.frameGeometry()
        min_w = max(self.minimumWidth(), 1)
        min_h = max(self.minimumHeight(), 1)
        width = max(width, min_w)
        height = max(height, min_h)

        if zone == "top-left":
            return QRect(base.right() - width, base.bottom() - height, width, height)
        if zone == "top-right":
            return QRect(base.left(), base.bottom() - height, width, height)
        if zone == "bottom-left":
            return QRect(base.right() - width, base.top(), width, height)
        if zone == "bottom-right":
            return QRect(base.left(), base.top(), width, height)
        if zone == "left":
            return QRect(base.right() - width, base.top(), width, base.height())
        if zone == "right":
            return QRect(base.left(), base.top(), width, base.height())
        if zone == "top":
            return QRect(base.left(), base.bottom() - height, base.width(), height)
        if zone == "bottom":
            return QRect(base.left(), base.top(), base.width(), height)
        return QRect(base)

    def _root_mouse_press(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            return

        zone = self._resize_zone_for_pos(event.position().toPoint())
        if zone is None:
            return

        self._is_resizing = True
        self._resize_zone = zone
        self._resize_start_geo = self.frameGeometry()
        self.setCursor(self._cursor_for_resize_zone(zone))
        event.accept()

    def _root_mouse_move(self, event):
        pos = event.position().toPoint()
        if self._is_resizing and self._resize_zone and self._resize_start_geo is not None:
            self._apply_resize(event.globalPosition().toPoint())
            event.accept()
            return

        zone = self._resize_zone_for_pos(pos)
        if zone is not None:
            self.setCursor(self._cursor_for_resize_zone(zone))
        else:
            self.unsetCursor()
        event.accept()

    def _root_mouse_release(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_resizing = False
            self._resize_zone = None
            self._resize_start_geo = None
            self.unsetCursor()
            event.accept()

    def _root_leave_event(self, event):
        self.unsetCursor()
        super().leaveEvent(event)

    def _apply_resize(self, global_pos: QPoint):
        if not self._resize_zone or self._resize_start_geo is None:
            return

        zone = self._resize_zone
        start = self._resize_start_geo
        min_w = max(self.minimumWidth(), 1)
        min_h = max(self.minimumHeight(), 1)
        current = QRect(start)

        if zone in {"left", "top-left", "bottom-left"}:
            new_left = min(global_pos.x(), start.right() - min_w)
            if new_left < start.right() - min_w:
                current.setLeft(new_left)
            else:
                current.setLeft(start.right() - min_w)
        if zone in {"right", "top-right", "bottom-right"}:
            new_right = max(global_pos.x(), start.left() + min_w)
            current.setRight(new_right)
        if zone in {"top", "top-left", "top-right"}:
            new_top = min(global_pos.y(), start.bottom() - min_h)
            current.setTop(new_top)
        if zone in {"bottom", "bottom-left", "bottom-right"}:
            new_bottom = max(global_pos.y(), start.top() + min_h)
            current.setBottom(new_bottom)

        if current.width() < min_w:
            current.setWidth(min_w)
        if current.height() < min_h:
            current.setHeight(min_h)

        self.setGeometry(current)

    def _build_side_panel(self):
        panel = QFrame()
        panel.setObjectName("SidePanel")
        panel.setFixedWidth(300)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 30, 20, 30)
        layout.setSpacing(18)

        layout.addStretch(1)

        self.hud = JarvisHUD()
        layout.addWidget(self.hud, 0, Qt.AlignmentFlag.AlignHCenter)

        self.status_label = QLabel(STATE_LABELS["idle"])
        self.status_label.setObjectName("StatusLabel")
        layout.addWidget(self.status_label)

        self.sub_status_label = QLabel("core temperature nominal")
        self.sub_status_label.setObjectName("SubStatusLabel")
        layout.addWidget(self.sub_status_label)

        layout.addStretch(2)

        hint = QLabel("Press Enter to transmit a command")
        hint.setObjectName("SubStatusLabel")
        hint.setWordWrap(True)
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(hint)

        return panel

    def _build_chat_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 24, 24, 20)
        layout.setSpacing(14)

        self.log_output = QTextEdit()
        self.log_output.setObjectName("LogOutput")
        self.log_output.setReadOnly(True)
        self.log_output.setFont(QFont("Consolas", 10))
        layout.addWidget(self.log_output, 1)

        # --- Interactive Action Row (for Yes/No choices) ---
        self.confirm_row = QWidget()
        confirm_layout = QHBoxLayout(self.confirm_row)
        confirm_layout.setContentsMargins(0, 0, 0, 0)
        confirm_layout.setSpacing(10)

        self.btn_yes = QPushButton("CONFIRM [Y]")
        self.btn_yes.setStyleSheet(
            f"background-color: {ACCENT_GREEN}; color: {BG_DARK}; font-weight: bold; border-radius: 12px; padding: 8px;"
        )
        self.btn_yes.clicked.connect(lambda: self._handle_confirmation("y"))

        self.btn_no = QPushButton("CANCEL [N]")
        self.btn_no.setStyleSheet(
            f"background-color: {ACCENT_RED}; color: white; font-weight: bold; border-radius: 12px; padding: 8px;"
        )
        self.btn_no.clicked.connect(lambda: self._handle_confirmation("n"))

        confirm_layout.addWidget(self.btn_yes)
        confirm_layout.addWidget(self.btn_no)
        self.confirm_row.setVisible(False)
        layout.addWidget(self.confirm_row)

        input_row = QHBoxLayout()
        input_row.setSpacing(10)

        self.input_field = QLineEdit()
        self.input_field.setObjectName("InputField")
        self.input_field.setPlaceholderText("Type a command or ask me anything...")
        self.input_field.returnPressed.connect(self._send_command)
        input_row.addWidget(self.input_field, 1)

        self.send_btn = QPushButton("SEND")
        self.send_btn.setObjectName("SendBtn")
        self.send_btn.setFixedSize(90, 40)
        self.send_btn.clicked.connect(self._send_command)
        input_row.addWidget(self.send_btn)

        layout.addLayout(input_row)

        self._append_system_line("JARVIS online. All systems nominal.")
        return panel

    def prompt_user_confirmation(self, message: str):
        self._append_system_line(message)
        self.confirm_row.setVisible(True)
        self.input_field.setEnabled(False)
        self.send_btn.setEnabled(False)

    def _handle_confirmation(self, choice: str):
        self.confirm_row.setVisible(False)
        self.input_field.setEnabled(True)
        self.send_btn.setEnabled(True)
        self.input_field.setText(choice)
        self._send_command()

    def _set_state(self, state: str, sub_text: str | None = None):
        color = STATE_COLORS.get(state, ACCENT_CYAN)
        self.hud.set_state(state)
        self.status_label.setText(STATE_LABELS.get(state, state.upper()))
        self.status_label.setStyleSheet(f"color: {color};")
        if sub_text:
            self.sub_status_label.setText(sub_text)

    def _timestamp(self):
        return datetime.now().strftime("%H:%M:%S")

    def _append_system_line(self, text: str):
        self.log_output.append(f'<span style="color:{TEXT_MUTED};">[{self._timestamp()}] {text}</span>')

    def _append_user_line(self, text: str):
        self.log_output.append(
            f'<span style="color:{ACCENT_CYAN};"><b>YOU</b></span> '
            f'<span style="color:{TEXT_MUTED};">[{self._timestamp()}]</span><br>'
            f'<span>{text}</span>'
        )

    def _begin_jarvis_line(self):
        self.log_output.append(
            f'<span style="color:{STATE_COLORS["speaking"]};"><b>JARVIS</b></span> '
            f'<span style="color:{TEXT_MUTED};">[{self._timestamp()}]</span>'
        )
        self.log_output.append("")

    def _submit_command_text(self, text: str):
        text = text.strip()
        if not text or (self._worker and self._worker.isRunning()):
            return

        self._append_user_line(text)
        self.input_field.clear()
        self._set_state("processing", "analyzing request...")

        self._streaming_started = False

        self._worker = PipelineWorker(text)
        self._worker.chunk_received.connect(self._on_chunk_received)
        self._worker.shutdown_requested.connect(self._on_shutdown_requested)
        self._worker.finished.connect(self._on_pipeline_finished)
        self._worker.failed.connect(self._on_pipeline_failed)
        self._worker.start()

    def _send_command(self):
        self._submit_command_text(self.input_field.text())

    def _install_global_hotkey(self):
        if self._hotkey_enabled or keyboard is None:
            return

        try:
            keyboard.add_hotkey("ctrl+shift+space", self._hotkey_capture_started, suppress=False)
            keyboard.on_release_key("space", self._hotkey_capture_stopped)
            self._hotkey_enabled = True
        except Exception as exc:
            logger.warning("Global hotkey unavailable: %s", exc)

    def _hotkey_capture_started(self):
        if self._speech_worker is not None and self._speech_worker.isRunning():
            return

        QTimer.singleShot(0, self._begin_capture_from_hotkey)

    def _hotkey_capture_stopped(self, event):
        if getattr(event, "name", None) != "space":
            return
        if keyboard is not None and keyboard.is_pressed("ctrl") and keyboard.is_pressed("shift"):
            QTimer.singleShot(0, self._stop_capture_from_hotkey)

    def _begin_capture_from_hotkey(self):
        self._speech_worker = SpeechCaptureWorker()
        self._speech_worker.result_ready.connect(self._on_hotkey_transcription)
        self._speech_worker.error_ready.connect(self._on_hotkey_capture_error)
        self._speech_worker.stopped.connect(self._on_hotkey_capture_stopped)
        self._set_state("listening", "microphone live...")
        self._speech_worker.start()

    def _stop_capture_from_hotkey(self):
        if self._speech_worker is None or not self._speech_worker.isRunning():
            return
        self._speech_worker.request_stop()
        self._set_state("processing", "transcribing audio...")

    def _on_hotkey_transcription(self, text: str):
        if not text.strip():
            self._set_state("idle", "core temperature nominal")
            return
        self._submit_command_text(text)

    def _on_hotkey_capture_error(self, error: str):
        self._set_state("error", "microphone unavailable")
        self._append_system_line(f"Speech capture error: {error}")
        QTimer.singleShot(2000, lambda: self._set_state("idle", "core temperature nominal"))

    def _on_hotkey_capture_stopped(self):
        if self._speech_worker is not None and self._speech_worker.isRunning():
            return
        self._speech_worker = None

    def _on_chunk_received(self, chunk: str):
        if not self._streaming_started:
            self._begin_jarvis_line()
            self._set_state("speaking", "response streaming...")
            self._streaming_started = True

        cursor = self.log_output.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.insertText(chunk)
        self.log_output.setTextCursor(cursor)
        self.log_output.ensureCursorVisible()

    def _on_pipeline_finished(self, result: str):
        if self._streaming_started:
            # Text already rendered live via _on_chunk_received; just wind down state.
            QTimer.singleShot(400, lambda: self._set_state("idle", "core temperature nominal"))
        else:
            # Non-streamed responses (git tools, spotify, etc.) — keep the typewriter effect.
            self._set_state("speaking", "response ready")
            self._begin_jarvis_line()
            self._start_typing_effect(result)

        if "(y/n)" in result.lower():
            QTimer.singleShot(
                len(result) * 16 + 200,
                lambda: self.prompt_user_confirmation("Awaiting confirmation..."),
            )

    def _on_pipeline_failed(self, error: str):
        self._set_state("error", "an error occurred")
        self._append_system_line(f"Error: {error}")
        QTimer.singleShot(2000, lambda: self._set_state("idle", "core temperature nominal"))

    def _on_shutdown_requested(self):
        self._set_state("idle", "shutting down...")
        self._append_system_line("Shutting down. Goodbye, sir!")
        QTimer.singleShot(250, QApplication.instance().quit)

    def _start_typing_effect(self, full_text: str):
        self._typing_buffer = full_text
        self._typing_index = 0
        self._typing_timer.start(16)
        self._streaming_started = False

    def _type_next_chunk(self):
        if self._typing_index >= len(self._typing_buffer):
            self._typing_timer.stop()
            QTimer.singleShot(600, lambda: self._set_state("idle", "core temperature nominal"))
            return

        chunk = self._typing_buffer[self._typing_index]
        cursor = self.log_output.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.insertText(chunk)
        self.log_output.setTextCursor(cursor)
        self._typing_index += 1


def main():
    app = QApplication(sys.argv)
    window = JarvisMainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()