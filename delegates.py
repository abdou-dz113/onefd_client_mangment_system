"""
delegates.py
────────────
Three plug-and-play QStyledItemDelegate subclasses for the CMS table:

  PillBadgeDelegate   – renders any cell as a soft rounded-pill badge.
                        Pass a color_map {value → (bg_hex, text_hex)} to
                        color-code levels, exam statuses, etc.

  DeleteButtonDelegate – draws a trash-icon button in a column; emits
                         delete_requested(row: int) when clicked.

  ExamStatusDelegate  – convenience subclass of PillBadgeDelegate wired
                         to the four exam progress states.

Usage (in main.py / TabelWidget.init_table_settings):
──────────────────────────────────────────────────────
    from delegates import PillBadgeDelegate, DeleteButtonDelegate, ExamStatusDelegate

    # Level badge (column 3)
    self.level_delegate = PillBadgeDelegate(LEVEL_COLORS)
    self.setItemDelegateForColumn(3, self.level_delegate)

    # Exam status badges (columns 9–13)
    self.exam_delegate = ExamStatusDelegate()
    for col in range(9, 14):
        self.setItemDelegateForColumn(col, self.exam_delegate)

    # Delete button (last column — add one extra column for it)
    self.delete_delegate = DeleteButtonDelegate()
    self.delete_delegate.delete_requested.connect(self.on_delete_requested)
    self.setItemDelegateForColumn(DELETE_COL, self.delete_delegate)
"""

from PyQt6.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem, QApplication
from PyQt6.QtCore    import Qt, QRect, QSize, QPoint, pyqtSignal, QObject
from PyQt6.QtGui     import (
    QPainter, QColor, QPen, QBrush, QFont,
    QFontMetrics, QPainterPath, QCursor,
)


# ──────────────────────────────────────────────────────────────────────────────
# Color maps  (feel free to customise)
# ──────────────────────────────────────────────────────────────────────────────

# Level badge colors  {level_index_as_str → (bg, text)}
# Matching the soft-pastel pill style in your screenshot
LEVEL_COLORS: dict[str, tuple[str, str]] = {
    "أولى متوسط":   ("#E8F0FF", "#3D5BA9"),   # soft blue
    "ثانية متوسط":  ("#F0EAFF", "#6B3FA0"),   # soft purple
    "ثالثة متوسط":  ("#EAF6FF", "#2176AE"),   # sky blue
    "رابعة متوسط":  ("#E6FBF4", "#1A7F5E"),   # mint green
    "أولى ثانوي":   ("#FFFBE6", "#8A6D00"),   # soft gold
    "ثانية ثانوي":  ("#FFF0E6", "#C26000"),   # soft orange
    "ثالثة ثانوي":  ("#FFE8E8", "#B83232"),   # soft red
    # Numeric fallback keys (raw level int stored as string)
    "0": ("#E8F0FF", "#3D5BA9"),
    "1": ("#F0EAFF", "#6B3FA0"),
    "2": ("#EAF6FF", "#2176AE"),
    "3": ("#E6FBF4", "#1A7F5E"),
    "4": ("#FFFBE6", "#8A6D00"),
    "5": ("#FFF0E6", "#C26000"),
    "6": ("#FFE8E8", "#B83232"),
}

# Exam / devoir status colors  {int_value_as_str → (bg, text, label)}
EXAM_COLORS: dict[str, tuple[str, str, str]] = {
    "0": ("#FFE8E8", "#B83232", "غير منجز"),
    "1": ("#FFF3E0", "#C26000", "منجز غير مدفوع"),
    "2": ("#E6F3FF", "#1A5FA8", "مدفوع غير منجز"),
    "3": ("#E6FAF0", "#1A7F5E", "منجز مدفوع"),
}


# ──────────────────────────────────────────────────────────────────────────────
# PillBadgeDelegate
# ──────────────────────────────────────────────────────────────────────────────

