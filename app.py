# import streamlit as st
# import pandas as pd
# from datetime import datetime
# from backend import (
#     load_data, compute_balances,
#     add_payment, add_borrower,
#     save_borrowers, save_payments,
#     monthly_summary
# )

# SHEET_URL = "https://docs.google.com/spreadsheets/d/1pS0OCxO8tg85gVdOz8XeVw_WAvmXeVLHGHWompwFPjo/edit"


# st.set_page_config(page_title="Family Loan Tracker", layout="wide")

# st.title("📘 Family Loan Management System")

# borrowers, payments, borrowers_ws, payments_ws = load_data(SHEET_URL)
# borrowers = compute_balances(borrowers, payments)

# tab1, tab2, tab3 = st.tabs(["Existing Borrower", "New Borrower", "Monthly Report"])

# # ---------------- EXISTING BORROWER ----------------
# with tab1:
#     names = borrowers["name"].tolist()
#     selected = st.selectbox("Select Borrower", names)

#     b = borrowers[borrowers["name"] == selected].iloc[0]

#     st.subheader("Borrower Info")
#     st.write(f"**Department:** {b['department']}")
#     st.write(f"**Phone:** {b['phone']}")

#     st.subheader("Loan Status")
#     col1, col2 = st.columns(2)

#     with col1:
#         st.metric("Principal Remaining", b["principal_remaining"])
#         principal_pay = st.number_input("Principal Paid", min_value=0.0)

#     with col2:
#         st.metric("Interest Remaining", b["interest_remaining"])
#         interest_pay = st.number_input("Interest Paid", min_value=0.0)

#     if st.button("Submit Payment"):
#         payments = add_payment(
#             b["borrower_id"], principal_pay, interest_pay, payments
#         )
#         borrowers = compute_balances(borrowers, payments)

#         save_borrowers(borrowers, borrowers_ws)
#         save_payments(payments, payments_ws)

#         st.success("Payment saved!")

# # ---------------- NEW BORROWER ----------------
# with tab2:
#     st.subheader("Add New Borrower")

#     col1, col2 = st.columns(2)

#     with col1:
#         name = st.text_input("Name")
#         dept = st.text_input("Department")
#         phone = st.text_input("Phone")

#     with col2:
#         principal = st.number_input("Principal (RM)", min_value=0.0)
#         start_date = st.date_input("Start Date")
#         months = st.number_input("Months to Pay", min_value=1)

#     if st.button("Create Loan"):
#         borrowers = add_borrower(
#             borrowers, name, dept, phone, principal, start_date, months
#         )

#         save_borrowers(borrowers, borrowers_ws)

#         st.success("Borrower added successfully!")

# # ---------------- MONTHLY REPORT ----------------
# with tab3:
#     st.subheader("Monthly Financial Report")

#     month = st.selectbox("Month", list(range(1, 13)))
#     year = st.selectbox("Year", [2024, 2025, 2026])

#     result = monthly_summary(payments, borrowers, month, year)

#     st.metric("Interest Collected", result["interest_income"])
#     st.metric("Principal Collected", result["principal_income"])
#     st.metric("Outstanding Interest", result["outstanding_interest"])
#     st.metric("Outstanding Principal", result["outstanding_principal"])
#     st.metric("Profit (Interest)", result["profit"])

#     st.write("### Borrowers with Pending Interest")
#     pending = borrowers[borrowers["interest_remaining"] > 0][["name", "interest_remaining"]]
#     st.table(pending)


#(NEW)
# import streamlit as st
# import pandas as pd
# import plotly.express as px
# import plotly.graph_objects as go
# from datetime import datetime
# from backend import (
#     load_data, compute_balances,
#     add_payment, add_borrower,
#     save_borrowers, save_payments,
#     monthly_summary, get_payment_history,
#     calculate_payment_schedule, get_dashboard_stats
# )

# # Configuration
# SHEET_URL = "https://docs.google.com/spreadsheets/d/1pS0OCxO8tg85gVdOz8XeVw_WAvmXeVLHGHWompwFPjo/edit"

# # Page config
# st.set_page_config(
#     page_title="Loan Manager Pro",
#     page_icon="💰",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # Custom CSS for better styling
# st.markdown("""
#     <style>
#     .main-header {
#         font-size: 2.5rem;
#         font-weight: 700;
#         color: #1f2937;
#         margin-bottom: 0.5rem;
#     }
#     .sub-header {
#         font-size: 1.1rem;
#         color: #6b7280;
#         margin-bottom: 2rem;
#     }
#     .metric-card {
#         background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#         padding: 1.5rem;
#         border-radius: 0.5rem;
#         color: white;
#         box-shadow: 0 4px 6px rgba(0,0,0,0.1);
#     }
#     .success-card {
#         background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
#         padding: 1.5rem;
#         border-radius: 0.5rem;
#         color: #1f2937;
#         box-shadow: 0 4px 6px rgba(0,0,0,0.1);
#     }
#     .warning-card {
#         background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
#         padding: 1.5rem;
#         border-radius: 0.5rem;
#         color: #1f2937;
#         box-shadow: 0 4px 6px rgba(0,0,0,0.1);
#     }
#     .stTabs [data-baseweb="tab-list"] {
#         gap: 2rem;
#     }
#     .stTabs [data-baseweb="tab"] {
#         height: 3rem;
#         padding: 0 2rem;
#         font-size: 1rem;
#         font-weight: 600;
#     }
#     div[data-testid="stMetricValue"] {
#         font-size: 2rem;
#         font-weight: 700;
#     }
#     </style>
# """, unsafe_allow_html=True)

# # Load data
# @st.cache_data(ttl=60)
# def load_app_data():
#     return load_data(SHEET_URL)

# borrowers, payments, borrowers_ws, payments_ws = load_app_data()
# borrowers = compute_balances(borrowers, payments)

