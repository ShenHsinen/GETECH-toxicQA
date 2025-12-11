import streamlit as st
import pandas as pd

st.title("🔍 毒化物查詢系統")

# 讀取 CSV
df = pd.read_csv("List_NAS.csv")

# 設定要檢查的欄位範圍（G~N）
cols_to_check = df.columns[6:14]  # 假設 G~N 是第7~14欄

# 使用者輸入產品編號
pid = st.text_input("請輸入產品編號 (Product#)")

if pid:
    subset = df[df['Product#'] == pid]

    if subset.empty:
        st.warning("找不到此產品編號")
    else:
        found = False
        for idx, row in subset.iterrows():
            # 找出 G~N 欄位為 'Y' 的欄位
            cols_with_Y = [col for col in cols_to_check if row[col] == 'Y']
            if cols_with_Y:
                found = True
                st.write({
                    "Cas No.": row['CAS#'],
                    "濃度": row['WeightConversion'],
                    "毒化物類型": cols_with_Y,
                    "備註": f"{row.get('備註', '')}, {row.get('備註2', '')}"
                })

        if not found:
            st.info("這個產品在 G~N 欄位沒有 'Y'")
