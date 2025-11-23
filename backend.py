# import streamlit as st
# import gspread
# import pandas as pd
# from google.oauth2.service_account import Credentials
# from datetime import datetime

# # Connect to Google Sheets using Streamlit Secrets

# def get_gsheet_client():
#     scopes = [
#         "https://www.googleapis.com/auth/spreadsheets",
#         "https://www.googleapis.com/auth/drive"
#     ]
#     creds_dict = st.secrets["gcp_service_account"]
#     creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
#     client = gspread.authorize(creds)
#     return client


# # Load all sheets
# def load_data(sheet_url):
#     client = get_gsheet_client()
#     sh = client.open_by_url(sheet_url)

#     borrowers_ws = sh.worksheet("borrowers")
#     payments_ws = sh.worksheet("payments")

#     borrowers = pd.DataFrame(borrowers_ws.get_all_records())
#     payments = pd.DataFrame(payments_ws.get_all_records())

#     return borrowers, payments, borrowers_ws, payments_ws

# # Save borrowers back to Google Sheet
# def save_borrowers(df, worksheet):
#     worksheet.clear()
#     worksheet.update([df.columns.values.tolist()] + df.values.tolist())

# # Save payments back to Google Sheet
# def save_payments(df, worksheet):
#     worksheet.clear()
#     worksheet.update([df.columns.values.tolist()] + df.values.tolist())

# # Compute balances
# def compute_balances(borrowers, payments):
#     for idx, row in borrowers.iterrows():
#         pid = row["borrower_id"]
#         df = payments[payments["borrower_id"] == pid]

#         principal_paid = df["principal_paid"].sum() if not df.empty else 0
#         interest_paid = df["interest_paid"].sum() if not df.empty else 0

#         borrowers.at[idx, "principal_remaining"] = row["principal_total"] - principal_paid
#         borrowers.at[idx, "interest_remaining"] = row["interest_total"] - interest_paid

#     return borrowers

# # Add a new payment
# def add_payment(pid, principal, interest, payments):
#     new_id = (payments["payment_id"].max() + 1) if len(payments) else 1

#     new_row = {
#         "payment_id": new_id,
#         "borrower_id": pid,
#         "date": datetime.now().strftime("%Y-%m-%d"),
#         "principal_paid": principal,
#         "interest_paid": interest
#     }
#     payments = pd.concat([payments, pd.DataFrame([new_row])], ignore_index=True)
#     return payments

# # Add new borrower
# def add_borrower(borrowers, name, dept, phone, principal, start_date, months):
#     new_id = (borrowers["borrower_id"].max() + 1) if len(borrowers) else 1

#     interest_total = principal * 0.10

#     new_row = {
#         "borrower_id": new_id,
#         "name": name,
#         "department": dept,
#         "phone": phone,
#         "principal_total": principal,
#         "interest_total": interest_total,
#         "loan_start_date": str(start_date),
#         "months_to_pay": months,
#         "principal_remaining": principal,
#         "interest_remaining": interest_total
#     }

#     borrowers = pd.concat([borrowers, pd.DataFrame([new_row])], ignore_index=True)
#     return borrowers

# # Monthly summary
# def monthly_summary(payments, borrowers, month, year):
#     df = payments[
#         (pd.to_datetime(payments["date"]).dt.month == month) &
#         (pd.to_datetime(payments["date"]).dt.year == year)
#     ]

#     interest_income = df["interest_paid"].sum()
#     principal_income = df["principal_paid"].sum()
#     outstanding_interest = borrowers["interest_remaining"].sum()
#     outstanding_principal = borrowers["principal_remaining"].sum()

#     return {
#         "interest_income": interest_income,
#         "principal_income": principal_income,
#         "outstanding_interest": outstanding_interest,
#         "outstanding_principal": outstanding_principal,
#         "profit": interest_income
#     }

import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import numpy as np

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

# Load all sheets with error handling
@st.cache_data(ttl=60)
def load_data(sheet_url):
    try:
        client = get_gsheet_client()
        sh = client.open_by_url(sheet_url)
        borrowers_ws = sh.worksheet("borrowers")
        payments_ws = sh.worksheet("payments")
        
        borrowers = pd.DataFrame(borrowers_ws.get_all_records())
        payments = pd.DataFrame(payments_ws.get_all_records())
        
        # Convert data types
        if not borrowers.empty:
            borrowers['principal_total'] = pd.to_numeric(borrowers['principal_total'], errors='coerce')
            borrowers['interest_total'] = pd.to_numeric(borrowers['interest_total'], errors='coerce')
            borrowers['principal_remaining'] = pd.to_numeric(borrowers['principal_remaining'], errors='coerce')
            borrowers['interest_remaining'] = pd.to_numeric(borrowers['interest_remaining'], errors='coerce')
            borrowers['months_to_pay'] = pd.to_numeric(borrowers['months_to_pay'], errors='coerce')
        
        if not payments.empty:
            payments['principal_paid'] = pd.to_numeric(payments['principal_paid'], errors='coerce')
            payments['interest_paid'] = pd.to_numeric(payments['interest_paid'], errors='coerce')
            payments['date'] = pd.to_datetime(payments['date'], errors='coerce')
        
        return borrowers, payments, borrowers_ws, payments_ws
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame(), pd.DataFrame(), None, None

