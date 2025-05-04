# from win32 import win32api
import datetime
import getpass
import os
import pathlib
import pickle
import sqlite3

# from PyQt5.QtWidgets import QApplication , QMainWindow
# from PyQt5.QtChart import QChart, QPieSeries ,QPieSlice
import sys
import threading
import webbrowser
import winreg
from datetime import date, timedelta
from sqlite3 import Error
from time import sleep, time

import psutil
import pythoncom

# for shortcut in startup
import win32com.client
import win32gui
import win32process

# from PyQt5.QtWidgets import *
# from PyQt5.QtGui import *
from PyQt5.Qt import Qt
from PyQt5.QtChart import (
    QBarCategoryAxis,
    QBarSet,
    QChart,
    QChartView,
    QHorizontalStackedBarSeries,
    QPieSeries,
    QPieSlice,
)
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QBrush, QColor, QIcon, QPainter
from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QMainWindow,
    QMenu,
    QSystemTrayIcon,
    QVBoxLayout,
    QWidget,
)
from PyQt5.uic import loadUi

import constants
from utilFunctions import *

# from PyQt5 import # QtWidgets # uic #, #QtChart  #QtGui #QtCore


# from PyQt5 import *
# from PyQt5.Qt import *


previousWindow = ""
currentWindow = ""
activeTime = 0
seconds_elapsed = 0
end_time = time()
start_time = time()

package_dir = os.path.abspath(os.path.dirname(__file__))
db_dir = os.path.join(package_dir, constants.db_name)

db_name = db_dir
full_name_current = ""
full_name_previous = ""
isShown = True

current_date = datetime.date.today()


# pause on error
# TODO send traceback to server
def myexcepthook(type, value, traceback, oldhook=sys.excepthook):
    oldhook(type, value, traceback)
    input(
        "Error occurred please send a mail to developer or using contact us!.Press Enter to exit."
    )


sys.excepthook = myexcepthook


def create_database(db_file):
    """create a database connection to a SQLite database"""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        # print(sqlite3.version)
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()


def create_table(table_name):
    global db_name
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    table_command = """
    CREATE TABLE {tableName} (
        uid TEXT PRIMARY KEY,
        programName TEXT NOT NULL,
        usageTime REAL NOT NULL,
        FullName TEXT,
        timeStamp timestamp NOT NULL)
     """.format(
        tableName=table_name
    )

    cur.execute(table_command)
    con.close()
    print("table created")


def dict_factory(cursor, row):
    d = {}
    # print (str(cursor.description))
    for usageTime, col in enumerate(cursor.description):
        d[col[0]] = row[usageTime]
    return d


def get_todays_entries():
    global db_name, current_date

    # get days entries in hashmap , dict

    # query = """ SELECT  * FROM {name} WHERE timeStamp = date('{date}') """.format(name = current_table_name(),date=current_date)
    query = """ SELECT  * FROM {name} WHERE strftime('%Y-%m-%d', timeStamp) == date('{date}') """.format(
        name=current_table_name(), date=current_date
    )

    con = sqlite3.connect(db_name)
    con.row_factory = dict_factory
    cur = con.cursor()
    cur.execute(query)
    dict_list = cur.fetchall()

    con.commit()
    con.close()

    # cleaning dict list

    # simple_dict = {}

    # for item in dict_list:

    #     name = item.get('programName')
    #     timetaken = item.get('usageTime')
    #     simple_dict[name] = timetaken

    # print (dict_list)

    # convert to percentage and readable time

    total_seconds = 0.0

    for item in dict_list:
        if len(item.get("programName")) > 0:
            total_seconds = total_seconds + item.get("usageTime")

    # print (int(total_seconds))

    complete_dict = {}

    for item in dict_list:
        timeUsage = item.get("usageTime")
        # add time , percentage , time readable , program description
        percentage = float("{:.1f}".format(100.0 * timeUsage / total_seconds))
        program_full_name = item.get("FullName")
        readable_time = getTime(timeUsage)

        program = item.get("programName")

        # remove empty entires
        if len(program) > 0:
            # add only if percentage is greater than 3%
            if percentage >= 3:
                complete_dict[program] = [
                    timeUsage,
                    percentage,
                    readable_time,
                    program_full_name,
                ]

    if current_date != datetime.date.today():
        if len(dict_list) == 0:
            complete_dict["isEmpty"] = [getTime(total_seconds)]

    complete_dict["total_time_today"] = [getTime(total_seconds)]

    return complete_dict


