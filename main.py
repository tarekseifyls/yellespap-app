import json
import os
from datetime import datetime

from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.list import TwoLineAvatarIconListItem, OneLineListItem, IconLeftWidget, IconRightWidget, ThreeLineListItem
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDFillRoundFlatIconButton, MDIconButton
from kivymd.uix.pickers import MDDatePicker
from kivymd.toast import toast
from kivy.core.window import Window
from kivy.clock import mainthread

from database import StoreDatabase
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A6
from reportlab.lib.units import mm

Window.size = (360, 750)

KV = '''
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
        orientation: 'vertical'
        padding: "30dp"
        spacing: "30dp"
        md_bg_color: app.theme_cls.primary_color
        Widget:
            size_hint_y: 0.2
        MDLabel:
            text: "YELLES PAP\\nSTATIONARY"
            halign: "center"
            font_style: "H4"
            theme_text_color: "Custom"
            text_color: 1, 1, 1, 1
            bold: True
        MDCard:
            size_hint_y: None
            height: "200dp"
            padding: "20dp"
            radius: [15]
            orientation: "vertical"
            spacing: "15dp"
            elevation: 4
            MDLabel:
                text: "Security Check"
                halign: "center"
                font_style: "H6"
                theme_text_color: "Secondary"
            MDTextField:
                id: login_pin
                hint_text: "Enter PIN"
                password: True
                input_filter: "int"
                max_text_length: 4
                mode: "rectangle"
                halign: "center"
            MDFillRoundFlatButton:
                text: "UNLOCK STORE"
                font_size: "18sp"
                size_hint_x: 1
                on_release: app.do_login()
        Widget:

<DashboardScreen>:
    name: "dashboard"
    MDBoxLayout:
        orientation: 'vertical'
        MDTopAppBar:
            title: "YellesPaP"
            elevation: 2
            right_action_items: [["cog", lambda x: app.open_settings()], ["reload", lambda x: app.update_dashboard()]]
            left_action_items: [["calendar", lambda x: app.show_date_picker()]]
        MDBoxLayout:
            size_hint_y: None
            height: "110dp"
            padding: "15dp"
            MDCard:
                orientation: "vertical"
                padding: "10dp"
                radius: [15]
                md_bg_color: app.theme_cls.primary_color
                MDLabel:
                    id: date_label
                    text: "Today's Net Cash"
                    theme_text_color: "Custom"
                    text_color: 1,1,1,0.8
                    halign: "center"
                MDBoxLayout:
                    orientation: 'horizontal'
                    size_hint_y: None
                    height: "40dp"
                    padding: "10dp"
                    MDLabel:
                        id: daily_total_label
                        text: "**** DZD"
                        theme_text_color: "Custom"
                        text_color: 1,1,1,1
                        halign: "center"
                        font_style: "H4"
                        bold: True
                        size_hint_x: 0.8
                    MDIconButton:
                        id: eye_btn
                        icon: "eye-off"
                        theme_text_color: "Custom"
                        text_color: 1,1,1,1
                        on_release: app.toggle_revenue_privacy()
        MDCard:
            size_hint_y: None
            height: "140dp"
            padding: "15dp"
            spacing: "10dp"
            orientation: "vertical"
            elevation: 0
            MDTextField:
                id: quick_amount
                hint_text: "Amount (DZD)"
                input_filter: "float"
                mode: "rectangle"
            MDBoxLayout:
                spacing: "10dp"
                MDFillRoundFlatIconButton:
                    icon: "cash-plus"
                    text: "SALE"
                    size_hint_x: 0.33
                    md_bg_color: 0.2, 0.7, 0.2, 1
                    on_release: app.add_sale()
                MDFillRoundFlatIconButton:
                    icon: "cash-minus"
                    text: "EXPENSE"
                    size_hint_x: 0.33
                    md_bg_color: 0.8, 0.2, 0.2, 1
                    on_release: app.open_expense_dialog()
                MDFillRoundFlatIconButton:
                    icon: "book-open-page-variant"
                    text: "DEBTS"
                    size_hint_x: 0.33
                    md_bg_color: 0.2, 0.2, 0.6, 1
                    on_release: app.open_credit_screen()
        MDLabel:
            text: "  Recent Activity (Tap to Edit)"
            size_hint_y: None
            height: "30dp"
            theme_text_color: "Secondary"
            font_style: "Caption"
        ScrollView:
            MDList:
                id: transaction_list
    MDFloatingActionButton:
        icon: "plus"
        elevation: 4
        pos_hint: {"center_x": 0.85, "center_y": 0.1}
        on_release: app.open_new_receipt()

<CreditScreen>:
    name: "credits"
    MDBoxLayout:
        orientation: 'vertical'
        MDTopAppBar:
            title: "Unpaid / Debts"
            left_action_items: [["arrow-left", lambda x: app.go_back()]]
            elevation: 2
        MDBoxLayout:
            size_hint_y: None
            height: "60dp"
            padding: "10dp"
            MDFillRoundFlatIconButton:
                icon: "cash-plus"
                text: "ADD EXTERNAL PAYMENT"
                size_hint_x: 1
                on_release: app.open_manual_payment_dialog()
        ScrollView:
            MDList:
                id: credit_list

<ReceiptScreen>:
    name: "receipt_form"
    MDBoxLayout:
        orientation: 'vertical'
        MDTopAppBar:
            title: "Receipt Editor"
            left_action_items: [["arrow-left", lambda x: app.go_back()]]
            elevation: 2
        ScrollView:
            MDBoxLayout:
                orientation: 'vertical'
                padding: "20dp"
                spacing: "15dp"
                size_hint_y: None
                height: self.minimum_height
                MDTextField:
                    id: client_name
                    hint_text: "Client Name"
                    mode: "rectangle"
                MDCard:
                    orientation: "vertical"
                    size_hint_y: None
                    height: "140dp"
                    padding: "10dp"
                    spacing: "5dp"
                    radius: [10]
                    MDLabel:
                        text: "Add Item"
                        font_style: "Subtitle2"
                        size_hint_y: None
                        height: "20dp"
                    MDTextField:
                        id: product_name
                        hint_text: "Product"
                        size_hint_y: None
                        height: "40dp"
                    MDBoxLayout:
                        orientation: 'horizontal'
                        spacing: "10dp"
                        size_hint_y: None
                        height: "50dp"
                        MDTextField:
                            id: product_price
                            hint_text: "Price"
                            input_filter: "float"
                            size_hint_x: 0.4
                        MDTextField:
                            id: product_qty
                            hint_text: "Qty"
                            input_filter: "int"
                            text: "1"
                            size_hint_x: 0.3
                        MDIconButton:
                            icon: "plus-circle"
                            theme_text_color: "Custom"
                            text_color: app.theme_cls.primary_color
                            on_release: app.add_to_cart()
                MDList:
                    id: cart_list
                    size_hint_y: None
                    height: "100dp"
                MDCard:
                    id: receipt_preview
                    size_hint_y: None
                    height: "300dp"
                    padding: 0
                    radius: [0]
                    elevation: 4
                    RelativeLayout:
                        Image:
                            source: "assets/signature_bg.png"
                            allow_stretch: True
                            keep_ratio: False
                            opacity: 0.1
                        MDBoxLayout:
                            orientation: "vertical"
                            padding: "20dp"
                            MDLabel:
                                text: "YELLES PAP STATIONARY"
                                halign: "center"
                                font_style: "H6"
                                size_hint_y: 0.15
                                bold: True
                            MDBoxLayout:
                                orientation: "horizontal"
                                size_hint_y: 0.1
                                MDLabel:
                                    id: preview_date
                                    text: "Date: --"
                                    font_style: "Caption"
                                    halign: "left"
                                MDLabel:
                                    id: preview_client
                                    text: "Client: --"
                                    font_style: "Caption"
                                    halign: "right"
                                    bold: True
                            MDSeparator:
                                height: "2dp"
                            MDLabel:
                                id: preview_items
                                text: "\\nAdd items..."
                                valign: "top"
                                halign: "left"
                                size_hint_y: 0.6
                                font_style: "Body2"
                            MDSeparator:
                                height: "2dp"
                            MDLabel:
                                id: preview_total
                                text: "TOTAL: 0.00 DZD"
                                halign: "right"
                                font_style: "H5"
                                size_hint_y: 0.15
                                bold: True
                        MDLabel:
                            id: status_stamp
                            text: "PAID"
                            halign: "left"
                            valign: "bottom"
                            font_style: "H5"
                            theme_text_color: "Custom"
                            text_color: 0, 0.8, 0, 1
                            bold: True
                            size_hint: None, None
                            size: "100dp", "40dp"
                            pos_hint: {"x": 0.05, "y": 0.02}
                MDTextField:
                    id: amount_paid_input
                    hint_text: "Amount Paid Today"
                    input_filter: "float"
                    mode: "rectangle"
                    on_text: app.update_receipt_preview()
                MDBoxLayout:
                    size_hint_y: None
                    height: "40dp"
                    MDLabel:
                        text: "Mark as Fully Paid?"
                    MDSwitch:
                        id: paid_switch
                        active: True
                        on_active: app.on_switch_active(self, self.active)
                MDFillRoundFlatIconButton:
                    id: save_btn
                    icon: "file-pdf-box"
                    text: "SAVE & PRINT"
                    size_hint_x: 1
                    on_release: app.save_receipt()

<SettingsScreen>:
    name: "settings"
    MDBoxLayout:
        orientation: 'vertical'
        MDTopAppBar:
            title: "Settings"
            left_action_items: [["arrow-left", lambda x: app.go_back()]]
            elevation: 2
        ScrollView:
            MDBoxLayout:
                orientation: 'vertical'
                padding: "20dp"
                spacing: "20dp"
                size_hint_y: None
                height: self.minimum_height
                MDLabel:
                    text: "Reports"
                    font_style: "H6"
                MDFillRoundFlatIconButton:
                    icon: "chart-bar"
                    text: "WORKER EXPENSE REPORT"
                    size_hint_x: 1
                    on_release: app.open_report_screen()
                MDFillRoundFlatIconButton:
                    icon: "cash-multiple"
                    text: "EXTERNAL PAYMENTS REPORT"
                    size_hint_x: 1
                    on_release: app.open_external_report()
                MDFillRoundFlatIconButton:
                    icon: "file-excel"
                    text: "EXPORT CSV"
                    size_hint_x: 1
                    on_release: app.export_data()
                MDSeparator:
                MDLabel:
                    text: "Manage Workers"
                    font_style: "H6"
                MDBoxLayout:
                    spacing: "10dp"
                    size_hint_y: None
                    height: "50dp"
                    MDTextField:
                        id: new_worker_name
                        hint_text: "Name"
                    MDIconButton:
                        icon: "plus-box"
                        on_release: app.add_worker()
                MDList:
                    id: worker_list
                    size_hint_y: None
                    height: "150dp"
                MDSeparator:
                MDLabel:
                    text: "PIN"
                    font_style: "H6"
                MDTextField:
                    id: old_pin
                    hint_text: "Old PIN"
                    password: True
                    input_filter: "int"
                    max_text_length: 4
                MDTextField:
                    id: new_pin
                    hint_text: "New PIN"
                    password: True
                    input_filter: "int"
                    max_text_length: 4
                MDTextField:
                    id: confirm_pin
                    hint_text: "Confirm"
                    password: True
                    input_filter: "int"
                    max_text_length: 4
                MDFillRoundFlatButton:
                    text: "UPDATE PIN"
                    on_release: app.change_pin()

<ReportScreen>:
    name: "report"
    MDBoxLayout:
        orientation: 'vertical'
        MDTopAppBar:
            id: worker_toolbar
            title: "Monthly Expenses"
            left_action_items: [["arrow-left", lambda x: app.go_back_settings()]]
            right_action_items: [["chevron-left", lambda x: app.change_report_month(-1)], ["chevron-right", lambda x: app.change_report_month(1)]]
            elevation: 2
        MDLabel:
            id: month_label
            text: "This Month"
            halign: "center"
            size_hint_y: None
            height: "40dp"
            bold: True
        ScrollView:
            MDList:
                id: report_list

<ExternalReportScreen>:
    name: "ext_report"
    MDBoxLayout:
        orientation: 'vertical'
        MDTopAppBar:
            id: ext_toolbar
            title: "Client Payments"
            left_action_items: [["arrow-left", lambda x: app.go_back_settings()]]
            right_action_items: [["chevron-left", lambda x: app.change_report_month(-1)], ["chevron-right", lambda x: app.change_report_month(1)]]
            elevation: 2
        MDLabel:
            text: "Tap to Edit or Delete (Requires PIN)"
            halign: "center"
            theme_text_color: "Secondary"
            font_style: "Caption"
            size_hint_y: None
            height: "30dp"
        ScrollView:
            MDList:
                id: ext_list

<WorkerDetailScreen>:
    name: "worker_detail"
    MDBoxLayout:
        orientation: 'vertical'
        MDTopAppBar:
            id: detail_toolbar
            title: "History"
            left_action_items: [["arrow-left", lambda x: app.go_back_report()]]
            elevation: 2
        ScrollView:
            MDList:
                id: detail_list
'''

