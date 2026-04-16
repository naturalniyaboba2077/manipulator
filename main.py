from datetime import datetime
import math

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem

import ui

try:
    from motion.core import RobotControl, LedLamp
except Exception:
    from fake_motion import RobotControl, LedLamp


class LogStore:
    def __init__(self): 
        self.items = []
        self.save_path = ""

    def set_save_path(self, path: str) -> None:
        self.save_path = path.strip()

    def add(self, text: str) -> None:
        stamp = datetime.now().strftime("%H:%M:%S")
        line = f"{stamp} | {text}"
        self.items.insert(0, line)
        self._autosave()

    def as_text(self) -> str:
        return "\n".join(self.items)

    def save_now(self) -> tuple[bool, str]:
        if not self.save_path:
            return False, "Путь сохранения не задан"
        try:
            with open(self.save_path, "w", encoding="utf-8") as file:
                file.write(self.as_text())
            return True, "Логи сохранены"
        except Exception as error:
            return False, f"Ошибка сохранения: {error}"

    def _autosave(self) -> None:
        if not self.save_path:
            return
        try:
            with open(self.save_path, "w", encoding="utf-8") as file:
                file.write(self.as_text())
        except Exception:
            pass


class RobotGui(QMainWindow, ui.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.robot = RobotControl("192.168.2.100")
        self.lamp = LedLamp("192.168.2.101")
        self.logger = LogStore()

        self.is_power_on = False
        self.is_manual_mode = False
        self.is_paused = False
        self.is_emergency = False
        self.is_gripper_on = False
        self.is_conveyor_on = False
        self.control_mode = "cart" 
        self.motors_deg = [0.0] * 6

        self._prepare_tables()
        self._connect_signals()
        self._apply_ui_state()
        self._set_status_lamp("off")
        self._log("GUI запущен")

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._periodic_update)
        self.timer.start(250)

    def _prepare_tables(self) -> None:
        self.tableWidget_2.setRowCount(4)
        self.tableWidget_2.setColumnCount(2)
        self.tableWidget_2.setVerticalHeaderLabels(["Класс 1", "Класс 2", "Класс 3", "Брак"])
        self.tableWidget_2.setHorizontalHeaderLabels(["Кол-во", "Время последнего перемещения"])

        for row in range(4):
            self.tableWidget_2.setItem(row, 0, QTableWidgetItem("0"))
            self.tableWidget_2.setItem(row, 1, QTableWidgetItem("-"))

    def _connect_signals(self) -> None:
        self.pushButton_10.clicked.connect(self.on_power_toggle)
        self.pushButton.clicked.connect(self.on_pause_toggle)
        self.pushButton_2.clicked.connect(self.on_emergency_stop)
        self.pushButton_3.clicked.connect(self.on_move_to_start)
        self.pushButton_4.clicked.connect(self.on_manual_mode_toggle)
        self.pushButton_11.clicked.connect(self.on_gripper_toggle)
        self.pushButton_12.clicked.connect(self.on_conveyor_toggle)
        self.pushButton_13.clicked.connect(self.on_save_logs_click)
        self.pushButton_5.clicked.connect(self.on_save_logs_click)

        self.comboBox.currentTextChanged.connect(self.on_control_mode_change)

        self.pushButton_6.clicked.connect(lambda: self.on_stat_inc(0))
        self.pushButton_7.clicked.connect(lambda: self.on_stat_inc(1))
        self.pushButton_8.clicked.connect(lambda: self.on_stat_inc(3))

        self.horizontalSlider.valueChanged.connect(lambda v: self.on_slider_changed(0, v))
        self.horizontalSlider_2.valueChanged.connect(lambda v: self.on_slider_changed(1, v))
        self.horizontalSlider_3.valueChanged.connect(lambda v: self.on_slider_changed(2, v))
        self.horizontalSlider_4.valueChanged.connect(lambda v: self.on_slider_changed(3, v))
        self.horizontalSlider_5.valueChanged.connect(lambda v: self.on_slider_changed(4, v))
        self.horizontalSlider_6.valueChanged.connect(lambda v: self.on_slider_changed(5, v))

    def _apply_ui_state(self) -> None:
        manual_controls_enabled = self.is_power_on and self.is_manual_mode and not self.is_emergency
        for slider in (
            self.horizontalSlider,
            self.horizontalSlider_2,
            self.horizontalSlider_3,
            self.horizontalSlider_4,
            self.horizontalSlider_5,
            self.horizontalSlider_6,
            self.comboBox,
        ):
            slider.setEnabled(manual_controls_enabled)

    def _log(self, message: str) -> None:
        self.logger.set_save_path(self.lesavepath.text())
        self.logger.add(message)
        self.textBrowser.setText(self.logger.as_text())

    def _set_status_lamp(self, state: str) -> None:
        color_map = {
            "off": ("white", "white", "white", "white", "0000"),
            "working": ("green", "white", "white", "white", "1000"),
            "idle": ("white", "blue", "white", "white", "0100"),
            "pause": ("white", "white", "yellow", "white", "0010"),
            "emergency": ("white", "white", "white", "red", "0001"),
        }
        c1, c2, c3, c4, lamp_code = color_map[state]
        self.label_8.setStyleSheet(f"background-color: {c1};")
        self.label_9.setStyleSheet(f"background-color: {c2};")
        self.label_10.setStyleSheet(f"background-color: {c3};")
        self.label_11.setStyleSheet(f"background-color: {c4};")
        try:
            self.lamp.setLamp(lamp_code)
        except Exception:
            pass

    def _safe_call(self, fn, *args):
        try:
            return fn(*args)
        except Exception as error:
            self._log(f"Ошибка API: {error}")
            return None

    def on_power_toggle(self) -> None:
        self.is_power_on = not self.is_power_on
        if self.is_power_on:
            self.pushButton_10.setText("Выкл")
            connected = self._safe_call(self.robot.connect)
            if connected:
                self._log("Робот включен")
            else:
                self._log("Не удалось подключиться к роботу")
            self._safe_call(self.robot.engage)
            self._safe_call(self.robot.moveToInitialPose)
            self._log("Робот на стартовой позиции")
            self._set_status_lamp("idle")
        else:
            self.pushButton_10.setText("Вкл")
            self.is_manual_mode = False
            self.is_paused = False
            self.is_emergency = False
            self._safe_call(self.robot.stop)
            self._safe_call(self.robot.moveToInitialPose)
            self._safe_call(self.robot.conveyer_stop)
            self._safe_call(self.robot.toolOFF)
            self._safe_call(self.robot.disengage)
            self._log("Робот выключен (возврат на старт, конвейер и схват остановлены)")
            self._set_status_lamp("off")
            self.pushButton_4.setText("Начало работы в ручном режиме управления")

        self._apply_ui_state()

    def on_pause_toggle(self) -> None:
        if not self.is_power_on:
            self._log("Пауза недоступна: робот выключен")
            return
        if self.is_emergency:
            self._log("Пауза недоступна во время аварийной остановки")
            return

        self.is_paused = not self.is_paused
        if self.is_paused:
            self.pushButton.setText("Возобновить")
            self._safe_call(self.robot.pause)
            self._set_status_lamp("pause")
            self._log("Пауза")
        else:
            self.pushButton.setText("Пауза")
            self._safe_call(self.robot.play)
            self._set_status_lamp("working" if self.is_manual_mode else "idle")
            self._log("Работа продолжена")

    def on_emergency_stop(self) -> None:
        self.is_emergency = True
        self.is_manual_mode = False
        self.pushButton_4.setText("Начало работы в ручном режиме управления")
        self._safe_call(self.robot.stop)
        self._safe_call(self.robot.reset)
        self._safe_call(self.robot.conveyer_stop)
        self._set_status_lamp("emergency")
        self._apply_ui_state()
        self._log("Аварийная остановка системы")

    def on_move_to_start(self) -> None:
        if not self.is_power_on:
            self._log("Возврат на старт недоступен: робот выключен")
            return
        self._safe_call(self.robot.moveToStart)
        self._set_status_lamp("idle")
        self._log("Робот на стартовой позиции")

    def on_manual_mode_toggle(self) -> None:
        if not self.is_power_on:
            self._log("Сначала включите систему")
            return
        if self.is_emergency:
            self._log("Сначала снимите аварийную остановку (перезапуском системы)")
            return

        self.is_manual_mode = not self.is_manual_mode
        if self.is_manual_mode:
            self.pushButton_4.setText("Остановить ручной режим управления")
            self._log("Робот в режиме ручного управления")
            self.on_control_mode_change(self.comboBox.currentText())
            self._set_status_lamp("working")
        else:
            self.pushButton_4.setText("Начало работы в ручном режиме управления")
            self._safe_call(self.robot.setJointVelocity, [0.0] * 6)
            self._safe_call(self.robot.setCartesianVelocity, [0.0] * 6)
            self._set_status_lamp("idle")
            self._log("Ручной режим остановлен")

        self._apply_ui_state()

    def on_control_mode_change(self, text: str) -> None:
        if text == "по градусам":
            self.control_mode = "joint"
            self.label.setText("J1")
            self.label_2.setText("J2")
            self.label_3.setText("J3")
            self.label_4.setText("J4")
            self.label_5.setText("J5")
            self.label_6.setText("J6")
            self._safe_call(self.robot.manualJointMode)
            self._log("Режим Move J (по joint)")
        else:
            self.control_mode = "cart"
            self.label.setText("X")
            self.label_2.setText("Y")
            self.label_3.setText("Z")
            self.label_4.setText("Rx")
            self.label_5.setText("Ry")
            self.label_6.setText("Rz")
            self._safe_call(self.robot.manualCartMode)
            self._log("Режим Move L (по координатам)")

    def on_gripper_toggle(self) -> None:
        if not self.is_power_on:
            self._log("Схват недоступен: робот выключен")
            return

        self.is_gripper_on = not self.is_gripper_on
        if self.is_gripper_on:
            self.pushButton_11.setText("Открыть (0)")
            self._safe_call(self.robot.toolON)
            self._log("Схват: закрыть (1)")
        else:
            self.pushButton_11.setText("Закрыть (1)")
            self._safe_call(self.robot.toolOFF)
            self._log("Схват: открыть (0)")

    def on_conveyor_toggle(self) -> None:
        if not self.is_power_on:
            self._log("Конвейер недоступен: робот выключен")
            return
        if self.is_emergency:
            self._log("Конвейер заблокирован аварийной остановкой")
            return

        self.is_conveyor_on = not self.is_conveyor_on
        if self.is_conveyor_on:
            self.pushButton_12.setText("Выключить конвейер")
            self._safe_call(self.robot.conveyer_start)
            self._log("Конвейер включен")
        else:
            self.pushButton_12.setText("Включить конвейер")
            self._safe_call(self.robot.conveyer_stop)
            self._log("Конвейер выключен")

    def on_save_logs_click(self) -> None:
        self.logger.set_save_path(self.lesavepath.text())
        ok, message = self.logger.save_now()
        self._log(message)
        if not ok:
            self._set_status_lamp("pause")

    def on_stat_inc(self, row: int) -> None:
        item = self.tableWidget_2.item(row, 0)
        value = 0
        if item is not None:
            try:
                value = int(item.text())
            except Exception:
                value = 0
        value += 1
        self.tableWidget_2.setItem(row, 0, QTableWidgetItem(str(value)))
        time_text = datetime.now().strftime("%H:%M:%S")
        self.tableWidget_2.setItem(row, 1, QTableWidgetItem(time_text))

    def on_slider_changed(self, axis: int, value: int) -> None:
        self.motors_deg[axis] = float(value)
        if not (self.is_power_on and self.is_manual_mode and not self.is_emergency):
            return

        normalized = [v / 100.0 for v in self.motors_deg]
        if self.control_mode == "joint":
            self._safe_call(self.robot.setJointVelocity, normalized)
        else:
            self._safe_call(self.robot.setCartesianVelocity, normalized)

    def _periodic_update(self) -> None:
        self._update_motor_table()

    def _update_motor_table(self) -> None:
        temperatures = self._safe_call(self.robot.getActualTemperature)
        ticks = self._safe_call(self.robot.getMotorPositionTick)
        radians_values = self._safe_call(self.robot.getMotorPositionRadians)

        if not isinstance(temperatures, list):
            temperatures = [temperatures if temperatures is not None else 0.0] * 6
        if not isinstance(ticks, list):
            ticks = [0.0] * 6
        if not isinstance(radians_values, list):
            radians_values = [math.radians(v) for v in self.motors_deg]

        for i in range(6):
            temp = temperatures[i] if i < len(temperatures) else temperatures[0]
            tick = ticks[i] if i < len(ticks) else 0.0
            rad = radians_values[i] if i < len(radians_values) else math.radians(self.motors_deg[i])
            deg = math.degrees(rad)

            self.tableWidget.setItem(i, 0, QTableWidgetItem(f"{temp:.1f}"))
            self.tableWidget.setItem(i, 1, QTableWidgetItem(f"{tick}"))
            self.tableWidget.setItem(i, 2, QTableWidgetItem(f"{rad:.4f}"))
            self.tableWidget.setItem(i, 3, QTableWidgetItem(f"{deg:.2f}"))


if __name__ == "__main__":
    app = QApplication([])
    window = RobotGui()
    window.show()
    app.exec()