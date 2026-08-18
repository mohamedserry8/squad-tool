import streamlit as st
import re
import requests
from datetime import datetime

# إعدادات الصفحة
st.set_page_config(page_title="أداة مطابقة اللاعبين", page_icon="⚽", layout="wide")

def extract_smart_ids(text):
    extracted_ids = set()
    lines = text.split('\n')
    for line in lines:
        if 'http' in line.lower() or 'match_id' in line.lower() or 'gatekeeper' in line.lower():
            continue
        found_ids = re.findall(r'\b[1-9]\d{4,7}\b', line)
        extracted_ids.update(found_ids)
    return extracted_ids

# تصميم الواجهة
st.markdown("<h1 style='text-align: center;'>⚽ أداة مطابقة التشكيل مع القائمة</h1>", unsafe_allow_html=True)
st.write("---")

col1, col2, col3 = st.columns(3)
with col1:
    email = st.text_input("📧 Your Email")
with col2:
    match_name = st.text_input("🏟️ Match ID", placeholder="مثال: Arsenal vs Chelsea")
with col3:
    team_type = st.radio("👕 Team", ["Home", "Away"])

col4, col5 = st.columns(2)
with col4:
    lineup_text = st.text_area("1️⃣ الصق التشكيل هنا (Lineup)", height=200)
with col5:
    squad_text = st.text_area("2️⃣ الصق القائمة هنا (Squad)", height=200)

if st.button("🔍 قـارن الآن", use_container_width=True):
    if not email.strip() or not match_name.strip():
        st.warning("⚠️ من فضلك.. لازم تكتب الإيميل واسم الماتش الأول!")
    elif not lineup_text.strip() or not squad_text.strip():
        st.warning("⚠️ من فضلك.. انسخ والصق بيانات التشكيل والقائمة!")
    else:
        lineup_ids = extract_smart_ids(lineup_text)
        squad_ids = extract_smart_ids(squad_text)
        missing_from_squad = lineup_ids - squad_ids
        missing_count = len(missing_from_squad)

        # إرسال البيانات لجوجل شيت بصمت
        try:
            form_url = "https://docs.google.com/forms/d/e/1FAIpQLSe75mzMIymqcCL23jZ9zzUcQYML68w10oB5qEcThoisfintGQ/formResponse"
            form_data = {
                "entry.2043479514": email,
                "entry.1713311979": match_name,
                "entry.1430286001": team_type,
                "entry.24887221": missing_count,
                "entry.784474876": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            requests.post(form_url, data=form_data)
        except Exception:
            pass

        # إظهار النتيجة
        st.write("### 📊 نتيجة المقارنة:")
        if not lineup_ids:
            st.error("❌ مفيش أي أرقام ID واضحة في بيانات التشكيل. تأكد إنك نسخت الجدول صح.")
        elif not missing_from_squad:
            st.success("✅ ممتاز! كل اللاعبين اللي في التشكيل موجودين في القائمة.")
        else:
            st.warning(f"🔴 تحذير: يوجد {missing_count} لاعب في التشكيل مش موجودين في القائمة:")
            for player_id in sorted(missing_from_squad):
                st.write("➔ الناقص ID:")
                st.code(player_id, language="text")
