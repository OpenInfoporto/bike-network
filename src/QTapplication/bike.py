import sys
from PyQt4.Qt import *
from PyQt4.QtGui import * 
from PyQt4.QtCore import * 
from PyQt4 import QtCore, QtGui
from httpWidget import Ui_HttpWidget
import json
import httplib2

import thread
import time

#richieste rest
class Rest(object):
    def __init__(self, mainUrl, port):
        self.URL = mainUrl + ":" + port
        self.http = httplib2.Http(disable_ssl_certificate_validation=True)
    
    #method to get auth token for rest requests
    def getToken(self):
        command = "/api/commons/signin_device/"
        headers, content = self.http.request(self.URL+command, "POST", json.dumps({'username': 'dev001', 'password': 'dev001'}), headers={'Content-type': 'application/json'})
        contentDecoded = json.loads(content)
        return contentDecoded["payload"]["token"]
    
    #method to return available bike order
    def checkOrder(self, number = None):
        command = "/api/store/check_order/"
        data = {'number': number, 'code': 'BIKE'}
        headers, content = self.http.request(self.URL+command, "POST", json.dumps(data), headers={'Authorization': 'Token '+self.getToken(),'Content-type': 'application/json'})
        return json.loads(content)
        
    #method to confirm consumed bike order
    def pickBike(self, number = None, order_num = None, bike_id = None):
        command = "/api/bike/pick/"
        data = {'number': number, 'order_num': order_num, 'bike_id': bike_id}
        print data
        headers, content = self.http.request(self.URL+command, "POST", json.dumps(data), headers={'Authorization': 'Token '+self.getToken(),'Content-type': 'application/json'})
        return json.loads(content)
        
    #method to confirm consumed bike order
    def giveBackBike(self, bike_id = None):
        command = "/api/bike/giveback/"
        data = {'bike_id': bike_id}
        print data
        headers, content = self.http.request(self.URL+command, "POST", json.dumps(data), headers={'Authorization': 'Token '+self.getToken(),'Content-type': 'application/json'})
        return json.loads(content)   

#pagina web
class WebTab(QtGui.QWidget):
    def __init__(self, parent=None):
        super(WebTab, self).__init__(parent)
        self.ui = Ui_HttpWidget()
        self.ui.setupUi(self)
        
        # set margins
        '''
        l = self.layout()
        l.setMargin(0)
        self.ui.horizontalLayout.setMargin(6)
        '''
        
        # set the default page
        url = 'http://google.it'
        self.ui.url.setText(url)
        
        # load page
        self.ui.webView.setUrl(QtCore.QUrl(url))
        
        # history buttons:
        self.ui.back.setEnabled(False)
        self.ui.next.setEnabled(False)
        
        #stop button:
        self.ui.stop.setEnabled(False)

        QtCore.QObject.connect(self.ui.back,QtCore.SIGNAL("clicked()"), self.back)
        QtCore.QObject.connect(self.ui.next,QtCore.SIGNAL("clicked()"), self.next)
        QtCore.QObject.connect(self.ui.url,QtCore.SIGNAL("returnPressed()"), self.url_changed)
        QtCore.QObject.connect(self.ui.webView,QtCore.SIGNAL("linkClicked (const QUrl&)"), self.link_clicked)
        QtCore.QObject.connect(self.ui.webView,QtCore.SIGNAL("urlChanged (const QUrl&)"), self.link_clicked)
        QtCore.QObject.connect(self.ui.webView,QtCore.SIGNAL("titleChanged (const QString&)"), self.title_changed)
        QtCore.QObject.connect(self.ui.reload,QtCore.SIGNAL("clicked()"), self.reload_page)
        QtCore.QObject.connect(self.ui.stop,QtCore.SIGNAL("clicked()"), self.stop_page)

        QtCore.QMetaObject.connectSlotsByName(self)
  
    def url_changed(self):
        #Url have been changed by user
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

        url = str(self.ui.url.text())
        #bug fix: it loads urls with no http
        if(str(self.ui.url.text())[0:3] != "http"):
            self.ui.url.setText("http://"+url)
        
        url = self.ui.url.text()
        self.ui.webView.setUrl(QtCore.QUrl(url))
    
    def stop_page(self):
        #Stop loading the page
        self.close()
  
    def title_changed(self, title):
        #Web page title changed - change the tab name
        self.setWindowTitle(title)
  
    def reload_page(self):
        #Reload the web page
        self.ui.webView.setUrl(QtCore.QUrl(self.ui.url.text()))
    
  
    def link_clicked(self, url):
        #Update the URL if a link on a web page is clicked
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
        #Back button clicked, go one page back
        page = self.ui.webView.page()
        history = page.history()
        history.back()
        if history.canGoBack():
          self.ui.back.setEnabled(True)
        else:
          self.ui.back.setEnabled(False)
  
    def next(self):
        #Next button clicked, go to next page
        page = self.ui.webView.page()
        history = page.history()
        history.forward()
        if history.canGoForward():
          self.ui.next.setEnabled(True)
        else:
          self.ui.next.setEnabled(False)
      
