# 🧾 ReceiptIQ – Intelligent Receipt Processing System

ReceiptIQ is an AI-powered desktop application that automates receipt and invoice data extraction using OCR. It processes images and PDFs to identify vendor details, total amounts, and purchased items, then stores the structured data in a MySQL database with options to view and export it to Excel.


## 🚀 Features

* 📂 Upload receipts in **Image (JPG, PNG)** or **PDF** format
* 🔍 Extract text using **PaddleOCR**
* 🧠 Automatically detect:

  * Vendor Name
  * Total Amount
  * Product List
* 💾 Save extracted data to **MySQL database**
* 📊 View saved bills in GUI
* 📁 Export data to **Excel (.xlsx)**
* 🖥️ User-friendly **Tkinter interface**


## 🛠️ Technologies Used

* **OCR Engine:** PaddleOCR
* **Image Processing:** OpenCV
* **PDF Processing:** PyMuPDF (fitz)
* **Frontend (GUI):** Tkinter
* **Database:** MySQL
* **Data Handling & Export:** Pandas


## 🧠 How It Works

1. Upload a receipt (image or PDF)
2. Image is preprocessed using OpenCV
3. PaddleOCR extracts text
4. Regex-based parsing extracts key details
5. Data is displayed in GUI
6. Data is stored in MySQL
7. Export to Excel if needed
   

## 🗄️ Database Setup

### Create Database

```sql
CREATE DATABASE bill_scanner;
```

### Create Table

```sql
CREATE TABLE bills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vendor_name VARCHAR(255),
    total_amount VARCHAR(50),
    products TEXT,
    full_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```


## ⚙️ Installation

### 1. Clone Repository

```bash
git clone https://github.com/godarapiyush2/receiptiq-ai.git
cd receiptiq-ai
```

### 2. Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install paddleocr opencv-python pandas pymysql mysql-connector-python pymupdf numpy
```

---

## ▶️ Run the Application

```bash
python bill_entry_app.py
```

---

## ⚠️ Known Issues

* OCR accuracy depends on image quality
* Complex bill formats may not parse perfectly
* PaddleOCR installation may require additional setup on some systems


## 🔮 Future Improvements

* 🤖 AI-based smart categorization
* 📱 Mobile version
* ☁️ Cloud database integration
* 📊 Expense analytics dashboard


## 👨‍💻 Author

**Piyush**


## ⭐ Project Tagline

**“Turn receipts into structured data instantly.”**


## 📜 License

This project is open-source and free to use.
