from PyQt4.QtGui import QApplication, QWidget, QPainter, QPainterPath, QPen, QRadialGradient, QFont, QFontMetrics, QColor, QMatrix, QPolygonF
from PyQt4.QtCore import Qt, QString, QPointF, QPoint, QRectF

class DMCircularGauge(QWidget):
    def __init__(self, channel='', lim_low_channel=30.0, lim_hi_channel=100.0):
        super(DMCircularGauge,self).__init__()

        self._channel = channel
        self._limits = [lim_low_channel,lim_hi_channel]
        self.channel_value = 70
        print self.percentage

    def initUI(self):
        pass

    def paintEvent(self, event):
        height_offset = 50.0
        if self.height() >= self.width()/2 + height_offset:
            height = (self.width()/2.0)
            width = self.width()
        else:
            height = self.height()-height_offset
            width = height*2
        width_offset = (self.width()-width)/2.0

        # Initialize QPainter properties
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # First main draw gauge arc
        pen = QPen(painter.pen())
        pen.setWidth(3)
        pen.setColor(Qt.black)
        painter.setPen(pen)
        dial_bg = QRadialGradient(QPointF(self.width()/2.0, self.height()-height_offset), height)
        dial_bg.setColorAt(0, Qt.lightGray)
        dial_bg.setColorAt(1, Qt.black)
        painter.setBrush(dial_bg)
        arc_path = QPainterPath(QPointF(width_offset, self.height()-height_offset))
        arc_path.arcTo(QRectF(width_offset, self.height()-(height+height_offset), width, height*2), 180, -180)
        painter.drawPath(arc_path)

        # Add bottom block for label and overflow
        bottom_path = QPainterPath(QPointF(width_offset, self.height()-height_offset-1))
        bottom_path.lineTo(QPointF(width_offset, self.height()))
        bottom_path.lineTo(QPointF(width+width_offset, self.height()))
        bottom_path.lineTo(QPointF(width + width_offset, self.height()-height_offset-1))
        painter.drawPath(bottom_path)

        # Make the painter ready to draw scale labels
        #drawWidth = self.width() / 100
        font = QFont(painter.font())
        font.setPixelSize(max(width/50, 10))
        font_metric = QFontMetrics(font)
        painter.setFont(font)
        pen.setColor(Qt.white)
        painter.setPen(pen)

        percentIncrease = 1 / 8.0
        #print scale_text.size(), percentIncrease

        inc = (self.lim_hi-self.lim_low)/8.0
        scale = self.lim_low
        percent = 0.0
        for i in range(0,8,1):
            #print percent
            point = QPointF(arc_path.pointAtPercent(percent))
            angle = arc_path.angleAtPercent(percent) # Clockwise is negative

            painter.save()
            # Move the virtual origin to the point on the curve
            painter.translate(point)
            # Rotate to match the angle of the curve
            # Clockwise is positive so we negate the angle from above
            painter.rotate(-angle)
            # Draw a line width above the origin to move the text above the line
            # and let Qt do the transformations
            #print scale
            painter.drawText(QPoint(0, pen.width() + 10), QString("|"))
            painter.restore()

            point = QPointF(arc_path.pointAtPercent(max(percent-0.01,0.0)))
            angle = arc_path.angleAtPercent(max(percent-0.01,0.0))
            painter.save()
            scale_str = QString(str(scale))
            painter.translate(point)
            painter.rotate(-angle)
            painter.drawText(0, pen.width() + 30, font_metric.width(scale_str), font_metric.height(),
                             Qt.AlignHCenter, scale_str)
            painter.restore()
            scale += inc
            percent += percentIncrease
        point = QPointF(arc_path.pointAtPercent(percent))
        angle = arc_path.angleAtPercent(percent)  # Clockwise is negative
        painter.save()
        painter.translate(point)
        painter.rotate(-angle)
        painter.drawText(QPoint(0, pen.width() + 10), QString("|"))
        painter.restore()
        point = QPointF(arc_path.pointAtPercent(max(percent - 0.01, 0.0)))
        angle = arc_path.angleAtPercent(max(percent - 0.01, 0.0))
        painter.save()
        scale_str = QString(str(scale))
        painter.translate(point)
        painter.rotate(-angle)
        painter.drawText(0, pen.width() + 30, font_metric.width(scale_str), font_metric.height(),
                         Qt.AlignHCenter, scale_str)
        painter.restore()

        needle_base_width = 14
        #needle_length = height*0.9
        needle_tip = QPointF(arc_path.pointAtPercent(self.percentage))
        needle_base_center = QPointF(self.width() / 2, self.height() - height_offset)
        needle_angle = arc_path.angleAtPercent(self.percentage)
        #left_edge_angle = needle_angle-90
        #right_edge_angle = needle_anlge+90


        # Draw Highlight side of needle
        #pen = QPen(painter.pen())
        pen.setWidth(1)
        pen.setColor(Qt.cyan) # QColor(230,230,230,255))
        painter.setPen(pen)
        painter.setBrush(Qt.cyan) #QColor(230,230,230,255))
        #painter.save()
        #painter.rotate(needle_angle)
        needle_left = QPolygonF([QPointF(self.width() / 2 - needle_base_width/2, self.height() - height_offset),
                                 needle_base_center,
                                 needle_tip])
        #painter.drawPolygon(QPointF(self.width() / 2 - needle_base_width/2, self.height() - height_offset),
        #                    needle_base_center,
        #                    needle_tip)
        #transform = QMatrix()
        #transform.rotate(10)
        #needle_left = transform.map(needle_left)
        painter.drawPolygon(needle_left)
        #painter.restore()

        # Draw shadow side of needle
        #pen = QPen(painter.pen())
        #pen.setWidth(1)
        pen.setColor(Qt.darkCyan) # QColor(80,80,80,255))
        painter.setPen(pen)
        painter.setBrush(Qt.darkCyan) # QColor(80,80,80,255))
        needle_right = QPolygonF([QPointF(self.width() / 2 + needle_base_width / 2, self.height() - height_offset),
                                 needle_base_center,
                                 needle_tip])
        #painter.save()
        #painter.rotate(needle_angle)
        #painter.drawPolygon(QPointF(self.width() / 2 + needle_base_width/2, self.height() - height_offset),
        #                    needle_base_center,
        #                    needle_tip)
        #transform = QMatrix()
        #transform.rotate(needle_angle)
        #needle_right = transform.map(needle_right)
        painter.drawPolygon(needle_right)
        #painter.restore()

        # Draw needle axel pin
        pin_diameter = 20
        pen = QPen(painter.pen())
        pen.setWidth(1)
        pen.setColor(Qt.black)
        painter.setPen(pen)
        pin_bg = QRadialGradient(QPointF(self.width() / 2.0 - 4, self.height() - height_offset - 5), 15)
        pin_bg.setColorAt(0, Qt.lightGray)
        pin_bg.setColorAt(1, Qt.black)
        painter.setBrush(pin_bg)
        painter.drawEllipse((self.width() / 2) - (pin_diameter/2),
                            self.height() - height_offset - (pin_diameter/2),
                            pin_diameter,
                            pin_diameter)


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