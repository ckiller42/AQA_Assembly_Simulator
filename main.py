import multiprocessing
import sys
import os
import time
import py
import ctypes
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from subprocess import *


def setPic(holder: QLabel, file):
    try:
        pixmap = QPixmap(file)
        holder.setPixmap(pixmap)
        holder.resize(pixmap.width(), pixmap.height())
        return holder
    except:
        raise FileNotFoundError


class LineEdit(QTextEdit):
    # Text Box
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("Enter text here")
        self.setAlignment(Qt.AlignmentFlag.AlignTop)
        # Auto resizing
        self.textChanged.connect(self.autoResize)
        self.margins = self.contentsMargins()
        # Shortcut actions
        self.copy_action = QAction("Copy", self)
        self.copy_action.setStatusTip("Copy")
        self.copy_action.setShortcut(QKeySequence("Ctrl+c"))
        self.copy_action.triggered.connect(self.copyClicked)

        self.paste_action = QAction("Paste", self)
        self.paste_action.setStatusTip("Paste")
        self.paste_action.setShortcut(QKeySequence("Ctrl+v"))
        self.paste_action.triggered.connect(self.pasteClicked)

        self.cut_action = QAction("Cut", self)
        self.cut_action.setStatusTip("Cut")
        self.cut_action.setShortcut(QKeySequence("Ctrl+x"))
        self.cut_action.triggered.connect(self.cutClicked)

        self.zoom_in = QAction(QIcon("./icon/magnifier-zoom-in.png"), "Zoom in", self)
        self.zoom_in.setStatusTip("Zoom In")
        self.zoom_in.setShortcut(QKeySequence("Ctrl+="))
        self.zoom_in.triggered.connect(self.zoomIn)

        self.zoom_out = QAction(QIcon("./icon/magnifier-zoom-out.png"), "Zoom out", self)
        self.zoom_out.setStatusTip("Zoom Out")
        self.zoom_out.setShortcut(QKeySequence("Ctrl+-"))
        self.zoom_out.triggered.connect(self.zoomOut)

    def autoResize(self):
        self.document().setTextWidth(self.viewport().width())
        height = int(self.document().size().height() + self.margins.top() + self.margins.bottom())
        self.setFixedHeight(height)

    def resizeEvent(self, a0, QResizeEvent=None):
        self.autoResize()

    def contextMenuEvent(self, a0, QContextMenuEvent=None):
        context = QMenu(self)
        context.addAction(self.cut_action)
        context.addAction(self.copy_action)
        context.addAction(self.paste_action)
        context.exec(a0.globalPos())

    def copyClicked(self):
        text = self.toPlainText()
        QApplication.clipboard().setText(text)
        print(QApplication.clipboard().text())

    def pasteClicked(self):
        self.insertPlainText(QApplication.clipboard().text())

    def cutClicked(self):
        self.copyClicked()
        self.deleteLater()


class InsertTextDialog(QDialog):
    def __init__(self, title):
        super().__init__()
        self.setWindowTitle(title)
        self.__layout = QVBoxLayout()
        self.setLayout(self.__layout)
        self.__textbox = LineEdit()
        self.__layout.addWidget(self.__textbox)
        self.__textbox.textChanged.connect(self.__textChange)
        QBtn = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        self.__buttonbox = QDialogButtonBox(QBtn)
        self.__buttonbox.accepted.connect(self.accept)
        self.__buttonbox.rejected.connect(self.reject)
        self.__layout.addWidget(self.__buttonbox)

        self.text = ""

    def __textChange(self):
        self.text = self.__textbox.toPlainText()


