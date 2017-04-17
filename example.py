import sys
from PyQt4 import QtGui
from pyqtpaint import PyQtPaint


class SampleCode(QtGui.QDialog):
    def __init__(self, *args, **kwargs):
        super(SampleCode, self).__init__(*args, **kwargs)
        layout = QtGui.QVBoxLayout()

        # create PyQtPaint widget
        paint = PyQtPaint(1920, 1080)

        # set pen attributes
        paint.set_pen_color(QtGui.QColor(80, 230, 140, 255))
        paint.set_pen_size(40)
        paint.set_pen_blur(2)

        layout.addWidget(paint)
        self.setLayout(layout)

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    test_window = SampleCode()
    test_window.show()
    sys.exit(app.exec_())
