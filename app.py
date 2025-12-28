from flask import Flask, render_template, request, redirect, session
#from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

import json
from models import db, User, Medicine, Batch
from datetime import datetime, date
from collections import defaultdict
import random
import smtplib
from email.message import EmailMessage

import pandas as pd

from flask import send_file
from io import StringIO, BytesIO
import csv
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import date





# ---------- LOAD CSV DATA ----------
sales_df = pd.read_csv("data1/pharmacy_sales_clean (1)_yourgpt.csv")

# Clean column names
sales_df.columns = sales_df.columns.str.strip()

# Convert date column safely
if "Date" in sales_df.columns:
    sales_df["Date"] = pd.to_datetime(sales_df["Date"], errors="coerce")
elif "Sale_Date" in sales_df.columns:
    sales_df["Date"] = pd.to_datetime(sales_df["Sale_Date"], errors="coerce")


from datetime import date

def get_expiry_status(expiry_date):
    today = date.today()
    days_left = (expiry_date - today).days

    if days_left < 0:
        return "Expired"
    elif days_left <= 30:
        return "Expiring Soon"
    elif days_left <= 90:
        return "Near Expiry"
    else:
        return "Safe"


# ==========================
# APP CONFIG
# ==========================
app = Flask(__name__)
app.secret_key = "hackathon_secret_key"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# ==========================
# USER MODEL
# ==========================


# ==========================
# LOGIN REQUIRED DECORATOR
# ==========================
def login_required(fn):
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect("/login")
        return fn(*args, **kwargs)
    wrapper.__name__ = fn.__name__
    return wrapper

# ==========================
# LOAD NOISY JSON FILES
# ==========================
def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read().strip()
        if not content.startswith("["):
            content = "[" + content
        if not content.endswith("]"):
            content = content + "]"
        return json.loads(content)

# ==========================
# NORMALIZATION
# ==========================
def normalize(name):
    return name.lower().replace("-", " ").strip()

# ==========================
# CLEAN PURCHASES
# ==========================
def clean_purchases(data):
    clean = []
    for r in data:
        if "Batch_Number" not in r:
            continue
        try:
            expiry = datetime.strptime(r["Expiry_Date"], "%Y-%m-%d")
        except:
            continue

        clean.append({
            "Drug_Name": normalize(r["Drug_Name"]),
            "Batch_Number": r["Batch_Number"],
            "Expiry_Date": expiry,
            "Qty_Received": r["Qty_Received"]
        })

    print("Clean purchases:", len(clean))
    return clean

# ==========================
# CLEAN SALES
# ==========================
def clean_sales(data):
    clean = []
    today = datetime.today()

    for r in data:
        try:
            date = datetime.strptime(r["Date"], "%Y-%m-%d")
            if date > today:
                continue
        except:
            continue

        if r["MRP_Unit_Price"] <= 0:
            continue

        clean.append({
            "Drug_Name": normalize(r["Drug_Name"]),
            "Qty_Sold": r["Qty_Sold"],
            "Total_Amount": r["Qty_Sold"] * r["MRP_Unit_Price"]
        })

    print("Clean sales:", len(clean))
    return clean

# ==========================
# LOAD & CLEAN DATA
# ==========================
purchases_raw = load_json("data/pharmacy_purchases_noisy.json")
sales_raw = load_json("data/pharmacy_sales_noisy.json")

purchases = clean_purchases(purchases_raw)
sales = clean_sales(sales_raw)

SEASONAL_MEDICINES = {
    "Monsoon": {
        "medicines": [
            "paracetamol",
            "ors",
            "zinc",
            "azithromycin",
            "amoxicillin"
        ],
        "reason": "Higher cases of viral fever, dehydration, and infections"
    },
    "Winter": {
        "medicines": [
            "paracetamol",
            "cough syrup",
            "cetirizine",
            "vitamin c",
            "vitamin d"
        ],
        "reason": "Cold, cough, flu, and respiratory infections"
    },
    "Summer": {
        "medicines": [
            "ors",
            "electral",
            "vitamin b complex",
            "pantoprazole"
        ],
        "reason": "Dehydration, acidity, and heat-related illness"
    }
}