# # Sidebar
# with st.sidebar:
#     st.image("https://img.icons8.com/fluency/96/money-bag.png", width=80)
#     st.title("💼 Loan Manager")
#     st.markdown("---")
    
#     # Quick Stats
#     stats = get_dashboard_stats(borrowers, payments)
#     st.metric("Active Loans", f"{stats['active_loans']}/{stats['total_loans']}")
#     st.metric("Total Outstanding", f"RM {stats['total_outstanding']:,.2f}")
#     st.metric("Collection Rate", f"{stats['collection_rate']:.1f}%")
    
#     st.markdown("---")
#     st.info("💡 **Tip**: Click on any borrower to see detailed payment history and schedule")
    
#     # Refresh button
#     if st.button("🔄 Refresh Data", use_container_width=True):
#         st.cache_data.clear()
#         st.rerun()

# # Main header
# st.markdown('<h1 class="main-header">💰 Loan Management System</h1>', unsafe_allow_html=True)
# st.markdown('<p class="sub-header">Manage borrowers, track payments, and monitor your loan portfolio</p>', unsafe_allow_html=True)

# # Main tabs
# tab1, tab2, tab3, tab4, tab5 = st.tabs([
#     "📊 Dashboard",
#     "👤 Borrower Details",
#     "➕ New Borrower",
#     "💳 Record Payment",
#     "📈 Reports"
# ])

# # ============= DASHBOARD TAB =============
# with tab1:
#     st.subheader("Portfolio Overview")
    
#     # Key metrics
#     col1, col2, col3, col4 = st.columns(4)
    
#     with col1:
#         st.metric(
#             "Total Borrowers",
#             stats['total_loans'],
#             delta=f"{stats['active_loans']} active"
#         )
    
#     with col2:
#         st.metric(
#             "Principal Outstanding",
#             f"RM {stats['principal_outstanding']:,.2f}"
#         )
    
#     with col3:
#         st.metric(
#             "Interest Outstanding",
#             f"RM {stats['interest_outstanding']:,.2f}"
#         )
    
#     with col4:
#         st.metric(
#             "Total Outstanding",
#             f"RM {stats['total_outstanding']:,.2f}"
#         )
    
#     st.markdown("---")
    
#     # Charts
#     col1, col2 = st.columns(2)
    
#     with col1:
#         st.subheader("Outstanding Balance by Borrower")
#         if not borrowers.empty:
#             chart_data = borrowers[borrowers['principal_remaining'] > 0].copy()
#             chart_data['total_remaining'] = chart_data['principal_remaining'] + chart_data['interest_remaining']
#             chart_data = chart_data.sort_values('total_remaining', ascending=True).tail(10)
            
#             fig = px.bar(
#                 chart_data,
#                 x='total_remaining',
#                 y='name',
#                 orientation='h',
#                 title="Top 10 Outstanding Balances",
#                 labels={'total_remaining': 'Amount (RM)', 'name': 'Borrower'},
#                 color='total_remaining',
#                 color_continuous_scale='Reds'
#             )
#             fig.update_layout(showlegend=False, height=400)
#             st.plotly_chart(fig, use_container_width=True)
    
#     with col2:
#         st.subheader("Loan Status Distribution")
#         if not borrowers.empty:
#             status_data = pd.DataFrame({
#                 'Status': ['Fully Paid', 'Active'],
#                 'Count': [
#                     len(borrowers[borrowers['principal_remaining'] == 0]),
#                     len(borrowers[borrowers['principal_remaining'] > 0])
#                 ]
#             })
            
#             fig = px.pie(
#                 status_data,
#                 values='Count',
#                 names='Status',
#                 title="Loan Status",
#                 color_discrete_sequence=['#84fab0', '#fa709a']
#             )
#             fig.update_layout(height=400)
#             st.plotly_chart(fig, use_container_width=True)
    
#     # Active borrowers table
#     st.subheader("Active Borrowers Overview")
#     if not borrowers.empty:
#         active = borrowers[borrowers['principal_remaining'] > 0].copy()
#         active['total_remaining'] = active['principal_remaining'] + active['interest_remaining']
#         active['progress'] = ((active['principal_total'] - active['principal_remaining']) / active['principal_total'] * 100).round(1)
        
#         display_cols = ['name', 'department', 'phone', 'principal_remaining', 'interest_remaining', 'total_remaining', 'progress']
#         display_df = active[display_cols].sort_values('total_remaining', ascending=False)
        
#         st.dataframe(
#             display_df.style.format({
#                 'principal_remaining': 'RM {:,.2f}',
#                 'interest_remaining': 'RM {:,.2f}',
#                 'total_remaining': 'RM {:,.2f}',
#                 'progress': '{:.1f}%'
#             }),
#             use_container_width=True,
#             height=400
#         )
#     else:
#         st.info("No active borrowers")

# # ============= BORROWER DETAILS TAB =============
# with tab2:
#     if not borrowers.empty:
#         col1, col2 = st.columns([2, 1])
        
#         with col1:
#             names = borrowers["name"].tolist()
#             selected = st.selectbox("🔍 Select Borrower", names, key="borrower_select")
        
#         with col2:
#             search_filter = st.selectbox("Filter by Status", ["All", "Active Only", "Fully Paid"], key="status_filter")
        
#         b = borrowers[borrowers["name"] == selected].iloc[0]
        
#         # Borrower info card
#         st.markdown("---")
#         col1, col2, col3 = st.columns(3)
        
#         with col1:
#             st.markdown("### 👤 Borrower Information")
#             st.write(f"**Name:** {b['name']}")
#             st.write(f"**Department:** {b['department']}")
#             st.write(f"**Phone:** {b['phone']}")
#             st.write(f"**Start Date:** {b['loan_start_date']}")
#             st.write(f"**Term:** {b['months_to_pay']} months")
        
