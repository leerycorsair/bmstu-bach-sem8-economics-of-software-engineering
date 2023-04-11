from PyQt5 import QtWidgets, QtCore
from cocomo import cocomo
import cocomo.cocomo_consts as cc
from interface import Ui_MainWindow

from PyQt5.QtWidgets import QMessageBox


class AppWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super(AppWindow, self).__init__()
        self.ui_setup()

    def ui_setup(self) -> None:
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.bind_buttons()
        self.show()

    def bind_buttons(self) -> None:
        self.ui.calc_button.clicked.connect(self.calc_perform)
        self.ui.graph_button.clicked.connect(self.graph_perform)

    def calc_perform(self) -> None:
        try:
            model = self.model_init()
            report = model.calc_model()
            model.print_report(report)
            QMessageBox.about(self, "Успех!", "Отчет сохранен в сооветствующей директории")
        except:
            QMessageBox.warning(self, "Внимание!",
                                "Некорректные входные данные")

    def graph_perform(self) -> None:
        try:
            model = self.model_init()
            model.cmp_params()
        except:
            QMessageBox.warning(self, "Внимание!",
                                "Некорректные входные данные")

    def model_init(self) -> cocomo.CocomoModel:
        try:
            kloc = int(self.ui.kloc_entry.text())
            mode = self.ui.mode_cb.currentText()
            salary = float(self.ui.salary_entry.text())

            params = cocomo.CocomoParams(
                cc.RELY_PARAMS[self.ui.rely_cb.currentText()],
                cc.DATA_PARAMS[self.ui.data_cb.currentText()],
                cc.CPLX_PARAMS[self.ui.cplx_cb.currentText()],
                cc.TIME_PARAMS[self.ui.time_cb.currentText()],
                cc.STOR_PARAMS[self.ui.stor_cb.currentText()],
                cc.VIRT_PARAMS[self.ui.virt_cb.currentText()],
                cc.TURN_PARAMS[self.ui.turn_cb.currentText()],
                cc.ACAP_PARAMS[self.ui.acap_cb.currentText()],
                cc.AEXP_PARAMS[self.ui.aexp_cb.currentText()],
                cc.PCAP_PARAMS[self.ui.pcap_cb.currentText()],
                cc.VEXP_PARAMS[self.ui.vexp_cb.currentText()],
                cc.LEXP_PARAMS[self.ui.lexp_cb.currentText()],
                cc.MODP_PARAMS[self.ui.modp_cb.currentText()],
                cc.TOOL_PARAMS[self.ui.tool_cb.currentText()],
                cc.SCED_PARAMS[self.ui.sced_cb.currentText()],
            )

            return cocomo.CocomoModel(kloc, mode, salary, params)

        except:
            QMessageBox.warning(self, "Внимание!",
                                "Некорректные входные данные")