# ==========================
# ROUTES
# ==========================
@app.route("/")
def index():
    return render_template("index.html")

# ---------- REGISTER ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        if User.query.filter_by(email=email).first():
            return "User already exists"

        otp = str(random.randint(100000, 999999))
        hashed_password = generate_password_hash(password)

        user = User(
            name=name,
            email=email,
            password_hash=hashed_password,
            otp=otp,
            is_verified=False
        )

        db.session.add(user)
        db.session.commit()

        send_otp_email(email, otp)
        session["verify_email"] = email

        return redirect("/verify-otp")

    return render_template("register.html")

@app.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():
    email = session.get("verify_email")

    # If no email in session → go back to register
    if not email:
        return redirect("/register")

    user = User.query.filter_by(email=email).first()

    if not user:
        return redirect("/register")

    if request.method == "POST":
        entered_otp = request.form.get("otp", "").strip()

        # Debug (optional – remove later)
        print("Entered OTP:", entered_otp)
        print("Stored OTP:", user.otp)

        if entered_otp == user.otp:
            user.is_verified = True
            user.otp = None  # clear OTP after success
            db.session.commit()

            session.pop("verify_email", None)
            return redirect("/login")

        # OTP mismatch
        return "Invalid OTP"

    # GET request → show OTP page
    return render_template("verify_otp.html", email=email)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if not user or not user.password_hash:
            return "Invalid credentials"

        if not check_password_hash(user.password_hash, password):
            return "Wrong password"

        if not user.is_verified:
            return "Please verify OTP first"

        session["user_id"] = user.id
        session["user_name"] = user.name

        return redirect("/dashboard")

    return render_template("login.html")



# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")
from collections import defaultdict
from datetime import datetime

# ---------- DASHBOARD ----------
from collections import defaultdict
from datetime import datetime

# ---------- DASHBOARD ----------
@app.route("/dashboard")
@login_required
def dashboard():
    today = datetime.today()

    # ---------- KPIs (FROM PURCHASES) ----------
    medicines = len(set(p["Drug_Name"] for p in purchases))
    batches = len(purchases)

    expiring = len([
        p for p in purchases
        if 0 <= (p["Expiry_Date"] - today).days <= 30
    ])

    # ---------- STOCK CHART ----------
    stock_map = defaultdict(int)
    for p in purchases:
        stock_map[p["Drug_Name"]] += p["Qty_Received"]

    stock_labels = list(stock_map.keys())[:10]
    stock_values = [stock_map[k] for k in stock_labels]

    # ---------- EXPIRY PIE ----------
    expiry_buckets = {"<30 days": 0, "30–90 days": 0, ">90 days": 0}
    for p in purchases:
        days = (p["Expiry_Date"] - today).days
        if days < 30:
            expiry_buckets["<30 days"] += 1
        elif days <= 90:
            expiry_buckets["30–90 days"] += 1
        else:
            expiry_buckets[">90 days"] += 1

    # ---------- CSV-BASED KPIs (FROM data1 CSV) ----------
    total_sales_value = round(sales_df["Total_Amount"].sum(), 2)

    monthly_sales = (
        sales_df
        .dropna(subset=["Date"])
        .groupby(sales_df["Date"].dt.to_period("M"))
        .agg({
            "Qty_Sold": "sum",
            "Total_Amount": "sum"
        })
    )

    avg_medicines_sold = (
        round(monthly_sales["Qty_Sold"].mean(), 1)
        if not monthly_sales.empty else 0
    )

    # ---------- CHART DATA ----------
    months = monthly_sales.index.astype(str).tolist()
    sales_values = monthly_sales["Total_Amount"].round(2).tolist()
    medicines_sold_values = monthly_sales["Qty_Sold"].tolist()

    # ---------- DEBUG (REMOVE LATER) ----------
    print("Total Sales:", total_sales_value)
    print("Avg Medicines Sold:", avg_medicines_sold)

    # ---------- RENDER ----------
    # Determine pharmacy name from session or DB (registered at signup)
    pharmacy_name = session.get("user_name")
    if not pharmacy_name:
        try:
            user = User.query.get(session.get("user_id"))
            pharmacy_name = user.name if user else None
        except Exception:
            pharmacy_name = None

    return render_template(
        "dashboard.html",

        # Purchase-based KPIs
        medicines=medicines,
        batches=batches,
        expiring=expiring,

        # Charts
        stock_labels=stock_labels,
        stock_values=stock_values,
        expiry_labels=list(expiry_buckets.keys()),
        expiry_values=list(expiry_buckets.values()),

        # CSV-based KPIs & charts
        months=months,
        sales_values=sales_values,
        medicines_sold_values=medicines_sold_values,
        total_sales_value=total_sales_value,
        avg_medicines_sold=avg_medicines_sold,

        # Template context: pharmacy name
        pharmacy_name=pharmacy_name
    )



