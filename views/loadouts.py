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

class LoadoutsTab(QWidget):

    def __init__(self, app, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.app: "LootNanny" = app

        layout = QVBoxLayout()

        form_inputs = QFormLayout()

        # Weapon Loadouts
        self.weapons = WeaponTable({"Name": [], "Amp": [], "Scope": [], "Sight 1": [],
                         "Sight 2": [], "Damage": [], "Accuracy": [], "KeyMap": []}, 25, 8)
        self.weapons.itemClicked.connect(self.weapon_table_selected)
        self.redraw_weapons()
        form_inputs.addRow("Weapons", self.weapons)

        self.delete_weapon_btn = QPushButton("Delete Loadout")
        self.delete_weapon_btn.released.connect(self.delete_loadout)
        self.delete_weapon_btn.hide()
        form_inputs.addWidget(self.delete_weapon_btn)

        self.add_weapon_btn = QPushButton("Add Weapon Loadout")
        self.add_weapon_btn.released.connect(self.add_new_weapon)
        form_inputs.addWidget(self.add_weapon_btn)

        # Healing Tool Loadouts
        self.healing_tools = HealingToolTable({"Name": [], "Heal": [], "Economy": [], "KeyMap": []}, 25, 4)
        self.healing_tools.itemClicked.connect(self.healing_tools_table_selected)
        self.redraw_healing_tools()
        form_inputs.addRow("Healing Tools", self.healing_tools)

        self.delete_healing_tool_btn = QPushButton("Delete Healing Tool Loadout")
        self.delete_healing_tool_btn.released.connect(self.delete_healing_tool_loadout)
        self.delete_healing_tool_btn.hide()
        form_inputs.addWidget(self.delete_healing_tool_btn)

        self.add_healing_tool_btn = QPushButton("Add Healing Tool Loadout")
        self.add_healing_tool_btn.released.connect(self.add_new_healing_tool)
        form_inputs.addWidget(self.add_healing_tool_btn)

        # Group Loadout buttons
        self.select_loadout_btn = QPushButton("Select Loadout")
        self.select_loadout_btn.released.connect(self.select_loadout)
        self.select_loadout_btn.hide()
        form_inputs.addWidget(self.select_loadout_btn)

        # Active Loadout
        self.active_loadout = QLineEdit(text="", enabled=False)
        form_inputs.addRow("Active Loadout:", self.active_loadout)

        # Calculated Configuration
        self.ammo_burn_text = QLineEdit(text="0", enabled=False)
        form_inputs.addRow("Ammo Burn:", self.ammo_burn_text)

        self.weapon_decay_text = QLineEdit(text="0.0", enabled=False)
        form_inputs.addRow("Tool Decay:", self.weapon_decay_text)

        # Set Layout
        layout.addLayout(form_inputs)

        self.setLayout(layout)

        if self.app.config.selected_loadout.value:
            self.active_loadout.setText(self.app.config.selected_loadout.value[0])
            self.recalculateWeaponFields()

    def weapon_table_selected(self):
        indexes = self.weapons.selectionModel().selectedRows()
        if not indexes:
            self.delete_weapon_btn.hide()
            self.select_loadout_btn.hide()
            self.selected_index = None
            return

        self.delete_weapon_btn.show()
        self.select_loadout_btn.show()
        self.selected_index = indexes[-1].row()
        self.delete_weapon_btn.setEnabled(True)

    def healing_tools_table_selected(self):
        indexes = self.healing_tools.selectionModel().selectedRows()
        if not indexes:
            self.delete_healing_tools_btn.hide()
            self.select_loadout_btn.hide()
            self.selected_index = None
            return

        self.delete_healing_tool_btn.show()
        self.select_loadout_btn.show()
        self.selected_index = indexes[-1].row()
        self.delete_healing_tool_btn.setEnabled(True)

    def select_loadout(self):
        # need to figure out what selection weapon or healing tool is done
        self.app.config.selected_loadout = self.app.config.loadouts.value[self.selected_index]
        self.active_loadout.setText(self.app.config.selected_loadout.value[0])
        self.recalculateWeaponFields()

    def delete_loadout(self):
        del self.app.config.loadouts.value[self.selected_index]
        self.app.config.save()
        self.redraw_weapons()

    def delete_healing_tool_loadout(self):
        del self.app.config.healing_loadouts.value[self.selected_index]
        self.app.config.save()
        self.redraw_healing_tools()

    def loadout_to_data(self):
        d = {"Name": [], "Amp": [], "Scope": [], "Sight 1": [],
                         "Sight 2": [], "Damage": [], "Accuracy": [], "KeyMap": []}
        for loadout in self.app.config.loadouts.value:
            if isinstance(loadout, list):
                loadout = Loadout(*loadout)
            loadout: Loadout
            d["Name"].append(loadout.weapon)
            d["Amp"].append(loadout.amp)
            d["Scope"].append(loadout.scope)
            d["Sight 1"].append(loadout.sight_1)
            d["Sight 2"].append(loadout.sight_2)
            d["Damage"].append(loadout.damage_enh)
            d["Accuracy"].append(loadout.accuracy_enh)
            d["KeyMap"].append(loadout.keymap)
        return d

    def healingLoadout_to_data(self):
        d = {"Name": [], "Heal": [], "Economy": [], "KeyMap": []}
        for healingLoadout in self.app.config.healing_loadouts.value:
            if isinstance(healingLoadout, list):
                healingLoadout = HealingLoadout(*healingLoadout)
            healingLoadout: HealingLoadout
            d["Name"].append(healingLoadout.heal_tool)
            d["Heal"].append(healingLoadout.heal_enh)
            d["Economy"].append(healingLoadout.economy_enh)
            d["KeyMap"].append(healingLoadout.keymap)
        return d

    def redraw_weapons(self):
        self.weapons.clear()
        self.weapons.setData(self.loadout_to_data())

    def redraw_healing_tools(self):
        self.healing_tools.clear()
        self.healing_tools.setData(self.healingLoadout_to_data())

    def add_new_weapon(self):
        weapon_popout = WeaponPopOut(self)
        if self.app.config.theme == "light":
            self.set_stylesheet(weapon_popout, "light.qss")
        else:
            self.set_stylesheet(weapon_popout, "dark.qss")
        self.add_weapon_btn.setEnabled(False)

    def add_new_healing_tool(self):
        healing_tool_popout = HealingToolPopOut(self)
        if self.app.config.theme == "light":
            self.set_stylesheet(healing_tool_popout, "light.qss")
        else:
            self.set_stylesheet(weapon_popout, "dark.qss")
        self.add_healing_tool_btn.setEnabled(False)

    def add_weapon_cancled(self):
        self.add_weapon_btn.setEnabled(True)

    def add_healing_tool_cancled(self):
        self.add_healing_tool_btn.setEnabled(True)

    def on_added_weapon(self, weapon: str, amp: str, scope: str, sight_1: str, sight_2: str, d_enh: int, a_enh: int, km: str):
        new_loadout = Loadout(weapon, amp, scope, sight_1, sight_2, d_enh, a_enh, km)
        self.app.config.loadouts.value.append(new_loadout)
        self.app.config.save()
        self.redraw_weapons()

    def on_added_healing_tool(self, healingtool: str, h_enh: int, e_enh: int, km: str):
        new_healingloadout = HealingLoadout(healingtool, h_enh, e_enh, km)
        self.app.config.healing_loadouts.value.append(new_healingloadout)
        self.app.config.save()
        self.redraw_healing_tools()

    def recalculateWeaponFields(self):
        self.app.combat_module.recalculateWeaponLoadout()
        self.ammo_burn_text.setText(str(int(self.app.combat_module.ammo_burn)))
        self.weapon_decay_text.setText("%.6f" % self.app.combat_module.decay)
        self.app.save_config()

class WeaponPopOut(QWidget):
    def __init__(self, parent: LoadoutsTab):
        super().__init__()

        self.parent = parent

        # this will hide the title bar
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)

        # set the title
        self.setWindowTitle("Add Weapon")

        # setting  the geometry of window
        self.setGeometry(100, 100, 340, 100)


        self.weapon = ""
        self.amp = "Unamped"
        self.scope = "None"
        self.sight_1 = "None"
        self.sight_2 = "None"
        self.damage_enhancers = 0
        self.accuracy_enhancers = 0
        self.keymap = ""

        self.layout = self.create_widgets()
        self.resize_to_contents()

        self.show()

    def resize_to_contents(self):
        self.setFixedSize(self.layout.sizeHint())

    def create_widgets(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        form_inputs = QFormLayout()

        # Weapon Configuration
        self.weapon_option = QComboBox()
        self.weapon_option.addItems(sorted(ALL_WEAPONS))
        form_inputs.addRow("Weapon:", self.weapon_option)
        self.weapon_option.currentIndexChanged.connect(self.on_field_changed)

        self.amp_option = QComboBox()
        self.amp_option.addItems(["Unamped"] + sorted(ALL_ATTACHMENTS))
        form_inputs.addRow("Amplifier:", self.amp_option)
        self.amp_option.currentIndexChanged.connect(self.on_field_changed)

        self.scope_option = QComboBox()
        self.scope_option.addItems(["None"] + sorted(SCOPES))
        form_inputs.addRow("Scope:", self.scope_option)
        self.scope_option.currentIndexChanged.connect(self.on_field_changed)

        self.sight_1_option = QComboBox()
        self.sight_1_option.addItems(["None"] + sorted(SIGHTS))
        form_inputs.addRow("Sight 1:", self.sight_1_option)
        self.sight_1_option.currentIndexChanged.connect(self.on_field_changed)

        self.sight_2_option = QComboBox()
        self.sight_2_option.addItems(["None"] + sorted(SIGHTS))
        form_inputs.addRow("Sight 2:", self.sight_2_option)
        self.sight_2_option.currentIndexChanged.connect(self.on_field_changed)

        self.damage_enhancers_txt = QLineEdit(text="0")
        form_inputs.addRow("Damage Enhancers:", self.damage_enhancers_txt)
        self.damage_enhancers_txt.editingFinished.connect(self.on_field_changed)

        self.accuracy_enhancers_txt = QLineEdit(text="0")
        form_inputs.addRow("Accuracy Enhancers:", self.accuracy_enhancers_txt)
        self.accuracy_enhancers_txt.editingFinished.connect(self.on_field_changed)
        layout.addLayout(form_inputs)

        self.keymap_txt = QLineEdit(text="0")
        form_inputs.addRow("KeyMap:", self.keymap_txt)
        self.keymap_txt.editingFinished.connect(self.on_field_changed)
        layout.addLayout(form_inputs)

        h_layout = QHBoxLayout()

        cancel = QPushButton("Cancel")
        cancel.released.connect(self.cancel)

        confirm = QPushButton("Confirm")
        confirm.released.connect(self.confirm)

        h_layout.addWidget(cancel)
        h_layout.addWidget(confirm)

        layout.addLayout(h_layout)

        layout.addStretch()
        return layout

    def cancel(self):
        self.parent.add_weapon_cancled()
        self.close()

    def confirm(self):
        self.parent.on_added_weapon(
            self.weapon,
            self.amp,
            self.scope,
            self.sight_1,
            self.sight_2,
            self.damage_enhancers,
            self.accuracy_enhancers,
            self.keymap
        )
        self.close()

    def on_field_changed(self):
        self.scope = self.scope_option.currentText()
        self.sight_1 = self.sight_1_option.currentText()
        self.sight_2 = self.sight_2_option.currentText()
        self.weapon = self.weapon_option.currentText()
        self.amp = self.amp_option.currentText()
        self.damage_enhancers = min(10, int(self.damage_enhancers_txt.text()))
        self.accuracy_enhancers = min(10, int(self.accuracy_enhancers_txt.text()))
        self.keymap = self.keymap_txt.text()

        self.damage_enhancers_txt.setText(str(self.damage_enhancers))
        self.accuracy_enhancers_txt.setText(str(self.accuracy_enhancers))

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint (event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

    def closeEvent(self, event):
        event.accept()  # let the window close

class HealingToolPopOut(QWidget):
    def __init__(self, parent: LoadoutsTab):
        super().__init__()

        self.parent = parent

        # this will hide the title bar
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)

        # set the title
        self.setWindowTitle("Add Healing Tool")

        # setting  the geometry of window
        self.setGeometry(100, 100, 340, 100)


        self.weapon = ""
        self.healing_enhancers = 0
        self.economy_enhancers = 0
        self.keymap = ""

        self.layout = self.create_widgets()
        self.resize_to_contents()

        self.show()

    def resize_to_contents(self):
        self.setFixedSize(self.layout.sizeHint())

    def create_widgets(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        form_inputs = QFormLayout()

        # Healing Tool Configuration
        self.healing_tool_option = QComboBox()
        self.healing_tool_option.addItems(sorted(ALL_HEALING_TOOLS))
        form_inputs.addRow("Healing Tool:", self.healing_tool_option)
        self.healing_tool_option.currentIndexChanged.connect(self.on_field_changed)

        self.healing_enhancers_txt = QLineEdit(text="0")
        form_inputs.addRow("Healing Enhancers:", self.healing_enhancers_txt)
        self.healing_enhancers_txt.editingFinished.connect(self.on_field_changed)

        self.economy_enhancers_txt = QLineEdit(text="0")
        form_inputs.addRow("Economy Enhancers:", self.economy_enhancers_txt)
        self.economy_enhancers_txt.editingFinished.connect(self.on_field_changed)
        layout.addLayout(form_inputs)

        self.keymap_txt = QLineEdit(text="0")
        form_inputs.addRow("KeyMap:", self.keymap_txt)
        self.keymap_txt.editingFinished.connect(self.on_field_changed)
        layout.addLayout(form_inputs)

        h_layout = QHBoxLayout()

        cancel = QPushButton("Cancel")
        cancel.released.connect(self.cancel)

        confirm = QPushButton("Confirm")
        confirm.released.connect(self.confirm)

        h_layout.addWidget(cancel)
        h_layout.addWidget(confirm)

        layout.addLayout(h_layout)

        layout.addStretch()
        return layout

    def cancel(self):
        self.parent.add_healing_tool_cancled()
        self.close()

    def confirm(self):
        self.parent.on_added_healing_tool(
            self.healing_tool,
            self.healing_enhancers,
            self.economy_enhancers,
            self.keymap
        )
        self.close()

    def on_field_changed(self):
        self.healing_tool = self.healing_tool_option.currentText()
        self.healing_enhancers = min(10, int(self.healing_enhancers_txt.text()))
        self.economy_enhancers = min(10, int(self.economy_enhancers_txt.text()))
        self.keymap = self.keymap_txt.text()

        self.healing_enhancers_txt.setText(str(self.healing_enhancers))
        self.economy_enhancers_txt.setText(str(self.economy_enhancers))

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint (event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

    def closeEvent(self, event):
        event.accept()  # let the window close