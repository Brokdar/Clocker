"""Module for generating a PDF report"""
import ctypes
from calendar import Calendar
from datetime import date
from pathlib import Path
from typing import Optional, Tuple, Union

from fpdf import FPDF

from clocker import converter
from clocker.model import AbsenceType, WorkDay
from clocker.statistics import StatisticHandler


class Reporter:
    """Class for generating PDF reports"""

    def __init__(self, out: str, statistic: StatisticHandler):
        self.__stats = statistic
        self.__out = Path(out)
        self.__primary_color = (29, 30, 73)
        self.__secondary_color = (125, 196, 234)

    def generate(self, month: int, year: int, data: list[WorkDay]):
        """Generate a PDF report for the given month and year.\n
        self.__out/{month}-{year}_ClockerReport.pdf

        Args:
            month (int): month of the report
            year (int): year of the report
            data (list[WorkDay]): all workday records for the given month and year
        """

        pdf = FPDF()
        pdf.add_page()

        pdf.set_title(f'Monthly Report - {month:02}/{year}')
        pdf.set_author(_get_windows_username())

        self.__create_title_banner(pdf, month, year)
        self.__create_month_overview(pdf, month, year,
                                     [day for day in data if day.date.month == month and day.date.year == year])

        statistics = self.__stats.collect(data)
        text = ' | '.join([
            f'Vacation Days {statistics.count.vacation}/{statistics.accessable_vacation_days} ({statistics.accessable_vacation_days - statistics.count.vacation})',  # pylint: disable = line-too-long
            f'Flex Days {statistics.count.flex}',
            f'Sick Days {statistics.count.sick}',
            f'Flextime {converter.delta_to_str(statistics.flextime)}'
        ])

        pdf.ln(10)
        pdf.set_text_color(*self.__primary_color)
        pdf.set_font('helvetica', size=11, style='')
        pdf.cell(pdf.epw, txt=text, ln=1, align='C')

        if not self.__out.exists():
            self.__out.mkdir(parents=True, exist_ok=True)

        path = self.__out.joinpath(f'{month:02}-{year}_ClockerReport.pdf')
        pdf.output(path)

    def __create_title_banner(self, pdf: FPDF, month: int, year: int):
        pdf.set_fill_color(*self.__primary_color)
        coords = [(70, 0), (pdf.w, 0), (pdf.w, 30), (45, 30)]
        pdf.polygon(coords, True)
        pdf.image('docs/img/logo.png', x=7, y=0, w=30, h=30)

        pdf.set_font("helvetica", "B", 24)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(w=pdf.epw, txt='Monthly Report', ln=1, align='C')

        pdf.set_font(size=16, style='I')
        pdf.cell(w=pdf.epw, h=10, txt=f'{month:02}/{year}', ln=1, align='C')
        pdf.ln(20)

    def __create_month_overview(self, pdf: FPDF, month: int, year: int, data: list[WorkDay]):
        pdf.set_text_color(99, 99, 99)
        pdf.set_font('Courier', size=9)
        pdf.cell(pdf.epw, txt='[W]orkday, [V]acation, [F]lexday, [S]ick, [H]oliday', ln=15, align='L')
        pdf.ln(3)

        header = ['Date', 'Type', 'Start', 'End', 'Pause', 'Duration', 'Flextime']
        col_width = pdf.epw / len(header)

        pdf.set_text_color(0, 0, 0)
        pdf.set_fill_color(*self.__secondary_color)
        pdf.set_font('helvetica', size=10, style='B')
        line_height = pdf.font_size * 2
        for col_name in header:
            pdf.cell(col_width, line_height, col_name, border=1, align='C', fill=True)
        pdf.ln(line_height)

        pdf.set_font(size=9, style="")
        line_height = pdf.font_size * 2

        cal = Calendar()
        idx = 0
        for day in cal.itermonthdates(year, month):
            if day.month != month or day.year != year:
                continue

            if idx < len(data) and day == data[idx].date:
                self.__add_row(pdf, data[idx])
                idx += 1
            else:
                self.__add_row(pdf, day)

            pdf.ln(line_height)

    def __add_row(self, pdf: FPDF, data: Union[date, WorkDay]):
        if isinstance(data, date):
            background_color = (255, 255, 255)
            if data.weekday() >= 5:
                background_color = (235, 235, 235)

            _add_cell(pdf, data.strftime('%d.%m.%Y'), background=background_color)
            _add_cell(pdf, background=background_color)
            _add_cell(pdf, background=background_color)
            _add_cell(pdf, background=background_color)
            _add_cell(pdf, background=background_color)
            _add_cell(pdf, background=background_color)
            _add_cell(pdf, background=background_color)
        else:
            _add_cell(pdf, data.date.strftime('%d.%m.%Y'))
            _add_cell(pdf, converter.enum_to_abbreviation(data.absence))

            if data.absence != AbsenceType.WORKDAY:
                _add_cell(pdf)
                _add_cell(pdf)
                _add_cell(pdf)
                _add_cell(pdf)
                _add_cell(pdf)
            else:
                _add_cell(pdf, converter.time_to_str(data.begin) if data.begin is not None else None)
                _add_cell(pdf, converter.time_to_str(data.end) if data.end is not None else None)
                _add_cell(pdf, converter.delta_to_str(data.pause))
                _add_cell(pdf, converter.delta_to_str(data.duration))
                _add_cell(pdf, converter.delta_to_str(self.__stats.flextime(data)))


def _add_cell(pdf: FPDF, data: Optional[str] = None, align: str = 'C', background: Tuple = (255, 255, 255)):
    height = pdf.font_size * 2
    width = pdf.epw / 7

    pdf.set_fill_color(*background)
    pdf.cell(width, height, data if data is not None else '', border=1, align=align, fill=True)


def _get_windows_username() -> str:
    get_user_name_ex = ctypes.windll.secur32.GetUserNameExW
    name_display = 3

    size = ctypes.pointer(ctypes.c_ulong(0))
    get_user_name_ex(name_display, None, size)

    name_buffer = ctypes.create_unicode_buffer(size.contents.value)
    get_user_name_ex(name_display, name_buffer, size)
    return name_buffer.value
