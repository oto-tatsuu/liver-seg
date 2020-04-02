import sys

from PySide2.QtWidgets import QApplication

from MainFrame import MainFrame

if __name__=='__main__':
    app=QApplication(sys.argv)
    m=MainFrame()
    m.resize(1200,800)
    m.show()
    sys.exit(app.exec_())
