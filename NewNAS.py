import streamlit as st
import pandas as pd

st.title("🔍 毒化物查詢系統")

# -------------------- 讀取資料 --------------------
df = pd.read_csv("List_NAS.csv")
df_doc = pd.read_csv("Document_NAS.csv")

# 清理欄位名稱，去掉多餘空白
df.columns = df.columns.str.strip()
df_doc.columns = df_doc.columns.str.strip()

# 要檢查是否含 Y 的欄位（假設 G~N）
cols_to_check = df.columns[5:13]

# -------------------- 使用者輸入 --------------------
pids_input = st.text_area(
    "請輸入產品編號（可用逗號或換行分隔多個）"
)

# 新增查詢按鈕
if st.button("查詢"):
    if not pids_input.strip():
        st.warning("請先輸入產品編號")
    else:
        # 拆成多個產品編號，去掉空白
        pids = [p.strip() for p in pids_input.replace('\n', ',').split(',') if p.strip()]

        for pid in pids:
            st.subheader(f"產品編號：{pid}")

            subset = df[df['產品編號'] == pid]

            if subset.empty:
                st.warning("查無此產品編號")
                continue

            # -------------------- 查毒化物成分 --------------------

            G_COL = cols_to_check[0]   # G 欄位
            OTHER_COLS = cols_to_check[1:]  # H~N

            results = []
            for _, row in subset.iterrows():
            hit_cols = []
        
            # 1️⃣ G~N 欄位：判斷 Y（原本邏輯）
            for col in cols_to_check:
                if 'Y' in str(row[col]).upper():
                    hit_cols.append(col)
        
            # 2️⃣ 只針對 G 欄位：N + 限值
            g_value = str(row[G_COL])
            if ('N' in g_value) and ('限值0.1-10%' in g_value):
                hit_cols.append('G')
        
            # 去重
            hit_cols = list(set(hit_cols))
        
            if hit_cols:
                results.append({
                    "Cas No.": row.get('CAS NO', ''),
                    "成分名稱": row.get('成分名稱', ''),
                    "濃度": f"{row.get('濃度', '')}{row.get('單位', '')}",
                    "命中欄位": "、".join(hit_cols),
                    "申請文件類別": row.get('申請文件類別', ''),
                    "產品包裝": row.get('產品包裝', '')
                })


            if results:
                result_df = pd.DataFrame(results)
                st.table(result_df)
            else:
                st.success("沒有毒化物成分")

            # -------------------- 查文件需求 --------------------
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
                        st.table(doc_subset)
            else:
                st.success("此產品無需準備任何申請文件")
