from PyQt5.uic import loadUi


class UiInterface:
    """Загрузка ui файла"""

    def __init__(self, main_win):
        self.main_win = main_win
        self.setup_ui()

    def setup_ui(self):
        loadUi('./GUI/ui_farm.ui', self.main_win)
        self.main_win.setWindowTitle('Farm')