# Save borrowers back to Google Sheet
def save_borrowers(df, worksheet):
    try:
        worksheet.clear()
        worksheet.update([df.columns.values.tolist()] + df.values.tolist())
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Error saving borrowers: {str(e)}")
        return False

# Save payments back to Google Sheet
def save_payments(df, worksheet):
    try:
        worksheet.clear()
        worksheet.update([df.columns.values.tolist()] + df.values.tolist())
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Error saving payments: {str(e)}")
        return False

# Compute balances and payment status
def compute_balances(borrowers, payments):
    if borrowers.empty:
        return borrowers
    
    for idx, row in borrowers.iterrows():
        pid = row["borrower_id"]
        df = payments[payments["borrower_id"] == pid]
        principal_paid = df["principal_paid"].sum() if not df.empty else 0
        interest_paid = df["interest_paid"].sum() if not df.empty else 0
        borrowers.at[idx, "principal_remaining"] = row["principal_total"] - principal_paid
        borrowers.at[idx, "interest_remaining"] = row["interest_total"] - interest_paid
    return borrowers

# Calculate payment schedule
def calculate_payment_schedule(principal, interest_rate, months, start_date):
    monthly_principal = principal / months
    monthly_interest = (principal * interest_rate) / months
    
    schedule = []
    current_date = pd.to_datetime(start_date)
    
    for month in range(1, months + 1):
        payment_date = current_date + timedelta(days=30 * month)
        schedule.append({
            'month': month,
            'due_date': payment_date.strftime('%Y-%m-%d'),
            'principal_due': monthly_principal,
            'interest_due': monthly_interest,
            'total_due': monthly_principal + monthly_interest
        })
    
    return pd.DataFrame(schedule)

# Get payment history for borrower
def get_payment_history(borrower_id, payments):
    if payments.empty:
        return pd.DataFrame()
    
    history = payments[payments["borrower_id"] == borrower_id].copy()
    if not history.empty:
        history = history.sort_values('date', ascending=False)
        history['total_paid'] = history['principal_paid'] + history['interest_paid']
    return history

# Add a new payment
def add_payment(pid, principal, interest, payments):
    new_id = int(payments["payment_id"].max() + 1) if len(payments) > 0 else 1
    new_row = {
        "payment_id": new_id,
        "borrower_id": int(pid),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "principal_paid": float(principal),
        "interest_paid": float(interest)
    }
    payments = pd.concat([payments, pd.DataFrame([new_row])], ignore_index=True)
    return payments

# Add new borrower
def add_borrower(borrowers, name, dept, phone, principal, interest_rate, start_date, months):
    new_id = int(borrowers["borrower_id"].max() + 1) if len(borrowers) > 0 else 1
    interest_total = principal * interest_rate
    new_row = {
        "borrower_id": new_id,
        "name": name,
        "department": dept,
        "phone": phone,
        "principal_total": float(principal),
        "interest_total": float(interest_total),
        "loan_start_date": str(start_date),
        "months_to_pay": int(months),
        "principal_remaining": float(principal),
        "interest_remaining": float(interest_total)
    }
    borrowers = pd.concat([borrowers, pd.DataFrame([new_row])], ignore_index=True)
    return borrowers

# Monthly summary with enhanced metrics
def monthly_summary(payments, borrowers, month, year):
    if payments.empty:
        df = pd.DataFrame()
    else:
        payments_copy = payments.copy()
        payments_copy['date'] = pd.to_datetime(payments_copy['date'], errors='coerce')
        df = payments_copy[
            (payments_copy["date"].dt.month == month) &
            (payments_copy["date"].dt.year == year)
        ]
    
    interest_income = df["interest_paid"].sum() if not df.empty else 0
    principal_income = df["principal_paid"].sum() if not df.empty else 0
    outstanding_interest = borrowers["interest_remaining"].sum() if not borrowers.empty else 0
    outstanding_principal = borrowers["principal_remaining"].sum() if not borrowers.empty else 0
    
    return {
        "interest_income": interest_income,
        "principal_income": principal_income,
        "outstanding_interest": outstanding_interest,
        "outstanding_principal": outstanding_principal,
        "profit": interest_income,
        "total_collected": interest_income + principal_income,
        "num_payments": len(df)
    }

# Get dashboard statistics
def get_dashboard_stats(borrowers, payments):
    total_loans = len(borrowers)
    active_loans = len(borrowers[borrowers['principal_remaining'] > 0])
    total_principal_out = borrowers['principal_remaining'].sum()
    total_interest_out = borrowers['interest_remaining'].sum()
    total_outstanding = total_principal_out + total_interest_out
    
    # Calculate collection rate
    if not borrowers.empty:
        total_expected = borrowers['principal_total'].sum() + borrowers['interest_total'].sum()
        total_collected = total_expected - total_outstanding
        collection_rate = (total_collected / total_expected * 100) if total_expected > 0 else 0
    else:
        collection_rate = 0
    
    return {
        'total_loans': total_loans,
        'active_loans': active_loans,
        'total_outstanding': total_outstanding,
        'principal_outstanding': total_principal_out,
        'interest_outstanding': total_interest_out,
        'collection_rate': collection_rate
    }