class PillBadgeDelegate(QStyledItemDelegate):
    """
    Renders a cell value as a centred, soft pill badge.

    color_map: dict mapping the cell's text/int value (as str) to
               (bg_hex, text_hex).  Unmapped values fall back to a
               neutral gray pill.
    """

    FALLBACK = ("#F0F0F0", "#666666")
    H_PAD    = 14   # horizontal padding inside pill
    V_PAD    = 5    # vertical padding inside pill
    RADIUS   = 20   # corner radius (high → fully round ends)

    def __init__(self, color_map: dict, parent=None):
        super().__init__(parent)
        self.color_map = color_map

    # ── paint ─────────────────────────────────────────────────────────────────
    def paint(self, painter: QPainter,
              option: QStyleOptionViewItem, index):

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        raw   = index.data(Qt.ItemDataRole.DisplayRole) or ""
        key   = str(raw).strip()
        bg, fg = self.color_map.get(key, self.FALLBACK)

        # ── pill geometry ──────────────────────────────────────────────────
        font = self._pill_font(option)
        fm   = QFontMetrics(font)
        text_w = fm.horizontalAdvance(key)
        text_h = fm.height()

        pill_w = text_w + self.H_PAD * 2
        pill_h = text_h + self.V_PAD * 2
        pill_h = max(pill_h, 26)

        # centre the pill inside the cell rect
        cell = option.rect
        x = cell.x() + (cell.width()  - pill_w) // 2
        y = cell.y() + (cell.height() - pill_h) // 2
        pill_rect = QRect(x, y, pill_w, pill_h)

        # ── draw background ────────────────────────────────────────────────
        path = QPainterPath()
        path.addRoundedRect(
            float(pill_rect.x()), float(pill_rect.y()),
            float(pill_rect.width()), float(pill_rect.height()),
            float(self.RADIUS), float(self.RADIUS)
        )
        painter.fillPath(path, QColor(bg))

        # ── draw text ──────────────────────────────────────────────────────
        painter.setFont(font)
        painter.setPen(QPen(QColor(fg)))
        painter.drawText(
            pill_rect,
            Qt.AlignmentFlag.AlignCenter,
            key
        )

        painter.restore()

    # ── size hint ──────────────────────────────────────────────────────────────
    def sizeHint(self, option, index):
        return QSize(option.rect.width(), 44)

    # ── helpers ────────────────────────────────────────────────────────────────
    @staticmethod
    def _pill_font(option: QStyleOptionViewItem) -> QFont:
        f = QFont(option.font)
        f.setPointSize(10)
        f.setWeight(QFont.Weight.Medium)
        return f


# ──────────────────────────────────────────────────────────────────────────────
# ExamStatusDelegate   (convenience subclass)
# ──────────────────────────────────────────────────────────────────────────────

class ExamStatusDelegate(PillBadgeDelegate):
    """
    Like PillBadgeDelegate but reads the numeric status (0-3) and
    shows the Arabic label instead of the raw number.
    """

    def __init__(self, parent=None):
        super().__init__(color_map={}, parent=parent)

    def paint(self, painter, option, index):
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        raw = str(index.data(Qt.ItemDataRole.DisplayRole) or "").strip()
        info = EXAM_COLORS.get(raw)
        if info:
            bg, fg, label = info
        else:
            bg, fg, label = "#F0F0F0", "#666666", raw

        font = self._pill_font(option)
        fm   = QFontMetrics(font)
        text_w = fm.horizontalAdvance(label)
        text_h = fm.height()

        pill_w = text_w + self.H_PAD * 2
        pill_h = max(text_h + self.V_PAD * 2, 26)

        cell = option.rect
        x = cell.x() + (cell.width()  - pill_w) // 2
        y = cell.y() + (cell.height() - pill_h) // 2
        pill_rect = QRect(x, y, pill_w, pill_h)

        path = QPainterPath()
        path.addRoundedRect(
            float(pill_rect.x()), float(pill_rect.y()),
            float(pill_rect.width()), float(pill_rect.height()),
            float(self.RADIUS), float(self.RADIUS)
        )
        painter.fillPath(path, QColor(bg))

        painter.setFont(font)
        painter.setPen(QPen(QColor(fg)))
        painter.drawText(pill_rect, Qt.AlignmentFlag.AlignCenter, label)

        painter.restore()


# ──────────────────────────────────────────────────────────────────────────────
# DeleteButtonDelegate
# ──────────────────────────────────────────────────────────────────────────────