def contact_us_fun():
    # open web page
    # will do as website is made
    print("contact_us_fun")
    webbrowser.open(constants.contact_url, new=0, autoraise=True)


# Needed for Wayland applications
# os.environ["QT_QPA_PLATFORM"] = "xcb"
# Change the current dir to the temporary one created by PyInstaller
try:
    os.chdir(sys._MEIPASS)
    print(sys._MEIPASS)
except:
    pass


def suffix(d):
    return "th" if 11 <= d <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(d % 10, "th")


def custom_strftime(format, t):
    return t.strftime(format).replace("{S}", str(t.day) + suffix(t.day))


class MainWindow(QMainWindow):

    def closeEvent(self, event):
        global isShown
        # do stuff
        event.ignore()

        # hide window
        self.hide()
        isShown = False

    def onRefresh(self, event):

        # complete_dict[program] = [timeUsage,percentage,readable_time,program_full_name]
        main_dict = get_todays_entries()

        # print(str(main_dict))

        # changing the background color
        # self.setStyleSheet("background-color: #363636;")
        # setStyleSheet("font-family: Arial;font-style: bold;font-size: 15pt")

        # set the title
        # self.setWindowTitle("Screen Time")

        # self.graphWidget = pg.PlotWidget()
        # self.setCentralWidget(self.graphWidget)

        series = QPieSeries()
        series.setHoleSize(0.55)
        series.setLabelsVisible(False)

        for key in main_dict:

            slice = QPieSlice()

            lst = main_dict[key]
            # print(str(len(lst)))
            if len(lst) > 1 and int(lst[1]) > 0:
                slice = series.append(
                    "<font size=4> <p style='text-align:center;'> "
                    + lst[3]
                    + " <b>"
                    + str(int(lst[1]))
                    + "%"
                    + "</b></p></font>",
                    lst[1],
                )
                slice.setLabelVisible()
                slice.setLabelArmLengthFactor(0.15)

        # series.append("Example1 30%",30.0)

        chart = QChart()
        chart.addSeries(series)

        chart.setTitle(
            "<font size=4> <p style='text-align:center;'> Usage Time </p></font>"
        )

        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setTheme(QChart.ChartThemeDark)
        # chart.animation

        chart.setBackgroundBrush(QBrush(QColor("transparent")))
        chart.legend().setVisible(True)
        chartview = QChartView(chart)
        chartview.setRenderHint(QPainter.Antialiasing)
        chartview

        # self.pie_chart_container.setStyleSheet("background-color: #363636;")

        QWidget().setLayout(self.pie_chart_container.layout())

        self.pie_chart_container.setContentsMargins(0, 0, 0, 0)
        lay = QHBoxLayout(self.pie_chart_container)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(chartview)

        # todays total usage
        self.Todat_total_usage_num.setText(main_dict.get("total_time_today")[0])

        # most used program
        mst_usd_program = ""
        mst_time = 0
        for key in main_dict:
            lst = main_dict[key]
            if len(lst) > 1 and int(lst[1]) > 0:
                # print("lst[0]="+str(int(lst[0]))+" mst_time=${mst_time}" )
                if int(lst[0]) > mst_time:
                    mst_time = int(lst[0])
                    mst_usd_program = lst[3]
                    # print(mst_usd_program)

        self.most_used_program_num.setText(mst_usd_program)
        self.most_used_program_time.setText(getTime(mst_time))

        # adding horizontal graph
        set0 = QBarSet("<font size=4> Time </font>")

        try:
            del main_dict["total_time_today"]
        except:
            pass

        # print(sorted(main_dict.items(),
        # key=lambda e: int((e[1])[0] ),reverse=True ) )

        # sorting the dict desc
        sorted_main_dict = dict(
            sorted(main_dict.items(), key=lambda e: int((e[1])[0]), reverse=False)
        )

        # print(str(sorted_main_dict))

        for key in sorted_main_dict:
            lst = sorted_main_dict[key]
            # remove total time and 0%
            if len(lst) > 1 and int(lst[1]) > 0.5:
                set0.append(int(lst[1]))

        series = QHorizontalStackedBarSeries()

        series.append(set0)

        chart = QChart()
        chart.addSeries(series)

        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setTheme(QChart.ChartThemeDark)

        # software name ,time on side
        axisY = QBarCategoryAxis()

        for key in sorted_main_dict:
            lst = sorted_main_dict[key]
            # remove total time and 0%
            if len(lst) > 1 and int(lst[1]) > 0.5:
                axisY.append(
                    "<font size=4>  <p style='text-align:right;'> "
                    + lst[3]
                    + "<br/>"
                    + lst[2]
                    + "</p></font>"
                )

        chart.addAxis(axisY, Qt.AlignLeft)
        series.attachAxis(axisY)

        # axisX = QtChart.QValueAxis()
        # chart.addAxis(axisX, Qt.AlignBottom)
        # series.attachAxis(axisX)
        # axisX.applyNiceNumbers()

        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)

        # chart background transparent
        chart.setBackgroundBrush(QBrush(QColor("transparent")))
        chart.legend().setVisible(True)

        chartview = QChartView(chart)
        chartview.setRenderHint(QPainter.Antialiasing)

        # self.bar_graph.setStyleSheet("background-color: #363636;")

        QWidget().setLayout(self.bar_graph.layout())

        self.bar_graph.setContentsMargins(0, 0, 0, 0)
        lay = QHBoxLayout(self.bar_graph)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(chartview)

        self.bar_graph.repaint()

        current_date_txt = custom_strftime("{S} %B", current_date)
        self.date_text.setText(current_date_txt)

        main_dict = get_todays_entries()
        today_time = main_dict.get("total_time_today")[0]
        # print(main_dict)
        if today_time != "0":
            # self.loading_1.setVisible(False)
            # self.loading_2.setVisible(False)
            self.comeback.setVisible(False)

        # get is empty from database if isEmpty than show no data
        # available text box
        isEmpty = main_dict.get("isEmpty")
        if isEmpty != None:
            self.comeback.setVisible(True)
            self.comeback.setText("No Data Available !!")
        else:
            self.comeback.setVisible(False)

    def changeDate(self, goto):
        global current_date
        # if 1 than left(before) if 0 than right(after)
        if goto == 1:
            # print("change left")
            # if(current_date != datetime.date.today() - timedelta(days = 7)):
            current_date = current_date - timedelta(days=1)
            main_window.onRefresh(main_window)

        if goto == 0:
            # print("change right")
            if current_date != datetime.date.today():
                current_date = current_date + timedelta(days=1)
                main_window.onRefresh(main_window)

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # Load the UI Page
        THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
        my_file = os.path.join(THIS_FOLDER, "main.ui")

        # get ui from string
        # f = io.StringIO(ui_file)

        # ui_file_name = "main.ui"
        # ui_file = QFile(ui_file_name)
        # if not ui_file.open(QIODevice.ReadOnly):
        #     print(f"Cannot open {ui_file_name}: {ui_file.errorString()}")
        #     sys.exit(-1)

        # uic.loadUi(f, self)

        loadUi(my_file, self)

        # complete_dict[program] = [timeUsage,percentage,readable_time,program_full_name]
        main_dict = get_todays_entries()

        # print(str(main_dict))

        # changing the background color
        self.setStyleSheet("background-color: #363636;")
        # setStyleSheet("font-family: Arial;font-style: bold;font-size: 15pt")

        # set the title
        self.setWindowTitle("Screen Time")

        self.setWindowIcon(QIcon("systray.png"))

        # self.graphWidget = pg.PlotWidget()
        # self.setCentralWidget(self.graphWidget)

        # set window size fixed
        width = self.frameGeometry().width()
        height = self.frameGeometry().height()
        # setting  the fixed size of window
        self.setFixedSize(width, height)

        series = QPieSeries()
        series.setHoleSize(0.55)
        series.setLabelsVisible(False)

        for key in main_dict:

            slice = QPieSlice()

            lst = main_dict[key]
            # print(str(len(lst)))
            if len(lst) > 1 and int(lst[1]) > 0:
                slice = series.append(
                    "<font size=4> <p style='text-align:center;'> "
                    + lst[3]
                    + " <b>"
                    + str(int(lst[1]))
                    + "%"
                    + "</b></p></font>",
                    lst[1],
                )
                slice.setLabelVisible()
                slice.setLabelArmLengthFactor(0.15)

        # series.append("Example1 30%",30.0)

        chart = QChart()
        chart.addSeries(series)

        chart.setTitle(
            "<font size=4> <p style='text-align:center;'> Usage Time </p></font>"
        )

        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setTheme(QChart.ChartThemeDark)
        # chart.animation

        chart.setBackgroundBrush(QBrush(QColor("transparent")))
        chart.legend().setVisible(True)
        chartview = QChartView(chart)
        chartview.setRenderHint(QPainter.Antialiasing)
        chartview

        self.pie_chart_container.setStyleSheet("background-color: #363636;")

        self.pie_chart_container.setContentsMargins(0, 0, 0, 0)
        lay = QHBoxLayout(self.pie_chart_container)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(chartview)

        # todays total usage
        self.Todat_total_usage_num.setText(main_dict.get("total_time_today")[0])

        # most used program
        mst_usd_program = ""
        mst_time = 0
        for key in main_dict:
            lst = main_dict[key]
            if len(lst) > 1 and int(lst[1]) > 0:
                # print("lst[0]="+str(int(lst[0]))+" mst_time=${mst_time}" )
                if int(lst[0]) > mst_time:
                    mst_time = int(lst[0])
                    mst_usd_program = lst[3]
                    # print(mst_usd_program)

        self.most_used_program_num.setText(mst_usd_program)
        self.most_used_program_time.setText(getTime(mst_time))

        # adding horizontal graph
        set0 = QBarSet("<font size=4> Time </font>")

        try:
            del main_dict["total_time_today"]
        except:
            pass

        # print(sorted(main_dict.items(),
        # key=lambda e: int((e[1])[0] ),reverse=True ) )

        # sorting the dict desc
        sorted_main_dict = dict(
            sorted(main_dict.items(), key=lambda e: int((e[1])[0]), reverse=False)
        )

        # print(str(sorted_main_dict))

        for key in sorted_main_dict:
            lst = sorted_main_dict[key]
            # remove total time and 0%
            if len(lst) > 1 and int(lst[1]) > 0.5:
                set0.append(int(lst[1]))

        series = QHorizontalStackedBarSeries()

        series.append(set0)

        chart = QChart()
        chart.addSeries(series)

        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setTheme(QChart.ChartThemeDark)

        # software name ,time on side
        axisY = QBarCategoryAxis()

        for key in sorted_main_dict:
            lst = sorted_main_dict[key]
            # remove total time and 0%
            if len(lst) > 1 and int(lst[1]) > 0.5:
                axisY.append(
                    "<font size=4>  <p style='text-align:right;'> "
                    + lst[3]
                    + "<br/>"
                    + lst[2]
                    + "</p></font>"
                )

        chart.addAxis(axisY, Qt.AlignLeft)
        series.attachAxis(axisY)

        # axisX = QtChart.QValueAxis()
        # chart.addAxis(axisX, Qt.AlignBottom)
        # series.attachAxis(axisX)
        # axisX.applyNiceNumbers()

        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)

        # chart background transparent
        chart.setBackgroundBrush(QBrush(QColor("transparent")))
        chart.legend().setVisible(True)

        chartview = QChartView(chart)
        chartview.setRenderHint(QPainter.Antialiasing)

        self.bar_graph.setStyleSheet("background-color: #363636;")

        self.bar_graph.setContentsMargins(0, 0, 0, 0)
        lay = QHBoxLayout(self.bar_graph)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(chartview)

        self.refresh_button.clicked.connect(self.onRefresh)
        self.refresh_button.setIcon(QIcon("refresh.png"))
        self.refresh_button.setIconSize(QSize(30, 30))
        self.refresh_button.setStyleSheet("background-color: rgba(0, 0, 0, 0);")

        # contact us button
        self.contact_button.clicked.connect(contact_us_fun)

        # arrow buttons
        self.button_left.clicked.connect(lambda: self.changeDate(1))
        self.button_left.setIcon(QIcon("left_arrow.png"))
        self.button_left.setIconSize(QSize(30, 30))
        layout = QVBoxLayout(self)
        layout.addWidget(self.button_left)
        self.button_left.setStyleSheet("background-color: rgba(0, 0, 0, 0);")

        self.button_right.clicked.connect(lambda: self.changeDate(0))
        self.button_right.setIcon(QIcon("right_arrow.png"))
        self.button_right.setIconSize(QSize(30, 30))
        layout = QVBoxLayout(self)
        layout.addWidget(self.button_right)
        self.button_right.setStyleSheet("background-color: rgba(0, 0, 0, 0);")

        current_date_txt = custom_strftime("{S} %B", current_date)
        self.date_text.setText(current_date_txt)

        # hide loading if data is there
        main_dict = get_todays_entries()
        today_time = main_dict.get("total_time_today")[0]
        if today_time != "0":
            # self.loading_1.setVisible(False)
            # self.loading_2.setVisible(False)
            self.comeback.setVisible(False)