class ShowTextWindow(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.__textLabel = QLabel()
        layout.addWidget(self.__textLabel)

    def setText(self, text):
        self.__textLabel.setText(text)


class PaginatedList(QWidget):
    def __init__(self):
        super().__init__()
        self._layout = QVBoxLayout()
        self.setLayout(self._layout)
        # Create the stacked widget containing each page
        self._stackWidget = QStackedWidget(parent=self)
        self._layout.addWidget(self._stackWidget)
        # Layout for the page numbers below the stacked widget
        self._pagination_layout = QHBoxLayout()
        self._pagination_layout.addStretch(0)
        self._layout.addLayout(self._pagination_layout)

    def switch_page(self, page):
        if int(page) > 26:
            MainWindow.PopMsgBox('Page Number Out of Index')
            return
        if page == "":
            self._stackWidget.setCurrentIndex(0)
        else:
            self._stackWidget.setCurrentIndex(int(page) - 1)

    def locate_on_screen(self, flag):
        # flag: 0 - topleft; 1 - topright
        qr = self.frameGeometry()
        cp = QGuiApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        if flag == 0:
            self.move(qr.topLeft())
        elif flag == 1:
            self.move(qr.topRight())


class ShowMemory(PaginatedList):
    change_signal = pyqtSignal((int, int))

    def __init__(self):
        super().__init__()
        self.setFixedSize(600, 600)
        self.locate_on_screen(1)
        self._pagination_layout.addWidget(QLabel("Page: "))
        self._pageInput = LineEdit()
        self._pagination_layout.addWidget(self._pageInput)
        self._goBtn = QPushButton("Go")
        self._goBtn.clicked.connect(lambda: self.switch_page(self._pageInput.toPlainText()))
        self._pagination_layout.addWidget(self._goBtn)
        # Line seperator
        self._lineSeperator = QFrame()
        self._lineSeperator.setMinimumWidth(1)
        self._lineSeperator.setFixedHeight(20)
        self._lineSeperator.setFrameShape(QFrame.Shape.HLine)
        self._lineSeperator.setFrameShadow(QFrame.Shadow.Sunken)
        self._lineSeperator.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        memaddr = 0
        for i in range(26):
            page = QWidget()
            layout = QVBoxLayout(page)
            for _ in range(20):
                if i == 25 and _ == 12:
                    break
                tmp = QLabelClickable(text=str(hex(memaddr) + ' '*20 + '0'*16), index=_+i*20)
                tmp.setCursor(Qt.CursorShape.PointingHandCursor)
                tmp.clicked.connect(self.doubleClicked)
                layout.addWidget(tmp)
                layout.addStretch(1)
                layout.addWidget(self._lineSeperator)
                memaddr += 1
            self._stackWidget.addWidget(page)

    def doubleClicked(self, status, addr):
        dlg = InsertTextDialog(f"New address value at {hex(addr)}")
        if dlg.exec():
            self.changeVal(addr, dlg.text)
            self.change_signal.emit(addr, int(dlg.text))

    def changeVal(self, memAddr, val):
        # memAddr is in decimal
        page = memAddr // 20
        item = memAddr % 20
        CurWidget = self._stackWidget.widget(page).layout().itemAt(item<<1).widget()
        # print(page,item,CurWidget)
        tmp = bin(int(val))[2:]
        tmp = (16 - len(tmp)) * "0" + tmp
        CurWidget.setText(hex(memAddr) + ' '*20 + tmp)


class ShowRegs(PaginatedList):
    # Don't have to do pagination. But rest properties are needed
    def __init__(self):
        super().__init__()
        self.setFixedSize(600, 600)
        self.locate_on_screen(0)
        self.__page = QWidget()
        self.__layout = QVBoxLayout(self.__page)
        self.__layout.addWidget(QLabel('PC' + ' '*20 + '0'*16))
        self.__layout.addStretch(1)
        self.__layout.addWidget(QLabel('IR' + ' '*20 + '0'*16))
        self.__layout.addStretch(1)
        self.__layout.addWidget(QLabel('MAR' + ' '*20 + '0'*16))
        self.__layout.addStretch(1)
        self.__layout.addWidget(QLabel('MDR' + ' '*20 + '0'*16))
        self.__layout.addStretch(1)
        for i in range(8):
            self.__layout.addWidget(QLabel('R' + str(i) + ' '*20 + '0'*16))
            self.__layout.addStretch(1)
        self._stackWidget.addWidget(self.__page)

    def changeVal(self, reg: str, val):
        if reg[0] == 'R':
            num = (int(reg[1]) << 1) + 8
            CurWidget = self.__layout.itemAt(num).widget()
        elif reg == 'PC':
            CurWidget = self.__layout.itemAt(0).widget()
        elif reg == 'IR':
            CurWidget = self.__layout.itemAt(2).widget()
        elif reg == 'MAR':
            CurWidget = self.__layout.itemAt(4).widget()
        elif reg == 'MDR':
            CurWidget = self.__layout.itemAt(6).widget()
        else:
            raise ValueError
        if val == -1:
            CurWidget.setText(reg + ' ' * 20 + str(val))
        else:
            CurWidget.setText(reg + ' ' * 20 + bin(val & 0xffff)[2:].rjust(16, '0'))


class QLabelClickable(QLabel):
    clicked = pyqtSignal((str, int))

    def __init__(self, parent=None, text="", index=-1):
        super().__init__(parent)
        self.setText(text)
        self.index = index
        self.status = ""

    def mousePressEvent(self, ev, QMouseEvent=None):
        self.status = "Click"

    def mouseReleaseEvent(self, ev, QMouseEvent=None):
        if self.status == "Click":
            QTimer.singleShot(QApplication.instance().doubleClickInterval(), self.performSingleClickAction)
        else:
            self.clicked.emit(self.status, self.index)

    def mouseDoubleClickEvent(self, *args, **kwargs):
        self.status = "Double Click"

    def performSingleClickAction(self):
        pass


class QRedLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color:red")

    def show(self, mode=0):
        super().show()
        # 0: execute; 1: fetch; 2: decode; 3: execute and fetch
        if mode == 1:
            self.setStyleSheet("background-color:yellow")
        elif mode == 2:
            self.setStyleSheet("background-color:blue")
        elif mode == 3:
            self.setStyleSheet("background-color:orange")


class QGreenLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color:green")


class CheckChangeThread(QThread):
    any_signal = pyqtSignal(int)

    def __init__(self, parent=None, index=0):
        super().__init__(parent)
        self.index = index
        self.is_running = True
        self.flag = 0

    def run(self):
        print("Starting Thread...", self.index)
        while True:
            time.sleep(0.05)
            if change_flag[0] == 1:
                print("[+] Change detected!")
                self.flag = 1
                self.any_signal.emit(self.flag)


    def stop(self):
        self.is_running = False
        self.flag = 0
        change_flag[0] = 0
        print("Stopping Thread...", self.index)
        self.terminate()


class MainWindow(QMainWindow):
    def __init__(self, reg_list, memory_list):
        super().__init__()
        self.setWindowTitle("Data Path Simulator")
        self.setMinimumSize(1200, 800)
        self.setStatusBar(QStatusBar(self))
        self.__widget = QWidget()
        self.setCentralWidget(self.__widget)
        # Mouse tracking on for showing value
        self.setMouseTracking(True)
        # Variables
        self.threading = {}
        self.reg_list = reg_list
        self.memory_list = memory_list
        self.__OrigFlag = False  # If start address set or not
        self.NowInstruct = ""
        self.__CntInstruct = 0
        self.__Opcode = ""
        self.__FromRegister = 0
        self.__ToRegister = 0
        self.__Operand = ""
        self.__Condition = ""
        self.__OperandMode = 0  # 0: Immediate;  1: Register
        self._style1 = [1, 2, 5, 11]
        self._style2 = [3, 4, 8, 9, 10, 12, 13]
        self.__registers = []
        self.__conditions = ['', 'EQ', 'NE', 'GT', 'LT']
        self.__OpcodeList = ['', 'LDR', 'STR', 'ADD', 'SUB', 'MOV', 'CMP', 'B', 'AND', 'ORR', 'EOR', 'MVN', 'LSL', 'LSR', 'HALT']
        # layouts
        self.__layout = QHBoxLayout()
        self.__ControlLayout = QVBoxLayout()
        self.__InstructionLayout = QHBoxLayout()
        self.__BtnLayout = QHBoxLayout()
        self.__CoreLayout = QVBoxLayout()
        self.__InstBtnLayout = QHBoxLayout()
        self.__widget.setLayout(self.__layout)
        # UI Components
        self.__toolbar = QToolBar("Main toolbar")
        self.__menu = self.menuBar()
        self.__mouseCoordinatesLabel = QLabel(self)
        self.__backgroundLabel = QLabel()
        self.__InstructionLabel = QLabel()
        self.__AddLabelBtn = QPushButton('Insert Label')
        self.__OpcodeOpts = QComboBox()
        self.__RdOpts = QComboBox()
        self.__RnOpts = QComboBox()
        self.__ConditionOpts = QComboBox()
        self.__OperandBox = LineEdit()
        self.__AddToTxtBtn = QPushButton('Add')
        self.__ClearBtn = QPushButton('Clear')
        self.__AssembleBtn = QPushButton('Assemble')
        self.__RunBtn = QPushButton('Run')
        self.__NextInstBtn = QPushButton('>')
        self.__DoneSimulateBtn = QPushButton('Done Simulation')
        self.__new_action = QAction(QIcon("./Icons/exclamation-white.png"), "New", self)
        # New Window
        self.__MachineCodeWin = ShowTextWindow()
        self.__OrigWin = InsertTextDialog("Set Start Address")
        self.__ShowMemWin = ShowMemory()
        self.__ShowRegWin = ShowRegs()
        # Labels for demonstration
        self.__DataBusLabel1 = QRedLabel(self)
        self.__DataBusLabel2 = QRedLabel(self)
        self.__DataBusLabel3 = QRedLabel(self)
        self.__InRegData = QRedLabel(self)
        self.__InRegCtrl = QGreenLabel(self)
        self.__SrcReg1 = QGreenLabel(self)
        self.__SrcReg2 = QGreenLabel(self)
        self.__RegToSrc = QRedLabel(self)
        self.__SrcMuxOut = QRedLabel(self)
        self.__SrcMuxCtrl = QGreenLabel(self)
        self.__RegOut = QRedLabel(self)
        self.__AluOutData = QRedLabel(self)
        self.__AluOutCtrl = QGreenLabel(self)
        self.__InMarData = QRedLabel(self)
        self.__InMarCtrl = QGreenLabel(self)
        self.__OutMar1 = QRedLabel(self)
        self.__OutMar2 = QRedLabel(self)
        self.__MemRWCtrl = QGreenLabel(self)
        self.__MemToMDR1 = QRedLabel(self)
        self.__MemToMDR2 = QRedLabel(self)
        self.__OutMDRData = QRedLabel(self)
        self.__OutMDRCtrl = QGreenLabel(self)
        self.__InMDRData = QRedLabel(self)
        self.__InMDRCtrl = QGreenLabel(self)
        self.__MDRToMem1 = QRedLabel(self)
        self.__MDRToMem2 = QRedLabel(self)
        self.__InIrData = QRedLabel(self)
        self.__InIrCtrl = QGreenLabel(self)
        self.__IrToNode = QRedLabel(self)
        self.__IrToSrcMuxSext1 = QRedLabel(self)
        self.__IrToSrcMuxSext2 = QRedLabel(self)
        self.__IrToSrcMuxSext3 = QRedLabel(self)
        self.__IrToSrcMuxSext4 = QRedLabel(self)
        self.__IrSextToSrcMux1 = QRedLabel(self)
        self.__IrSextToSrcMux2 = QRedLabel(self)
        self.__IrToFSMNode = QRedLabel(self)
        self.__FSMNodeMode = QRedLabel(self)
        self.__FSMNodeInst1 = QRedLabel(self)
        self.__FSMNodeInst2 = QRedLabel(self)
        self.__IrTo7Sext1 = QRedLabel(self)
        self.__IrTo7Sext2 = QRedLabel(self)
        self.__NodeTo8Sext = QRedLabel(self)
        self.__8SextToPcMux1 = QRedLabel(self)
        self.__8SextToPcMux2 = QRedLabel(self)
        self.__8SextToPcMux3 = QRedLabel(self)
        self.__7SextToAMux = QRedLabel(self)
        self.__AmuxCtrl = QGreenLabel(self)
        self.__OutAmuxData = QRedLabel(self)
        self.__OutAmuxCtrl = QGreenLabel(self)
        self.__InPcMux1 = QRedLabel(self)
        self.__InPcMux2 = QRedLabel(self)
        self.__InPcMux3 = QRedLabel(self)
        self.__PcMuxCtrl = QGreenLabel(self)
        self.__InPcData = QRedLabel(self)
        self.__InPcCtrl = QGreenLabel(self)
        self.__OutPcData = QRedLabel(self)
        self.__OutPcCtrl = QGreenLabel(self)
        self.__InPcPlus1 = QRedLabel(self)
        self.__InPcPlus2 = QRedLabel(self)
        self.__OutPcPlus1 = QRedLabel(self)
        self.__OutPcPlus2 = QRedLabel(self)
        self.__OutPcPlus3 = QRedLabel(self)
        self.__8SextToAMux1 = QRedLabel(self)
        self.__8SextToAMux2 = QRedLabel(self)
        self.__BusToLogic = QRedLabel(self)
        self.__EqLogic = QGreenLabel(self)
        self.__GtLogic = QGreenLabel(self)
        self.__EqToFSM1 = QGreenLabel(self)
        self.__EqToFSM2 = QGreenLabel(self)
        self.__GtToFSM1 = QGreenLabel(self)
        self.__GtToFSM2 = QGreenLabel(self)

        self.UISetUp()
        self.initAnimate()

        while not self.__OrigFlag:
            if self.__OrigWin.exec() and self.__OrigWin.text != "":
                self.__OrigFlag = True
                self.__Opcode = ".ORIG"
                self.__Operand = self.__OrigWin.text
                self.__AddInstruct()

    def UISetUp(self):
        self.__ClearAllInstruct(0)
        self.setStyleSheet("""
            QScrollBar:vertical{
                border: none;
                background-color: rgba(255, 255, 255, 0);
                width: 10px;
                margin: 0px 0px 0px 0px;
            }
        """)
        self.__NextInstBtn.hide()
        self.__DoneSimulateBtn.hide()
        # Animation labels setup
        self.__DataBusLabel1.setGeometry(359, 571-2, 654, 5)  # -15
        self.__DataBusLabel2.setGeometry(1007, 117-2, 5, 460)
        self.__DataBusLabel3.setGeometry(359, 117-2, 654, 5)
        self.__InRegData.setGeometry(908, 119-2, 3, 73)
        self.__InRegCtrl.setGeometry(917, 170-2, 24, 3)
        self.__SrcReg1.setGeometry(967, 311-2, 24, 3)
        self.__SrcReg2.setGeometry(837, 305-2, 18, 3)
        self.__RegToSrc.setGeometry(882, 342-2, 2, 31)
        self.__SrcMuxOut.setGeometry(864, 401-2, 2, 15)
        self.__SrcMuxCtrl.setGeometry(823, 390-2, 13, 3)
        self.__RegOut.setGeometry(945, 341-2, 2, 77)
        self.__AluOutData.setGeometry(911, 501-15, 2, 76)
        self.__AluOutCtrl.setGeometry(921, 560-15, 22, 3)
        self.__InMarData.setGeometry(735, 589-15, 2, 30)
        self.__InMarCtrl.setGeometry(745, 619-15, 22, 3)
        self.__OutMar1.setGeometry(735, 655-15, 2, 35)
        self.__OutMar2.setGeometry(681, 688-15, 56, 2)
        self.__MemRWCtrl.setGeometry(596, 624-15, 4, 20)
        self.__MemToMDR1.setGeometry(471, 689-15, 54, 2)
        self.__MemToMDR2.setGeometry(471, 662-15, 2, 30)
        self.__MDRToMem1.setGeometry(447, 656-15, 2, 56)
        self.__MDRToMem2.setGeometry(447, 710-15, 71, 2)
        self.__OutMDRData.setGeometry(471, 597-15, 2, 33)
        self.__OutMDRCtrl.setGeometry(481, 625-15, 20, 3)
        self.__InMDRData.setGeometry(447, 590-15, 2, 33)
        self.__InMDRCtrl.setGeometry(416, 612-15, 22, 3)
        self.__InIrData.setGeometry(515, 533-15, 2, 52)
        self.__InIrCtrl.setGeometry(525, 560-15, 22, 3)
        self.__IrToNode.setGeometry(515, 434-15, 2, 62)
        self.__IrToFSMNode.setGeometry(515, 432-15, 88, 2)
        self.__FSMNodeMode.setGeometry(603, 433-15, 88, 2)
        self.__FSMNodeInst1.setGeometry(603, 399-15, 2, 34)
        self.__FSMNodeInst2.setGeometry(603, 399-15, 88, 2)
        self.__IrToSrcMuxSext1.setGeometry(515, 392-15, 2, 41)
        self.__IrToSrcMuxSext2.setGeometry(515, 392-15, 138, 2)
        self.__IrToSrcMuxSext3.setGeometry(652, 335-15, 2, 58)
        self.__IrToSrcMuxSext4.setGeometry(652, 335-15, 61, 2)
        self.__IrSextToSrcMux1.setGeometry(746, 335-15, 105, 2)
        self.__IrSextToSrcMux2.setGeometry(850, 335-15, 2, 50)
        self.__IrTo7Sext1.setGeometry(408, 433-15, 108, 2)
        self.__IrTo7Sext2.setGeometry(408, 294-15, 2, 141)
        self.__NodeTo8Sext.setGeometry(408, 365-15, 23, 2)
        self.__8SextToPcMux1.setGeometry(461, 365-15, 67, 2)
        self.__8SextToPcMux2.setGeometry(526, 253-15, 2, 114)
        self.__8SextToPcMux3.setGeometry(526, 237-15, 2, 16)
        self.__7SextToAMux.setGeometry(410, 237-15, 2, 40)
        self.__AmuxCtrl.setGeometry(382, 221-15, 13, 3)
        self.__OutAmuxData.setGeometry(420, 136-15, 2, 79)
        self.__OutAmuxCtrl.setGeometry(392, 162-15, 22, 3)
        self.__InPcMux1.setGeometry(449, 136-15, 2, 110)
        self.__InPcMux2.setGeometry(449, 245-15, 66, 2)
        self.__InPcMux3.setGeometry(513, 237-15, 2, 9)
        self.__PcMuxCtrl.setGeometry(484, 222-15, 13, 3)
        self.__InPcData.setGeometry(527, 205-15, 2, 10)
        self.__InPcCtrl.setGeometry(507, 207-15, 13, 3)
        self.__OutPcData.setGeometry(528, 136-15, 2, 49)
        self.__OutPcCtrl.setGeometry(536, 144-15, 22, 3)
        self.__InPcPlus1.setGeometry(526, 166-15, 57, 2)
        self.__InPcPlus2.setGeometry(581, 166-15, 2, 23)
        self.__OutPcPlus1.setGeometry(581, 207-15, 2, 48)
        self.__OutPcPlus2.setGeometry(542, 253-15, 41, 2)
        self.__OutPcPlus3.setGeometry(542, 237-15, 2, 18)
        self.__8SextToAMux1.setGeometry(428, 253-15, 99, 2)
        self.__8SextToAMux2.setGeometry(428, 237-15, 2, 18)
        self.__BusToLogic.setGeometry(815, 545-15, 2, 40)
        self.__EqLogic.setGeometry(802, 527-15, 15, 14)
        self.__GtLogic.setGeometry(817, 527-15, 14, 14)
        self.__EqToFSM1.setGeometry(807, 466-15, 2, 61)
        self.__EqToFSM2.setGeometry(782, 466-15, 27, 2)
        self.__GtToFSM1.setGeometry(823, 457-15, 2, 70)
        self.__GtToFSM2.setGeometry(783, 457-15, 42, 2)
        # Labels
        self.__mouseCoordinatesLabel.setGeometry(10, 100, 250, 30)
        self.__backgroundLabel = setPic(self.__backgroundLabel, 'components/img/EPQ_Data_Path_Design_new.png')
        self.__OperandBox.setPlaceholderText("Type Operand Here")
        # Drop down list opts
        self.__OpcodeOpts.addItems(self.__OpcodeList)
        self.__ConditionOpts.addItems(self.__conditions)
        self.__ConditionOpts.hide()
        for i in range(12):
            self.__registers.append(str(i))
        self.__RnOpts.addItems(self.__registers)
        self.__RdOpts.addItems(self.__registers)
        # UI Signals
        self.__AddLabelBtn.clicked.connect(self.__insertLabel)
        self.__AddToTxtBtn.clicked.connect(self.__AddInstruct)
        self.__ClearBtn.clicked.connect(lambda: self.__ClearAllInstruct(1))
        self.__AssembleBtn.clicked.connect(self.__Assemble)
        self.__RunBtn.clicked.connect(self.__Run)
        self.__OperandBox.textChanged.connect(self.__OperandChange)
        self.__RdOpts.currentIndexChanged.connect(self.__RdChange)
        self.__RnOpts.currentIndexChanged.connect(self.__RnChange)
        self.__OpcodeOpts.currentIndexChanged.connect(self.__OpcodeChange)
        self.__ConditionOpts.currentIndexChanged.connect(self.__ConditionChange)
        self.__NextInstBtn.clicked.connect(self.__nextInst)
        self.__DoneSimulateBtn.clicked.connect(self.__doneSimulate)
        # Toolbar set up
        self.addToolBar(self.__toolbar)
        self.__new_action.setStatusTip("Help")
        self.__new_action.triggered.connect(self.help)
        self.__new_action.setShortcut(QKeySequence("Ctrl+/"))
        self.__toolbar.addAction(self.__new_action)
        # Menu bar
        file_menu = self.__menu.addMenu("File")
        file_menu.addAction(self.__new_action)
        # Layout
        self.__BtnLayout.addWidget(self.__AddToTxtBtn)
        self.__BtnLayout.addWidget(self.__ClearBtn)
        self.__BtnLayout.addWidget(self.__AssembleBtn)
        self.__InstructionLayout.addWidget(self.__OpcodeOpts)
        self.__InstructionLayout.addWidget(self.__RdOpts)
        self.__InstructionLayout.addWidget(self.__RnOpts)
        self.__InstructionLayout.addWidget(self.__ConditionOpts)
        self.__InstructionLayout.addWidget(self.__OperandBox)
        self.__ControlLayout.addWidget(QLabel("Instruction:"))
        self.__ControlLayout.addWidget(self.__InstructionLabel)
        self.__ControlLayout.addWidget(self.__AddLabelBtn)
        self.__ControlLayout.addLayout(self.__InstructionLayout)
        self.__ControlLayout.addLayout(self.__BtnLayout)
        self.__ControlLayout.addWidget(self.__RunBtn)
        self.__InstBtnLayout.addWidget(self.__NextInstBtn)
        self.__InstBtnLayout.addWidget(self.__DoneSimulateBtn)
        self.__CoreLayout.addWidget(self.__backgroundLabel)
        self.__CoreLayout.addLayout(self.__InstBtnLayout)
        self.__layout.addLayout(self.__ControlLayout)
        self.__layout.addLayout(self.__CoreLayout)

    def initAnimate(self):
        self.__DataBusLabel1.setHidden(True)
        self.__DataBusLabel2.setHidden(True)
        self.__DataBusLabel3.setHidden(True)
        self.__InRegData.setHidden(True)
        self.__InRegCtrl.setHidden(True)
        self.__SrcReg1.setHidden(True)
        self.__SrcReg2.setHidden(True)
        self.__RegToSrc.setHidden(True)
        self.__SrcMuxOut.setHidden(True)
        self.__SrcMuxCtrl.setHidden(True)
        self.__RegOut.setHidden(True)
        self.__AluOutData.setHidden(True)
        self.__AluOutCtrl.setHidden(True)
        self.__InMarData.setHidden(True)
        self.__InMarCtrl.setHidden(True)
        self.__OutMar1.setHidden(True)
        self.__OutMar2.setHidden(True)
        self.__MemRWCtrl.setHidden(True)
        self.__MemToMDR1.setHidden(True)
        self.__MemToMDR2.setHidden(True)
        self.__OutMDRData.setHidden(True)
        self.__OutMDRCtrl.setHidden(True)
        self.__InMDRData.setHidden(True)
        self.__InMDRCtrl.setHidden(True)
        self.__MDRToMem1.setHidden(True)
        self.__MDRToMem2.setHidden(True)
        self.__InIrData.setHidden(True)
        self.__InIrCtrl.setHidden(True)
        self.__IrToNode.setHidden(True)
        self.__IrToSrcMuxSext1.setHidden(True)
        self.__IrToSrcMuxSext2.setHidden(True)
        self.__IrToSrcMuxSext3.setHidden(True)
        self.__IrToSrcMuxSext4.setHidden(True)
        self.__IrSextToSrcMux1.setHidden(True)
        self.__IrSextToSrcMux2.setHidden(True)
        self.__IrToFSMNode.setHidden(True)
        self.__FSMNodeMode.setHidden(True)
        self.__FSMNodeInst1.setHidden(True)
        self.__FSMNodeInst2.setHidden(True)
        self.__IrTo7Sext1.setHidden(True)
        self.__IrTo7Sext2.setHidden(True)
        self.__NodeTo8Sext.setHidden(True)
        self.__8SextToPcMux1.setHidden(True)
        self.__8SextToPcMux2.setHidden(True)
        self.__8SextToPcMux3.setHidden(True)
        self.__7SextToAMux.setHidden(True)
        self.__AmuxCtrl.setHidden(True)
        self.__OutAmuxData.setHidden(True)
        self.__OutAmuxCtrl.setHidden(True)
        self.__InPcMux1.setHidden(True)
        self.__InPcMux2.setHidden(True)
        self.__InPcMux3.setHidden(True)
        self.__PcMuxCtrl.setHidden(True)
        self.__InPcData.setHidden(True)
        self.__InPcCtrl.setHidden(True)
        self.__OutPcData.setHidden(True)
        self.__OutPcCtrl.setHidden(True)
        self.__InPcPlus1.setHidden(True)
        self.__InPcPlus2.setHidden(True)
        self.__OutPcPlus1.setHidden(True)
        self.__OutPcPlus2.setHidden(True)
        self.__OutPcPlus3.setHidden(True)
        self.__8SextToAMux1.setHidden(True)
        self.__8SextToAMux2.setHidden(True)
        self.__BusToLogic.setHidden(True)
        self.__EqLogic.setHidden(True)
        self.__GtLogic.setHidden(True)
        self.__EqToFSM1.setHidden(True)
        self.__EqToFSM2.setHidden(True)
        self.__GtToFSM1.setHidden(True)
        self.__GtToFSM2.setHidden(True)

    @staticmethod
    def PopMsgBox(text):
        msg = QMessageBox()
        msg.setWindowTitle("Error")
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setText(text)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()

    def __insertLabel(self):
        dlg = InsertTextDialog("Insert Label")
        if dlg.exec():
            try:
                with open('records.txt', 'a+') as file:
                    file.write(dlg.text + ':\n')
                    self.__InstructionLabel.setText(self.__InstructionLabel.text() + dlg.text + ':\n')
            except FileNotFoundError:
                print("File Not Found!")

    def __OpcodeChange(self):
        self.__RnOpts.hide()
        self.__RdOpts.hide()
        self.__ConditionOpts.hide()
        self.__OperandBox.hide()
        self.__OperandBox.setText('')
        if self.__OpcodeOpts.currentIndex() != 0 and self.__OpcodeOpts.currentIndex() != 14:
            self.__OperandBox.show()
        self.__Opcode = self.__OpcodeOpts.currentText()
        if self.__OpcodeOpts.currentIndex() in self._style1 or self.__OpcodeOpts.currentIndex() in self._style2:
            self.__RdOpts.show()
            if self.__OpcodeOpts.currentIndex() in self._style2:
                self.__RnOpts.show()
        if self.__OpcodeOpts.currentIndex() == 6:
            self.__RnOpts.show()
        if self.__OpcodeOpts.currentIndex() == 7:
            self.__ConditionOpts.show()

    def __OperandChange(self):
        self.__Operand = self.__OperandBox.toPlainText()

    def __RdChange(self):
        self.__ToRegister = int(self.__RdOpts.currentText())

    def __RnChange(self):
        self.__FromRegister = int(self.__RnOpts.currentText())

    def __ConditionChange(self):
        self.__Condition = self.__ConditionOpts.currentText()

    def __AddInstruct(self):
        if self.__CntInstruct > 30:
            self.PopMsgBox("Too Much Instruction!")
            return
        if self.__Opcode == "":
            self.PopMsgBox("Opcode Empty!")
            return
        if self.__Operand == "" and self.__Opcode != 'HALT':
            self.PopMsgBox("Operand Empty!")
            return
        if self.__Opcode == '.ORIG':
            self.NowInstruct = f'{self.__Opcode} {self.__Operand}'
        else:
            index = self.__OpcodeList.index(self.__Opcode)
            if index in self._style1:
                self.NowInstruct = f'{self.__Opcode} R{self.__ToRegister} {self.__Operand}'
            elif index in self._style2:
                self.NowInstruct = f'{self.__Opcode} R{self.__ToRegister} R{self.__FromRegister} {self.__Operand}'
            elif index == 7:
                if self.__Condition == '':
                    self.NowInstruct = f'{self.__Opcode} {self.__Operand}'
                else:
                    self.NowInstruct = f'{self.__Opcode} {self.__Condition} {self.__Operand}'
            elif index == 6:
                self.NowInstruct = f'{self.__Opcode} R{self.__FromRegister} {self.__Operand}'
            elif index == 14:
                self.NowInstruct = 'HALT'
        try:
            self.__CntInstruct += 1
            with open('records.txt', 'a+') as file:
                file.write(self.NowInstruct + '\n')
                self.__InstructionLabel.setText(self.__InstructionLabel.text() + self.NowInstruct + '\n')
        except FileNotFoundError:
            print("File Not Found!")

    def __ClearAllInstruct(self, flag):
        try:
            self.__InstructionLabel.setText('')
            with open('machine_code.txt', 'w+') as file:
                file.write('')
            with open('records.txt', 'r') as file:
                tmp = file.readlines()
            with open('records.txt', 'w') as file:
                print(tmp)
                file.write('')
                if len(tmp):
                    if flag:
                        file.write(tmp[0])
                        self.__InstructionLabel.setText(tmp[0])
            self.__CntInstruct = 0
        except FileNotFoundError:
            raise FileNotFoundError

    def __nextInst(self):
        instruction_queue.put(1)

    def __doneSimulate(self):
        instruction_queue.put(0)

    def mouseMoveEvent(self, event):
        x = event.position().x()
        y = event.position().y()
        self.__mouseCoordinatesLabel.setText(f"Mouse coordinates: ({x}, {y})")

    def __Assemble(self):
        try:
            # Capture stdout
            # capture = py.io.StdCaptureFD()
            print("[+] C code successfully imported\n")
            program_path = "./assembler"
            # Load file
            program = Popen([program_path])
            file = "./records.txt"
            out, err = program.communicate(input=file.encode('ascii'))
            print(out, err)
            print("[+] Assembly code is successfully assembled")
        except:
            print("Failed...")
            return ""
        try:
            with open('machine_code.txt', 'r') as f:
                text = f.readlines()
            res = ""
            for c in text:
                res += c
            self.__MachineCodeWin.setText(res)
            self.__MachineCodeWin.show()
        except:
            raise FileNotFoundError

    def __Run(self):
        # Current Bug: Program exit accidentally when clicking run
        # Prev or next instruction just change PC in Control Struct
        try:
            if os.stat('./machine_code.txt').st_size == 0:
                MainWindow.PopMsgBox("Assembly code not assembled yet")
                return
        except:
            raise FileNotFoundError
        self.__NextInstBtn.show()
        self.__DoneSimulateBtn.show()
        self.__ShowMemWin.show()
        self.__ShowMemWin.change_signal.connect(self.__memChangedManual)
        self.__ShowRegWin.show()
        self.threading[1] = CheckChangeThread(index=1)
        self.threading[1].any_signal.connect(self.__updateData)
        print("About to start simulate process")
        simulate_result = process_pool.apply_async(self.RunSimulation,
                                                   (instruction_queue, reg_list, memory_list, change_list, change_flag, logic_list))
        self.threading[1].start()

    def __animationChange(self):
        self.initAnimate()
        NowOpcode = reg_list[9] >> 12
        Mode = (reg_list[9] >> 5) & 1
        EQ = logic_list[0]
        GT = logic_list[1]
        Condition = (reg_list[9] >> 9) & 0x7

        def checkCondition():
            if Condition == 0 and EQ == 1: return True
            elif Condition == 1 and EQ == 0: return True
            elif Condition == 2 and GT == 1: return True
            elif Condition == 3 and GT == 0: return True
            elif Condition == 4: return True
            else: return False

        self.__InIrCtrl.show()
        self.__InIrData.show(2)
        self.__IrToNode.show(2)
        self.__IrToFSMNode.show(2)
        self.__FSMNodeInst1.show(2)
        self.__FSMNodeInst2.show(2)
        self.__DataBusLabel1.show(3)
        self.__DataBusLabel2.show(3)
        self.__DataBusLabel3.show(3)

        self.__InPcCtrl.show()
        self.__InPcData.show(2)
        self.__OutPcCtrl.show()
        self.__OutPcData.show(1)
        self.__InPcPlus1.show(1)
        self.__InPcPlus2.show(1)
        self.__OutPcPlus1.show(2)
        self.__OutPcPlus2.show(2)
        self.__OutPcPlus3.show(2)

        if NowOpcode == 11 or NowOpcode == 12:
            self.__BusToLogic.show()
            if EQ == 1:
                self.__EqLogic.show()
                self.__EqToFSM1.show()
                self.__EqToFSM2.show()
            if GT == 1:
                self.__GtLogic.show()
                self.__GtToFSM1.show()
                self.__GtToFSM2.show()

        if NowOpcode == 0 or NowOpcode == 1 or (NowOpcode == 12 and checkCondition()) or NowOpcode == 14:
            self.__InMarData.show(3)
            self.__InMarCtrl.show()
            self.__OutMar1.show(3)
            self.__OutMar2.show(3)
            self.__OutMDRCtrl.show()

            self.__IrTo7Sext1.show(2)
            self.__IrTo7Sext2.show(2)
            if NowOpcode == 14:
                self.__7SextToAMux.show(2)
            else:
                self.__NodeTo8Sext.show(2)
                self.__8SextToPcMux1.show(2)
                self.__8SextToPcMux2.show(2)

            self.__8SextToAMux1.show(2)
            self.__8SextToAMux2.show(2)
            self.__AmuxCtrl.show()
            self.__OutAmuxCtrl.show()
            self.__OutAmuxData.show(2)

            if NowOpcode == 0: # trapcode == 0x23 for input
                self.__InRegData.show()
                self.__InRegCtrl.show()
                self.__MemToMDR1.show(3)
                self.__MemToMDR2.show(3)
                self.__OutMDRData.show(3)
            if NowOpcode == 1:  # trapcode == 0x25 for output
                self.__SrcReg1.show()
                self.__RegOut.show()
                self.__AluOutCtrl.show()
                self.__AluOutData.show()
                self.__MemRWCtrl.show()
                self.__InMDRData.show()
                self.__InMDRCtrl.show()
                self.__MDRToMem1.show()
                self.__MDRToMem2.show()
                self.__MemToMDR1.show(1)
                self.__MemToMDR2.show(1)
                self.__OutMDRData.show(1)
        elif NowOpcode == 2 or NowOpcode == 3 or NowOpcode == 4 or NowOpcode == 5 or NowOpcode == 6 or NowOpcode == 7 or NowOpcode == 8 or NowOpcode == 9 or NowOpcode == 10 or NowOpcode == 11:
            self.__InMarData.show(1)
            self.__InMarCtrl.show()
            self.__OutMar1.show(1)
            self.__OutMar2.show(1)
            self.__MemToMDR1.show(1)
            self.__MemToMDR2.show(1)
            self.__OutMDRCtrl.show()
            self.__OutMDRData.show(1)
            self.__FSMNodeMode.show(2)

            self.__InRegCtrl.show()
            self.__InRegData.show()
            self.__SrcMuxCtrl.show()
            self.__SrcMuxOut.show()
            self.__AluOutData.show()
            self.__AluOutCtrl.show()
            if Mode:
                self.__IrToSrcMuxSext1.show(2)
                self.__IrToSrcMuxSext2.show(2)
                self.__IrToSrcMuxSext3.show(2)
                self.__IrToSrcMuxSext4.show(2)
                self.__IrSextToSrcMux1.show(2)
                self.__IrSextToSrcMux2.show(2)
            else:
                self.__SrcReg2.show()
                self.__RegToSrc.show()
            if not NowOpcode == 2 and not NowOpcode == 8:
                self.__SrcReg1.show()
                self.__RegOut.show()
        elif NowOpcode == 13:
            self.initAnimate()

    def __updateData(self):
        self.threading[1].stop()
        print("[+] Updating data from current instruction")
        # Update memory value in UI
        for i in range(len(memory_list)):
            # print(memory_list[i])
            self.__ShowMemWin.changeVal(i, memory_list[i])
        # Update register value in UI
        for i in range(8):
            self.__ShowRegWin.changeVal('R'+str(i), reg_list[i])
        self.__ShowRegWin.changeVal('PC', reg_list[8])
        self.__ShowRegWin.changeVal('IR', reg_list[9])
        self.__ShowRegWin.changeVal('MAR', reg_list[10])
        self.__ShowRegWin.changeVal('MDR', reg_list[11])
        self.__animationChange()
        self.threading[1].start()

    def __memChangedManual(self, addr, val):
        # memory_list is int or ctypes.int
        memory_list[addr] = val
        change_list[0] = addr
        change_list[1] = val
        print("Activating Queue")
        instruction_queue.put(2)

    @staticmethod
    def RunSimulation(in_queue, reg_list, memory_list, change_list, change_flag, logic_list):
        try:
            with open('./machine_code.txt', 'r') as f:
                instructions = f.readlines()
                for i in range(len(instructions)):
                    instructions[i] = instructions[i].replace('\n', '')
            # Convert instructions into ctypes ready for update
            NumOfInst = len(instructions)
            instructionsC = ctypes.pointer(ctypes.c_int(0))
            for i in range(NumOfInst):
                instructionsC[i] = int(instructions[i], 2)
            # Load Shared Library
            print("[+] C code successfully imported")
            program_path = './components/control.so'
            # Link Control C File
            controlLib = ctypes.CDLL(program_path)
            # # Test
            # testFunc = controlLib.testLink
            # testFunc.argtypes = [ctypes.c_char_p]
            # testFunc(bytes(instructions[0], 'utf-8'))
            # Define functions
            ControlConst = controlLib.createControl
            ControlConst.argtypes = [ctypes.c_int, ctypes.c_int]
            ControlConst.restype = ctypes.POINTER(Control)
            initFunc = controlLib.init
            initFunc.argtypes = [ctypes.POINTER(Control), ctypes.POINTER(ctypes.c_int), ctypes.c_int]
            DoInstructionFunc = controlLib.doInstruct
            DoInstructionFunc.argtypes = [ctypes.POINTER(Control)]
            ControlDestroy = controlLib.freeControl
            ControlDestroy.argtypes = [ctypes.POINTER(Control)]
            ChangeMemFunc = controlLib.setMemVal
            ChangeMemFunc.argtypes = [ctypes.POINTER(Control), ctypes.c_int, ctypes.c_int]
            # Create Control struct instance
            ControlUnit = ControlConst(int(instructions[0], 2), 0x200)
            instructions.pop(0)

            # Fetch information of memory and registers
            def fetch_info():
                gpr = ControlUnit.contents.reg.contents.registers
                pc = ControlUnit.contents.PC
                ir = ControlUnit.contents.IR
                mar = ControlUnit.contents.MAR
                mdr = ControlUnit.contents.MDR
                memory = ControlUnit.contents.memory.contents.data
                eq = ControlUnit.contents.eq
                gt = ControlUnit.contents.gt
                logic_list[:] = [eq] + [gt]
                gprTmp = gpr[:]
                # print(pc.value)
                # print(pc.value, ir.value, mar.value, mdr.value)
                reg_list[:] = gprTmp + [pc] + [ir] + [mar] + [mdr]
                memory_list[:] = memory[:0x200]

            # Synchronise memory in C from instruction list
            initFunc(ControlUnit, instructionsC, NumOfInst)
            print('Memory:', bin(ControlUnit.contents.memory.contents.data[0])[2:].rjust(16, '0'))
            # print(ControlUnit.contents.memory.contents.data)
            fetch_info()
            change_flag[0] = 1
            # PC to be controlled by CurrentInstructionIndex
            # Once CurrentInstruction Index changed, increase PC
            # Stop the loop when the machine is halted
            while True:
                now = in_queue.get()
                print("Current Queue:", now)
                if now == 0 or ControlUnit.contents.HALT:
                    print("Control is stopped")
                    break
                elif now == 2:
                    # Update mem in c
                    print("Memory changed manually")
                    ChangeMemFunc(ControlUnit, change_list[0], change_list[1])
                    # print(ControlUnit.contents.reg[0])
                # If flag is ready, do the next instruction
                else:
                    print(now)
                    DoInstructionFunc(ControlUnit)
                    fetch_info()
                    print(memory_list[0])
                    # Omit signal to main process for updating both lists
                    change_flag[0] = 1
                print(ControlUnit.contents.HALT)
            # Free pointers
            ControlDestroy(ControlUnit)
        except:
            print("Failed...")
            return ""

    def help(self):
        print("Help pressed")
        pass


# C structs
class Memory(ctypes.Structure):
    # Data should be list, but is int pointer in c source code
    _fields_ = [('size', ctypes.c_int),
                ('data', ctypes.POINTER(ctypes.c_int)),
                ('read', ctypes.POINTER(ctypes.c_int)),
                ('write', ctypes.c_void_p),
                ('freeMemory', ctypes.c_void_p)]


class ALU(ctypes.Structure):
    _fields_ = [('add', ctypes.POINTER(ctypes.c_int)),
                ('and', ctypes.POINTER(ctypes.c_int)),
                ('isEqual', ctypes.POINTER(ctypes.c_int)),
                ('isGreat', ctypes.POINTER(ctypes.c_int)),
                ('sub', ctypes.POINTER(ctypes.c_int)),
                ('orr', ctypes.POINTER(ctypes.c_int)),
                ('eor', ctypes.POINTER(ctypes.c_int)),
                ('mvn', ctypes.POINTER(ctypes.c_int)),
                ('lsl', ctypes.POINTER(ctypes.c_int)),
                ('lsr', ctypes.POINTER(ctypes.c_int)),]


class Reg(ctypes.Structure):
    _fields_ = [('registers', ctypes.c_int * 8),
                ('read', ctypes.POINTER(ctypes.c_int)),
                ('write', ctypes.c_void_p)]


class Control(ctypes.Structure):
    # doInstruct return type might be struct Control
    _fields_ = [('HALT', ctypes.c_bool),
                ('IR', ctypes.c_int),
                ('PC', ctypes.c_int),
                ('MAR', ctypes.c_int),
                ('MDR', ctypes.c_int),
                ('eq', ctypes.c_int),
                ('gt', ctypes.c_int),
                ('memory', ctypes.POINTER(Memory)),
                ('alu', ctypes.POINTER(ALU)),
                ('reg', ctypes.POINTER(Reg)),
                ('doInstruct', ctypes.c_void_p)]


def main(share, memory):
    app = QApplication(sys.argv)
    window = MainWindow(share, memory)
    window.show()
    app.exec()


if __name__ == '__main__':
    multiprocessing.freeze_support()
    multiprocessing.set_start_method('spawn')
    manager = multiprocessing.Manager()
    instruction_queue = manager.Queue()
    # 0-7: GPRs; 8: MAR; 9: MDR; 10: PC; 11: IR
    reg_list = manager.list()
    reg_list[:] = [0 for _ in range(12)]
    memory_list = manager.list()
    memory_list[:] = [0 for _ in range(0x200)]
    change_list = manager.list()
    change_list.append(0)
    change_list.append(0)
    change_flag = manager.list()
    change_flag.append(0)
    logic_list = manager.list()
    logic_list.append(-1)
    logic_list.append(-1)
    process_pool = multiprocessing.Pool()
    main(reg_list, memory_list)
    process_pool.close()
    process_pool.join()