KV_PIN = '''
MDBoxLayout:
    orientation: "vertical"
    spacing: "12dp"
    size_hint_y: None
    height: "80dp"
    MDTextField:
        id: pin_field
        hint_text: "Enter PIN"
        input_filter: "int"
        max_text_length: 4
        password: True
'''

KV_EXPENSE = '''
MDBoxLayout:
    orientation: "vertical"
    spacing: "10dp"
    size_hint_y: None
    height: "250dp"
    MDLabel:
        text: "Select Worker"
        theme_text_color: "Secondary"
        font_style: "Caption"
    ScrollView:
        MDList:
            id: worker_selection_list
    MDTextField:
        id: expense_note
        hint_text: "Note"
'''

KV_VERSEMENT = '''
MDBoxLayout:
    orientation: "vertical"
    spacing: "10dp"
    size_hint_y: None
    height: "150dp"
    MDLabel:
        id: debt_info
        text: "Debt: 0"
        halign: "center"
        font_style: "H6"
    MDTextField:
        id: versement_amount
        hint_text: "Enter Amount"
        input_filter: "float"
'''

KV_MANUAL_PAY = '''
MDBoxLayout:
    orientation: "vertical"
    spacing: "10dp"
    size_hint_y: None
    height: "200dp"
    MDTextField:
        id: manual_client
        hint_text: "Client Name"
    MDTextField:
        id: manual_amount
        hint_text: "Amount (DZD)"
        input_filter: "float"
'''

