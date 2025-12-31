import streamlit as st
import pandas as pd

st.title("🔍 毒化物查詢系統")

# 讀取資料
df = pd.read_csv("List_NAS.csv")
df_doc = pd.read_csv("Document_NAS.csv")

# 清理欄位名稱
df.columns = df.columns.str.strip()
df_doc.columns = df_doc.columns.str.strip()

# ====== 檢查文件檔欄位（除錯用，可之後刪）======
# st.write(df_doc.columns)

# 要檢查是否含 Y 的欄位（G~N）
cols_to_check = df.columns[5:13]

pid = st.text_input("請輸入產品編號")

if pid:
    subset = df[df['產品編號'] == pid]

    if subset.empty:
        st.warning("查無此產品編號")
    else:
        results = []

        for _, row in subset.iterrows():
            cols_with_Y = [
                col for col in cols_to_check
                if 'Y' in str(row[col]).upper()
            ]

            if cols_with_Y:
                results.append({
                    "Cas No.": row.get('CAS NO', ''),
                    "濃度": f"{row.get('濃度', '')}{row.get('單位', '')}",
                    "毒化物類型": ", ".join(cols_with_Y),
                    "申請文件類別": row.get('申請文件類別', ''),
                    "備註": row.get('產品包裝', '')
                })

        st.subheader(f"產品編號：{pid}")

        if results:
            result_df = pd.DataFrame(results)
            st.dataframe(result_df.reset_index(drop=True))
        else:
            st.success("沒有毒化物成分")

        # ====== 查詢文件需求 ======
        doc_types = set()

        for r in results:
            if r.get("申請文件類別"):
                for d in str(r["申請文件類別"]).split("、"):
                    doc_types.add(d.strip())

        if doc_types:
            st.subheader("📄 需準備的相關文件")

            DOC_COL = "參考" 

            if DOC_COL not in df_doc.columns:
                st.error(f"文件檔中找不到欄位：{DOC_COL}")
            else:
                doc_subset = df_doc[df_doc[DOC_COL].isin(doc_types)]

                if doc_subset.empty:
                    st.info("找不到對應的文件需求資料")
                else:
                    st.dataframe(doc_subset.reset_index(drop=True))
        else:
            st.success("此產品無需準備任何申請文件")