@app.route("/seasonal")
@login_required
def seasonal():
    month = datetime.now().month

    if month in [6, 7, 8, 9]:
        season = "Monsoon"
    elif month in [10, 11, 12, 1]:
        season = "Winter"
    else:
        season = "Summer"

    seasonal_info = SEASONAL_MEDICINES[season]

    # Check which seasonal medicines exist in inventory
    inventory_meds = set(p["Drug_Name"] for p in purchases)

    seasonal_meds = []
    for med in seasonal_info["medicines"]:
        seasonal_meds.append({
            "name": med,
            "available": med in inventory_meds
        })

    # Determine pharmacy name from session or DB
    pharmacy_name = session.get("user_name")
    if not pharmacy_name:
        try:
            user = User.query.get(session.get("user_id"))
            pharmacy_name = user.name if user else None
        except Exception:
            pharmacy_name = None

    return render_template(
        "seasonal_intelligence.html",
        season=season,
        reason=seasonal_info["reason"],
        medicines=seasonal_meds,
        pharmacy_name=pharmacy_name
    )



# ---------- INVENTORY (FEFO) ----------
@app.route("/inventory")
@login_required
def inventory():
    inventory = []
    today = date.today()

    # 1️⃣ JSON-based inventory
    for p in purchases:
       inventory.append({
    "drug": p["Drug_Name"],
    "batch": p["Batch_Number"],
    "expiry": p["Expiry_Date"].date(),
    "qty": p["Qty_Received"],
    "source": "JSON",
    "expiry_status": get_expiry_status(p["Expiry_Date"].date())
})

    # 2️⃣ DB-based inventory (AUTO-REMOVE EXPIRED)
    for b in Batch.query.join(Medicine).all():
        if b.expiry_date < today:
            continue

        inventory.append({
    "drug": b.medicine.name,
    "batch": b.batch_number,
    "expiry": b.expiry_date,
    "qty": b.quantity,
    "source": "USER",
    "expiry_status": get_expiry_status(b.expiry_date)
})


    # 3️⃣ FEFO sorting
    inventory.sort(
        key=lambda x: x["expiry"] if isinstance(x["expiry"], date) else date.max
    )

    # ---------- CHART DATA ----------
    stock_per_medicine = defaultdict(int)
    source_count = defaultdict(int)
    expiry_buckets = {"<30 days": 0, "30-90 days": 0, ">90 days": 0}

    for item in inventory:
        stock_per_medicine[item["drug"]] += item["qty"]
        source_count[item["source"]] += item["qty"]

        days_left = (item["expiry"] - today).days
        if days_left <= 30:
            expiry_buckets["<30 days"] += item["qty"]
        elif days_left <= 90:
            expiry_buckets["30-90 days"] += item["qty"]
        else:
            expiry_buckets[">90 days"] += item["qty"]

    expired_count = Batch.query.filter(Batch.expiry_date < today).count()

    return render_template(
        "inventory.html",
        inventory=inventory,
        expired_count=expired_count,
        stock_labels=list(stock_per_medicine.keys()),
        stock_values=list(stock_per_medicine.values()),
        source_labels=list(source_count.keys()),
        source_values=list(source_count.values()),
        expiry_labels=list(expiry_buckets.keys()),
        expiry_values=list(expiry_buckets.values()),
        now=datetime.now(),
        get_expiry_status=get_expiry_status,
    )

    #return render_template("inventory.html", inventory=inventory)




