from PyQt4.QtGui import (
    QWidget, QPainter, QPainterPath, QPen, QRadialGradient, QLinearGradient,
    QFont, QFontMetrics, QColor, QPolygonF
)
from PyQt4.QtCore import Qt, QString, QPointF, QPoint, QRectF, SIGNAL
from numpy import linspace


class DMCircularGauge(QWidget):
    _value = 0.0
    percentage = 0.0

    lolo_arc = QPainterPath()
    low_arc = QPainterPath()
    high_arc = QPainterPath()
    hihi_arc = QPainterPath()

    def __init__(self, channel=None, range_low=None, range_high=None, parent=None):
        super(DMCircularGauge, self).__init__(parent)

        self.channel = channel
        self._channel = self.channel.value
        if range_low is None:
            range_low = self.channel.range()[0]
        if range_high is None:
            range_high = self.channel.range()[1]
        self.range = [range_low, range_high]
        self.connect(self.channel, SIGNAL('new_value(float)'), self.update_value)
        self.connect(self.channel, SIGNAL('new_limits(float, float, float, float)'), self.update_limits)

        self.width_ref = 400.0
        self.height_ref = 240.0
        self.resize(self.width_ref, self.height_ref)
        self.ref_aspect_ratio = self.width_ref / self.height_ref

        self.dial_v_offset = self.height() * 0.1
        self.dial_height = self.width() / 2.0
        self.dial_width = self.width()

        self.dial = QPainterPath(QPointF(0.0, self.dial_width))
        self.dial.arcTo(0.0, 1.0, self.dial_width, self.dial_height * 2, 180, -180)
        self.dial.lineTo(self.dial_width, self.height_ref)
        self.dial.lineTo(0.0, self.height_ref)
        self.dial.lineTo(0.0, self.dial_height)

        self.dial_bg = QRadialGradient(QPointF(self.width()/2.0, self.height()-self.dial_v_offset), self.dial_height)
        self.dial_bg.setColorAt(0, Qt.lightGray)
        self.dial_bg.setColorAt(0.98, QColor(50, 50, 50, 255))
        self.dial_bg.setColorAt(1, Qt.black)

        needle_base_width = 24
        self.needle_left = QPolygonF([QPoint(0, 0),
                                      QPoint(0, -needle_base_width/2.0),
                                      QPoint(self.dial_height*0.9, 0.0)])
        self.needle_right = QPolygonF([QPoint(0, 0),
                                      QPoint(0, needle_base_width / 2.0),
                                      QPoint(self.dial_height * 0.9, 0.0)])

        pin_diameter = 28
        self.pin_rect = QRectF(-pin_diameter / 2.0, -pin_diameter / 2.0, pin_diameter, pin_diameter)
        self.pin_bg = QRadialGradient(QPointF(0.0, -pin_diameter / 5.0), pin_diameter * 0.75)
        self.pin_bg.setColorAt(0, Qt.lightGray)
        self.pin_bg.setColorAt(1, Qt.black)

        self.shadow_rect = QRectF(-self.dial_width / 2, -self.dial_height / 2, self.dial_width, self.dial_height * 1.1)
        self.gloss_rect = QRectF(-self.dial_width / 5, -self.dial_height / 2, self.dial_width / 2.5, self.dial_height / 2)
        self.gloss_gradient = QLinearGradient(QPointF(0.0, -self.dial_height / 2), QPointF(0.0, 0.0))
        self.gloss_gradient.setColorAt(0.0, QColor(255, 255, 255, 120))
        self.gloss_gradient.setColorAt(0.95, QColor(255, 255, 255, 0))

        limits = self.channel.limits()
        self.update_limits(limits[0], limits[1], limits[2], limits[3])

    def paintEvent(self, event):
        # Initialize QPainter properties
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)
        if self.height() <= self.width() / self.ref_aspect_ratio:
            v_scale = self.height()
            h_scale = v_scale * self.ref_aspect_ratio
        else:
            h_scale = self.width()
            v_scale = h_scale / self.ref_aspect_ratio
        # Scale all objects proportionate to window size
        painter.scale(h_scale / self.width_ref, v_scale / self.height_ref)
        painter.save()

        # First main draw gauge background
        pen = QPen(painter.pen())
        pen.setWidth(1)
        pen.setColor(Qt.black)
        painter.setPen(pen)
        painter.setBrush(self.dial_bg)
        painter.drawPath(self.dial)

        pen.setWidth(16)
        pen.setCapStyle(Qt.FlatCap)
        pen.setJoinStyle(Qt.BevelJoin)

        pen.setColor(Qt.yellow)
        painter.setPen(pen)
        painter.drawPath(self.low_arc)
        painter.drawPath(self.high_arc)

        pen.setColor(Qt.red)
        painter.setPen(pen)
        painter.drawPath(self.lolo_arc)
        painter.drawPath(self.hihi_arc)

        painter.restore()

        # Display actual value
        painter.save()
        painter.setClipPath(self.dial)  # Don't allow label text to extend outside of main shape
        font = QFont()
        font.setPixelSize(min(max(self.dial_width / 2, 20), 50))
        painter.setFont(font)
        sevr = self.channel.sevr.lower()
        if sevr == 'major':
            color = Qt.red
        elif sevr == 'minor':
            color = Qt.yellow
        elif sevr == 'invalid':
            color = Qt.magenta
        else:
            color = Qt.green
        pen.setColor(color)
        painter.setPen(pen)
        font_metric = QFontMetrics(font)
        painter.translate(self.dial_width / 2, self.dial_height / 2)
        label = QString().setNum(self.channel_value, 'f', 2)
        painter.drawText(QPointF(0.0 - font_metric.width(label) / 2.0, font_metric.height() / 2.0),
                         label)
        font = QFont()
        font.setPixelSize(min(max(self.dial_width / 10, 10), 20))
        painter.setFont(font)
        pen.setColor(Qt.black)
        painter.setPen(pen)
        font_metric = QFontMetrics(font)
        pv_label = self.channel.name + ' (' + self.channel.egu + ')'
        painter.drawText(QPointF(0.0 - font_metric.width(pv_label) / 2.0,
                                 (self.dial_height / 2.0) + (font_metric.height() * 1.5)),
                         pv_label)
        painter.restore()

        # Next add division markers
        painter.save()
        painter.translate(self.dial_width / 2, self.dial_height * 0.98)
        pen.setColor(Qt.cyan)
        pen.setWidth(2)
        painter.setPen(pen)
        for i in range(0, 31):
            if (i % 5) != 0:
                painter.drawLine(-self.dial_width / 2.1, 0.0, -self.dial_width / 2.2, 0.0)
            else:
                painter.drawLine(-self.dial_width / 2.1, 0.0, -self.dial_width / 2.3, 0.0)
            painter.rotate(6.0)
        painter.restore()

        # Layout division text labels
        painter.save()
        painter.setClipPath(self.dial)  # Don't allow label text to extend outside of main shape
        painter.translate(self.dial_width / 2, self.dial_height * 0.98)
        pen.setColor(Qt.cyan)
        painter.setPen(pen)
        font = QFont()
        font.setPixelSize(min(max(self.dial_width / 10, 10), 20))
        painter.setFont(font)
        font_metric = QFontMetrics(font)
        labels = linspace(self.lim_low, self.lim_hi, 7)
        painter.rotate(-90)
        for i in range(0, 7):
            label = QString().setNum(labels[i], 'f', 2)
            painter.drawText(QPointF(0.0 - font_metric.width(label) / 2.0, -self.dial_height * 0.75), label)
            painter.rotate(30)
        painter.restore()

        # Draw needle at appropriate angle for data
        painter.save()
        painter.translate(self.dial_width / 2, self.dial_height * 0.98)
        painter.rotate(-180 * (1.0 - self.percentage))

        if self.percentage <= 0.5:
            shadow = max(490 * self.percentage, 127)
            needle_left_color = QColor(0, shadow, shadow)  # Qt.darkCyan  # QColor(80,80,80,255)
            needle_right_color = Qt.cyan  # QColor(230,230,230,255)
        else:
            shadow = max(125 / self.percentage, 127)
            needle_left_color = Qt.cyan  # QColor(230,230,230,255)
            needle_right_color = QColor(0, shadow, shadow)  # Qt.darkCyan  # QColor(80,80,80,255)

        # Draw Highlight side of needle
        pen.setWidth(1)
        pen.setColor(needle_left_color)
        painter.setPen(pen)
        painter.setBrush(needle_left_color)
        painter.drawPolygon(self.needle_left)

        # Draw shadow side of needle
        pen.setColor(needle_right_color)
        painter.setPen(pen)
        painter.setBrush(needle_right_color)
        painter.drawPolygon(self.needle_right)
        painter.restore()

        # Draw needle axel pin
        painter.save()
        pen.setWidth(1)
        pen.setColor(Qt.black)
        painter.setPen(pen)
        painter.setBrush(self.pin_bg)
        painter.translate(self.dial_width / 2, self.dial_height * 0.98)
        painter.drawEllipse(self.pin_rect)
        painter.restore()

        # Draw glass reflection and shadow effects
        painter.save()
        painter.setClipPath(self.dial)
        painter.translate(self.dial_width / 2.0, self.dial_height / 2.0)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0, 0, 0, 20))
        painter.drawEllipse(self.shadow_rect)
        painter.setBrush(self.gloss_gradient)
        painter.drawEllipse(self.gloss_rect)
        painter.restore()

        painter.end()

    @property
    def lim_hi(self):
        return self.range[1]

    @lim_hi.setter
    def lim_hi(self, lim):
        self.range[1] = lim

    @property
    def lim_low(self):
        return self.range[0]

    @lim_low.setter
    def lim_low(self, lim):
        self.range[0] = lim

    def update_value(self, value=0.0):
        self.channel_value = value
        # print 'Value updated!'
        self.update()

    @property
    def channel_value(self):
        return self._value

    @channel_value.setter
    def channel_value(self, value):
        self._value = value
        self.update_percentage()

    def update_limits(self, lolo, low, high, hihi):
        full_range = self.lim_hi - self.lim_low
        left_x = self.dial_width * 0.025
        right_x = self.dial_width * 0.975

        angle = -180 * (1 - (self.lim_hi - lolo) / full_range)
        self.lolo_arc = self.make_arc(left_x, self.dial_height, 180.0, angle)

        angle = -180 * (1 - (self.lim_hi - low) / full_range)
        self.low_arc = self.make_arc(left_x, self.dial_height, 180.0, angle)

        angle = 180 * (self.lim_hi - high) / full_range
        self.high_arc = self.make_arc(right_x, self.dial_height, 0.0, angle)

        angle = 180 * (self.lim_hi - hihi) / full_range
        self.hihi_arc = self.make_arc(right_x, self.dial_height, 0.0, angle)

    def make_arc(self, start_x, start_y, start_angle, end_angle):
        arc = QPainterPath(QPointF(start_x, start_y))
        arc.arcTo(self.dial_width * 0.025, self.dial_width * 0.025,  # self.dial_width * 0.15,
                  self.dial_width * 0.95, self.dial_width * 0.95,
                  start_angle, end_angle)
        return arc

    def update_percentage(self):
        value = min(max(self.channel_value, self.lim_low), self.lim_hi)
        self.percentage = (value - self.lim_low) / (self.lim_hi - self.lim_low)

    def channels(self):
        pass
