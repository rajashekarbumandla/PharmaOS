import pandas as pd

# ---------- LOAD DATA ----------
purchase_df = pd.read_csv("data1/pharmacy_purchases_noisy (1).csv")
sales_df = pd.read_csv("data1/pharmacy_sales_clean (1)_yourgpt.csv")

# ---------- CLEAN ----------
purchase_df["Drug_Name"] = purchase_df["Drug_Name"].str.lower().str.strip()
sales_df["Drug_Name"] = sales_df["Drug_Name"].str.lower().str.strip()

# ---------- STOCK ----------
def get_stock(drug):
    received = purchase_df[purchase_df["Drug_Name"] == drug]["Qty_Received"].sum()
    sold = sales_df[sales_df["Drug_Name"] == drug]["Qty_Sold"].sum()

    if received == 0:
        return None

    stock = received - sold
    return f"The current stock of {drug.title()} is {int(stock)} units."


# ---------- EXPIRY ----------
def get_expiry(drug):
    rows = purchase_df[purchase_df["Drug_Name"] == drug]
    if rows.empty:
        return None

    expiry_dates = rows["Expiry_Date"].dropna().unique().tolist()
    return f"{drug.title()} batches expire on: {expiry_dates}."


# ---------- SALES ----------
def get_sales(drug):
    rows = sales_df[sales_df["Drug_Name"] == drug]
    if rows.empty:
        return None

    total_qty = int(rows["Qty_Sold"].sum())
    total_amt = rows["Total_Amount"].sum()

    return (
        f"Total sales of {drug.title()}: {total_qty} units, "
        f"Revenue: ₹{total_amt:.2f}."
    )


# ---------- SUPPLIER ----------
def get_supplier(drug):
    rows = purchase_df[purchase_df["Drug_Name"] == drug]
    if rows.empty:
        return None

    suppliers = rows["Supplier_Name"].dropna().unique().tolist()
    return f"{drug.title()} supplied by: {suppliers}."


# ---------- CHATBOT ----------
def chatbot_response(query):
    q = query.lower().strip()

    # Greeting
    if q in ["hi", "hello", "hey"]:
        return "Hello 👋 I can help with stock, expiry, sales, or supplier details."

    # Find drug name
    drug_found = None
    for drug in purchase_df["Drug_Name"].unique():
        if drug in q:
            drug_found = drug
            break

    if drug_found is None:
        return "❌ Drug not found in records."

    if "stock" in q:
        return get_stock(drug_found) or "Stock data not available."

    if "expiry" in q or "expire" in q:
        return get_expiry(drug_found) or "Expiry data not available."

    if "sale" in q or "sold" in q:
        return get_sales(drug_found) or "Sales data not available."

    if "supplier" in q:
        return get_supplier(drug_found) or "Supplier data not available."

    return "Please ask about stock, expiry, sales, or supplier."