KV_EDIT_PAYMENT = '''
MDBoxLayout:
    orientation: "vertical"
    spacing: "10dp"
    size_hint_y: None
    height: "280dp"
    MDTextField:
        id: edit_client
        hint_text: "Client Name"
        mode: "rectangle"
    MDTextField:
        id: edit_amount
        hint_text: "Amount"
        input_filter: "float"
        mode: "rectangle"
    MDTextField:
        id: edit_note
        hint_text: "Note"
        mode: "rectangle"
'''

class LoginScreen(Screen): pass
class DashboardScreen(Screen): pass
class ReceiptScreen(Screen): pass
class SettingsScreen(Screen): pass
class ReportScreen(Screen): pass
class ExternalReportScreen(Screen): pass
class WorkerDetailScreen(Screen): pass
class CreditScreen(Screen): pass

class StoreApp(MDApp):
    cart_items = []
    cart_total = 0.0
    current_receipt_id = None
    is_revenue_visible = False
    active_date = None
    dialog = None
    exp_dialog = None
    vers_dialog = None
    man_dialog = None
    edit_pay_dialog = None
    temp_expense_amount = 0.0
    temp_receipt_id = None
    temp_client_name = ""
    current_edit_payment = None
    pending_action = None
    report_date = None

    def build(self):
        self.db = StoreDatabase()
        self.theme_cls.primary_palette = "Teal"
        self.active_date = datetime.now().strftime("%Y-%m-%d")
        self.report_date = datetime.now()
        Builder.load_string(KV_PIN)
        Builder.load_string(KV_EXPENSE)
        Builder.load_string(KV_VERSEMENT)
        Builder.load_string(KV_MANUAL_PAY)
        Builder.load_string(KV_EDIT_PAYMENT)
        return Builder.load_string(KV)

    # --- SECURITY WRAPPER ---
    def secure_action(self, callback_func):
        self.pending_action = callback_func
        self.show_pin_dialog(is_security_check=True)

    def check_pin(self, x):
        pin_input = self.dialog.content_cls.ids.pin_field.text
        if pin_input == self.db.get_pin():
            self.dialog.dismiss()
            self.dialog.content_cls.ids.pin_field.text = ""
            if not self.pending_action:
                self.is_revenue_visible = True
                self.update_dashboard()
            else:
                self.pending_action()
                self.pending_action = None
        else:
            toast("WRONG PIN")

    def show_pin_dialog(self, is_security_check=False):
        self.dialog = MDDialog(title="Security PIN", type="custom", content_cls=Builder.load_string(KV_PIN), buttons=[MDFlatButton(text="UNLOCK", on_release=self.check_pin)])
        self.dialog.open()

    def do_login(self):
        entered_pin = self.root.get_screen('login').ids.login_pin.text
        real_pin = self.db.get_pin()
        if entered_pin == real_pin: self.login_success()
        else: toast("WRONG PIN")

    def login_success(self):
        self.root.current = "dashboard"
        self.update_dashboard()
        self.root.get_screen('login').ids.login_pin.text = ""

    # --- DASHBOARD ---
    def update_dashboard(self, date_str=None):
        if date_str: self.active_date = date_str
        lst = self.root.get_screen('dashboard').ids.transaction_list
        lst.clear_widgets()
        txs = self.db.get_daily_transactions(self.active_date)
        for t in txs:
            if t.get('is_deleted') == 1: icon, color, pre = "delete-outline", (0.5,0.5,0.5,1), "X"
            elif t['type'] == 'expense': icon, color, pre = "cash-minus", (0.8,0.2,0.2,1), "-"
            elif t['type'] == 'quick': icon, color, pre = "cash-plus", (0.2,0.6,0.2,1), "+"
            elif t['type'] == 'receipt':
                status = t.get('status', 'Paid')
                if status == 'Unpaid': icon, color, pre = "alert-circle", (0.8,0.2,0.2,1), "+"
                elif status == 'Partial': icon, color, pre = "clock-alert", (1,0.5,0,1), "+"
                else: icon, color, pre = "check-circle", (0.2,0.6,0.2,1), "+"
            else: icon, color, pre = "cash-check", (0.2,0.2,0.6,1), "+"
            text = t['desc']
            if t.get('is_deleted') == 1: text = f"[s]{text}[/s]" 
            status_text = f" [{t.get('status', '')}]" if t['type'] == 'receipt' and t.get('status') != 'Paid' else ""
            li = TwoLineAvatarIconListItem(text=f"{text}{status_text}", secondary_text=f"{pre} {t['amount']:,.2f} | {t['time']}", on_release=lambda x, i=t: self.handle_click(i))
            li.add_widget(IconLeftWidget(icon=icon, theme_text_color="Custom", text_color=color))
            lst.add_widget(li)
        tot = self.db.get_daily_total(self.active_date)
        lbl = self.root.get_screen('dashboard').ids.daily_total_label
        btn = self.root.get_screen('dashboard').ids.eye_btn
        if self.is_revenue_visible: lbl.text = f"{tot:,.2f} DZD"; btn.icon = "eye"
        else: lbl.text = "****"; btn.icon = "eye-off"
        self.root.get_screen('dashboard').ids.date_label.text = "Today's Net Cash" if self.active_date == datetime.now().strftime("%Y-%m-%d") else f"Net Cash: {self.active_date}"

    def show_date_picker(self):
        picker = MDDatePicker(); picker.bind(on_save=self.on_date_save); picker.open()
    def on_date_save(self, instance, value, date_range):
        self.update_dashboard(value.strftime("%Y-%m-%d"))

    # --- MONTH NAVIGATION ---
    def change_report_month(self, direction):
        m = self.report_date.month + direction; y = self.report_date.year
        if m < 1: m = 12; y -= 1
        elif m > 12: m = 1; y += 1
        self.report_date = self.report_date.replace(year=y, month=m, day=1)
        if self.root.current == "report": self.update_report_list()
        elif self.root.current == "ext_report": self.refresh_external_report_list()

    # --- MANUAL PAYMENTS ---
    def open_manual_payment_dialog(self):
        content = Builder.load_string(KV_MANUAL_PAY)
        self.man_dialog = MDDialog(title="External Payment", type="custom", content_cls=content, buttons=[MDFlatButton(text="SAVE", on_release=self.save_manual_payment)])
        self.man_dialog.open()
    def save_manual_payment(self, x):
        name = self.man_dialog.content_cls.ids.manual_client.text; amt_txt = self.man_dialog.content_cls.ids.manual_amount.text
        if not name or not amt_txt: return
        try:
            amt = float(amt_txt); self.db.add_external_payment(name, amt); self.man_dialog.dismiss()
            pdf = self.generate_versement_pdf(name, amt); toast(f"Saved & PDF: {pdf}"); self.update_dashboard()
        except: toast("Invalid Amount")

    # --- EDIT/DELETE ---
    def open_external_report(self):
        self.root.current = "ext_report"; self.report_date = datetime.now(); self.refresh_external_report_list()
    def refresh_external_report_list(self):
        month_str = self.report_date.strftime("%Y-%m"); display_str = self.report_date.strftime("%B %Y")
        self.root.get_screen('ext_report').ids.ext_toolbar.title = f"Payments: {display_str}"
        lst = self.root.get_screen('ext_report').ids.ext_list; lst.clear_widgets()
        data = self.db.get_monthly_external_payments(month_str)
        if not data: lst.add_widget(OneLineListItem(text="No external payments"))
        for d in data:
            txt = f"{d['client']}: {d['amount']:,.2f} DZD"; note = d['note']
            if d['is_deleted'] == 1: txt = f"[s]{txt}[/s] (DELETED)"; note = "VOIDED TRANSACTION"
            item = ThreeLineListItem(text=txt, secondary_text=f"{d['date']} | {d['time']}", tertiary_text=note, on_release=lambda x, p=d: self.open_edit_payment_dialog(p))
            lst.add_widget(item)
    def open_edit_payment_dialog(self, payment_data):
        if payment_data.get('is_deleted') == 1: toast("Cannot edit deleted payment"); return
        self.current_edit_payment = payment_data
        content = Builder.load_string(KV_EDIT_PAYMENT)
        content.ids.edit_client.text = payment_data['client']; content.ids.edit_amount.text = str(payment_data['amount']); content.ids.edit_note.text = payment_data['note']
        self.edit_pay_dialog = MDDialog(title="Edit Payment (SECURE)", type="custom", content_cls=content, buttons=[MDFlatButton(text="DELETE", theme_text_color="Custom", text_color=(1,0,0,1), on_release=lambda x: self.secure_action(self.delete_payment_confirm)), MDFlatButton(text="SAVE", on_release=lambda x: self.secure_action(self.update_payment_execute))])
        self.edit_pay_dialog.open()
    def update_payment_execute(self):
        c = self.edit_pay_dialog.content_cls
        try:
            amt = float(c.ids.edit_amount.text); name = c.ids.edit_client.text
            self.db.update_payment(self.current_edit_payment['id'], name, amt, c.ids.edit_note.text); self.edit_pay_dialog.dismiss()
            self.update_dashboard(); self.refresh_external_report_list(); pdf = self.generate_versement_pdf(name, amt); toast(f"Updated & New PDF: {pdf}")
        except: toast("Invalid Amount")
    def delete_payment_confirm(self):
        self.db.delete_payment(self.current_edit_payment['id']); self.edit_pay_dialog.dismiss(); self.update_dashboard(); self.refresh_external_report_list(); toast("Payment Marked as Deleted")

    # --- RECEIPTS ---
    def open_new_receipt(self):
        self.cart_items = []; self.cart_total = 0.0; self.current_receipt_id = None
        s = self.root.get_screen('receipt_form'); s.ids.cart_list.clear_widgets(); s.ids.client_name.text = ""; s.ids.amount_paid_input.text = "" 
        self.update_receipt_preview(); self.root.current = "receipt_form"
    def add_to_cart(self):
        s = self.root.get_screen('receipt_form')
        try:
            p = float(s.ids.product_price.text); q = int(s.ids.product_qty.text); n = s.ids.product_name.text
            if not n: return
            t = p*q; self.cart_items.append({"name":n, "price":p, "qty":q, "total":t}); self.cart_total += t
            s.ids.cart_list.add_widget(OneLineListItem(text=f"{q}x {n} - {t:,.2f}"))
            s.ids.product_name.text=""; s.ids.product_price.text=""; s.ids.product_qty.text="1"; self.update_receipt_preview()
        except: pass
    def on_switch_active(self, instance, value):
        s = self.root.get_screen('receipt_form')
        if value: s.ids.amount_paid_input.text = str(self.cart_total)
        else: s.ids.amount_paid_input.text = "0.0"
        self.update_receipt_preview()
    def update_receipt_preview(self, *args):
        s = self.root.get_screen('receipt_form'); s.ids.preview_client.text = f"Client: {s.ids.client_name.text}"; s.ids.preview_date.text = datetime.now().strftime("%Y-%m-%d %H:%M")
        txt = ""; 
        for i in self.cart_items: txt += f"{i['qty']}x {i['name']:<15} {i['total']:,.2f}\n"
        s.ids.preview_items.text = txt; s.ids.preview_total.text = f"TOTAL: {self.cart_total:,.2f}"
        try: paid_now = float(s.ids.amount_paid_input.text)
        except: paid_now = 0.0
        if paid_now >= self.cart_total and self.cart_total > 0: s.ids.status_stamp.text = "PAID"; s.ids.status_stamp.text_color = (0, 0.8, 0, 1)
        elif paid_now > 0: s.ids.status_stamp.text = "PARTIAL"; s.ids.status_stamp.text_color = (1, 0.5, 0, 1)
        else: s.ids.status_stamp.text = "UNPAID"; s.ids.status_stamp.text_color = (0.8, 0, 0, 1)
    def save_receipt(self):
        if not self.cart_items: return
        s = self.root.get_screen('receipt_form'); c = s.ids.client_name.text or "Unknown"; items_txt = ", ".join([f"{i['qty']}x {i['name']}" for i in self.cart_items])
        try: paid_now = float(s.ids.amount_paid_input.text)
        except: paid_now = 0.0
        status = "Paid" if paid_now >= self.cart_total else ("Partial" if paid_now > 0 else "Unpaid")
        self.db.save_receipt(self.current_receipt_id, c, items_txt, json.dumps(self.cart_items), self.cart_total, paid_now, status)
        pdf = self.generate_pdf_receipt(c, status, paid_now); toast(f"Saved: {pdf}"); self.update_dashboard(); self.go_back()
    def generate_pdf_receipt(self, client_name, status, paid_now):
        filename = f"Receipt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        c = canvas.Canvas(filename, pagesize=A6); width, height = A6
        c.setFont("Helvetica-Bold", 14); c.drawCentredString(width/2, height - 20*mm, "YELLES PAP STATIONARY")
        c.setFont("Helvetica", 10); c.drawString(10*mm, height - 35*mm, f"Date: {datetime.now().strftime('%Y-%m-%d')}")
        c.drawString(10*mm, height - 40*mm, f"Client: {client_name}"); c.line(10*mm, height - 45*mm, width - 10*mm, height - 45*mm)
        y = height - 55*mm
        for item in self.cart_items: c.drawString(10*mm, y, f"{item['qty']}x {item['name']}"); c.drawRightString(width - 10*mm, y, f"{item['total']:,.2f}"); y -= 5*mm
        c.line(10*mm, y - 2*mm, width - 10*mm, y - 2*mm); y -= 10*mm
        c.setFont("Helvetica-Bold", 12); c.drawString(10*mm, y, "TOTAL:"); c.drawRightString(width - 10*mm, y, f"{self.cart_total:,.2f} DZD"); y -= 10*mm
        c.setFont("Helvetica", 10); c.drawString(10*mm, y, f"Paid Now: {paid_now:,.2f} DZD"); y -= 10*mm
        c.drawString(10*mm, y, f"Remaining: {max(0, self.cart_total - paid_now):,.2f} DZD")
        stamp_path = "assets/stamp.png"
        if os.path.exists(stamp_path): c.drawImage(stamp_path, width - 40*mm, 15*mm, width=30*mm, height=30*mm, mask='auto')
        else:
            y -= 20*mm; c.saveState(); c.translate(20*mm, y); c.rotate(15); c.setFont("Helvetica-Bold", 24)
            if status == 'Paid': c.setFillColorRGB(0, 0.8, 0, 0.3); c.drawString(0, 0, "PAID")
            elif status == 'Partial': c.setFillColorRGB(1, 0.5, 0, 0.3); c.drawString(0, 0, "PARTIAL")
            else: c.setFillColorRGB(0.8, 0, 0, 0.3); c.drawString(0, 0, "UNPAID")
            c.restoreState()
        c.save(); 
        try: os.startfile(filename)
        except: pass
        return filename
    def load_receipt(self, rid):
        d = self.db.get_receipt_details(rid)
        if not d: return
        self.current_receipt_id = rid; self.cart_items = d['cart']; self.cart_total = d['total']
        s = self.root.get_screen('receipt_form'); s.ids.client_name.text = d['client']
        s.ids.cart_list.clear_widgets()
        for i in self.cart_items: s.ids.cart_list.add_widget(OneLineListItem(text=f"{i['qty']}x {i['name']} - {i['total']}"))
        paid_val = d.get('paid', 0.0); s.ids.amount_paid_input.text = str(paid_val)
        s.ids.paid_switch.active = (d.get('status') == 'Paid')
        self.update_receipt_preview(); self.root.current = "receipt_form"
    def handle_click(self, item):
        if item.get('is_deleted') == 1: toast("Item is deleted"); return
        if item['type'] == 'receipt': self.load_receipt(item['id'])
        elif item['type'] == 'payment': self.open_edit_payment_dialog(item)
        else: toast("History Item (Read Only)")

    # --- CREDITS / DEBTS ---
    def open_credit_screen(self):
        self.root.current = "credits"; lst = self.root.get_screen('credits').ids.credit_list; lst.clear_widgets()
        unpaid = self.db.get_unpaid_receipts()
        for r in unpaid:
            remaining = r['total'] - r['paid']
            li = ThreeLineListItem(text=f"{r['client']}", secondary_text=f"Total: {r['total']} | Paid: {r['paid']}", tertiary_text=f"REMAINING: {remaining:,.2f} DZD (Date: {r['date']})", on_release=lambda x, rid=r['id'], rem=remaining, name=r['client']: self.show_versement_dialog(rid, rem, name))
            lst.add_widget(li)
    def show_versement_dialog(self, receipt_id, remaining, client_name):
        self.temp_receipt_id = receipt_id; self.temp_client_name = client_name
        content = Builder.load_string(KV_VERSEMENT); content.ids.debt_info.text = f"Owes: {remaining:,.2f} DZD"
        self.vers_dialog = MDDialog(title=f"Pay - {client_name}", type="custom", content_cls=content, buttons=[MDFlatButton(text="PAY", on_release=self.confirm_versement)]); self.vers_dialog.open()
    def confirm_versement(self, x):
        try:
            amt = float(self.vers_dialog.content_cls.ids.versement_amount.text); self.db.add_versement(self.temp_receipt_id, amt); toast("Payment Added!"); self.vers_dialog.dismiss()
            pdf = self.generate_versement_pdf(self.temp_client_name, amt); toast(f"PDF Generated: {pdf}"); self.open_credit_screen(); self.update_dashboard()
        except: toast("Invalid Amount")
    def generate_versement_pdf(self, client, amount):
        filename = f"Versement_{client}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        c = canvas.Canvas(filename, pagesize=A6); width, height = A6
        c.setFont("Helvetica-Bold", 14); c.drawCentredString(width/2, height - 20*mm, "YELLES PAP - PAYMENT")
        c.setFont("Helvetica", 10); c.drawString(10*mm, height - 40*mm, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        c.drawString(10*mm, height - 45*mm, f"Client: {client}"); c.line(10*mm, height - 55*mm, width - 10*mm, height - 55*mm)
        c.setFont("Helvetica-Bold", 16); c.drawCentredString(width/2, height - 75*mm, f"RECEIVED: {amount:,.2f} DZD")
        c.setFont("Helvetica", 10); c.drawCentredString(width/2, height - 90*mm, "Thank you for your payment.")
        stamp_path = "assets/stamp.png"
        if os.path.exists(stamp_path): c.drawImage(stamp_path, width - 40*mm, 15*mm, width=30*mm, height=30*mm, mask='auto')
        c.save(); 
        try: os.startfile(filename)
        except: pass
        return filename

    # --- EXPENSES ---
    def open_expense_dialog(self):
        tf = self.root.get_screen('dashboard').ids.quick_amount
        if not tf.text: toast("Enter Amount"); return
        self.temp_expense_amount = float(tf.text)
        content = Builder.load_string(KV_EXPENSE)
        for w in self.db.get_all_workers():
            item = OneLineAvatarIconListItem(text=w, on_release=lambda x, name=w: self.confirm_expense(name))
            item.add_widget(IconLeftWidget(icon="account"))
            content.ids.worker_selection_list.add_widget(item)
        self.exp_dialog = MDDialog(title=f"Take: {self.temp_expense_amount}", type="custom", content_cls=content)
        self.exp_dialog.open()
    def confirm_expense(self, worker):
        note = self.exp_dialog.content_cls.ids.expense_note.text; self.db.add_transaction(self.temp_expense_amount, True, worker, note)
        self.exp_dialog.dismiss(); self.root.get_screen('dashboard').ids.quick_amount.text = ""; self.update_dashboard(); toast(f"Saved: {worker}")
    def add_sale(self):
        tf = self.root.get_screen('dashboard').ids.quick_amount
        if tf.text: self.db.add_transaction(float(tf.text), False, "Store", "Quick Sale"); tf.text=""; self.update_dashboard()

    # --- SETTINGS / REPORTS ---
    def open_settings(self): self.root.current = "settings"; self.refresh_worker_list()
    def change_pin(self):
        s=self.root.get_screen('settings'); o=s.ids.old_pin.text; n=s.ids.new_pin.text; c=s.ids.confirm_pin.text
        if o!=self.db.get_pin(): toast("OLD PIN INCORRECT"); return
        if len(n)==4 and n==c: self.db.update_pin(n); toast("PIN Updated"); s.ids.old_pin.text=""; s.ids.new_pin.text=""; s.ids.confirm_pin.text=""
        else: toast("Check PIN details")
    def open_report_screen(self): self.root.current="report"; self.report_date = datetime.now(); self.update_report_list()
    def update_report_list(self):
        month_str = self.report_date.strftime("%Y-%m"); display_str = self.report_date.strftime("%B %Y")
        self.root.get_screen('report').ids.worker_toolbar.title = f"Expenses: {display_str}"
        lst=self.root.get_screen('report').ids.report_list; lst.clear_widgets()
        for w,a in self.db.get_monthly_worker_expenses(month_str).items():
            if a: lst.add_widget(TwoLineAvatarIconListItem(text=w, secondary_text=f"{a:,.2f} DZD", on_release=lambda x,n=w:self.open_worker_detail(n)))
    def open_worker_detail(self, n):
        self.root.current="worker_detail"; self.root.get_screen('worker_detail').ids.detail_toolbar.title=f"History: {n}"
        lst=self.root.get_screen('worker_detail').ids.detail_list; lst.clear_widgets()
        for h in self.db.get_worker_history(n): lst.add_widget(ThreeLineListItem(text=f"{h['amount']:,.2f} DZD", secondary_text=f"{h['date']} | {h['time']}", tertiary_text=h['note']))
    
    # --- WORKERS ---
    def refresh_worker_list(self):
        lst = self.root.get_screen('settings').ids.worker_list; lst.clear_widgets()
        for w in self.db.get_all_workers():
            li = OneLineAvatarIconListItem(text=w); li.add_widget(IconRightWidget(icon="trash-can", on_release=lambda x, n=w: self.remove_worker(n))); lst.add_widget(li)
    def add_worker(self):
        tf = self.root.get_screen('settings').ids.new_worker_name
        if tf.text: self.db.add_worker(tf.text); tf.text=""; self.refresh_worker_list()
    def remove_worker(self, n): self.db.delete_worker(n); self.refresh_worker_list()

    # --- UTILS ---
    def export_data(self): f=self.db.export_to_csv(); toast(f"Saved: {f}") if f else toast("Error")
    def toggle_revenue_privacy(self): self.secure_action(None)
    def go_back(self): self.root.current = "dashboard"
    def go_back_settings(self): self.root.current = "settings"
    def go_back_report(self): self.root.current = "report"
    def on_stop(self): self.db.close()

if __name__ == "__main__": StoreApp().run()