# ---------- FORECAST ----------
@app.route("/forecast")
@login_required
def forecast():
    demand = {}
    for s in sales:
        demand[s["Drug_Name"]] = demand.get(s["Drug_Name"], 0) + s["Qty_Sold"]

    forecast_data = []
    labels = []
    avg_values = []
    reorder_values = []

    for drug, qty in demand.items():
        avg = qty // 30
        reorder = max(0, avg)

        forecast_data.append({
            "drug": drug,
            "avg": avg,
            "reorder": reorder
        })

        labels.append(drug)
        avg_values.append(avg)
        reorder_values.append(reorder)

    # Determine pharmacy name from session or DB (so template can show user name)
    pharmacy_name = session.get("user_name")
    if not pharmacy_name:
        try:
            user = User.query.get(session.get("user_id"))
            pharmacy_name = user.name if user else None
        except Exception:
            pharmacy_name = None

    return render_template(
        "forecast.html",
        forecast=forecast_data,
        labels=labels,
        avg_values=avg_values,
        reorder_values=reorder_values,
        pharmacy_name=pharmacy_name
    )




# ---------- ALERTS ----------
@app.route("/alerts")
@login_required
def alerts():
    alerts = []
    for p in purchases:
        days = (p["Expiry_Date"] - datetime.today()).days
        if days <= 15:
            alerts.append({
                "drug": p["Drug_Name"],
                "msg": f"Expires in {days} days"
            })
    # Determine pharmacy name from session or DB
    pharmacy_name = session.get("user_name")
    if not pharmacy_name:
        try:
            user = User.query.get(session.get("user_id"))
            pharmacy_name = user.name if user else None
        except Exception:
            pharmacy_name = None

    return render_template("alerts.html", alerts=alerts, pharmacy_name=pharmacy_name)

@app.route("/add_medicine", methods=["GET", "POST"])
@login_required
def add_medicine():
    if request.method == "POST":
        name = normalize(request.form["name"])
        safety = int(request.form["safety_stock"])
        stock = int(request.form["current_stock"])

        med = Medicine(
            name=name,
            safety_stock=safety,
            current_stock=stock
        )
        db.session.add(med)
        db.session.commit()

        return redirect("/inventory")

    return render_template("add_medicine.html")
@app.route("/add_batch", methods=["GET", "POST"])
@login_required
def add_batch():
    medicines = Medicine.query.all()

    if request.method == "POST":
        medicine_id = int(request.form["medicine_id"])
        batch_number = request.form["batch_number"]
        expiry_date = datetime.strptime(
            request.form["expiry_date"], "%Y-%m-%d"
        )
        quantity = int(request.form["quantity"])

        if expiry_date <= datetime.today():
            return "Expiry date must be in the future"

        batch = Batch(
            medicine_id=medicine_id,
            batch_number=batch_number,
            expiry_date=expiry_date,
            quantity=quantity
        )

        db.session.add(batch)

        medicine = Medicine.query.get(medicine_id)
        medicine.current_stock += quantity

        db.session.commit()

        return redirect("/inventory")

    return render_template("add_batch.html", medicines=medicines)

import os
import smtplib
from email.message import EmailMessage

