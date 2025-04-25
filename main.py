# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QApplication
import sys
from test import App

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec_())