#         with col2:
#             st.markdown("### 💵 Loan Details")
#             st.write(f"**Principal:** RM {b['principal_total']:,.2f}")
#             st.write(f"**Interest:** RM {b['interest_total']:,.2f}")
#             st.write(f"**Total Loan:** RM {b['principal_total'] + b['interest_total']:,.2f}")
#             progress = ((b['principal_total'] - b['principal_remaining']) / b['principal_total'] * 100)
#             st.progress(progress / 100)
#             st.write(f"**Progress:** {progress:.1f}%")
        
#         with col3:
#             st.markdown("### 📊 Outstanding Balance")
#             st.metric("Principal", f"RM {b['principal_remaining']:,.2f}")
#             st.metric("Interest", f"RM {b['interest_remaining']:,.2f}")
#             total_remaining = b['principal_remaining'] + b['interest_remaining']
#             st.metric("Total", f"RM {total_remaining:,.2f}")
            
#             if total_remaining == 0:
#                 st.success("✅ Fully Paid!")
        
#         # Payment history
#         st.markdown("---")
#         st.subheader("💳 Payment History")
        
#         history = get_payment_history(b['borrower_id'], payments)
#         if not history.empty:
#             col1, col2 = st.columns([2, 1])
            
#             with col1:
#                 st.dataframe(
#                     history[['date', 'principal_paid', 'interest_paid', 'total_paid']].style.format({
#                         'principal_paid': 'RM {:,.2f}',
#                         'interest_paid': 'RM {:,.2f}',
#                         'total_paid': 'RM {:,.2f}'
#                     }),
#                     use_container_width=True,
#                     height=300
#                 )
            
#             with col2:
#                 st.metric("Total Payments", len(history))
#                 st.metric("Principal Paid", f"RM {history['principal_paid'].sum():,.2f}")
#                 st.metric("Interest Paid", f"RM {history['interest_paid'].sum():,.2f}")
#         else:
#             st.info("No payment history yet")
        
#         # Payment schedule
#         st.markdown("---")
#         st.subheader("📅 Expected Payment Schedule")
#         schedule = calculate_payment_schedule(
#             b['principal_total'],
#             b['interest_total'] / b['principal_total'],
#             b['months_to_pay'],
#             b['loan_start_date']
#         )
#         st.dataframe(
#             schedule.style.format({
#                 'principal_due': 'RM {:,.2f}',
#                 'interest_due': 'RM {:,.2f}',
#                 'total_due': 'RM {:,.2f}'
#             }),
#             use_container_width=True,
#             height=300
#         )
#     else:
#         st.info("No borrowers found. Add a new borrower to get started!")

# # ============= NEW BORROWER TAB =============
# with tab3:
#     st.subheader("➕ Add New Borrower")
    
#     with st.form("new_borrower_form"):
#         col1, col2 = st.columns(2)
        
#         with col1:
#             st.markdown("##### Personal Information")
#             name = st.text_input("Full Name *", placeholder="Enter borrower's name")
#             dept = st.text_input("Department", placeholder="e.g., Operations, Sales")
#             phone = st.text_input("Phone Number *", placeholder="e.g., 0123456789")
        
#         with col2:
#             st.markdown("##### Loan Details")
#             principal = st.number_input("Principal Amount (RM) *", min_value=0.0, step=100.0, format="%.2f")
#             interest_rate = st.number_input("Interest Rate (%)", min_value=0.0, max_value=100.0, value=10.0, step=0.5, format="%.2f")
#             start_date = st.date_input("Start Date *", value=datetime.now())
#             months = st.number_input("Term (Months) *", min_value=1, max_value=120, value=12)
        
#         # Calculate and show summary
#         if principal > 0:
#             interest_amount = principal * (interest_rate / 100)
#             total_amount = principal + interest_amount
#             monthly_payment = total_amount / months if months > 0 else 0
            
#             st.markdown("---")
#             st.markdown("##### Loan Summary")
#             col1, col2, col3, col4 = st.columns(4)
#             col1.metric("Principal", f"RM {principal:,.2f}")
#             col2.metric("Interest", f"RM {interest_amount:,.2f}")
#             col3.metric("Total", f"RM {total_amount:,.2f}")
#             col4.metric("Monthly Payment", f"RM {monthly_payment:,.2f}")
        
#         submitted = st.form_submit_button("Create Loan", use_container_width=True, type="primary")
        
#         if submitted:
#             if not name or not phone:
#                 st.error("Please fill in all required fields (*)")
#             elif principal <= 0:
#                 st.error("Principal amount must be greater than 0")
#             else:
#                 borrowers = add_borrower(
#                     borrowers, name, dept, phone, principal, 
#                     interest_rate/100, start_date, months
#                 )
#                 if save_borrowers(borrowers, borrowers_ws):
#                     st.success(f"✅ Loan created successfully for {name}!")
#                     st.balloons()
#                     st.cache_data.clear()
#                 else:
#                     st.error("Failed to save borrower. Please try again.")

# # ============= RECORD PAYMENT TAB =============
# with tab4:
#     st.subheader("💳 Record New Payment")
    
#     if not borrowers.empty:
#         active_borrowers = borrowers[borrowers['principal_remaining'] > 0]
        
#         if not active_borrowers.empty:
#             with st.form("payment_form"):
#                 selected = st.selectbox(
#                     "Select Borrower *",
#                     active_borrowers["name"].tolist(),
#                     key="payment_borrower_select"
#                 )
                
#                 b = active_borrowers[active_borrowers["name"] == selected].iloc[0]
                
#                 # Show current balance
#                 col1, col2, col3 = st.columns(3)
#                 with col1:
#                     st.metric("Principal Remaining", f"RM {b['principal_remaining']:,.2f}")
#                 with col2:
#                     st.metric("Interest Remaining", f"RM {b['interest_remaining']:,.2f}")
#                 with col3:
#                     total_rem = b['principal_remaining'] + b['interest_remaining']
#                     st.metric("Total Remaining", f"RM {total_rem:,.2f}")
                
#                 st.markdown("---")
                
#                 col1, col2 = st.columns(2)
                