#popup
class MyPopup(QWidget):
    def __init__(self, restCaller, message = "ERRORE", type = None, number = None, order_num = None):
        QWidget.__init__(self)
        resolution = QtGui.QDesktopWidget().screenGeometry()
        
        self.restCaller = restCaller
        self.number = number
        self.order_num = order_num

        self.lbl = QtGui.QLabel(message, self)
        font = QFont("Sans Serif", 50, QFont.Bold)
        self.lbl.setFont(font)
        self.lbl.setStyleSheet("QLabel { background-color: rgba(222, 222, 222, 222); } ")
        self.lbl.move((resolution.width() / 2) - (self.frameSize().width() / 2),(resolution.height() / 1.5) - (self.frameSize().height() / 1.5))
        
        self.btn1 = QPushButton("OK",self)
        self.btn1.setFont(font)
        self.btn1.move((resolution.width() / 2) - (self.frameSize().width() / 2),(resolution.height() / 0.95) - (self.frameSize().height() / 0.95))
        
        self.setAutoFillBackground(True)
        palette = QPalette()
        palette.setBrush(QPalette.Background, QBrush(QPixmap("ibike.jpg")))
        self.setPalette(palette)
        
        if(type == "in"):
            self.connect(self.btn1, SIGNAL("clicked()"), self.consegna)
        elif(type == "out"):
            self.connect(self.btn1, SIGNAL("clicked()"), self.ritiro)
        else:
            self.connect(self.btn1, SIGNAL("clicked()"), self.chiudi)
    
    #ritiro bici
    def ritiro(self):
        print "ritiro"
        #sblocco della bici
        bikeId = 1 #mettere bikeId
        self.confermaRitiro(bikeId)
        #bug fix: workaroud for focus

    
    def confermaRitiro(self, bikeId = None):
        print "bici sbloccata"
        #pick
        print self.restCaller.pickBike(self.number, self.order_num, bikeId) #mettere bikeId
        
        self.close()

    #consegna bici
    def consegna(self):
        print "consegna"
        #blocco della bici
        bikeId = 1 #mettere bikeId
        self.confermaConsegna(bikeId)
        
    def confermaConsegna(self, bike_id = None):
        print "bici bloccata"
        print self.restCaller.giveBackBike(bike_id) #mettere bikeId
        self.close()
    
    #chiusura popup
    def chiudi(self):
        self.close()
        