def checkDBandTable():
    global db_name

    con = sqlite3.connect(db_name)

    # checking database
    if not (os.path.isfile(db_name)):
        print("creating database")
        try:
            create_database(db_name)
        except:
            print("error creating databases")

    # commit the changes to db
    con.commit()
    # close the connection
    con.close()
    # checking table

    con = sqlite3.connect(db_name)

    c = con.cursor()
    # get the count of tables with the name
    c.execute(
        """ SELECT count(name) FROM sqlite_master  WHERE type ='table' AND name ='{tableName}' """.format(
            dbName=db_name, tableName=current_table_name()
        )
    )

    # if the count is 1, then table exists
    if c.fetchone()[0] == 1:
        print("Table exists.")

    else:
        print("creating table .")
        try:
            create_table(current_table_name())

        except BaseException as e:
            print("error creating table")
            print(str(e))

    # commit the changes to db
    con.commit()
    # close the connection
    con.close()


def shouldPrint():
    return False


def printSoftwareInfo():
    return False


# start program on startup
def addToReg():
    try:
        ##get current file path
        package_dir = os.path.abspath(os.path.dirname(__file__))
        file_dir = os.path.join(package_dir, constants.software_name + ".exe")
        print(package_dir)
        print(file_dir)

        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE,
        )
        winreg.SetValueEx(key, "speed", 0, winreg.REG_SZ, file_dir)
        # file_path is path of file
        print("add exe in regex successful")

    except Exception as e:
        print("Error to add exe in regex moreinfo=" + str(e))


