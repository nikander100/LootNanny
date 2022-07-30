from decimal import Decimal
import os
import json

from PyQt5.QtGui import *
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtWidgets import QFileDialog, QTextEdit, QFormLayout, QHBoxLayout, QHeaderView, QTabWidget, QCheckBox, QGridLayout, QComboBox, QLineEdit, QLabel, QApplication, QWidget, QPushButton, QVBoxLayout, QTableWidget, QTableWidgetItem

from data.weapons import ALL_WEAPONS
from data.healingtools import ALL_HEALING_TOOLS
from data.sights_and_scopes import SIGHTS, SCOPES
from data.attachments import ALL_ATTACHMENTS
from modules.combat import Loadout, HealingLoadout
from utils.tables import WeaponTable, HealingToolTable


class ConfigTab(QWidget):

    def __init__(self, app, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.app: "LootNanny" = app

        layout = QVBoxLayout()

        form_inputs = QFormLayout()
        # Add widgets to the layout

        # Chat Location
        self.chat_location_text = QLineEdit(text=self.app.config.location.ui_value)
        form_inputs.addRow("Chat Location:", self.chat_location_text)
        self.chat_location_text.editingFinished.connect(self.onChatLocationChanged)

        btn = QPushButton("Find File")
        form_inputs.addWidget(btn)
        btn.clicked.connect(self.open_files)

        self.character_name = QLineEdit(text=self.app.config.name.ui_value)
        form_inputs.addRow("Character Name:", self.character_name)
        self.character_name.editingFinished.connect(self.onNameChanged)

        # Screenshots
        self.screenshots_enabled = True
        self.screenshot_directory = "~/Documents/Globals/"
        self.screenshot_delay_ms = 500

        self.screenshots_checkbox = QCheckBox()
        self.screenshots_checkbox.setChecked(self.app.config.screenshot_enabled.value)
        self.screenshots_checkbox.toggled.connect(self.update_screenshot_fields)
        form_inputs.addRow("Take Screenshot On global/hof", self.screenshots_checkbox)

        self.screenshots_directory_text = QLineEdit(text=self.app.config.screenshot_directory.ui_value)
        form_inputs.addRow("Screenshot Directory:", self.screenshots_directory_text)
        self.screenshots_directory_text.textChanged.connect(self.update_screenshot_fields)

        self.screenshots_delay = QLineEdit(text=self.app.config.screenshot_delay.ui_value)
        form_inputs.addRow("Screenshot Delay (ms):", self.screenshots_delay)
        self.screenshots_delay.textChanged.connect(self.update_screenshot_fields)

        self.screenshot_threshold = QLineEdit(text=self.app.config.screenshot_threshold.ui_value)
        form_inputs.addRow("Screenshot Threshold (PED):", self.screenshot_threshold)
        self.screenshot_threshold.textChanged.connect(self.update_screenshot_fields)

        self.streamer_window_layout_text = QTextEdit()
        self.streamer_window_layout_text.setText(self.app.config.streamer_layout.ui_value)
        self.streamer_window_layout_text.textChanged.connect(self.set_new_streamer_layout)

        form_inputs.addRow("Streamer Window Layout:", self.streamer_window_layout_text)

        # Set Layout
        layout.addLayout(form_inputs)

        self.setLayout(layout)

        if not os.path.exists(os.path.expanduser(self.screenshot_directory)):
            os.makedirs(os.path.expanduser(self.screenshot_directory))

    def update_screenshot_fields(self):
        self.app.config.screenshot_threshold = int(self.screenshot_threshold.text())
        self.app.config.screenshot_delay = int(self.screenshots_delay.text())
        self.app.config.screenshot_directory = self.screenshots_directory_text.text()
        self.app.config.screenshot_enabled = self.screenshots_checkbox.isChecked()

        if not os.path.exists(os.path.expanduser(self.app.config.screenshot_directory.value)):
            os.makedirs(os.path.expanduser(self.app.config.screenshot_directory.value))

    def set_new_streamer_layout(self):
        try:
            self.app.config.streamer_layout = json.loads(self.streamer_window_layout_text.toPlainText())
            self.streamer_window_layout_text.setStyleSheet("color: white;" if self.app.theme == "dark" else "color: black;")
        except:
            self.streamer_window_layout_text.setStyleSheet("color: red;")

    def open_files(self):
        path = QFileDialog.getOpenFileName(self, 'Open a file', '', 'All Files (*.*)')
        self.app.config.location = path[0]
        self.chat_location_text.setText(path[0])
        self.onChatLocationChanged()

    def onNameChanged(self):
        self.app.config.name = self.character_name.text()
        self.app.save_config()

    def onChatLocationChanged(self):
        if "*" in self.chat_location_text.text():
            print("Probably an error trying to resave this value, don't update")
            return
        self.app.config.location = self.chat_location_text.text()