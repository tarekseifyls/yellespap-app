import json
import os
import csv
from datetime import datetime

from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.utils import platform
from kivy.app import App

from kivymd.app import MDApp
from kivymd.toast import toast
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.list import (
    TwoLineAvatarIconListItem,
    OneLineAvatarIconListItem,
    OneLineListItem,
    ThreeLineListItem,
    IconLeftWidget,
    IconRightWidget,
)
from kivymd.uix.pickers import MDDatePicker

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A6
from reportlab.lib.units import mm

# ✅ IMPORT YOUR REAL DATABASE (FULL LOGIC)
from database import StoreDatabase

# Safe window sizing (desktop only)
if platform != "android":
    Window.size = (360, 750)

# ---------------- SCREENS ----------------
class LoginScreen(Screen): pass
class DashboardScreen(Screen): pass
class ReceiptScreen(Screen): pass
class SettingsScreen(Screen): pass
class ReportScreen(Screen): pass
class ExternalReportScreen(Screen): pass
class WorkerDetailScreen(Screen): pass
class CreditScreen(Screen): pass

# ---------------- APP ----------------
class StoreApp(MDApp):

    def build(self):
        # ✅ Android-safe DB handled inside database.py
        self.db = StoreDatabase("store_data.db")

        self.theme_cls.primary_palette = "Teal"
        return Builder.load_string(KV)

    # ---------- AUTH ----------
    def do_login(self):
        pin = self.root.get_screen("login").ids.login_pin.text
        if pin == self.db.get_pin():
            self.root.current = "dashboard"
            self.root.get_screen("login").ids.login_pin.text = ""
        else:
            toast("WRONG PIN")

    # ---------- SETTINGS ----------
    def update_pin(self, new_pin):
        self.db.update_pin(new_pin)
        toast("PIN UPDATED")

    # ---------- RECEIPT PDF ----------
    def generate_receipt_pdf(self, receipt_id, receipt_data):
        app = App.get_running_app()

        if platform == "android":
            base_path = app.user_data_dir
        else:
            base_path = "."

        pdf_path = os.path.join(base_path, f"receipt_{receipt_id}.pdf")

        c = canvas.Canvas(pdf_path, pagesize=A6)
        width, height = A6

        y = height - 10 * mm
        c.setFont("Helvetica", 9)
        c.drawString(10 * mm, y, "YELLES PAP STATIONARY")
        y -= 6 * mm

        for item in receipt_data["items"]:
            c.drawString(10 * mm, y, f"{item['name']} x{item['qty']}  {item['price']}")
            y -= 5 * mm

        y -= 5 * mm
        c.drawString(10 * mm, y, f"TOTAL: {receipt_data['total']}")

        c.showPage()
        c.save()

        toast("Receipt saved")

    def on_stop(self):
        self.db.close()

# ---------------- KV ----------------
KV = """
ScreenManager:
    LoginScreen:
    DashboardScreen:
    ReceiptScreen:
    SettingsScreen:
    ReportScreen:
    ExternalReportScreen:
    WorkerDetailScreen:
    CreditScreen:

<LoginScreen>:
    name: "login"
    MDBoxLayout:
        orientation: "vertical"
        padding: "30dp"
        spacing: "20dp"
        md_bg_color: app.theme_cls.primary_color

        Widget:
            size_hint_y: .3

        MDLabel:
            text: "YELLES PAP\\nSTATIONARY"
            halign: "center"
            theme_text_color: "Custom"
            text_color: 1,1,1,1
            font_style: "H4"
            bold: True

        MDCard:
            size_hint_y: None
            height: "200dp"
            padding: "20dp"
            radius: [20]

            MDBoxLayout:
                orientation: "vertical"
                spacing: "15dp"

                MDTextField:
                    id: login_pin
                    hint_text: "Enter PIN"
                    password: True
                    input_filter: "int"
                    max_text_length: 4

                MDRaisedButton:
                    text: "UNLOCK STORE"
                    on_release: app.do_login()

        Widget:

<DashboardScreen>:
    name: "dashboard"
    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "YellesPaP Store"
            elevation: 4

        MDLabel:
            text: "Dashboard"
            halign: "center"
"""

if __name__ == "__main__":
    StoreApp().run()
