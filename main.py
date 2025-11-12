from PyQt5.QtWidgets import QApplication
from home import Home
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Home()
    window.show()
    sys.exit(app.exec_())
