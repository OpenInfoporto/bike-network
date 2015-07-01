import sys
from PyQt4.Qt import *
from PyQt4.QtGui import * 
from PyQt4.QtCore import * 
from PyQt4 import QtCore, QtGui
from httpWidget import Ui_HttpWidget

#pagina web
class MyPopup(QtGui.QWidget):
  def __init__(self, parent=None):
    super(MyPopup, self).__init__(parent)
    self.ui = Ui_HttpWidget()
    self.ui.setupUi(self)
    
    # set margins
    l = self.layout()
    l.setMargin(0)
    self.ui.horizontalLayout.setMargin(6)
    
    # set the default page
    url = 'http://google.it'
    self.ui.url.setText(url)
    
    # load page
    self.ui.webView.setUrl(QtCore.QUrl(url))
    
    # history buttons:
    self.ui.back.setEnabled(False)
    self.ui.next.setEnabled(False)
    

    QtCore.QObject.connect(self.ui.back,QtCore.SIGNAL("clicked()"), self.back)
    QtCore.QObject.connect(self.ui.next,QtCore.SIGNAL("clicked()"), self.next)
    QtCore.QObject.connect(self.ui.url,QtCore.SIGNAL("returnPressed()"), self.url_changed)
    QtCore.QObject.connect(self.ui.webView,QtCore.SIGNAL("linkClicked (const QUrl&)"), self.link_clicked)
    QtCore.QObject.connect(self.ui.webView,QtCore.SIGNAL("urlChanged (const QUrl&)"), self.link_clicked)
    QtCore.QObject.connect(self.ui.webView,QtCore.SIGNAL("titleChanged (const QString&)"), self.title_changed)
    QtCore.QObject.connect(self.ui.reload,QtCore.SIGNAL("clicked()"), self.reload_page)
    QtCore.QObject.connect(self.ui.stop,QtCore.SIGNAL("clicked()"), self.stop_page)


    
    QtCore.QMetaObject.connectSlotsByName(self)

    self.showMaximized()
  
  def url_changed(self):
    """
    Url have been changed by user
    """
    page = self.ui.webView.page()
    history = page.history()
    if history.canGoBack():
      self.ui.back.setEnabled(True)
    else:
      self.ui.back.setEnabled(False)
    if history.canGoForward():
      self.ui.next.setEnabled(True)
    else:
      self.ui.next.setEnabled(False)
    
    url = self.ui.url.text()
    self.ui.webView.setUrl(QtCore.QUrl(url))
    
  def stop_page(self):
    """
    Stop loading the page
    """
    self.close()
  
  def title_changed(self, title):
    """
    Web page title changed - change the tab name
    """
    self.setWindowTitle(title)
  
  def reload_page(self):
    """
    Reload the web page
    """
    self.ui.webView.setUrl(QtCore.QUrl(self.ui.url.text()))
    
  
  def link_clicked(self, url):
    """
    Update the URL if a link on a web page is clicked
    """
    page = self.ui.webView.page()
    history = page.history()
    if history.canGoBack():
      self.ui.back.setEnabled(True)
    else:
      self.ui.back.setEnabled(False)
    if history.canGoForward():
      self.ui.next.setEnabled(True)
    else:
      self.ui.next.setEnabled(False)
    
    self.ui.url.setText(url.toString())
    
  def back(self):
    """
    Back button clicked, go one page back
    """
    page = self.ui.webView.page()
    history = page.history()
    history.back()
    if history.canGoBack():
      self.ui.back.setEnabled(True)
    else:
      self.ui.back.setEnabled(False)
  
  def next(self):
    """
    Next button clicked, go to next page
    """
    page = self.ui.webView.page()
    history = page.history()
    history.forward()
    if history.canGoForward():
      self.ui.next.setEnabled(True)
    else:
      self.ui.next.setEnabled(False)

             
#programma principale


class MainWindow(QMainWindow):
    def __init__(self, *args):
        QMainWindow.__init__(self, *args)
        self.cw = QWidget(self)
        self.setCentralWidget(self.cw)
        resolution = QtGui.QDesktopWidget().screenGeometry()

        #web button
        self.btn1 = QPushButton( self.cw)
        self.btn1.setIcon(QIcon('web.png'))
        self.btn1.setIconSize(QSize(70,70))
        self.btn1.move((resolution.width() / 1) - (self.frameSize().width() / 1),(resolution.height() / 0.55) - (self.frameSize().height() / 0.55))
        self.connect(self.btn1, SIGNAL("clicked()"), self.doit)

        #out button
        self.btn2 = QPushButton( self)
        self.btn2.setIcon(QIcon('out.png'))
        self.btn2.resize(QSize(100,80))
        self.btn2.move((resolution.width() / 3.5) - (self.frameSize().width() / 3.5),(resolution.height() / 1) - (self.frameSize().height() / 1))
        self.connect(self.btn2, SIGNAL("clicked()"), self.doRitira)

        #key
        self.text = QtGui.QTextEdit(self)
        self.text.resize(QSize(400,27))
        self.text.move((resolution.width() / 2) - (self.frameSize().width() / 2),(resolution.height() / 0.95) - (self.frameSize().height() / 0.95))


        #in button
        self.btn3 = QPushButton( self)
        self.btn3.setIcon(QIcon('in.png'))
        self.btn3.resize(QSize(100,80))
        self.btn3.move((resolution.width() / 1) - (self.frameSize().width() / 1),(resolution.height() / 1) - (self.frameSize().height() / 1))
        self.connect(self.btn3, SIGNAL("clicked()"), self.doConsegna)

        #label ibike
        self.lbl = QtGui.QLabel(" iBike", self)
        self.lbl.setStyleSheet("QLabel { background-color: rgba(222, 222, 222, 222); } ")
        self.lbl.setGeometry(300, 300, 410, 120)
        font = QFont("Sans Serif", 60, QFont.Bold)
        self.lbl.setFont(font)
        self.lbl.move((resolution.width() / 2) - (self.frameSize().width() / 2),(resolution.height() / 2.2) - (self.frameSize().height() / 2.2))

        #label 
        self.lbl = QtGui.QLabel(" Ritira la tua bicicletta usando il codice WelcomeKey", self)
        self.lbl.setStyleSheet("QLabel { background-color: rgba(222, 222, 222, 222); } ")
        self.lbl.setGeometry(300, 300, 410, 40)
        font = QFont("Sans Serif", 10, QFont.Bold)
        self.lbl.setFont(font)
        self.lbl.move((resolution.width() / 2) - (self.frameSize().width() / 2),(resolution.height() / 1.35) - (self.frameSize().height() / 1.35))

        self.showMaximized()


        self.w = None
        self.showMaximized()


    def doit(self):
        print "Opening a new popup window..."
        self.w = MyPopup()
        self.w.show()

    #in/out methods
    def doRitira(self):
        print "ritira bici"
        
    def doConsegna(self):
        print "consegna bici" 


class App(QApplication):
    def __init__(self, *args):
        QApplication.__init__(self, *args)
        self.main = MainWindow()
        palette = QPalette()
        
        #background
        palette.setBrush(QPalette.Background,QBrush(QPixmap("ibike.jpg")))
        self.main.setPalette(palette)

        self.main.show()


def main(args):
    global app
    app = App(args)

    app.exec_()

if __name__ == "__main__":
    main(sys.argv)