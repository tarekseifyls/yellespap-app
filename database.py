import sqlite3
import json
import csv
from datetime import datetime

class StoreDatabase:
    def __init__(self, db_name="store_data.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()
        self.perform_migrations()

    def create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS quick_sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL,
                is_expense INTEGER DEFAULT 0,
                worker_name TEXT, 
                note TEXT,
                date_str TEXT,
                time_str TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS receipts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_name TEXT,
                items_text TEXT,
                items_json TEXT, 
                total_price REAL,
                amount_paid REAL,
                status TEXT, 
                date_str TEXT,
                time_str TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                receipt_id INTEGER,
                client_name TEXT,
                amount REAL,
                date_str TEXT,
                time_str TEXT,
                note TEXT,
                is_deleted INTEGER DEFAULT 0
            )
        """)
        self.cursor.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS workers (name TEXT PRIMARY KEY)")
        self.cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('pin', '0000')")
        self.cursor.execute("INSERT OR IGNORE INTO workers (name) VALUES ('Store Expense')")
        self.conn.commit()

    def perform_migrations(self):
        try:
            self.cursor.execute("SELECT client_name FROM payments LIMIT 1")
        except sqlite3.OperationalError:
            self.cursor.execute("ALTER TABLE payments ADD COLUMN client_name TEXT")
            self.conn.commit()
        try:
            self.cursor.execute("SELECT is_deleted FROM payments LIMIT 1")
        except sqlite3.OperationalError:
            self.cursor.execute("ALTER TABLE payments ADD COLUMN is_deleted INTEGER DEFAULT 0")
            self.conn.commit()

    # --- PAYMENT EDITING ---
    def update_payment(self, payment_id, client_name, new_amount, new_note):
        self.cursor.execute("SELECT receipt_id FROM payments WHERE id=?", (payment_id,))
        row = self.cursor.fetchone()
        receipt_id = row[0] if row else None
        self.cursor.execute("UPDATE payments SET client_name=?, amount=?, note=? WHERE id=?", (client_name, new_amount, new_note, payment_id))
        if receipt_id: self.recalculate_receipt_balance(receipt_id)
        self.conn.commit()

    def delete_payment(self, payment_id):
        self.cursor.execute("SELECT receipt_id FROM payments WHERE id=?", (payment_id,))
        row = self.cursor.fetchone()
        receipt_id = row[0] if row else None
        self.cursor.execute("UPDATE payments SET is_deleted=1 WHERE id=?", (payment_id,))
        if receipt_id: self.recalculate_receipt_balance(receipt_id)
        self.conn.commit()

    def recalculate_receipt_balance(self, receipt_id):
        self.cursor.execute("SELECT SUM(amount) FROM payments WHERE receipt_id=? AND is_deleted=0", (receipt_id,))
        result = self.cursor.fetchone()
        total_paid = result[0] if result[0] else 0.0
        self.cursor.execute("SELECT total_price FROM receipts WHERE id=?", (receipt_id,))
        row = self.cursor.fetchone()
        if not row: return
        total_price = row[0]
        if total_paid >= total_price: status = "Paid"
        elif total_paid > 0: status = "Partial"
        else: status = "Unpaid"
        self.cursor.execute("UPDATE receipts SET amount_paid=?, status=? WHERE id=?", (total_paid, status, receipt_id))

    # --- EXTERNAL PAYMENTS ---
    def add_external_payment(self, client_name, amount, note="Manual Payment"):
        now = datetime.now()
        self.cursor.execute("INSERT INTO payments (receipt_id, client_name, amount, date_str, time_str, note, is_deleted) VALUES (NULL, ?, ?, ?, ?, ?, 0)", 
                            (client_name, amount, now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S"), note))
        self.conn.commit()

    def get_monthly_external_payments(self, month_str=None):
        if not month_str: month_str = datetime.now().strftime("%Y-%m")
        self.cursor.execute("SELECT id, client_name, amount, date_str, time_str, note, is_deleted FROM payments WHERE receipt_id IS NULL AND date_str LIKE ? ORDER BY date_str DESC, time_str DESC", (f"{month_str}%",))
        return [{"id": r[0], "client": r[1], "amount": r[2], "date": r[3], "time": r[4], "note": r[5], "is_deleted": r[6]} for r in self.cursor.fetchall()]

    # --- CORE TOTALS ---
    def get_daily_total(self, date_str=None):
        if not date_str: date_str = datetime.now().strftime("%Y-%m-%d")
        self.cursor.execute("SELECT amount FROM quick_sales WHERE date_str=? AND is_expense=0", (date_str,))
        total = sum(r[0] for r in self.cursor.fetchall())
        self.cursor.execute("SELECT amount FROM quick_sales WHERE date_str=? AND is_expense=1", (date_str,))
        total -= sum(r[0] for r in self.cursor.fetchall())
        self.cursor.execute("SELECT amount FROM payments WHERE date_str=? AND is_deleted=0", (date_str,))
        total += sum(r[0] for r in self.cursor.fetchall())
        return total

    def get_daily_transactions(self, date_str=None):
        if not date_str: date_str = datetime.now().strftime("%Y-%m-%d")
        items = []
        self.cursor.execute("SELECT id, amount, is_expense, worker_name, note, time_str FROM quick_sales WHERE date_str=?", (date_str,))
        for r in self.cursor.fetchall():
            items.append({"type": "expense" if r[2] else "quick", "id": r[0], "amount": r[1], "time": r[5], "desc": r[4] or ("Expense" if r[2] else "Quick Sale")})
        self.cursor.execute("SELECT id, client_name, total_price, status, time_str FROM receipts WHERE date_str=?", (date_str,))
        for r in self.cursor.fetchall():
            items.append({"type": "receipt", "id": r[0], "amount": r[2], "time": r[4], "desc": f"Receipt: {r[1]}", "status": r[3]})
        self.cursor.execute("SELECT p.id, p.amount, p.time_str, p.client_name, r.client_name, p.note, p.is_deleted FROM payments p LEFT JOIN receipts r ON p.receipt_id = r.id WHERE p.date_str=?", (date_str,))
        for r in self.cursor.fetchall():
            client = r[4] if r[4] else r[3]
            note = "Versement" if r[4] else "Ext. Payment"
            desc = f"{note}: {client}"
            if r[5]: desc += f" ({r[5]})"
            if r[6] == 1: desc = f"[s]{desc}[/s] (DELETED)"
            if "Initial Payment" not in (r[5] or ""):
                items.append({"type": "payment", "id": r[0], "amount": r[1], "time": r[2], "desc": desc, "client": client, "note": r[5] or "", "is_deleted": r[6]})
        items.sort(key=lambda x: x['time'], reverse=True)
        return items

    # --- STANDARD LOGIC ---
    def save_receipt(self, rid, client, txt, js, total, initial_payment, status):
        now = datetime.now()
        if rid:
            self.cursor.execute("UPDATE receipts SET client_name=?, items_text=?, items_json=?, total_price=?, amount_paid=?, status=? WHERE id=?", 
                                (client, txt, js, total, initial_payment, status, rid))
        else:
            self.cursor.execute("INSERT INTO receipts (client_name, items_text, items_json, total_price, amount_paid, status, date_str, time_str) VALUES (?,?,?,?,?,?,?,?)", 
                                (client, txt, js, total, initial_payment, status, now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S")))
            if initial_payment > 0:
                rid = self.cursor.lastrowid
                self.record_payment(rid, initial_payment, "Initial Payment", client)
        self.conn.commit()

    def record_payment(self, receipt_id, amount, note, client_name=None):
        now = datetime.now()
        self.cursor.execute("INSERT INTO payments (receipt_id, client_name, amount, date_str, time_str, note, is_deleted) VALUES (?, ?, ?, ?, ?, ?, 0)", 
                            (receipt_id, client_name, amount, now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S"), note))
        self.conn.commit()

    def add_versement(self, receipt_id, amount):
        self.cursor.execute("SELECT total_price, amount_paid, client_name FROM receipts WHERE id=?", (receipt_id,))
        row = self.cursor.fetchone()
        if row:
            self.record_payment(receipt_id, amount, "Versement", row[2])
            new_paid = row[1] + amount
            new_status = "Paid" if new_paid >= row[0] else "Partial"
            self.cursor.execute("UPDATE receipts SET amount_paid=?, status=? WHERE id=?", (new_paid, new_status, receipt_id))
            self.conn.commit()

    def get_receipt_details(self, rid):
        self.cursor.execute("SELECT * FROM receipts WHERE id=?", (rid,))
        r = self.cursor.fetchone()
        if r: return {"id": r[0], "client": r[1], "cart": json.loads(r[3]), "total": r[4], "paid": r[5], "status": r[6], "date": r[7]}
        return None

    def get_unpaid_receipts(self):
        self.cursor.execute("SELECT * FROM receipts WHERE status != 'Paid' ORDER BY date_str DESC")
        return [{"id": r[0], "client": r[1], "total": r[4], "paid": r[5], "date": r[7]} for r in self.cursor.fetchall()]

    # Workers
    def add_worker(self, name):
        try: self.cursor.execute("INSERT INTO workers (name) VALUES (?)", (name,)); self.conn.commit(); return True
        except: return False
    def delete_worker(self, name): self.cursor.execute("DELETE FROM workers WHERE name=?", (name,)); self.conn.commit()
    def get_all_workers(self): self.cursor.execute("SELECT name FROM workers"); return [row[0] for row in self.cursor.fetchall()]
    def get_monthly_worker_expenses(self, m=None):
        if not m: m = datetime.now().strftime("%Y-%m")
        self.cursor.execute("SELECT worker_name, SUM(amount) FROM quick_sales WHERE is_expense=1 AND date_str LIKE ? GROUP BY worker_name", (f"{m}%",))
        return {r[0]: r[1] for r in self.cursor.fetchall()}
    def get_worker_history(self, name):
        self.cursor.execute("SELECT amount, date_str, time_str, note FROM quick_sales WHERE is_expense=1 AND worker_name=? ORDER BY date_str DESC", (name,))
        return [{"amount": r[0], "date": r[1], "time": r[2], "note": r[3]} for r in self.cursor.fetchall()]

    # Utils
    def get_pin(self): self.cursor.execute("SELECT value FROM settings WHERE key='pin'"); return self.cursor.fetchone()[0]
    def update_pin(self, v): self.cursor.execute("UPDATE settings SET value=? WHERE key='pin'", (v,)); self.conn.commit()
    def add_transaction(self, amt, is_exp, w, n):
        now = datetime.now()
        self.cursor.execute("INSERT INTO quick_sales (amount, is_expense, worker_name, note, date_str, time_str) VALUES (?,?,?,?,?,?)", 
                            (amt, 1 if is_exp else 0, w, n, now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S")))
        self.conn.commit()
    def export_to_csv(self):
        filename = f"Store_Export_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.csv"
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Type", "Date", "Who", "Description", "Amount", "Status"])
                self.cursor.execute("SELECT * FROM quick_sales")
                for r in self.cursor.fetchall(): writer.writerow(["Cash", r[5], r[3], r[4], r[1], "Valid"])
                self.cursor.execute("SELECT * FROM payments")
                for r in self.cursor.fetchall(): 
                    status = "DELETED" if r[7] else "Valid"
                    writer.writerow(["Payment", r[4], r[2], r[6], r[3], status])
            return filename
        except: return None
    def close(self): self.conn.close()
