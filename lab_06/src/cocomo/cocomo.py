
from dataclasses import dataclass, fields
import cocomo.cocomo_consts as cc
from math import ceil
import os
from datetime import datetime
import matplotlib.pyplot as plt

from pytablewriter import MarkdownTableWriter


@dataclass
class CocomoParams:
    rely: float
    data: float
    cplx: float
    time: float
    stor: float
    virt: float
    turn: float
    acap: float
    aexp: float
    pcap: float
    vexp: float
    lexp: float
    modp: float
    tool: float
    sced: float


@dataclass
class _WorkReport:
    general_value: float
    full_value: float


@dataclass
class _TimeReport:
    general_value: float
    full_value: float


@dataclass
class _WBSReportItem:
    coef: int
    value: float


@dataclass
class _WBSReport:
    analysis: _WBSReportItem
    design: _WBSReportItem
    programming: _WBSReportItem
    testing: _WBSReportItem
    verification: _WBSReportItem
    documents: _WBSReportItem
    configuration: _WBSReportItem
    manual_creation: _WBSReportItem
    full: _WBSReportItem


@dataclass
class _TraditionalCycleReportItem:
    work_coef: int
    work_value: float
    time_coef: int
    time_value: float


@dataclass
class _TraditionalCycleReport:
    planning: _TraditionalCycleReportItem
    predesign: _TraditionalCycleReportItem
    design: _TraditionalCycleReportItem
    programming: _TraditionalCycleReportItem
    testing: _TraditionalCycleReportItem
    general: _TraditionalCycleReportItem
    full: _TraditionalCycleReportItem


@dataclass
class _WorkersReport:
    planning: int
    predesign: int
    design: int
    programming: int
    testing: int


@dataclass
class _CocomoReport:
    w_r: _WorkReport
    t_r: _TimeReport
    wbs_r: _WBSReport
    tr_r: _TraditionalCycleReport
    workers_r: _WorkersReport
    cost: float


