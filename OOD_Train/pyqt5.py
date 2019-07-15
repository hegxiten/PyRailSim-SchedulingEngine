#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Useful Links:
http://code.py40.com/pyqt5/
https://www.cnblogs.com/archisama/
http://www.qtcn.org/pyqtbook/
https://fishc.com.cn/forum.php?mod=viewthread&tid=59816&extra=page%3D1&page=1
https://www.zhihu.com/question/26492283
https://doc.qt.io/qt-5/

ZetCode PyQt5 tutorial 

This program shows a confirmation 
message box when we click on the close
button of the application window. 

author: Jan Bodnar
website: zetcode.com 
last edited: January 2015
"""

import sys
from PyQt5.QtWidgets import QWidget, QMessageBox, QApplication
# pylint c-extension-no-member may throw a warning


class Example(QWidget):
    
    def __init__(self):
        super().__init__()
        
        self.initUI()
        
        
    def initUI(self):               
        
        self.setGeometry(300, 300, 250, 150)        
        self.setWindowTitle('Message box')    
        self.show()
        
        
    def closeEvent(self, event):
        
        reply = QMessageBox.question(self, 'Message',"Are you sure to quit?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()        
        
        
if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())