#programma principale
class MainTab(QtGui.QWidget):
    def __init__(self, restCaller, parent=None):
        super(MainTab, self).__init__(parent)
        resolution = QtGui.QDesktopWidget().screenGeometry()
        
        self.restCaller = restCaller

        #out button
        self.btn1 = QPushButton( self)
        self.btn1.setIcon(QIcon('out.png'))
        self.btn1.resize(QSize(100,80))
        self.btn1.move((resolution.width() / 3.5) - (self.frameSize().width() / 3.5),(resolution.height() / 1) - (self.frameSize().height() / 1))
        self.connect(self.btn1, SIGNAL("clicked()"), self.doRitira)

        #key
        self.welcomeCard = QLineEdit(self)
        self.welcomeCard.resize(QSize(400,60))
        fontCard = QFont("Sans Serif", 35, QFont.Bold)
        self.welcomeCard.setFont(fontCard)
        self.welcomeCard.setAlignment(QtCore.Qt.AlignCenter)
        self.welcomeCard.move((resolution.width() / 2) - (self.frameSize().width() / 2),(resolution.height() / 0.98) - (self.frameSize().height() / 0.98))

        #in button
        self.btn2 = QPushButton( self)
        self.btn2.setIcon(QIcon('in.png'))
        self.btn2.resize(QSize(100,80))
        self.btn2.move((resolution.width() / 1) - (self.frameSize().width() / 1),(resolution.height() / 1) - (self.frameSize().height() / 1))
        self.connect(self.btn2, SIGNAL("clicked()"), self.doConsegna)

        #label ibike
        self.lbl = QtGui.QLabel("iBike", self)
        self.lbl.setStyleSheet("QLabel { background-color: rgba(222, 222, 222, 222); } ")
        self.lbl.setGeometry(300, 300, 410, 120)
        font = QFont("Sans Serif", 60, QFont.Bold)
        self.lbl.setFont(font)
        self.lbl.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        self.lbl.move((resolution.width() / 2) - (self.frameSize().width() / 2),(resolution.height() / 2.2) - (self.frameSize().height() / 2.2))

        #label 
        self.lbl = QtGui.QLabel("Ritira la tua bicicletta usando il codice WelcomeKey", self)
        self.lbl.setStyleSheet("QLabel { background-color: rgba(222, 222, 222, 222); } ")
        self.lbl.setGeometry(300, 300, 410, 40)
        font = QFont("Sans Serif", 10, QFont.Bold)
        self.lbl.setFont(font)
        self.lbl.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        self.lbl.move((resolution.width() / 2) - (self.frameSize().width() / 2),(resolution.height() / 1.35) - (self.frameSize().height() / 1.35))
    
    #popup call
    def doit(self, restCaller, message, type = None, number = None, order_num = None):
        print "Opening a new popup window..."
        self.w = MyPopup(restCaller, message, type, number, order_num)
        self.w.showFullScreen()
        
    #in/out methods
    def doRitira(self):
        contentDecoded = self.restCaller.checkOrder(str(self.welcomeCard.text()))
        
        print contentDecoded
        
        if(contentDecoded["status"] == 100 and len(contentDecoded["payload"])>0):
            print "ritira bici "+ str(self.welcomeCard.text()) + " ordine " + str(contentDecoded["payload"][0]["id"])
            self.doit("BICI PRONTA","out", str(self.welcomeCard.text()), str(contentDecoded["payload"][0]["id"]))
        else:
            print "NOT FOUND: "+str(contentDecoded["status"])
            self.doit(self.restCaller,"BICI NON DISPONIBILI")
        
        #bug fix: workaroud for focus        
        QTest.keyPress(self, Qt.Key_Tab);
        QTest.keyRelease(self, Qt.Key_Tab);
       
    def doConsegna(self):
        print "consegna bici "+str(self.welcomeCard.text())
        self.doit(self.restCaller,"BICI CONSEGNATA","in", str(self.welcomeCard.text()))
        #bug fix: workaroud for focus
        for i in range(0,3):
            QTest.keyPress(self, Qt.Key_Tab);
            QTest.keyRelease(self, Qt.Key_Tab);