userhome = os.path.expanduser("~")
name = os.path.split(userhome)[-1]
USER_NAME = name


# add program to startup folder
def add_to_startup():

    # file_path = os.path.dirname(os.path.realpath(__file__))
    # print(file_path)
    package_dir = os.path.abspath(os.path.dirname(__file__))
    file_path = os.path.join(package_dir, constants.software_name + ".exe")

    #     #C:\Users\Rohan\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup
    # bat_path = r'C:\Users\%s\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup' % USER_NAME
    # with open(bat_path + '\\' + "screentime.bat", "w+") as bat_file:
    #     bat_file.write(r'start "" "%s"' % file_path)
    # print("add to startup successful")

    startup_path = (
        r"C:\Users\%s\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup"
        % USER_NAME
    )
    icon_path = os.path.join(package_dir, "icon.ico")
    shortcut_name = os.path.join(startup_path, "Screentime.lnk")

    # Check if shortcut already exists
    if not os.path.exists(shortcut_name):
        print(f"Creating startup shortcut: {shortcut_name}")
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcut_name)
        shortcut.Targetpath = file_path
        shortcut.IconLocation = icon_path
        shortcut.WindowStyle = 7  # 7 - Minimized, 3 - Maximized, 1 - Normal
        shortcut.save()
        print("Startup shortcut created.")
    else:
        print(f"Startup shortcut already exists: {shortcut_name}")


