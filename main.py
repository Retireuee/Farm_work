import asyncio
import sys
from PyQt5 import QtWidgets
from asyncqt import QEventLoop
from SystemCRM import SystemCRM

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    system_crm = SystemCRM()
    with loop:
        sys.exit(loop.run_forever())
