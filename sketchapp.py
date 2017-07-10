from PyQt5.QtCore import QDir, QPoint, QRect, QSize, Qt
from PyQt5.QtGui import QImage, QImageWriter, QPainter, QPen, qRgb, QColor
from PyQt5.QtWidgets import (QAction, QApplication, QFileDialog,
        QInputDialog, QMainWindow, QMenu, QMessageBox, QWidget)
from loadtrainednetwork import mypredict #@UnresolvedImport
import numpy as np
class ScribbleArea(QWidget):
    def __init__(self, parent=None):
        super(ScribbleArea, self).__init__(parent)

        self.setAttribute(Qt.WA_StaticContents)
        self.modified = False
        self.scribbling = False
        self.myPenWidth = 45
        self.myPenColor = Qt.black
        self.image = QImage()
        self.lastPoint = QPoint()
        self.displayval=""

    def openImage(self, fileName):
        loadedImage = QImage()
        if not loadedImage.load(fileName):
            return False

        newSize = loadedImage.size().expandedTo(self.size())
        self.resizeImage(loadedImage, newSize)
        self.image = loadedImage
        self.modified = False
        self.update()
        return True

    def saveImage(self, fileName, fileFormat):
        visibleImage = self.image
        self.resizeImage(visibleImage, self.size())

        if visibleImage.save(fileName, fileFormat):
            self.modified = False
            return True
        else:
            return False

    def setPenWidth(self, newWidth):
        self.myPenWidth = newWidth
    
    def compressImageWithoutDebug(self):
        return(self.compressImage(False))
    def compressImageWithDebug(self):
        return(self.compressImage(True))
    
    def dispPredict(self):
        QMessageBox.about(self, "Prediction", self.compressImageWithoutDebug() )
        '''msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("test")
        msg.setInformativeText("This is additional information")
        msg.setWindowTitle("MessageBox demo")
        #QMessageBox.information(self, 'test', displayval, Union)'''
    
    def compressImage(self,debug):
        compressed_img=[]
        for h in range(0,28):
            height_col=[]
            for w in range(0,28):
                section_to_be_compressed=[]
                #order doesn't matter for w2/h2
                for w2 in range(18*w,18*(w+1)):
                    for h2 in range(18*h,18*(h+1)):
                        pixel=self.image.pixel(w2,h2)
                        rgbvals=QColor(pixel).getRgbF()
                        section_to_be_compressed.append(rgbvals)
                #avg pixel values for that area
                section_val=ScribbleArea.avgmulti(section_to_be_compressed)
                height_col.append(section_val)
            compressed_img.append(height_col)
        
        if(debug):
            #visual format
            for y in reversed(range(0,len(compressed_img[0]))):
                print("")
                for x in range(0,len(compressed_img)):
                    if(compressed_img[x][y][0]==0):
                        print("X", end=" ")
                    else:
                        print(" ", end=" ")
                    #print(compressed_img[x][y], end=" ")
            print("")
            
            #check that it formatted correctly by validating corners
            print("--Validate Corners--")
            print("(0,0)=%s"%compressed_img[0][0])
            print("(27,0)=%s"%compressed_img[27][0])
            print("(0,27)=%s"%compressed_img[0][27])
            print("(27,27)=%s"%compressed_img[27][27])
        wrapper=(compressed_img,)
        formatted_data=np.array(wrapper)
        formatted_data=formatted_data.astype('float32')
        prediction=mypredict(formatted_data)
        if(debug):
            print("--Result--")
            print("Prediction: %s"%prediction)
        self.displayval=str(prediction)
        return(str(prediction))
    @staticmethod
    def avgmulti(arr):
        total=0
        for i in arr:
            total+=ScribbleArea.avg(i)
        if (total/len(arr)<0.6):
            return([1])
        else:
            return([0])
    
    @staticmethod
    def avg(x):
        return((x[0]+x[1]+x[2])/3)
    
    def clearImage(self):
        self.image.fill(qRgb(255, 255, 255))
        self.modified = True
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.lastPoint = event.pos()
            self.scribbling = True

    def mouseMoveEvent(self, event):
        if (event.buttons() & Qt.LeftButton) and self.scribbling:
            self.drawLineTo(event.pos())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.scribbling:
            self.drawLineTo(event.pos())
            self.scribbling = False

    def paintEvent(self, event):
        painter = QPainter(self)
        dirtyRect = event.rect()
        painter.drawImage(dirtyRect, self.image, dirtyRect)

    def resizeEvent(self, event):
        if self.width() > self.image.width() or self.height() > self.image.height():
            newWidth = max(self.width() + 128, self.image.width())
            newHeight = max(self.height() + 128, self.image.height())
            self.resizeImage(self.image, QSize(newWidth, newHeight))
            self.update()

        super(ScribbleArea, self).resizeEvent(event)

    def drawLineTo(self, endPoint):
        painter = QPainter(self.image)
        painter.setPen(QPen(self.myPenColor, self.myPenWidth, Qt.SolidLine,
                Qt.RoundCap, Qt.RoundJoin))
        painter.drawLine(self.lastPoint, endPoint)
        self.modified = True

        rad = self.myPenWidth / 2 + 2
        self.update(QRect(self.lastPoint, endPoint).normalized().adjusted(-rad, -rad, +rad, +rad))
        self.lastPoint = QPoint(endPoint)

    def resizeImage(self, image, newSize):
        if image.size() == newSize:
            return

        newImage = QImage(newSize, QImage.Format_RGB32)
        newImage.fill(qRgb(255, 255, 255))
        painter = QPainter(newImage)
        painter.drawImage(QPoint(0, 0), image)
        self.image = newImage

    def isModified(self):
        return self.modified

    def penColor(self):
        return self.myPenColor

    def penWidth(self):
        return self.myPenWidth


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.saveAsActs = []

        self.scribbleArea = ScribbleArea()
        self.setCentralWidget(self.scribbleArea)

        self.createActions()
        self.createMenus()

        self.setWindowTitle("Draw a Digit")
        self.setFixedSize(504,525)
        #self.resize(504, 504)

    def closeEvent(self, event):
        event.accept()

    def open(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open File",
            QDir.currentPath())
        if fileName:
            self.scribbleArea.openImage(fileName)

    def save(self):
        action = self.sender()
        fileFormat = action.data()
        self.saveFile(fileFormat)


    def penWidth(self):
        newWidth, ok = QInputDialog.getInt(self, "Scribble",
                "Select pen width:", self.scribbleArea.penWidth(), 1, 50, 1)
        if ok:
            self.scribbleArea.setPenWidth(newWidth)

    def about(self):
        QMessageBox.about(self, "Draw a digit and see if the neural network can identify it!")

    def createActions(self):
        self.openAct = QAction("&Open...", self, shortcut="Ctrl+O",
                triggered=self.open)

        for format in QImageWriter.supportedImageFormats():
            format = str(format)

            text = format.upper() + "..."

            action = QAction(text, self, triggered=self.save)
            action.setData(format)
            self.saveAsActs.append(action)

        self.exitAct = QAction("E&xit", self, shortcut="Ctrl+Q",
                triggered=self.close)

        self.penWidthAct = QAction("Pen &Width...", self,
                triggered=self.penWidth)

        self.clearScreenAct = QAction("&Erase", self, shortcut="Ctrl+Z",
                triggered=self.scribbleArea.clearImage)
        
        self.printPixelArray= QAction("&Predict", self,
                triggered=self.scribbleArea.compressImageWithoutDebug)
        
        self.printCompressedImg= QAction("&Predict with Debug", self, shortcut="Ctrl+O",
                triggered=self.scribbleArea.compressImageWithDebug)
        
        self.aboutAct = QAction("&About", self, triggered=self.about)

        self.showPredict=QAction("&Recognize Digit", self, shortcut="Ctrl+P",
                                 triggered=self.scribbleArea.dispPredict)

        self.aboutQtAct = QAction("About &Qt", self,
                triggered=QApplication.instance().aboutQt)

    def createMenus(self):
        self.saveAsMenu = QMenu("&Save As", self)
        for action in self.saveAsActs:
            self.saveAsMenu.addAction(action)

        fileMenu = QMenu("&File", self)
        fileMenu.addAction(self.openAct)
        fileMenu.addMenu(self.saveAsMenu)
        fileMenu.addSeparator()
        fileMenu.addAction(self.exitAct)

        optionMenu = QMenu("&Options", self)
        optionMenu.addAction(self.penWidthAct)
        optionMenu.addSeparator()
        optionMenu.addAction(self.clearScreenAct)
        
        clearMenu = QMenu("&Clear",self)
        clearMenu.addAction(self.clearScreenAct)
        
        helpMenu = QMenu("&Help", self)
        helpMenu.addAction(self.aboutAct)
        helpMenu.addAction(self.aboutQtAct)

        self.menuBar().addMenu(fileMenu)
        self.menuBar().addMenu(optionMenu)
        self.menuBar().addMenu(helpMenu)
        self.menuBar().addAction(self.clearScreenAct)
        #self.menuBar().addAction(self.printPixelArray)
        #self.menuBar().addAction(self.printCompressedImg)
        self.menuBar().addAction(self.showPredict)

    def saveFile(self, fileFormat):
        initialPath = QDir.currentPath() + '/untitled.' + fileFormat

        fileName, _ = QFileDialog.getSaveFileName(self, "Save As", initialPath,
                "%s Files (*.%s);;All Files (*)" % (fileFormat.upper(), fileFormat))
        if fileName:
            return self.scribbleArea.saveImage(fileName, fileFormat)
            print('saved!')
        else:
            print('save failed')
        return False
'''class InfoBox(QWidget):
    def __init__(self, parent=None):
        super(InfoBox, self).__init__(parent)
        self.textbox=QLineEdit(self)
        self.textbox.move(20, 20)
        self.textbox.resize(280,40)
        global displayval
        self.textbox.setText(displayval)
        
class InfoWindow(QMainWindow):
    def __init__(self):
        super(InfoWindow, self).__init__()
        self.infoBox = InfoBox()
        self.setCentralWidget(self.infoBox)
        self.setWindowTitle("Prediction:")
        self.setFixedSize(185,185)

    def closeEvent(self, event):
        event.accept()
 '''   
if __name__ == '__main__':

    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    #infowindow=InfoWindow()
    #infowindow.show()
sys.exit(app.exec_())