# check if program is already running
def check_exe_exist():
    # exist = "Code.exe" in (p.name() for p in psutil.process_iter())
    # print("exist %s" % exist)
    already_running = 0
    for p in psutil.process_iter(["pid", "name", "username"]):
        # print(p.info["name"])
        if constants.software_name + ".exe" == p.info["name"]:
            already_running = already_running + 1
    if already_running > 1:
        sys.exit()
    print(already_running)


def updateDatabase(program, time_taken, full_name, db_name):

    if shouldPrint:
        print("updating table")

    # creating unique id for today
    # name_day_month_year

    current_date = date.today()
    year = str(current_date.year)
    month = str(current_date.month)
    day = str(current_date.day)

    uid = program + "_" + day + "_" + month + "_" + year
    timestamp = datetime.datetime.now()

    # insert if not exist or update if already exist
    # INSERT OR IGNORE INTO my_table (name, age) VALUES ('Karen', 34)
    #    uid TEXT PRIMARY KEY,
    #    programName TEXT NOT NULL,
    #    usageTime REAL NOT NULL,
    #    timestamp TEXT NOT NULL)

    try:

        con = sqlite3.connect(db_name)
        c = con.cursor()
        c.execute(
            """ INSERT OR IGNORE INTO {tableName} (uid,programName,usageTime,FullName,timeStamp)  VALUES ('{uid}','{programName}',{usageTime},'{FullName}','{timestamp}') """.format(
                uid=uid,
                programName=program,
                usageTime=time_taken,
                FullName=full_name,
                timestamp=timestamp,
                tableName=current_table_name(),
            )
        )

        c.execute(
            """ UPDATE {tableName} SET usageTime = usageTime + {usageTime}  WHERE uid ='{uid}'  """.format(
                uid=uid,
                programName=program,
                usageTime=time_taken,
                FullName=full_name,
                timestamp=timestamp,
                tableName=current_table_name(),
            )
        )

        # commit the changes to db
        con.commit()
        # close the connection
        con.close()

        if shouldPrint():
            print("added to database")

    except:

        if shouldPrint():
            print("updating table failed")
        # print('updating table failed') if shouldPrint()


