import streamlit as st
import pandas as pd
from datetime import datetime
import io

# הגדרות דף וסטייל ניאון סגול משודרג
st.set_page_config(page_title="OR AMAR STUDIO", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Assistant', sans-serif; direction: rtl; }
    .main { background-color: #050505; color: #ffffff; }
    
    h1 { color: #bc13fe; text-shadow: 0 0 15px #bc13fe, 0 0 30px #bc13fe; text-align: center; font-size: 3rem; }
    h3 { color: #bc13fe; text-align: right; border-bottom: 2px solid #bc13fe; padding-bottom: 10px; }
    
    /* עיצוב כפתורים */
    .stButton>button { 
        background-color: transparent; color: #bc13fe; 
        border: 2px solid #bc13fe; border-radius: 20px; 
        box-shadow: 0 0 10px #bc13fe; transition: 0.3s;
        width: 100%; font-weight: bold;
    }
    .stButton>button:hover { background-color: #bc13fe; color: white; box-shadow: 0 0 25px #bc13fe; }
    
    /* עיצוב תיבות קלט */
    input, select { background-color: #1a1a1a !important; color: #bc13fe !important; border: 1px solid #bc13fe !important; }
    label { color: #bc13fe !important; font-weight: bold; }
    
    /* עיצוב טבלה */
    .stDataFrame { border: 1px solid #bc13fe; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>OR AMAR - STUDIO</h1>", unsafe_allow_html=True)

# פונקציה לטעינת נתונים
def load_data():
    try:
        return pd.read_csv('clients.csv')
    except:
        return pd.DataFrame(columns=['ID', 'תאריך', 'שם מלא', 'טלפון', 'סוג', 'פירוט', 'תשלום', 'שיטה'])

if 'db' not in st.session_state:
    st.session_state.db = load_data()

# --- חלק 1: הוספת לקוח ---
st.markdown("<h3>⚡ רישום עסקה חדשה</h3>", unsafe_allow_html=True)

with st.container():
    with st.form("main_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            name = st.text_input("שם הלקוח")
            phone = st.text_input("טלפון")
        with c2:
            service = st.selectbox("תחום השירות", ["קעקוע", "פירסינג", "ליד לא רלוונטי"])
            # לוגיקה לבחירת פירוט לפי סוג שירות
            if service == "קעקוע":
                options = ["קעקוע גדול", "קעקוע קטן", "שרוול", "חידוש קעקוע"]
            elif service == "פירסינג":
                options = ["עיצוב אוזן", "הזמנת עגיל", "הורדה/החלפה של עגיל"]
            else:
                options = ["ליד לא רלוונטי"]
            detail = st.selectbox("פירוט השירות", options)
        with c3:
            price = st.number_input("סכום (₪)", min_value=0)
            method = st.selectbox("שיטת תשלום", ["מזומן", "ביט", "אשראי", "טרם שולם"])
            date = st.date_input("תאריך", datetime.now())

        if st.form_submit_button("🚀 שמור עסקה"):
            new_id = int(datetime.now().timestamp()) # יצירת מזהה ייחודי למחיקה
            new_row = pd.DataFrame([{
                'ID': new_id, 'תאריך': date.strftime("%d/%m/%Y"), 'שם מלא': name, 
                'טלפון': phone, 'סוג': service, 'פירוט': detail, 'תשלום': price, 'שיטה': method
            }])
            st.session_state.db = pd.concat([st.session_state.db, new_row], ignore_index=True)
            st.session_state.db.to_csv('clients.csv', index=False)
            st.balloons()
            st.success(f"העסקה של {name} נשמרה!")

st.write("---")

# --- חלק 2: ניהול ומחיקה ---
st.markdown("<h3>📋 ניהול לקוחות וביצועים</h3>", unsafe_allow_html=True)

if not st.session_state.db.empty:
    # יצירת עותק להצגה ללא עמודת ה-ID (כדי שיהיה נקי)
    df_display = st.session_state.db.copy()
    
    # סינון דוח
    filter_pay = st.multiselect("סנן לפי תשלום:", ["מזומן", "אשראי", "ביט"], default=["מזומן", "אשראי", "ביט"])
    df_filtered = df_display[df_display['שיטה'].isin(filter_pay)]
    
    st.dataframe(df_filtered.drop(columns=['ID']), use_container_width=True)

    # מנגנון מחיקה
    st.markdown("<p style='color: #bc13fe;'>להסרת לקוח מהרשימה:</p>", unsafe_allow_html=True)
    client_to_delete = st.selectbox("בחר לקוח להסרה:", st.session_state.db['שם מלא'].tolist())
    if st.button("❌ הסר לקוח נבחר"):
        st.session_state.db = st.session_state.db[st.session_state.db['שם מלא'] != client_to_delete]
        st.session_state.db.to_csv('clients.csv', index=False)
        st.warning(f"הלקוח {client_to_delete} הוסר מהמערכת.")
        st.rerun()

    # סיכום כספי
    total = df_filtered['תשלום'].sum()
    st.markdown(f"<div style='text-align: center; padding: 20px; border: 2px solid #bc13fe; border-radius: 15px;'> <h2 style='margin:0;'>סה\"כ הכנסות בסינון: ₪{total:,}</h2> </div>", unsafe_allow_html=True)

    # ייצוא
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_filtered.to_excel(writer, index=False)
    st.download_button("📂 הורד דוח סופי לרואת חשבון", output.getvalue(), f"OR_AMAR_REPORT.xlsx")
else:
    st.info("אין עדיין נתונים במערכת. תתחיל להפגיז!")