def send_otp_email(to_email, otp):
    try:
        EMAIL_USER = os.environ.get("EMAIL_USER")
        EMAIL_PASS = os.environ.get("EMAIL_PASS")

        if not EMAIL_USER or not EMAIL_PASS:
            print("Email env variables missing")
            return False

        msg = EmailMessage()
        msg["Subject"] = "PharmaOS OTP Verification"
        msg["From"] = EMAIL_USER
        msg["To"] = to_email
        msg.set_content(f"""
Hello,

Your OTP for PharmaOS login is:

{otp}

This OTP is valid for 5 minutes.

– PharmaOS Team
""")

        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as server:
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)

        return True

    except Exception as e:
        print("OTP Email Error:", e)
        return False




@app.route("/google-login")
def google_login():
    if not google.authorized:
        return redirect(url_for("google.login"))

    resp = google.get("/oauth2/v2/userinfo")
    info = resp.json()

    email = info["email"]
    name = info["name"]

    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(name=name, email=email, is_verified=True)
        db.session.add(user)
        db.session.commit()

    session["user_id"] = user.id
    session["user_name"] = user.name
    return redirect("/dashboard")

from chatbot_pandas import chatbot_response
from flask import jsonify
@app.route("/chatbot")
def chatbot_page():
    return render_template("chatbot.html")


@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("message", "")
    reply = chatbot_response(user_msg)
    return jsonify({"reply": reply})


def build_medicine_report():
    today = date.today()
    report = []

    medicines = Medicine.query.all()

    for med in medicines:
        batches = Batch.query.filter_by(medicine_id=med.id).all()
        active_batches = [b for b in batches if b.expiry_date >= today]
        expired_batches = [b for b in batches if b.expiry_date < today]

        nearest_expiry = (
            min([b.expiry_date for b in active_batches])
            if active_batches else None
        )

        # Stock status
        if med.current_stock == 0:
            status = "Out of Stock"
        elif med.current_stock <= med.safety_stock:
            status = "Low Stock"
        else:
            status = "Safe"

        report.append({
            "name": med.name,
            "stock": med.current_stock,
            "active_batches": len(active_batches),
            "expired_batches": len(expired_batches),
            "nearest_expiry": nearest_expiry,
            "status": status
        })

    return report
@app.route("/reports")
@login_required
def reports():
    report_data = build_medicine_report()
    return render_template("reports.html", reports=report_data)
@app.route("/reports/download/csv")
@login_required
def download_reports_csv():
    report_data = build_medicine_report()

    output = StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "Medicine",
        "Total Stock",
        "Active Batches",
        "Expired Batches",
        "Nearest Expiry",
        "Status"
    ])

    for r in report_data:
        writer.writerow([
            r["name"],
            r["stock"],
            r["active_batches"],
            r["expired_batches"],
            r["nearest_expiry"],
            r["status"]
        ])

    output.seek(0)

    return send_file(
        BytesIO(output.getvalue().encode()),
        mimetype="text/csv",
        as_attachment=True,
        download_name="medicine_report.csv"
    )
@app.route("/reports/download/pdf")
@login_required
def download_reports_pdf():
    report_data = build_medicine_report()

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    y = height - 40
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(40, y, "Pharmacy Medicine Report")
    y -= 30

    pdf.setFont("Helvetica", 10)

    headers = ["Medicine", "Stock", "Active", "Expired", "Nearest Expiry", "Status"]
    x_positions = [40, 170, 230, 300, 370, 470]

    for i, h in enumerate(headers):
        pdf.drawString(x_positions[i], y, h)

    y -= 15
    pdf.line(40, y, 550, y)
    y -= 15

    for r in report_data:
        if y < 50:
            pdf.showPage()
            y = height - 50

        pdf.drawString(40, y, r["name"])
        pdf.drawString(170, y, str(r["stock"]))
        pdf.drawString(230, y, str(r["active_batches"]))
        pdf.drawString(300, y, str(r["expired_batches"]))
        pdf.drawString(370, y, str(r["nearest_expiry"]))
        pdf.drawString(470, y, r["status"])
        y -= 15

    pdf.save()
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="medicine_report.pdf",
        mimetype="application/pdf"
    )





# ==========================
# RUN
# ==========================
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(host="0.0.0.0", port=5000)