def active_window_process_name():

    global previousWindow, currentWindow, end_time, start_time, seconds_elapsed, db_name, full_name_current, full_name_previous
    # This produces a list of PIDs active window relates to
    pid = win32process.GetWindowThreadProcessId(win32gui.GetForegroundWindow())

    # pid[-1] is the most likely to survive last longer
    currentWindow = psutil.Process(pid[-1]).name()

    # print( "file description "+ getFileDescription(psutil.Process(pid[-1]).as_dict().get("exe")) )

    full_name_current = getFileDescription(psutil.Process(pid[-1]).as_dict().get("exe"))

    if previousWindow != currentWindow:
        end_time = time()
        seconds_elapsed = end_time - start_time
        if printSoftwareInfo():
            print(
                previousWindow
                + " time taken ="
                + str(float("{:.2f}".format(seconds_elapsed)))
            )

        # update db
        if len(previousWindow) > 0:
            updateThread = threading.Thread(
                target=updateDatabase,
                args=(
                    previousWindow,
                    float("{:.2f}".format(seconds_elapsed)),
                    full_name_previous,
                    db_name,
                ),
            )
            updateThread.start()
        # change current window
        previousWindow = currentWindow
        full_name_previous = full_name_current
        if printSoftwareInfo():
            print("changed to " + currentWindow)
        start_time = time()


