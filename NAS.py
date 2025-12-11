import streamlit as st
import pandas as pd

# 固定讀取 Excel（不用上傳）
file_path = "/mnt/data/標準品_test.xlsx"
df = pd.read_excel(file_path)

st.title("🔍 產品毒化物查詢系統")

# 讓使用者輸入產品編號
prod_no = st.text_input("請輸入產品編號 (Product#)：")

# 定義毒化物欄位（G~N）
hazard_cols = df.columns[6:14]  # 依 G~N 排列，確認為第7~14欄

if prod_no:
    result = df[df["Product#"] == prod_no]

    if result.empty:
        st.warning("查無此產品編號")
    else:
        row = result.iloc[0]

        # 計算濃度：Weight / Conversion
        try:
            concentration_value = row["Weight"] / row["Conversion"]
            concentration = f"{concentration_value:.4f}"
        except:
            concentration = "資料錯誤"

        # 找出哪些毒化物欄位是 Y → 顯示表頭
        hazards = [col for col in hazard_cols if str(row[col]).upper() == "Y"]
        hazard_str = "、".join(hazards) if hazards else "無毒化物"

        # 顯示
        st.subheader("查詢結果")

        st.write(f"**產品編號 (Product#)：** {row['Product#']}")
        st.write(f"**濃度 (Weight ÷ Conversion)：** {concentration}")
        st.write(f"**毒化物類型：** {hazard_str}")

        # 顯示原始資料（可選）
        with st.expander("查看原始資料"):
            st.dataframe(result)
