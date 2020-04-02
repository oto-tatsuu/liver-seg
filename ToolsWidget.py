
from PySide2.QtWidgets import QSpinBox, QHBoxLayout, QPushButton, QWidget, QVBoxLayout


class ToolsWidget(QWidget):

    def __init__(self, parent=None):
        super(ToolsWidget, self).__init__(parent)
        self.initUI()
        pass

    def initUI(self):
        self.contour_epsilon=QSpinBox()
        self.generate_contour=QPushButton();
        self.generate_contour.setText("generate")
        self.contour_epsilon.setRange(3,20)
        self.contour_epsilon.setValue(10)
        l1=QHBoxLayout()
        l2=QVBoxLayout()
        self.b2=QPushButton("插点");
        self.b3=QPushButton();
        self.b4=QPushButton();
        l1.addWidget(self.contour_epsilon)
        l1.addSpacing(30)
        l1.addWidget(self.generate_contour)
        l1.setStretchFactor(self.contour_epsilon,1)
        l1.setStretchFactor(self.generate_contour,1)
        l2.addLayout(l1)
        l2.addWidget(self.b2)
        l2.addWidget(self.b3)
        l2.addWidget(self.b4)
        self.setLayout(l2)
        #面板属性设置
        # self.resize(200,800)
        # self.setAutoFillBackground(True)
        # palette = QPalette()
        # palette.setColor(QPalette.Background, QColor(255, 0, 0))
        pass
