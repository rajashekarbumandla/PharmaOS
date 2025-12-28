# 🏥 PharmacyOS – Smart Pharmacy Management System

PharmacyOS is a full-stack web application designed to digitally manage pharmacy operations such as medicines, batches, inventory, expiry tracking, analytics, reports, and secure user authentication using OTP verification.

It helps pharmacies reduce medicine wastage, maintain accurate stock levels, and make data-driven decisions.

---

## 📌 Problem Statement

Traditional pharmacies often face issues like:
- Manual stock tracking
- Medicine expiry losses
- No batch-wise control
- Lack of reports & analytics
- Security risks in user access

These problems lead to financial loss, inefficiency, and poor decision-making.

---

## 🎯 Project Objectives

- Digitize pharmacy inventory management  
- Track medicines batch-wise using FEFO  
- Reduce expired medicine wastage  
- Provide real-time inventory analytics  
- Secure user access using OTP verification  
- Generate downloadable reports  

---

## 🚀 Features

### 🔐 Authentication & Security
- User Registration & Login
- Email OTP verification
- Password hashing
- Session-based authentication
- Protected routes

---

### 💊 Medicine Management
- Add and manage medicines
- Track medicine type, unit, and total stock
- One medicine can have multiple batches

---

### 📦 Batch Management (FEFO)
- Add batches with:
  - Batch number
  - Expiry date
  - Quantity
- FEFO (First Expired First Out) principle
- Expired batches automatically ignored

---

### 📊 Inventory Dashboard
- Total inventory items
- Unique medicines count
- Expiring soon medicines
- Safe stock overview
- Batch-wise visibility

---

### 📈 Analytics & KPIs
- Stock levels per medicine
- Expiry status distribution
- Key Performance Indicators:
  - Total medicines
  - Active batches
  - Expiring soon count
  - Safe stock ratio

---

### 📄 Reports Module
- View all available medicines
- Batch-wise inventory report
- Download reports in CSV / PDF format

---

### 🔁 Alternative Medicine Suggestions
- Suggests equivalent brands when:
  - Medicine is out of stock
  - Medicine is expired

---

### 🌦️ Seasonal Intelligence
- Identifies seasonal medicine impact
- Highlights medicines with reduced effectiveness
- Suggests additional seasonal medicines

---

## 🧠 Key Concepts Used

- FEFO (First Expired First Out)
- Medicine–Batch relationship
- Inventory KPIs
- Data visualization
- Secure authentication
- Relational database design

---

## 🛠️ Tech Stack

### Backend
- Python
- Flask
- SQLAlchemy
- SQLite / MySQL

### Frontend
- HTML5
- CSS3
- JavaScript
- Chart.js

### Tools & Libraries
- Jinja2
- SMTP (Email OTP)
- Pandas
- ReportLab

---


---

## 🔄 Medicine vs Batch (Important Concept)

| Medicine | Batch |
|--------|-------|
| Logical product | Physical stock unit |
| No expiry date | Has expiry date |
| One medicine | Multiple batches |
| Example: Paracetamol | Batch A (2025), Batch B (2026) |

---

## 📊 KPIs (Key Performance Indicators)

- Total Medicines  
- Total Inventory Items  
- Active Batches  
- Expiring Soon Medicines  
- Safe Stock Count  

These KPIs help pharmacy owners take quick and accurate decisions.

---

## 🔐 OTP Verification Flow

PharmacyOS uses email-based OTP verification to ensure secure user registration and login.

### OTP Flow Steps:
1. User registers using name, email, and password.
2. System generates a 6-digit OTP.
3. OTP is sent to the user’s registered email.
4. User enters OTP on the Verify OTP page.
5. If OTP matches:
   - Account is marked as verified
   - User is redirected to Login
6. If OTP is incorrect or expired:
   - Verification fails
   - User must retry or request a new OTP

### Benefits:
- Prevents fake registrations
- Improves account security
- Ensures verified user access only

---

## 📄 Reports & Downloads

The Reports page provides complete visibility of available medicines and inventory data.

### Reports Page Features:
- Displays all available medicines
- Batch-wise stock details
- Expiry dates and quantities
- Safe and expiring stock identification

### Download Options:
- 📥 Download inventory reports as CSV
- 📄 Download reports as PDF
- Useful for audits, stock reviews, and record keeping

### Benefits:
- Easy data sharing
- Offline access to reports
- Helps in compliance and analysis

---


## 🚀 How to Run PharmaOS (Step-by-Step)

### 1. Clone the Repository
Open your terminal or command prompt and run:
```bash
git clone [https://github.com/rajashekarbumandla/PharmaOS.git](https://github.com/rajashekarbumandla/PharmaOS.git)
cd PharmaOS

```

---

### 2. Create and Activate Virtual Environment

**Windows:**

```bash
python -m venv venv
venv\Scripts\activate

```

**macOS / Linux:**

```bash
python3 -m venv venv
source venv/bin/activate

```

---

### 3. Install Required Libraries

Ensure your virtual environment is active, then run:

```bash
pip install -r requirements.txt

```

---

### 4. Run the Application

Start the Flask server:

```bash
python app.py

```

---

### 5. Open in Browser

Once the server is running, navigate to:
👉 **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 🔑 OTP & Authentication Note

* **Local Run:** The OTP is sent to the registered email address.
* **No Email Configured?** If you haven't set up SMTP credentials, check your **terminal/command prompt** output; the OTP will be printed there.
* **Cloud Deployment:** For hosted versions, check your **server logs** to retrieve the OTP.

```

👥 Team Details
This project was developed for ZENITH25.
Team Name: Bit Bash
Team Lead: B. Rajashekar
Team Members:
Member Name 1:B. Shanmukh Siddhartha
Member Name 2:G. Tejas
Member Name 3.P. Pranav Bharadwaj