#                 with col1:
#                     principal_pay = st.number_input(
#                         "Principal Payment (RM)",
#                         min_value=0.0,
#                         max_value=float(b['principal_remaining']),
#                         step=10.0,
#                         format="%.2f"
#                     )
                
#                 with col2:
#                     interest_pay = st.number_input(
#                         "Interest Payment (RM)",
#                         min_value=0.0,
#                         max_value=float(b['interest_remaining']),
#                         step=10.0,
#                         format="%.2f"
#                     )
                
#                 total_payment = principal_pay + interest_pay
                
#                 if total_payment > 0:
#                     st.markdown("---")
#                     st.markdown("##### Payment Summary")
#                     col1, col2, col3 = st.columns(3)
#                     col1.metric("Total Payment", f"RM {total_payment:,.2f}")
#                     col2.metric("New Principal Balance", f"RM {b['principal_remaining'] - principal_pay:,.2f}")
#                     col3.metric("New Interest Balance", f"RM {b['interest_remaining'] - interest_pay:,.2f}")
                
#                 submitted = st.form_submit_button("Record Payment", use_container_width=True, type="primary")
                
#                 if submitted:
#                     if total_payment == 0:
#                         st.error("Please enter a payment amount")
#                     else:
#                         payments = add_payment(
#                             b["borrower_id"], principal_pay, interest_pay, payments
#                         )
#                         borrowers = compute_balances(borrowers, payments)
                        
#                         success_save_borrowers = save_borrowers(borrowers, borrowers_ws)
#                         success_save_payments = save_payments(payments, payments_ws)
                        
#                         if success_save_borrowers and success_save_payments:
#                             st.success(f"✅ Payment of RM {total_payment:,.2f} recorded successfully!")
#                             st.cache_data.clear()
#                             st.balloons()
#                         else:
#                             st.error("Failed to save payment. Please try again.")
#         else:
#             st.info("🎉 All borrowers have fully paid their loans!")
#     else:
#         st.info("No borrowers found. Add a new borrower first.")

# # ============= REPORTS TAB =============
# with tab5:
#     st.subheader("📈 Financial Reports")
    
#     col1, col2 = st.columns([1, 3])
    
#     with col1:
#         st.markdown("##### Select Period")
#         month = st.selectbox("Month", list(range(1, 13)), index=datetime.now().month - 1)
#         year = st.selectbox("Year", [2023, 2024, 2025, 2026], index=1)
    
#     result = monthly_summary(payments, borrowers, month, year)
    
#     # Monthly metrics
#     st.markdown("---")
#     st.markdown(f"##### Report for {datetime(year, month, 1).strftime('%B %Y')}")
    
#     col1, col2, col3, col4 = st.columns(4)
    
#     with col1:
#         st.metric("Interest Collected", f"RM {result['interest_income']:,.2f}")
#     with col2:
#         st.metric("Principal Collected", f"RM {result['principal_income']:,.2f}")
#     with col3:
#         st.metric("Total Collected", f"RM {result['total_collected']:,.2f}")
#     with col4:
#         st.metric("Number of Payments", result['num_payments'])
    
#     st.markdown("---")
    
#     col1, col2 = st.columns(2)
    
#     with col1:
#         st.metric("Outstanding Principal", f"RM {result['outstanding_principal']:,.2f}")
#     with col2:
#         st.metric("Outstanding Interest", f"RM {result['outstanding_interest']:,.2f}")
    
#     # Pending interest table
#     st.markdown("---")
#     st.subheader("💰 Borrowers with Pending Balance")
    
#     if not borrowers.empty:
#         pending = borrowers[
#             (borrowers['principal_remaining'] > 0) | (borrowers['interest_remaining'] > 0)
#         ].copy()
        
#         if not pending.empty:
#             pending['total_pending'] = pending['principal_remaining'] + pending['interest_remaining']
#             display = pending[['name', 'department', 'principal_remaining', 'interest_remaining', 'total_pending']]
#             display = display.sort_values('total_pending', ascending=False)
            
#             st.dataframe(
#                 display.style.format({
#                     'principal_remaining': 'RM {:,.2f}',
#                     'interest_remaining': 'RM {:,.2f}',
#                     'total_pending': 'RM {:,.2f}'
#                 }),
#                 use_container_width=True,
#                 height=400
#             )
            
#             # Export option
#             csv = display.to_csv(index=False)
#             st.download_button(
#                 label="📥 Download Report (CSV)",
#                 data=csv,
#                 file_name=f"loan_report_{year}_{month:02d}.csv",
#                 mime="text/csv"
#             )
#         else:
#             st.success("🎉 All loans are fully paid!")
#     else:
#         st.info("No data available")

# # Footer
# st.markdown("---")
# st.markdown(
#     "<p style='text-align: center; color: #6b7280;'>Made with ❤️ for efficient loan management</p>",
#     unsafe_allow_html=True
# )


# (TEST)
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from backend import (
    load_data, compute_balances,
    add_payment, add_borrower,
    save_borrowers, save_payments,
    monthly_summary, get_payment_history,
    calculate_payment_schedule, get_dashboard_stats
)

# Configuration
SHEET_URL = "https://docs.google.com/spreadsheets/d/1pS0OCxO8tg85gVdOz8XeVw_WAvmXeVLHGHWompwFPjo/edit"