class _DeleteSignalHost(QObject):
    """Thin QObject used only to host the pyqtSignal."""
    delete_requested = pyqtSignal(int)   # emits row index


class DeleteButtonDelegate(QStyledItemDelegate):
    """
    Draws a small rounded 'delete' button (trash icon + 'حذف' label) in
    whatever column it is installed on.

    Connect to:
        delegate.delete_requested.connect(your_slot)   # slot receives int row
    """

    BTN_W  = 72
    BTN_H  = 30
    RADIUS = 8

    # soft red pill style
    BG_NORMAL  = "#FFE8E8"
    BG_HOVER   = "#FFD0D0"
    FG_NORMAL  = "#B83232"
    FG_HOVER   = "#8B1A1A"

    def __init__(self, parent=None):
        super().__init__(parent)
        self._signals = _DeleteSignalHost()
        self.delete_requested = self._signals.delete_requested
        self._hovered_row: int = -1

    # ── public interface ───────────────────────────────────────────────────────
    def set_hovered_row(self, row: int):
        self._hovered_row = row

    # ── paint ──────────────────────────────────────────────────────────────────
    def paint(self, painter, option, index):
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        row     = index.row()
        hovered = (row == self._hovered_row)

        bg = self.BG_HOVER  if hovered else self.BG_NORMAL
        fg = self.FG_HOVER  if hovered else self.FG_NORMAL

        cell = option.rect
        bx   = cell.x() + (cell.width()  - self.BTN_W) // 2
        by   = cell.y() + (cell.height() - self.BTN_H) // 2
        btn  = QRect(bx, by, self.BTN_W, self.BTN_H)

        # background pill
        path = QPainterPath()
        path.addRoundedRect(
            float(btn.x()), float(btn.y()),
            float(btn.width()), float(btn.height()),
            float(self.RADIUS), float(self.RADIUS)
        )
        painter.fillPath(path, QColor(bg))

        # trash icon (drawn with simple lines — no image file needed)
        painter.setPen(QPen(QColor(fg), 1.6,
                            Qt.PenStyle.SolidLine,
                            Qt.PenCapStyle.RoundCap,
                            Qt.PenJoinStyle.RoundJoin))
        self._draw_trash(painter, btn)

        # label
        font = QFont(option.font)
        font.setPointSize(9)
        font.setWeight(QFont.Weight.Medium)
        painter.setFont(font)
        painter.setPen(QPen(QColor(fg)))

        label_rect = QRect(btn.x() + 20, btn.y(), btn.width() - 20, btn.height())
        painter.drawText(label_rect, Qt.AlignmentFlag.AlignCenter, "حذف")

        painter.restore()

    def _draw_trash(self, painter: QPainter, btn: QRect):
        """Draw a minimal trash-can icon on the left side of the button."""
        cx = btn.x() + 12
        cy = btn.y() + btn.height() // 2

        # lid
        painter.drawLine(cx - 5, cy - 5, cx + 5, cy - 5)
        painter.drawLine(cx - 2, cy - 7, cx + 2, cy - 7)
        # body
        painter.drawRect(cx - 4, cy - 4, 8, 9)
        # inner lines
        painter.drawLine(cx - 1, cy - 2, cx - 1, cy + 3)
        painter.drawLine(cx + 1, cy - 2, cx + 1, cy + 3)

    # ── size hint ──────────────────────────────────────────────────────────────
    def sizeHint(self, option, index):
        return QSize(self.BTN_W + 20, 44)

    # ── mouse events ──────────────────────────────────────────────────────────
    def editorEvent(self, event, model, option, index):
        from PyQt6.QtCore import QEvent
        if event.type() == QEvent.Type.MouseButtonRelease:
            if self._btn_rect(option).contains(event.pos()):
                self.delete_requested.emit(index.row())
                return True
        return False

    def _btn_rect(self, option) -> QRect:
        cell = option.rect
        bx   = cell.x() + (cell.width()  - self.BTN_W) // 2
        by   = cell.y() + (cell.height() - self.BTN_H) // 2
        return QRect(bx, by, self.BTN_W, self.BTN_H)
