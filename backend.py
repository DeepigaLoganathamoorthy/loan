import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
from datetime import datetime

# Connect to Google Sheets using Streamlit Secrets

def get_gsheet_client():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds_dict = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    client = gspread.authorize(creds)
    return client


# Load all sheets
def load_data(sheet_url):
    client = get_gsheet_client()
    sh = client.open_by_url(sheet_url)

    borrowers_ws = sh.worksheet("borrowers")
    payments_ws = sh.worksheet("payments")

    borrowers = pd.DataFrame(borrowers_ws.get_all_records())
    payments = pd.DataFrame(payments_ws.get_all_records())

    return borrowers, payments, borrowers_ws, payments_ws

# Save borrowers back to Google Sheet
def save_borrowers(df, worksheet):
    worksheet.clear()
    worksheet.update([df.columns.values.tolist()] + df.values.tolist())

# Save payments back to Google Sheet
def save_payments(df, worksheet):
    worksheet.clear()
    worksheet.update([df.columns.values.tolist()] + df.values.tolist())

# Compute balances
def compute_balances(borrowers, payments):
    for idx, row in borrowers.iterrows():
        pid = row["borrower_id"]
        df = payments[payments["borrower_id"] == pid]

        principal_paid = df["principal_paid"].sum() if not df.empty else 0
        interest_paid = df["interest_paid"].sum() if not df.empty else 0

        borrowers.at[idx, "principal_remaining"] = row["principal_total"] - principal_paid
        borrowers.at[idx, "interest_remaining"] = row["interest_total"] - interest_paid

    return borrowers

# Add a new payment
def add_payment(pid, principal, interest, payments):
    new_id = (payments["payment_id"].max() + 1) if len(payments) else 1

    new_row = {
        "payment_id": new_id,
        "borrower_id": pid,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "principal_paid": principal,
        "interest_paid": interest
    }
    payments = pd.concat([payments, pd.DataFrame([new_row])], ignore_index=True)
    return payments

# Add new borrower
def add_borrower(borrowers, name, dept, phone, principal, start_date, months):
    new_id = (borrowers["borrower_id"].max() + 1) if len(borrowers) else 1

    interest_total = principal * 0.10

    new_row = {
        "borrower_id": new_id,
        "name": name,
        "department": dept,
        "phone": phone,
        "principal_total": principal,
        "interest_total": interest_total,
        "loan_start_date": str(start_date),
        "months_to_pay": months,
        "principal_remaining": principal,
        "interest_remaining": interest_total
    }

    borrowers = pd.concat([borrowers, pd.DataFrame([new_row])], ignore_index=True)
    return borrowers

# Monthly summary
def monthly_summary(payments, borrowers, month, year):
    df = payments[
        (pd.to_datetime(payments["date"]).dt.month == month) &
        (pd.to_datetime(payments["date"]).dt.year == year)
    ]

    interest_income = df["interest_paid"].sum()
    principal_income = df["principal_paid"].sum()
    outstanding_interest = borrowers["interest_remaining"].sum()
    outstanding_principal = borrowers["principal_remaining"].sum()

    return {
        "interest_income": interest_income,
        "principal_income": principal_income,
        "outstanding_interest": outstanding_interest,
        "outstanding_principal": outstanding_principal,
        "profit": interest_income
    }


