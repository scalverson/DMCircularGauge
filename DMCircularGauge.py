from PyQt4.QtGui import (
    QApplication, QWidget, QPainter, QPainterPath, QPen, QRadialGradient, QLinearGradient,
    QFont, QFontMetrics, QColor, QPolygonF
)
from PyQt4.QtCore import Qt, QString, QPointF, QPoint, QRectF
from numpy import linspace


class DMCircularGauge(QWidget):
    _value = 0.0
    percentage = 0.0

    def __init__(self, channel='', lim_low_channel=0.0, lim_hi_channel=90.0):
        super(DMCircularGauge, self).__init__()

        self._channel = channel
        self._limits = [lim_low_channel, lim_hi_channel]
        self.channel_value = 49.0

        self.width_ref = 400.0
        self.height_ref = 220.0
        self.resize(self.width_ref, self.height_ref)
        self.ref_aspect_ratio = self.width_ref / self.height_ref

        self.dial_v_offset = self.height() * 0.1
        if self.height() >= self.width() / 2 + self.dial_v_offset:
            self.dial_height = (self.width() / 2.0)
            self.dial_width = self.width()
        else:
            self.dial_height = self.height() - self.dial_v_offset
            self.dial_width = self.dial_height * 2
        self.dial_h_offset = (self.width() - self.dial_width) / 2.0

        self.dial = QPainterPath(QPointF(0.0, 200))
        self.dial.arcTo(0.0, 0.0, 400, 400, 180, -180)
        self.dial.lineTo(400, 220.0)
        self.dial.lineTo(0.0, 220.0)
        self.dial.lineTo(0.0, 200)

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
        painter.restore()

        # Display actual value
        painter.save()
        painter.setClipPath(self.dial)  # Don't allow label text to extend outside of main shape
        font = QFont()
        font.setPixelSize(min(max(self.dial_width / 2, 20), 50))
        painter.setFont(font)
        pen.setColor(Qt.green)
        painter.setPen(pen)
        font_metric = QFontMetrics(font)
        painter.translate(self.dial_width / 2, self.dial_height / 2)
        label = QString().setNum(self.channel_value, 'f', 2)
        painter.drawText(QPointF(0.0 - font_metric.width(label) / 2.0, font_metric.height() / 2.0),
                         label)
        painter.restore()

        # Next add division markers
        painter.save()
        painter.translate(self.dial_width / 2, self.dial_height * 0.98)
        pen.setColor(Qt.cyan)
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

        if self.percentage >= 0.5:
            needle_left_color = Qt.cyan  # QColor(230,230,230,255)
            needle_right_color = Qt.darkCyan  # QColor(80,80,80,255)
        else:
            needle_left_color = Qt.darkCyan  # QColor(80,80,80,255)
            needle_right_color = Qt.cyan  # QColor(230,230,230,255)

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
        return self._limits[1]

    @lim_hi.setter
    def lim_hi(self, lim):
        self._limits[1] = lim

    @property
    def lim_low(self):
        return self._limits[0]

    @lim_low.setter
    def lim_low(self, lim):
        self._limits[0] = lim

    @property
    def channel_value(self):
        return self._value

    @channel_value.setter
    def channel_value(self, value):
        self._value = value
        self.update_percentage()

    def update_percentage(self):
        value = min(max(self.channel_value,self.lim_low),self.lim_hi)
        self.percentage = (value-self.lim_low)/(self.lim_hi-self.lim_low)

    def channels(self):
        pass


if __name__ == "__main__":
    from sys import argv

    app = QApplication(argv)
    widget = DMCircularGauge()
    widget.show()
    widget.raise_()

    exit(app.exec_())