# Language translations
LANGUAGES = {
    'English': {
        'title': 'Loan Management System',
        'subtitle': 'Manage borrowers, track payments, and monitor your loan portfolio',
        'dashboard': 'Dashboard',
        'borrower_details': 'Borrower Details',
        'new_borrower': 'New Borrower',
        'record_payment': 'Record Payment',
        'reports': 'Reports',
        'total_borrowers': 'Total Borrowers',
        'active': 'Active',
        'principal': 'Principal',
        'interest': 'Interest',
        'outstanding': 'Outstanding',
        'total': 'Total',
        'collection_rate': 'Collection Rate',
        'refresh': 'Refresh Data',
        'name': 'Name',
        'department': 'Department',
        'phone': 'Phone',
        'amount': 'Amount',
        'date': 'Date',
        'payment': 'Payment',
        'remaining': 'Remaining',
        'paid': 'Paid',
        'month': 'Month',
        'year': 'Year',
        'submit': 'Submit',
        'create': 'Create',
        'select': 'Select',
        'loan': 'Loan',
        'status': 'Status',
        'progress': 'Progress',
        'history': 'History',
        'schedule': 'Schedule',
        'monthly_report': 'Monthly Report',
        'collected': 'Collected',
        'pending': 'Pending',
        'fully_paid': 'Fully Paid',
        'start_date': 'Start Date',
        'months': 'Months',
        'term': 'Term',
        'rate': 'Interest Rate',
        'portfolio': 'Portfolio Overview',
        'add': 'Add',
        'record': 'Record',
        'download': 'Download Report',
        'balance': 'Balance',
        'personal_info': 'Personal Information',
        'loan_details': 'Loan Details',
        'payment_history': 'Payment History',
        'success': 'Success',
        'error': 'Error',
        'no_data': 'No data available',
        'enter_amount': 'Enter amount',
        'full_name': 'Full Name',
        'total_payments': 'Total Payments',
        'new_balance': 'New Balance'
    },
    'Malay': {
        'title': 'Sistem Pengurusan Pinjaman',
        'subtitle': 'Urus peminjam, rekod bayaran, dan pantau portfolio pinjaman',
        'dashboard': 'Papan Pemuka',
        'borrower_details': 'Butiran Peminjam',
        'new_borrower': 'Peminjam Baru',
        'record_payment': 'Rekod Bayaran',
        'reports': 'Laporan',
        'total_borrowers': 'Jumlah Peminjam',
        'active': 'Aktif',
        'principal': 'Pokok',
        'interest': 'Bunga',
        'outstanding': 'Belum Bayar',
        'total': 'Jumlah',
        'collection_rate': 'Kadar Kutipan',
        'refresh': 'Muat Semula',
        'name': 'Nama',
        'department': 'Jabatan',
        'phone': 'Telefon',
        'amount': 'Jumlah',
        'date': 'Tarikh',
        'payment': 'Bayaran',
        'remaining': 'Baki',
        'paid': 'Dibayar',
        'month': 'Bulan',
        'year': 'Tahun',
        'submit': 'Hantar',
        'create': 'Cipta',
        'select': 'Pilih',
        'loan': 'Pinjaman',
        'status': 'Status',
        'progress': 'Kemajuan',
        'history': 'Sejarah',
        'schedule': 'Jadual',
        'monthly_report': 'Laporan Bulanan',
        'collected': 'Dikutip',
        'pending': 'Tertunggak',
        'fully_paid': 'Selesai Bayar',
        'start_date': 'Tarikh Mula',
        'months': 'Bulan',
        'term': 'Tempoh',
        'rate': 'Kadar Bunga',
        'portfolio': 'Ringkasan Portfolio',
        'add': 'Tambah',
        'record': 'Rekod',
        'download': 'Muat Turun Laporan',
        'balance': 'Baki',
        'personal_info': 'Maklumat Peribadi',
        'loan_details': 'Butiran Pinjaman',
        'payment_history': 'Sejarah Bayaran',
        'success': 'Berjaya',
        'error': 'Ralat',
        'no_data': 'Tiada data',
        'enter_amount': 'Masukkan jumlah',
        'full_name': 'Nama Penuh',
        'total_payments': 'Jumlah Bayaran',
        'new_balance': 'Baki Baru'
    },
    'Tamil': {
        'title': 'கடன் மேலாண்மை அமைப்பு',
        'subtitle': 'கடன் வாங்குபவர்களை நிர்வகித்தல், பணம் செலுத்துதல் மற்றும் கண்காணிப்பு',
        'dashboard': 'முதன்மை பக்கம்',
        'borrower_details': 'கடன் வாங்குபவர் விவரங்கள்',
        'new_borrower': 'புதிய கடன் வாங்குபவர்',
        'record_payment': 'பணம் பதிவு செய்',
        'reports': 'அறிக்கைகள்',
        'total_borrowers': 'மொத்த கடன் வாங்குபவர்கள்',
        'active': 'செயலில்',
        'principal': 'அசல்',
        'interest': 'வட்டி',
        'outstanding': 'நிலுவை',
        'total': 'மொத்தம்',
        'collection_rate': 'சேகரிப்பு விகிதம்',
        'refresh': 'புதுப்பிக்க',
        'name': 'பெயர்',
        'department': 'துறை',
        'phone': 'தொலைபேசி',
        'amount': 'தொகை',
        'date': 'தேதி',
        'payment': 'பணம்',
        'remaining': 'மீதம்',
        'paid': 'செலுத்தப்பட்டது',
        'month': 'மாதம்',
        'year': 'வருடம்',
        'submit': 'சமர்ப்பிக்க',
        'create': 'உருவாக்கு',
        'select': 'தேர்வு செய்',
        'loan': 'கடன்',
        'status': 'நிலை',
        'progress': 'முன்னேற்றம்',
        'history': 'வரலாறு',
        'schedule': 'அட்டவணை',
        'monthly_report': 'மாதாந்திர அறிக்கை',
        'collected': 'சேகரிக்கப்பட்டது',
        'pending': 'நிலுவையில்',
        'fully_paid': 'முழுமையாக செலுத்தப்பட்டது',
        'start_date': 'தொடக்க தேதி',
        'months': 'மாதங்கள்',
        'term': 'காலம்',
        'rate': 'வட்டி விகிதம்',
        'portfolio': 'போர்ட்ஃபோலியோ கண்ணோட்டம்',
        'add': 'சேர்',
        'record': 'பதிவு',
        'download': 'அறிக்கை பதிவிறக்கு',
        'balance': 'இருப்பு',
        'personal_info': 'தனிப்பட்ட தகவல்',
        'loan_details': 'கடன் விவரங்கள்',
        'payment_history': 'பணம் வரலாறு',
        'success': 'வெற்றி',
        'error': 'பிழை',
        'no_data': 'தரவு இல்லை',
        'enter_amount': 'தொகையை உள்ளிடவும்',
        'full_name': 'முழு பெயர்',
        'total_payments': 'மொத்த பணம்',
        'new_balance': 'புதிய இருப்பு'
    }
}

