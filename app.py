import streamlit as st
import pandas as pd
from datetime import datetime
from backend import (
    load_data, compute_balances,
    add_payment, add_borrower,
    save_borrowers, save_payments,
    monthly_summary
)

SHEET_URL = "https://docs.google.com/spreadsheets/d/1pS0OCxO8tg85gVdOz8XeVw_WAvmXeVLHGHWompwFPjo/edit"


st.set_page_config(page_title="Family Loan Tracker", layout="wide")

st.title("📘 Family Loan Management System")

borrowers, payments, borrowers_ws, payments_ws = load_data(SHEET_URL)
borrowers = compute_balances(borrowers, payments)

tab1, tab2, tab3 = st.tabs(["Existing Borrower", "New Borrower", "Monthly Report"])

# ---------------- EXISTING BORROWER ----------------
with tab1:
    names = borrowers["name"].tolist()
    selected = st.selectbox("Select Borrower", names)

    b = borrowers[borrowers["name"] == selected].iloc[0]

    st.subheader("Borrower Info")
    st.write(f"**Department:** {b['department']}")
    st.write(f"**Phone:** {b['phone']}")

    st.subheader("Loan Status")
    col1, col2 = st.columns(2)

    with col1:
        st.metric("Principal Remaining", b["principal_remaining"])
        principal_pay = st.number_input("Principal Paid", min_value=0.0)

    with col2:
        st.metric("Interest Remaining", b["interest_remaining"])
        interest_pay = st.number_input("Interest Paid", min_value=0.0)

    if st.button("Submit Payment"):
        payments = add_payment(
            b["borrower_id"], principal_pay, interest_pay, payments
        )
        borrowers = compute_balances(borrowers, payments)

        save_borrowers(borrowers, borrowers_ws)
        save_payments(payments, payments_ws)

        st.success("Payment saved!")

# ---------------- NEW BORROWER ----------------
with tab2:
    st.subheader("Add New Borrower")

    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input("Name")
        dept = st.text_input("Department")
        phone = st.text_input("Phone")

    with col2:
        principal = st.number_input("Principal (RM)", min_value=0.0)
        start_date = st.date_input("Start Date")
        months = st.number_input("Months to Pay", min_value=1)

    if st.button("Create Loan"):
        borrowers = add_borrower(
            borrowers, name, dept, phone, principal, start_date, months
        )

        save_borrowers(borrowers, borrowers_ws)

        st.success("Borrower added successfully!")

# ---------------- MONTHLY REPORT ----------------
with tab3:
    st.subheader("Monthly Financial Report")

    month = st.selectbox("Month", list(range(1, 13)))
    year = st.selectbox("Year", [2024, 2025, 2026])

    result = monthly_summary(payments, borrowers, month, year)

    st.metric("Interest Collected", result["interest_income"])
    st.metric("Principal Collected", result["principal_income"])
    st.metric("Outstanding Interest", result["outstanding_interest"])
    st.metric("Outstanding Principal", result["outstanding_principal"])
    st.metric("Profit (Interest)", result["profit"])

    st.write("### Borrowers with Pending Interest")
    pending = borrowers[borrowers["interest_remaining"] > 0][["name", "interest_remaining"]]
    st.table(pending)

