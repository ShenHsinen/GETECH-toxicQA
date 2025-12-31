import streamlit as st
import pandas as pd

st.title("🔍 毒化物查詢系統")

# 讀取 CSV
df = pd.read_csv("List_NAS.csv")
df_doc = pd.read_csv("Document_NAS.csv")

# 設定要檢查的欄位範圍（G~N）
cols_to_check = df.columns[5:13]  # 假設 F~M 是第7~14欄

# 使用者輸入產品編號
pid = st.text_input("請輸入產品編號")

if pid:
    subset = df[df['產品編號'] == pid]

    if subset.empty:
        st.warning("查無此產品編號")
    else:
        # 用來存結果的 list
        results = []

        for idx, row in subset.iterrows():
            # 找出 F~M 欄位為 'Y' 的欄位
            cols_with_Y = [col for col in cols_to_check if 'Y' in str(row[col]).upper()]
            if cols_with_Y:
                results.append({
                    "Cas No.": row['CAS NO'],
                    "濃度": f"{row.get('濃度', '')}{row.get('單位', '')}",
                    "需申請文件類別": ", ".join(cols_with_Y),
                    "申請文件類別": row['申請文件類別'],
                    "產品包裝": row['產品包裝']
                })

        if results:
            # 轉成 DataFrame 顯示表格
            result_df = pd.DataFrame(results)
            st.subheader(f"產品編號:{pid}")
            st.dataframe(result_df.reset_index(drop=True))

        else:
            st.info("無需申請文件")

        # -------- 依申請文件類別查第二個檔案 --------
        doc_types = set()

        for r in results:
            if r.get("申請文件類別"):
                for d in str(r["申請文件類別"]).split("、"):
                    doc_types.add(d.strip())

        if doc_types:
            st.subheader("📄 需準備的相關文件")

            doc_subset = df_doc[
                df_doc["申請文件類別"].isin(doc_types)
            ]

            if doc_subset.empty:
                st.info("找不到對應的文件需求資料")
            else:
                st.dataframe(doc_subset.reset_index(drop=True))
        else:
            st.success("此產品無需準備任何申請文件")
