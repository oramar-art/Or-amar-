import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import io

# הגדרות דף - סגנון סטודיו יוקרתי
st.set_page_config(page_title="OR AMAR STUDIO", layout="wide", initial_sidebar_state="collapsed")

# עיצוב ניאון סגול מתקדם
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Assistant', sans-serif; direction: rtl; background-color: #050505; color: white; }
    
    .stApp { background-color: #050505; }
    
    /* כותרת ניאון */
    .neon-title { color: #bc13fe; text-shadow: 0 0 10px #bc13fe, 0 0 20px #bc13fe; text-align: center; font-size: 50px; font-weight: bold; margin-bottom: 30px; }
    
    /* כרטיסי ניקוד (Metrics) */
    .metric-card { background: #1a1a1a; border: 1px solid #bc13fe; border-radius: 15px; padding: 20px; text-align: center; box-shadow: 0 0 15px rgba(188, 19, 254, 0.2); }
    
    /* עיצוב כפתורים */
    div.stButton > button { background-color: transparent; color: #bc13fe; border: 2px solid #bc13fe; border-radius: 30px; padding: 10px 25px; transition: 0.3s; font-weight: bold; width: 100%; }
    div.stButton > button:hover { background-color: #bc13fe; color: white; box-shadow: 0 0 20px #bc13fe; }
    
    /* עיצוב כפתור מחיקה ספציפי */
    .delete-btn { color: #ff4b4b !important; border-color: #ff4b4b !important; }
    
    /* טבלה */
    .stDataFrame { border: 1px solid #333; border-radius: 10px; }
    
    /* תיבות קלט */
    input, select, .stSelectbox { background-color: #121212 !important; color: white !important; border: 1px solid #bc13fe !important; }
    </style>
""", unsafe_allow_html=True)

# פונקציות לניהול נתונים
def load_data():
    try:
        df = pd.read_csv('clients.csv')
        if 'ID' not in df.columns: df['ID'] = range(len(df))
        return df
    except:
        return pd.DataFrame(columns=['ID', 'תאריך', 'שם מלא', 'טלפון', 'סוג', 'פירוט', 'תשלום', 'שיטה'])

if 'db' not in st.session_state:
    st.session_state.db = load_data()

st.markdown('<div class="neon-title">OR AMAR - TATTOO & PIERCING</div>', unsafe_allow_html=True)

# --- אזור עליון: מונים מרשימים ---
col_m1, col_m2, col_m3 = st.columns(3)
with col_m1:
    st.markdown(f'<div class="metric-card"><h2 style="color:#bc13fe;">לקוחות שטופלו</h2><h1>{len(st.session_state.db)}</h1></div>', unsafe_allow_html=True)
with col_m2:
    total_rev = st.session_state.db['תשלום'].sum()
    st.markdown(f'<div class="metric-card"><h2 style="color:#bc13fe;">הכנסה כוללת</h2><h1>₪{total_rev:,.0f}</h1></div>', unsafe_allow_html=True)
with col_m3:
    st.markdown(f'<div class="metric-card"><h2 style="color:#bc13fe;">היום</h2><h1>{datetime.now().strftime("%d/%m")}</h1></div>', unsafe_allow_html=True)

st.write("<br>", unsafe_allow_html=True)

# --- טופס הזנה חכם ---
with st.container():
    st.markdown("<h3 style='text-align:right; color:#bc13fe;'>סיום טיפול / קביעת תור</h3>", unsafe_allow_html=True)
    with st.form("add_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            name = st.text_input("שם הלקוח")
            phone = st.text_input("טלפון")
        with c2:
            service = st.selectbox("תחום השירות", ["קעקוע", "פירסינג", "ליד/אחר"])
            if service == "קעקוע":
                options = ["קעקוע קטן", "קעקוע גדול", "שרוול", "חידוש קעקוע"]
            elif service == "פירסינג":
                options = ["עיצוב אוזן", "הזמנת עגיל", "הורדה/החלפה של עגיל"]
            else:
                options = ["ליד לא רלוונטי", "ייעוץ"]
            detail = st.selectbox("פירוט", options)
        with c3:
            price = st.number_input("סכום ששולם", min_value=0)
            method = st.selectbox("שיטת תשלום", ["מזומן", "ביט", "אשראי", "טרם שולם"])
        
        if st.form_submit_button("✅ סיימתי טיפול - שמור במערכת"):
            new_id = int(datetime.now().timestamp())
            new_entry = pd.DataFrame([{
                'ID': new_id, 'תאריך': datetime.now().strftime("%d/%m/%Y"), 
                'שם מלא': name, 'טלפון': phone, 'סוג': service, 
                'פירוט': detail, 'תשלום': price, 'שיטה': method
            }])
            st.session_state.db = pd.concat([st.session_state.db, new_entry], ignore_index=True)
            st.session_state.db.to_csv('clients.csv', index=False)
            st.balloons()
            st.rerun()

st.write("---")

# --- דוחות וגרפים ---
col_chart, col_table = st.columns([1, 2])

with col_chart:
    st.markdown("<h3 style='text-align:right; color:#bc13fe;'>פילוח הכנסות</h3>", unsafe_allow_html=True)
    if not st.session_state.db.empty:
        fig = px.pie(st.session_state.db, values='תשלום', names='שיטה', 
                     color_discrete_sequence=['#bc13fe', '#8a2be2', '#4b0082', '#000000'],
                     hole=0.4)
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

with col_table:
    st.markdown("<h3 style='text-align:right; color:#bc13fe;'>רשימת לקוחות</h3>", unsafe_allow_html=True)
    # הצגת טבלה עם אפשרות מחיקה
    for index, row in st.session_state.db[::-1].iterrows(): # מציג מהחדש לישן
        col_data, col_del = st.columns([6, 1])
        with col_data:
            st.markdown(f"""
                <div style="background:#1a1a1a; padding:10px; border-radius:10px; margin-bottom:5px; border-right:4px solid #bc13fe;">
                <b>{row['שם מלא']}</b> | {row['פירוט']} | <b>₪{row['תשלום']}</b> ({row['שיטה']})
                </div>
            """, unsafe_allow_html=True)
        with col_del:
            if st.button("🗑️", key=f"del_{row['ID']}"):
                st.session_state.db = st.session_state.db.drop(index)
                st.session_state.db.to_csv('clients.csv', index=False)
                st.rerun()

# --- ייצוא ---
st.write("<br>", unsafe_allow_html=True)
output = io.BytesIO()
with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
    st.session_state.db.drop(columns=['ID']).to_excel(writer, index=False)
st.download_button("📤 הורד דוח סופי לרואת חשבון", output.getvalue(), f"OR_AMAR_REPORT.xlsx")