class MainWindow(QMainWindow):
    def __init__(self, restCaller, *args):
        QMainWindow.__init__(self, *args)

        self.active = 0
    
        self.tabs = QtGui.QTabWidget()
        self.tabs.setStyleSheet('QTabBar::tab{width: 380px; height: 40px; padding: 12px 15px; font-size: 30pt;}')
        
        # Create tabs
        tab1 = QtGui.QWidget() 
        tab2 = QtGui.QWidget()
        
        # Set layout of first tab
        vBoxlayout = QtGui.QVBoxLayout() 
        
        #background
        tab1.setAutoFillBackground(True)
        palette = QPalette()
        palette.setBrush(QPalette.Background, QBrush(QPixmap("ibike.jpg")))
        tab1.setPalette(palette)
        
        mainTab = MainTab(restCaller)
        vBoxlayout.addWidget(mainTab)
        tab1.setLayout(vBoxlayout)
        
        # Set layout of second tab
        webLayout = QtGui.QVBoxLayout()
        webWidget = WebTab()
        # add event
        webWidget.setMouseTracking(True)
        webWidget.installEventFilter(self)
        webWidget.ui.webView.setMouseTracking(True)
        webWidget.ui.webView.installEventFilter(self)
        webWidget.ui.url.setMouseTracking(True)
        webWidget.ui.url.installEventFilter(self)
        
        webLayout.addWidget(webWidget)
        tab2.setLayout(webLayout)

        # Add tabs
        self.tabs.addTab(tab1,"Bike")
        self.tabs.addTab(tab2,"Web")

        # test signals
        self.tabs.currentChanged.connect(self.onChange)
        self.tabs.blockSignals(False) #now listen the currentChanged signal
        
        # Set title and show
        self.tabs.setWindowTitle('IBIKE')
        self.tabs.showFullScreen()
        
        #bug fix: workaroud for focus
        for i in range(0,2):
            QTest.keyPress(self.tabs, Qt.Key_Tab);
            QTest.keyRelease(self.tabs, Qt.Key_Tab);
        
        # Create one thread as follows
        try:
            thread.start_new_thread( self.keepAlive, ("KeepAlive", 2, ) )
        except:
            print "Error: unable to start thread"

    
    #@pyqtSlot()  
    def onChange(self,i): #changed!
        if(i == 1):
            try:
                thread.start_new_thread( self.webIdle, ())
            except:
                print "Error: unable to start thread"
                
    def eventFilter(self, source, event):
        if (event.type() == QtCore.QEvent.MouseMove or event.type() == QtCore.QEvent.MouseButtonPress or event.type() == QtCore.QEvent.KeyPress ):
            self.active = 1
            
            #debug print
            '''
            if(event.type() == QtCore.QEvent.KeyPress):
                print('key pressed')
            else:
                pos = event.pos()
                if(event.type() == QtCore.QEvent.MouseButtonPress):
                    print('mouse click: (%d, %d)' % (pos.x(), pos.y()))
                else:
                    print('mouse move: (%d, %d)' % (pos.x(), pos.y()))
            '''

        return QtGui.QWidget.eventFilter(self, source, event)

    #Function for web idle thread
    def webIdle(self, threadName = "WebIdle", delay = 10):
        count = 0
        maxCount = 30
        
        while count < maxCount:
            time.sleep(delay)
            if(self.active == 1):
                count = 0
                self.active = 0
            else:
                count += 1
            
            if(self.tabs.currentIndex() == 0):
                        count += maxCount+1           
            
            #print "%s: %s" % ( threadName, time.ctime(time.time()) )
        
        if(self.tabs.currentIndex() == 1):
            self.tabs.setCurrentIndex( 0 )
            
    #Function for keepalive thread
    def keepAlive(self, threadName = "WebIdle", delay = 10):
        alive = True
        
        while alive:
            print "alive"
            time.sleep(delay)
        
def main(args):
    app = QtGui.QApplication(sys.argv)
    
    restCaller = Rest(sys.argv[1], sys.argv[2])
    
    app.main = MainWindow(restCaller)
    #avvio app
    app.exec_()
    
if __name__ == "__main__":
    main(sys.argv)