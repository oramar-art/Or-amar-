import streamlit as st
import pandas as pd
from datetime import datetime
import io

# הגדרות דף
st.set_page_config(page_title="אור עמר - סטודיו", layout="wide")

# כותרת מעוצבת
st.markdown("<h1 style='text-align: center; color: #D4AF37; direction: rtl;'>אור עמר - ניהול סטודיו קעקועים ופירסינג</h1>", unsafe_allow_html=True)

# טעינת נתונים
if 'db' not in st.session_state:
    try:
        st.session_state.db = pd.read_csv('clients.csv')
    except:
        st.session_state.db = pd.DataFrame(columns=[
            'תאריך', 'שם מלא', 'טלפון', 'סוג שירות', 'פירוט', 'שיטת תשלום', 'סהכ תשלום'
        ])

# תפריט צדי
st.sidebar.markdown("<div style='direction: rtl;'>", unsafe_allow_html=True)
st.sidebar.header("הוספת לקוח חדש")
with st.sidebar.form("customer_form", clear_on_submit=True):
    name = st.text_input("שם מלא")
    phone = st.text_input("טלפון")
    service_type = st.selectbox("תחום", ["פירסינג", "קעקוע", "ליד לא רלוונטי"])
    
    if service_type == "קעקוע":
        detail = st.selectbox("פירוט", ["קטן", "גדול", "שרוול", "חידוש קעקוע"])
    elif service_type == "פירסינג":
        detail = st.selectbox("פירוט", ["עיצוב אוזן", "הזמנת עגיל", "אחר"])
    else:
        detail = "לא רלוונטי"
    
    payment_method = st.selectbox("איך שילם?", ["ביט", "אשראי", "מזומן", "טרם שילם"])
    price = st.number_input("כמה שילם? (בשקלים)", min_value=0)
    date = st.date_input("תאריך", datetime.now())
    
    submitted = st.form_submit_button("שמור במערכת")
    if submitted:
        new_row = pd.DataFrame([{
            'תאריך': date.strftime("%Y-%m-%d"), 'שם מלא': name, 'טלפון': phone, 
            'סוג שירות': service_type, 'פירוט': detail, 
            'שיטת תשלום': payment_method, 'סהכ תשלום': price
        }])
        st.session_state.db = pd.concat([st.session_state.db, new_row], ignore_index=True)
        st.session_state.db.to_csv('clients.csv', index=False)
        st.success("נשמר!")

# הצגת נתונים
st.subheader("ניהול לקוחות והכנסות")
filter_method = st.multiselect("סנן דוח לפי שיטת תשלום:", ["מזומן", "אשראי", "ביט"], default=["מזומן", "אשראי", "ביט"])
df_to_show = st.session_state.db[st.session_state.db['שיטת תשלום'].isin(filter_method)]

st.dataframe(df_to_show, use_container_width=True)

# סיכום כספי
total = df_to_show['סהכ תשלום'].sum()
st.metric("סה\"כ הכנסות בסינון הנבחר", f"₪{total}")

# ייצוא לאקסל (הכי טוב לרואי חשבון)
output = io.BytesIO()
with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
    df_to_show.to_excel(writer, index=False, sheet_name='Sheet1')
st.download_button(label="הורד דוח לרואת חשבון (Excel)", data=output.getvalue(), file_name=f"report_{datetime.now().strftime('%m_%Y')}.xlsx")