# get description
# https://stackoverflow.com/questions/580924/how-to-access-a-files-properties-on-windows

# check if DB and table already exist
# do not remove from here
checkDBandTable()


app = QApplication(sys.argv)
main_window = MainWindow()


def showWindow(showWindow):
    global main_window, app, isShown
    print("showWindow =" + str(showWindow))
    isShown = showWindow
    if showWindow:
        main_window.show()
        # refresh window when opened
        main_window.onRefresh(main_window)

        # sys.exit(app.exec_())
    else:
        main_window.hide()
        # refresh window when closed
        # main_window.onRefresh(main_window)

    try:
        app.exec_()
    except Exception as e:
        print("app.exec_() error" + str(e))
        pass


# Adding an icon
icon = QSystemTrayIcon(QIcon("systray.png"), parent=app)
icon.setToolTip(constants.software_name)
icon.show()
# Adding item on the menu bar
# tray = QtWidgets.QSystemTrayIcon()
# tray.setIcon(icon)
# tray.setVisible(True)
# tray.setToolTip(constants.software_name)

# Creating the options

menu = QMenu()


def getButtonText():
    global isShown
    if isShown:
        return "Hide"
    else:
        return "Show"


def setState():
    global isShown

    # print("setState isShown ="+str(isShown))

    if isShown:
        showWindow(False)
    else:
        showWindow(True)


option1 = menu.addAction("Show / Hide")
option1.triggered.connect(setState)
# TODO SOLVE error addback
# menu.addAction(option1)

# To quit the app
quit = menu.addAction("Quit")
quit.triggered.connect(app.quit)
# menu.addAction(quit)

# on system tray icon click
icon.activated.connect(setState)

# Adding options to the System Tray
icon.setContextMenu(menu)


def main():
    # check if todays entries is empty
    main_dict = get_todays_entries()
    # print ("todays entries ="+str(get_todays_entries()))
    today_time = main_dict.get("total_time_today")[0]
    # set window is shown
    if today_time == "0":
        showWindow(False)
    else:
        showWindow(True)


def run_capture():
    isTrue = True

    while isTrue:
        # print(GetWindowText(GetForegroundWindow()))
        try:
            active_window_process_name()
        except BaseException as e:
            if printSoftwareInfo():
                print(str(e))
        sleep(0.3)


# t = threading.Thread(target=main)
# t.daemon = True
# t.start()

# def software_version_pickle():
#     file = open(constants.software_version_pickle_name, 'wb')
#     pickle.dump(constants.software_version,file)
#     file.close()

# def runUpdater():
#     print("updater")
#     # try:
#     #     os.startfile(constants.updater_name+".exe")
#     # except:
#     #     print("except updater 1")
#     try:
#         print('"'+str(pathlib.Path().resolve())+'\\updater\\'+constants.updater_name+'.exe"')
#         os.startfile('"'+str(pathlib.Path().resolve())+'\\updater\\'+constants.updater_name+'.exe"')
#         #os.system('"'+str(pathlib.Path().resolve())+'\\updater\\'+constants.updater_name+'.exe"')
#     except:
#         print("except updater 2")
#         pass
#         # pass

# add program to startup folder
# addToReg()

add_to_startup()
check_exe_exist()

# software_version_pickle()
# runUpdater()

t2 = threading.Thread(target=run_capture)
t2.daemon = True
t2.start()


sendToAnalytics()
main()