class CocomoModel:
    def __init__(self, kloc: int, mode: str, salary: float, params: CocomoParams) -> None:
        self.kloc = kloc
        self.mode = mode
        self.salary = salary
        self.params = params

    def calc_model(self) -> _CocomoReport:
        w_rep = self.__get_work(self.__get_EAF())
        t_rep = self.__get_time(w_rep.general_value)
        wbs_rep = self.__form_wbs_report(w_rep)
        tr_rep = self.__form_traditional_report(w_rep, t_rep)
        workers_rep = self.__form_workers_report(tr_rep)
        cost = self.__form_cost_report(wbs_rep)

        result = _CocomoReport(
            w_rep,
            t_rep,
            wbs_rep,
            tr_rep,
            workers_rep,
            cost
        )
        return result

    def print_report(self, r: _CocomoReport) -> None:
        curr_time = str(datetime.utcnow())
        for char in " -.:":
            curr_time = curr_time.replace(char, "")
        path = "{}".format(os.getcwd()) + "\\files\\" + curr_time
        if not os.path.exists(path):
            os.makedirs(path)

        def png_report():
            x = ["Этап 1", "Этап 2", "Этап 3", "Этап 4", "Этап 5"]
            y = [
                r.workers_r.planning,
                r.workers_r.predesign,
                r.workers_r.design,
                r.workers_r.programming,
                r.workers_r.testing]
            plt.xlabel('Этапы жизненного цикла ПО')
            plt.ylabel('Количество работников')
            plt.bar(x, y)
            plt.savefig(path+"\\workers_graph.png", dpi=400)
        png_report()

        def markdown_report():
            file = open(path + "\\report.md", "w", encoding="utf-8")
            general_report = self.__general_report_to_str(r)
            file.write(general_report)
            cost_report = "Бюджет проекта = {} руб.\n".format(round(r.cost))
            file.write(cost_report)
            traditional_report = self.__traditional_cycle_report_to_str(r)
            file.write(traditional_report)
            wbs_report = self.__wbs_report_to_str(r)
            file.write(wbs_report)
            workers_report = self.__workers_report_to_str(r)
            file.write(workers_report)
            workers_graph = "![graph]({})\n".format("\\workers_graph.png")
            file.write(workers_graph)
            file.close()
        markdown_report()

    def cmp_params(self) -> None:
        cplx_list = ["Очень низкий", "Номинальный", "Очень высокий"]
        params_list = ["Низкий", "Номинальный", "Высокий"]

        _, axes = plt.subplots(3, 2)
        for cplx in cplx_list:
            acap_work = []
            acap_time = []
            aexp_work = []
            aexp_time = []
            pcap_work = []
            pcap_time = []
            lexp_work = []
            lexp_time = []
            for param in params_list:
                work = self.__get_work(
                    cc.ACAP_PARAMS[param]*cc.CPLX_PARAMS[cplx]).general_value
                time = self.__get_time(work).general_value
                acap_work.append(work)
                acap_time.append(time)

                work = self.__get_work(
                    cc.AEXP_PARAMS[param]*cc.CPLX_PARAMS[cplx]).general_value
                time = self.__get_time(work).general_value
                aexp_work.append(work)
                aexp_time.append(time)

                work = self.__get_work(
                    cc.PCAP_PARAMS[param]*cc.CPLX_PARAMS[cplx]).general_value
                time = self.__get_time(work).general_value
                pcap_work.append(work)
                pcap_time.append(time)

                work = self.__get_work(
                    cc.LEXP_PARAMS[param]*cc.CPLX_PARAMS[cplx]).general_value
                time = self.__get_time(work).general_value
                lexp_work.append(work)
                lexp_time.append(time)

            plt.suptitle(f'Трудозатраты(слева), время(справа) при разных CPLX.\n'
                         f'Красный - ACAP, зеленый - AEXP, синий = PCAP, желтый - LEXP')
            axes[cplx_list.index(cplx)][0].plot(params_list, acap_work, 'r', params_list, aexp_work,
                                                'g', params_list, pcap_work, 'b', params_list, lexp_work, 'y')
            axes[cplx_list.index(cplx)][1].plot(params_list, acap_time, 'r', params_list, aexp_time,
                                                'g', params_list, pcap_time, 'b', params_list, lexp_time, 'y')
        plt.show()

    def __get_work(self, eaf: float) -> _WorkReport:
        value = cc.WORK_MULTI[self.mode] * eaf * (
            self.kloc ** cc.WORK_POWER[self.mode])
        result = _WorkReport(value, value * cc.WORK_FULL)
        return result

    def __get_time(self, work_value: float) -> _TimeReport:
        value = cc.TIME_MULTI[self.mode] * (
            work_value ** cc.TIME_POWER[self.mode])
        result = _TimeReport(value, value * cc.TIME_FULL)
        return result

    def __get_EAF(self) -> float:
        eaf = 1.00
        for field in fields(self.params):
            eaf *= getattr(self.params, field.name)
        return eaf

    def __form_traditional_report(self, w_rep: _WorkReport, t_rep: _TimeReport) -> _TraditionalCycleReport:
        result = _TraditionalCycleReport(*
                                         [_TraditionalCycleReportItem(
                                             coef[0],
                                             coef[0]*w_rep.general_value/100.0,
                                             coef[1],
                                             coef[1]*t_rep.general_value/100.0)
                                          for _, coef in cc.TRADITIONAL_CONSTS.items()])
        return result

    def __form_wbs_report(self, w_rep: _WorkReport) -> _WBSReport:
        result = _WBSReport(*
                            [_WBSReportItem(
                                coef,
                                coef*w_rep.full_value/100.0)
                             for _, coef in cc.WBS_CONSTS.items()])
        return result

    def __form_workers_report(self, tr_rep: _TraditionalCycleReport) -> _WorkersReport:
        result = _WorkersReport(
            ceil(tr_rep.planning.work_value/tr_rep.planning.time_value),
            ceil(tr_rep.predesign.work_value/tr_rep.predesign.time_value),
            ceil(tr_rep.design.work_value/tr_rep.design.time_value),
            ceil(tr_rep.programming.work_value/tr_rep.programming.time_value),
            ceil(tr_rep.testing.work_value/tr_rep.testing.time_value)
        )
        return result

    def __form_cost_report(self, wbs_rep: _WBSReport) -> float:
        result = self.salary * wbs_rep.full.value
        return result

    def __general_report_to_str(self, r: _CocomoReport) -> str:
        writer = MarkdownTableWriter(
            table_name="Оценка трудоемкости и времени разработки",
            headers=["Описание", "Общая величина", "Полная величина"],
            value_matrix=[
                ["Трудоемкость",
                 round(r.w_r.general_value, 2),
                 round(r.w_r.full_value, 2)],
                ["Время разработки",
                 round(r.t_r.general_value, 2),
                 round(r.t_r.full_value, 2)]])
        return writer.dumps()

    def __traditional_cycle_report_to_str(self, r: _CocomoReport) -> str:
        writer = MarkdownTableWriter(
            table_name="Распределение работ и времени по стадиям жизненного цикла",
            headers=["Вид деятельности", "Трудозатраты(%)",
                     "Трудозатраты", "Время(%)", "Время"],
            value_matrix=[
                ["Планирование и определение требований",
                 round(r.tr_r.planning.work_coef, 2),
                 round(r.tr_r.planning.work_value, 2),
                 round(r.tr_r.planning.time_coef, 2),
                 round(r.tr_r.planning.time_value, 2)],
                ["Проектирование продукта",
                 round(r.tr_r.predesign.work_coef, 2),
                 round(r.tr_r.predesign.work_value, 2),
                 round(r.tr_r.predesign.time_coef, 2),
                 round(r.tr_r.predesign.time_value, 2)],
                ["Детальное проектирование",
                 round(r.tr_r.design.work_coef, 2),
                 round(r.tr_r.design.work_value, 2),
                 round(r.tr_r.design.time_coef, 2),
                 round(r.tr_r.design.time_value, 2)],
                ["Кодирование и тестирование отдельных модулей",
                 round(r.tr_r.programming.work_coef, 2),
                 round(r.tr_r.programming.work_value, 2),
                 round(r.tr_r.programming.time_coef, 2),
                 round(r.tr_r.programming.time_value, 2)],
                ["Интеграция и тестирование",
                 round(r.tr_r.testing.work_coef, 2),
                 round(r.tr_r.testing.work_value, 2),
                 round(r.tr_r.testing.time_coef, 2),
                 round(r.tr_r.testing.time_value, 2)],
                ["Итого",
                 round(r.tr_r.general.work_coef, 2),
                 round(r.tr_r.general.work_value, 2),
                 round(r.tr_r.general.time_coef, 2),
                 round(r.tr_r.general.time_value, 2)],
                ["Итого + планирование",
                 round(r.tr_r.full.work_coef, 2),
                 round(r.tr_r.full.work_value, 2),
                 round(r.tr_r.full.time_coef, 2),
                 round(r.tr_r.full.time_value, 2)]])
        return writer.dumps()

    def __wbs_report_to_str(self, r: _CocomoReport) -> str:
        writer = MarkdownTableWriter(
            table_name="Декомпозиция работ по видам деятельности WBS",
            headers=["Вид деятельности", "Бюджет(%)", "Человеко-Месяцы"],
            value_matrix=[
                ["Анализ требований",
                 round(r.wbs_r.analysis.coef, 2),
                 round(r.wbs_r.analysis.value, 2)],
                ["Проектирование продукта",
                 round(r.wbs_r.design.coef, 2),
                 round(r.wbs_r.design.value, 2)],
                ["Программирование",
                 round(r.wbs_r.programming.coef, 2),
                 round(r.wbs_r.programming.value, 2)],
                ["Тестирование",
                 round(r.wbs_r.testing.coef, 2),
                 round(r.wbs_r.testing.value, 2)],
                ["Верификация и аттестация",
                 round(r.wbs_r.verification.coef, 2),
                 round(r.wbs_r.verification.value, 2)],
                ["Канцелярия проекта",
                 round(r.wbs_r.documents.coef, 2),
                 round(r.wbs_r.documents.value, 2)],
                ["Управление конфигурацией и QA",
                 round(r.wbs_r.configuration.coef, 2),
                 round(r.wbs_r.configuration.value, 2)],
                ["Создание руководств",
                 round(r.wbs_r.manual_creation.coef, 2),
                 round(r.wbs_r.manual_creation.value, 2)],
                ["Итого",
                 round(r.wbs_r.full.coef, 2),
                 round(r.wbs_r.full.value, 2)]])
        return writer.dumps()

    def __workers_report_to_str(self, r: _CocomoReport) -> str:
        writer = MarkdownTableWriter(
            table_name="Распределение количества рабочих по этапам жизненного цикла ПО",
            headers=["Этап", "Количество"],
            value_matrix=[
                ["Планирование и определение требований",
                 round(r.workers_r.planning, 2)],
                ["Проектирование продукта",
                 round(r.workers_r.predesign, 2)],
                ["Детальное проектирование",
                 round(r.workers_r.design, 2)],
                ["Кодирование и тестирование отдельных модулей",
                 round(r.workers_r.programming, 2)],
                ["Интеграция и тестирование",
                 round(r.workers_r.testing, 2)]])
        return writer.dumps()
