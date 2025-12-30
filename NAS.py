import streamlit as st
import pandas as pd

st.title("🔍 毒化物查詢系統")

# 讀取 CSV
df = pd.read_csv("List_NAS.csv")

# 設定要檢查的欄位範圍（G~N）
cols_to_check = df.columns[5:13]  # 假設 F~M 是第7~14欄

# 使用者輸入產品編號
pid = st.text_input("請輸入產品編號")

if pid:
    subset = df[df['產品編號'] == pid]

    if subset.empty:
        st.warning("找不到此產品編號")
    else:
        # 用來存結果的 list
        results = []

        for idx, row in subset.iterrows():
            # 找出 F~M 欄位為 'Y' 的欄位
            cols_with_Y = [col for col in cols_to_check if row[col] == 'Y']
            if cols_with_Y:
                results.append({
                    "Cas No.": row['CAS NO'],
                    "濃度": f"{row.get('濃度', '')}, {row.get('單位', '')}",
                    "需申請文件類別": ", ".join(cols_with_Y),
                    "申請文件類別": row['申請文件類別'],
                    "產品包裝": row['產品包裝']
                })

        if results:
            # 轉成 DataFrame 顯示表格
            result_df = pd.DataFrame(results)
            st.dataframe(result_df)  # 或 st.table(result_df)
        else:
            st.info("這個產品在 F~M 欄位沒有 'Y'")
