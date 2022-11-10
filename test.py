import sys
from PyQt5 import QtGui

class MovieTest(QtGui.QDialog):
    def __init__(self):
        super(MovieTest, self).__init__()

        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)

        self.loading_lbl = QtGui.QLabel()
        self.loading_lbl.setSizePolicy(QtGui.QSizePolicy.Ignored, QtGui.QSizePolicyIgnored)
        self.loading_lbl.setScaledContents(True)
        layout.addWidget(self.loading_lbl)
        loading_movie = QtGui.QMovie("loading-radial_loop.gif") # some gif in here
        self.loading_lbl.setMovie(loading_movie)
        loading_movie.start()

        self.setGeometry(50,50,100,100)
        self.setMinimumSize(10,10)

    def resizeEvent(self, event):
        rect = self.geometry()
        size = min(rect.width(), rect.height())
        movie = self.loading_lbl.movie()
        movie.setScaledSize(QtCore.QSize(size, size))
        self.loading_lbl.adjustSize()

def main():
    app = QtGui.QApplication(sys.argv)
    ex = MovieTest()
    ex.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()