# Page config
st.set_page_config(
    page_title="Loan Manager Pro",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Mobile-responsive CSS
st.markdown("""
    <style>
    /* Base styles */
    .main-header {
        font-size: clamp(1.5rem, 4vw, 2.5rem);
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 0.5rem;
        text-align: center;
    }
    .sub-header {
        font-size: clamp(0.9rem, 2vw, 1.1rem);
        color: #6b7280;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    /* Mobile-first metric styling */
    div[data-testid="stMetricValue"] {
        font-size: clamp(1.2rem, 3vw, 2rem) !important;
        font-weight: 700;
    }
    div[data-testid="stMetricLabel"] {
        font-size: clamp(0.75rem, 2vw, 0.9rem) !important;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        flex-wrap: wrap;
    }
    .stTabs [data-baseweb="tab"] {
        height: auto;
        min-height: 2.5rem;
        padding: 0.5rem 1rem;
        font-size: clamp(0.8rem, 2vw, 1rem);
        font-weight: 600;
        white-space: nowrap;
    }
    
    /* Form inputs - larger touch targets for mobile */
    .stTextInput input, .stNumberInput input, .stSelectbox select {
        font-size: 16px !important; /* Prevents zoom on iOS */
        padding: 0.75rem !important;
    }
    
    /* Button styling - larger for mobile */
    .stButton button {
        padding: 0.75rem 1.5rem !important;
        font-size: clamp(0.9rem, 2vw, 1rem) !important;
        width: 100%;
    }
    
    /* Sidebar adjustments */
    [data-testid="stSidebar"] {
        min-width: 250px;
    }
    
    /* Table responsiveness */
    .dataframe {
        font-size: clamp(0.75rem, 2vw, 0.9rem) !important;
        overflow-x: auto;
    }
    
    /* Card styles */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 0.5rem;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    
    /* Hide specific elements on very small screens */
    @media (max-width: 640px) {
        [data-testid="stSidebar"] {
            min-width: 200px;
        }
        .plot-container {
            height: 300px !important;
        }
    }
    
    /* Improve spacing on mobile */
    @media (max-width: 768px) {
        .block-container {
            padding: 1rem !important;
        }
        div[data-testid="column"] {
            min-width: 100% !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data(ttl=60)
def load_app_data():
    return load_data(SHEET_URL)

borrowers, payments, borrowers_ws, payments_ws = load_app_data()
borrowers = compute_balances(borrowers, payments)

# Sidebar with language selector
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/money-bag.png", width=60)
    
    # Language selector at top
    lang = st.selectbox(
        "🌐 Language / Bahasa / மொழி",
        ['Malay', 'English', 'Tamil'],
        index=0
    )
    t = LANGUAGES[lang]  # translation dictionary
    
    st.title(f"💼 {t['loan']}")
    st.markdown("---")
    
    # Quick Stats
    stats = get_dashboard_stats(borrowers, payments)
    st.metric(f"{t['active']} {t['loan']}", f"{stats['active_loans']}/{stats['total_loans']}")
    st.metric(f"{t['total']} {t['outstanding']}", f"RM {stats['total_outstanding']:,.2f}")
    st.metric(t['collection_rate'], f"{stats['collection_rate']:.1f}%")
    
    st.markdown("---")
    
    # Refresh button
    if st.button(f"🔄 {t['refresh']}", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# Main header
st.markdown(f'<h1 class="main-header">💰 {t["title"]}</h1>', unsafe_allow_html=True)
st.markdown(f'<p class="sub-header">{t["subtitle"]}</p>', unsafe_allow_html=True)

# Main tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    f"📊 {t['dashboard']}",
    f"👤 {t['borrower_details']}",
    f"➕ {t['new_borrower']}",
    f"💳 {t['record_payment']}",
    f"📈 {t['reports']}"
])

# ============= DASHBOARD TAB =============
with tab1:
    st.subheader(t['portfolio'])
    
    # Key metrics - stack on mobile
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.metric(
            t['total_borrowers'],
            stats['total_loans'],
            delta=f"{stats['active_loans']} {t['active']}"
        )
        st.metric(
            f"{t['interest']} {t['outstanding']}",
            f"RM {stats['interest_outstanding']:,.2f}"
        )
    
    with col2:
        st.metric(
            f"{t['principal']} {t['outstanding']}",
            f"RM {stats['principal_outstanding']:,.2f}"
        )
        st.metric(
            f"{t['total']} {t['outstanding']}",
            f"RM {stats['total_outstanding']:,.2f}"
        )
    
    st.markdown("---")
    
    # Charts - stack on mobile
    st.subheader(f"{t['outstanding']} {t['balance']}")
    if not borrowers.empty:
        chart_data = borrowers[borrowers['principal_remaining'] > 0].copy()
        chart_data['total_remaining'] = chart_data['principal_remaining'] + chart_data['interest_remaining']
        chart_data = chart_data.sort_values('total_remaining', ascending=True).tail(10)
        
        fig = px.bar(
            chart_data,
            x='total_remaining',
            y='name',
            orientation='h',
            labels={'total_remaining': f'{t["amount"]} (RM)', 'name': t['name']},
            color='total_remaining',
            color_continuous_scale='Reds'
        )
        fig.update_layout(showlegend=False, height=400, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)
    
    # Active borrowers table
    st.markdown("---")
    st.subheader(f"{t['active']} {t['loan']}")
    if not borrowers.empty:
        active = borrowers[borrowers['principal_remaining'] > 0].copy()
        active['total_remaining'] = active['principal_remaining'] + active['interest_remaining']
        active['progress'] = ((active['principal_total'] - active['principal_remaining']) / active['principal_total'] * 100).round(1)
        
        display_cols = ['name', 'phone', 'principal_remaining', 'interest_remaining', 'total_remaining', 'progress']
        display_df = active[display_cols].sort_values('total_remaining', ascending=False)
        display_df.columns = [t['name'], t['phone'], t['principal'], t['interest'], t['total'], t['progress']]
        
        st.dataframe(
            display_df.style.format({
                t['principal']: 'RM {:,.2f}',
                t['interest']: 'RM {:,.2f}',
                t['total']: 'RM {:,.2f}',
                t['progress']: '{:.1f}%'
            }),
            use_container_width=True,
            height=400
        )
    else:
        st.info(t['no_data'])

# ============= BORROWER DETAILS TAB =============
with tab2:
    if not borrowers.empty:
        selected = st.selectbox(f"🔍 {t['select']} {t['name']}", borrowers["name"].tolist(), key="borrower_select")
        
        b = borrowers[borrowers["name"] == selected].iloc[0]
        
        # Borrower info - stack on mobile
        st.markdown("---")
        
        # Info section
        st.markdown(f"### 👤 {t['personal_info']}")
        col1, col2 = st.columns([1, 1])
        with col1:
            st.write(f"**{t['name']}:** {b['name']}")
            st.write(f"**{t['department']}:** {b['department']}")
        with col2:
            st.write(f"**{t['phone']}:** {b['phone']}")
            st.write(f"**{t['start_date']}:** {b['loan_start_date']}")
        
        st.markdown("---")
        
        # Loan details
        st.markdown(f"### 💵 {t['loan_details']}")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(t['principal'], f"RM {b['principal_total']:,.2f}")
        with col2:
            st.metric(t['interest'], f"RM {b['interest_total']:,.2f}")
        with col3:
            st.metric(t['total'], f"RM {b['principal_total'] + b['interest_total']:,.2f}")
        
        progress = ((b['principal_total'] - b['principal_remaining']) / b['principal_total'] * 100)
        st.progress(progress / 100)
        st.write(f"**{t['progress']}:** {progress:.1f}%")
        
        st.markdown("---")
        
        # Outstanding balance
        st.markdown(f"### 📊 {t['outstanding']} {t['balance']}")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(t['principal'], f"RM {b['principal_remaining']:,.2f}")
        with col2:
            st.metric(t['interest'], f"RM {b['interest_remaining']:,.2f}")
        with col3:
            total_remaining = b['principal_remaining'] + b['interest_remaining']
            st.metric(t['total'], f"RM {total_remaining:,.2f}")
        
        if total_remaining == 0:
            st.success(f"✅ {t['fully_paid']}!")
        
        # Payment history
        st.markdown("---")
        st.subheader(f"💳 {t['payment_history']}")
        
        history = get_payment_history(b['borrower_id'], payments)
        if not history.empty:
            history_display = history[['date', 'principal_paid', 'interest_paid', 'total_paid']].copy()
            history_display.columns = [t['date'], t['principal'], t['interest'], t['total']]
            
            st.dataframe(
                history_display.style.format({
                    t['principal']: 'RM {:,.2f}',
                    t['interest']: 'RM {:,.2f}',
                    t['total']: 'RM {:,.2f}'
                }),
                use_container_width=True,
                height=300
            )
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(f"{t['total']} {t['payment']}", len(history))
            with col2:
                st.metric(f"{t['principal']} {t['paid']}", f"RM {history['principal_paid'].sum():,.2f}")
            with col3:
                st.metric(f"{t['interest']} {t['paid']}", f"RM {history['interest_paid'].sum():,.2f}")
        else:
            st.info(t['no_data'])
    else:
        st.info(t['no_data'])

# ============= NEW BORROWER TAB =============
with tab3:
    st.subheader(f"➕ {t['add']} {t['new_borrower']}")
    
    with st.form("new_borrower_form"):
        # Personal info
        st.markdown(f"##### {t['personal_info']}")
        name = st.text_input(f"{t['full_name']} *", placeholder=t['name'])
        
        col1, col2 = st.columns([1, 1])
        with col1:
            dept = st.text_input(t['department'], placeholder=t['department'])
        with col2:
            phone = st.text_input(f"{t['phone']} *", placeholder="0123456789")
        
        st.markdown("---")
        
        # Loan details
        st.markdown(f"##### {t['loan_details']}")
        col1, col2 = st.columns([1, 1])
        with col1:
            principal = st.number_input(f"{t['principal']} (RM) *", min_value=0.0, step=100.0, format="%.2f")
            start_date = st.date_input(f"{t['start_date']} *", value=datetime.now())
        with col2:
            interest_rate = st.number_input(f"{t['rate']} (%)", min_value=0.0, max_value=100.0, value=10.0, step=0.5, format="%.2f")
            months = st.number_input(f"{t['term']} ({t['months']}) *", min_value=1, max_value=120, value=12)
        
        # Summary
        if principal > 0:
            interest_amount = principal * (interest_rate / 100)
            total_amount = principal + interest_amount
            monthly_payment = total_amount / months if months > 0 else 0
            
            st.markdown("---")
            st.markdown(f"##### {t['loan']} {t['total']}")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric(t['principal'], f"RM {principal:,.2f}")
            col2.metric(t['interest'], f"RM {interest_amount:,.2f}")
            col3.metric(t['total'], f"RM {total_amount:,.2f}")
            col4.metric(f"{t['payment']}/{t['month']}", f"RM {monthly_payment:,.2f}")
        
        submitted = st.form_submit_button(f"{t['create']} {t['loan']}", use_container_width=True, type="primary")
        
        if submitted:
            if not name or not phone:
                st.error(f"{t['error']}: {t['enter_amount']}")
            elif principal <= 0:
                st.error(f"{t['error']}: {t['principal']}")
            else:
                borrowers = add_borrower(
                    borrowers, name, dept, phone, principal, 
                    interest_rate/100, start_date, months
                )
                if save_borrowers(borrowers, borrowers_ws):
                    st.success(f"✅ {t['success']}!")
                    st.balloons()
                    st.cache_data.clear()

# ============= RECORD PAYMENT TAB =============
with tab4:
    st.subheader(f"💳 {t['record']} {t['payment']}")
    
    if not borrowers.empty:
        active_borrowers = borrowers[borrowers['principal_remaining'] > 0]
        
        if not active_borrowers.empty:
            with st.form("payment_form"):
                selected = st.selectbox(
                    f"{t['select']} {t['name']} *",
                    active_borrowers["name"].tolist(),
                    key="payment_borrower_select"
                )
                
                b = active_borrowers[active_borrowers["name"] == selected].iloc[0]
                
                # Current balance
                st.markdown(f"##### {t['balance']} {t['remaining']}")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(t['principal'], f"RM {b['principal_remaining']:,.2f}")
                with col2:
                    st.metric(t['interest'], f"RM {b['interest_remaining']:,.2f}")
                with col3:
                    total_rem = b['principal_remaining'] + b['interest_remaining']
                    st.metric(t['total'], f"RM {total_rem:,.2f}")
                
                st.markdown("---")
                
                # Payment inputs
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    principal_pay = st.number_input(
                        f"{t['principal']} {t['payment']} (RM)",
                        min_value=0.0,
                        max_value=float(b['principal_remaining']),
                        step=10.0,
                        format="%.2f"
                    )
                
                with col2:
                    interest_pay = st.number_input(
                        f"{t['interest']} {t['payment']} (RM)",
                        min_value=0.0,
                        max_value=float(b['interest_remaining']),
                        step=10.0,
                        format="%.2f"
                    )
                
                total_payment = principal_pay + interest_pay
                
                if total_payment > 0:
                    st.markdown("---")
                    st.markdown(f"##### {t['new_balance']}")
                    col1, col2, col3 = st.columns(3)
                    col1.metric(f"{t['total']} {t['payment']}", f"RM {total_payment:,.2f}")
                    col2.metric(f"{t['principal']} {t['new_balance']}", f"RM {b['principal_remaining'] - principal_pay:,.2f}")
                    col3.metric(f"{t['interest']} {t['new_balance']}", f"RM {b['interest_remaining'] - interest_pay:,.2f}")
                
                submitted = st.form_submit_button(f"{t['record']} {t['payment']}", use_container_width=True, type="primary")
                
                if submitted:
                    if total_payment == 0:
                        st.error(f"{t['error']}: {t['enter_amount']}")
                    else:
                        payments = add_payment(
                            b["borrower_id"], principal_pay, interest_pay, payments
                        )
                        borrowers = compute_balances(borrowers, payments)
                        
                        if save_borrowers(borrowers, borrowers_ws) and save_payments(payments, payments_ws):
                            st.success(f"✅ {t['success']}! RM {total_payment:,.2f}")
                            st.cache_data.clear()
                            st.balloons()
        else:
            st.info(f"🎉 {t['fully_paid']}!")
    else:
        st.info(t['no_data'])

# ============= REPORTS TAB =============
with tab5:
    st.subheader(f"📈 {t['monthly_report']}")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        month = st.selectbox(t['month'], list(range(1, 13)), index=datetime.now().month - 1)
    with col2:
        year = st.selectbox(t['year'], [2023, 2024, 2025, 2026], index=1)
    
    result = monthly_summary(payments, borrowers, month, year)
    
    # Monthly metrics
    st.markdown("---")
    st.markdown(f"##### {t['monthly_report']} - {datetime(year, month, 1).strftime('%B %Y')}")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.metric(f"{t['interest']} {t['collected']}", f"RM {result['interest_income']:,.2f}")
        st.metric(f"{t['total']} {t['collected']}", f"RM {result['total_collected']:,.2f}")
    
    with col2:
        st.metric(f"{t['principal']} {t['collected']}", f"RM {result['principal_income']:,.2f}")
        st.metric(f"{t['total']} {t['payment']}", result['num_payments'])
    
    st.markdown("---")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.metric(f"{t['principal']} {t['outstanding']}", f"RM {result['outstanding_principal']:,.2f}")
    with col2:
        st.metric(f"{t['interest']} {t['outstanding']}", f"RM {result['outstanding_interest']:,.2f}")
    
    # Pending balance table
    st.markdown("---")
    st.subheader(f"💰 {t['pending']} {t['balance']}")
    
    if not borrowers.empty:
        pending = borrowers[
            (borrowers['principal_remaining'] > 0) | (borrowers['interest_remaining'] > 0)
        ].copy()
        
        if not pending.empty:
            pending['total_pending'] = pending['principal_remaining'] + pending['interest_remaining']
            display = pending[['name', 'department', 'principal_remaining', 'interest_remaining', 'total_pending']].copy()
            display = display.sort_values('total_pending', ascending=False)
            display.columns = [t['name'], t['department'], t['principal'], t['interest'], t['total']]
            
            st.dataframe(
                display.style.format({
                    t['principal']: 'RM {:,.2f}',
                    t['interest']: 'RM {:,.2f}',
                    t['total']: 'RM {:,.2f}'
                }),
                use_container_width=True,
                height=400
            )
            
            # Export option
            csv = display.to_csv(index=False)
            st.download_button(
                label=f"📥 {t['download']}",
                data=csv,
                file_name=f"loan_report_{year}_{month:02d}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.success(f"🎉 {t['fully_paid']}!")
    else:
        st.info(t['no_data'])

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #6b7280; font-size: 0.9rem;'>💚 Dibuat untuk pengurusan pinjaman yang mudah</p>",
    unsafe_allow_html=True
)
