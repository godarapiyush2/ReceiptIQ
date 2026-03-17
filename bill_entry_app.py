import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import mysql.connector
import re
import os
import fitz
import cv2
import numpy as np
from paddleocr import PaddleOCR


ocr = PaddleOCR(use_angle_cls=True, lang="en")


def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="YES",
        database="bill_scanner"
    )

def save_to_database(data):

    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO bills (vendor_name,total_amount,products,full_text)
        VALUES (%s,%s,%s,%s)
        """

        values = (
            data['Vendor Name'],
            data['Total Amount'],
            data['Products'],
            data['Full Text']
        )

        cursor.execute(query, values)
        conn.commit()

        cursor.close()
        conn.close()

        messagebox.showinfo("Success","Bill saved to MySQL!")

    except Exception as e:
        messagebox.showerror("Database Error",str(e))

def get_saved_bills():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT vendor_name,total_amount,created_at FROM bills")

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return rows

# ---------------- IMAGE PREPROCESSING ---------------- #

def preprocess_image(path):

    img = cv2.imread(path)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    blur = cv2.GaussianBlur(gray,(5,5),0)

    thresh = cv2.adaptiveThreshold(
        blur,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11,
        2
    )

    return thresh

# ---------------- OCR FUNCTIONS ---------------- #

def extract_text_from_image(path):

    try:

        img = preprocess_image(path)

        result = ocr.ocr(img)

        text = ""

        for line in result:
            for word in line:
                text += word[1][0] + "\n"

        return text

    except Exception as e:
        messagebox.showerror("OCR Error",str(e))
        return None


def extract_text_from_pdf(path):

    try:

        full_text = ""

        with fitz.open(path) as doc:

            for page in doc:

                pix = page.get_pixmap(dpi=300)

                img = np.frombuffer(
                    pix.samples,
                    dtype=np.uint8
                ).reshape(pix.height,pix.width,pix.n)

                result = ocr.ocr(img)

                for line in result:
                    for word in line:
                        full_text += word[1][0] + "\n"

        return full_text

    except Exception as e:
        messagebox.showerror("PDF OCR Error",str(e))
        return None

# ---------------- BILL PARSER ---------------- #

def parse_bill_text(text):

    data = {
        "Vendor Name":"N/A",
        "Total Amount":"N/A",
        "Products":"N/A",
        "Full Text":text
    }

    lines = [line.strip() for line in text.split("\n") if line.strip()]

    # Detect vendor
    for line in lines[:5]:
        if len(line) > 3 and not any(char.isdigit() for char in line):
            data["Vendor Name"] = line
            break

    # Detect total
    total_regex = re.compile(
        r'(total|grand total|amount|due)[^\d]*(\d+[.,]?\d*)',
        re.IGNORECASE
    )

    for line in reversed(lines):

        match = total_regex.search(line)

        if match:
            data["Total Amount"] = match.group(2)
            break

    # Detect items
    items = []

    item_regex = re.compile(r'.*\d+\.\d{2}')

    for line in lines:
        if item_regex.search(line):
            items.append(line)

    if items:
        data["Products"] = "\n".join(items)

    return data

# ---------------- GUI APPLICATION ---------------- #

class BillScannerApp:

    def __init__(self,root):

        self.root = root
        self.root.title("AI Bill Scanner")
        self.root.geometry("850x600")

        self.extracted_data = None
        self.file_path = None

        main_frame = ttk.Frame(root,padding=10)
        main_frame.pack(fill=tk.BOTH,expand=True)

        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X)

        ttk.Button(top_frame,text="Upload Bill",command=self.upload_bill).pack(side=tk.LEFT,padx=5)
        ttk.Button(top_frame,text="Save to Database",command=self.save_data).pack(side=tk.LEFT,padx=5)
        ttk.Button(top_frame,text="View Saved Bills",command=self.view_bills).pack(side=tk.LEFT,padx=5)
        ttk.Button(top_frame,text="Export to Excel",command=self.export_to_excel).pack(side=tk.LEFT,padx=5)

        self.status_label = ttk.Label(top_frame,text="Upload bill to start",relief=tk.SUNKEN)
        self.status_label.pack(side=tk.RIGHT,fill=tk.X,expand=True,padx=5)

        results_frame = ttk.LabelFrame(main_frame,text="Extracted Information")
        results_frame.pack(fill=tk.BOTH,expand=True,pady=10)

        self.tree = ttk.Treeview(results_frame,columns=("Field","Value"),show="headings")

        self.tree.heading("Field",text="Field")
        self.tree.heading("Value",text="Value")

        self.tree.column("Field",width=150)
        self.tree.column("Value",width=600)

        self.tree.pack(fill=tk.BOTH,expand=True)

        text_frame = ttk.LabelFrame(main_frame,text="Full OCR Text")
        text_frame.pack(fill=tk.BOTH,expand=True)

        self.text_widget = tk.Text(text_frame,height=10)
        self.text_widget.pack(fill=tk.BOTH,expand=True)

    # ---------------- FUNCTIONS ---------------- #

    def upload_bill(self):

        self.file_path = filedialog.askopenfilename(
            filetypes=[("Files","*.png *.jpg *.jpeg *.pdf")]
        )

        if not self.file_path:
            return

        ext = os.path.splitext(self.file_path)[1].lower()

        self.status_label.config(text="Processing...")

        if ext == ".pdf":
            raw_text = extract_text_from_pdf(self.file_path)
        else:
            raw_text = extract_text_from_image(self.file_path)

        if raw_text:
            self.extracted_data = parse_bill_text(raw_text)
            self.display_results()
            self.status_label.config(text="Extraction completed")

    def display_results(self):

        for i in self.tree.get_children():
            self.tree.delete(i)

        self.text_widget.delete("1.0",tk.END)

        data = self.extracted_data

        self.tree.insert("",tk.END,values=("Vendor Name",data["Vendor Name"]))
        self.tree.insert("",tk.END,values=("Total Amount",data["Total Amount"]))
        self.tree.insert("",tk.END,values=("Products",data["Products"]))

        self.text_widget.insert(tk.END,data["Full Text"])

    def save_data(self):

        if not self.extracted_data:
            messagebox.showwarning("No Data","Upload bill first")
            return

        save_to_database(self.extracted_data)

    def view_bills(self):

        rows = get_saved_bills()

        window = tk.Toplevel(self.root)
        window.title("Saved Bills")

        tree = ttk.Treeview(window,columns=("Vendor","Amount","Date"),show="headings")

        tree.heading("Vendor",text="Vendor")
        tree.heading("Amount",text="Amount")
        tree.heading("Date",text="Date")

        tree.pack(fill=tk.BOTH,expand=True)

        for row in rows:
            tree.insert("",tk.END,values=row)

    def export_to_excel(self):

        try:

            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT vendor_name,total_amount,products,created_at FROM bills")

            rows = cursor.fetchall()

            df = pd.DataFrame(rows,columns=["Vendor Name","Total Amount","Products","Date"])

            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel Files","*.xlsx")]
            )

            if file_path:
                df.to_excel(file_path,index=False)
                messagebox.showinfo("Success","Excel exported!")

            cursor.close()
            conn.close()

        except Exception as e:
            messagebox.showerror("Export Error",str(e))

# ---------------- RUN APP ---------------- #

if __name__ == "__main__":

    root = tk.Tk()
    app = BillScannerApp(root)
    root.mainloop()