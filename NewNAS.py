import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder


st.set_page_config(
    page_title="毒化物查詢系統",
    layout="wide"
)

st.title("🔍 毒化物查詢系統")

# -------------------- 讀取資料 --------------------
df = pd.read_csv("List_NAS.csv")
df_doc = pd.read_csv("Document_NAS.csv")

# 清理欄位名稱，去掉多餘空白
df.columns = df.columns.str.strip()
df_doc.columns = df_doc.columns.str.strip()

# 要檢查是否含 Y 的欄位（假設 F~M）
cols_to_check = df.columns[5:12]

# -------------------- 使用者輸入 --------------------
pids_input = st.text_area(
    "請輸入產品編號（可用逗號或換行分隔多個）"
)

# -------------------- 查詢 --------------------
if st.button("查詢"):
    if not pids_input.strip():
        st.warning("請先輸入產品編號")
    else:
        # 拆成多個產品編號
        pids = [
            p.strip()
            for p in pids_input.replace("\n", ",").split(",")
            if p.strip()
        ]

        for pid in pids:
            st.subheader(f"產品編號：{pid}")

            subset = df[df["產品編號"] == pid]

            if subset.empty:
                st.warning("查無此產品編號")
                continue

            # -------------------- 查毒化物成分 --------------------
            results = []

            G_COL = cols_to_check[1]        # F 欄位
            OTHER_COLS = cols_to_check[0:]  # F~M

            for _, row in subset.iterrows():
            
                # 只看 G 欄
                g_value = str(row[G_COL]).replace(" ", "")
            
                # 只要符合這個條件，備註才顯示
                if (
                    "N" in g_value
                    and "限值" in g_value
                    and ("0.1-10%" in g_value or "0.1–10%" in g_value)
                ):
                    results.append({
                        "Cas No.": row.get("CAS NO", ""),
                        "成分名稱": row.get("成分名稱", ""),
                        "濃度": f"{row.get('濃度', '')}{row.get('單位', '')}",
                        "申請文件類別": row.get("申請文件類別", ""),
                        "產品包裝": row.get("產品包裝", ""),
                        "備註": "關注化學物質 限值0.1-10%"
                    })

            # -------------------- 顯示毒化物結果 --------------------
            if results:
                result_df = pd.DataFrame(results)
            
                # 設定 AgGrid 選項
                gb = GridOptionsBuilder.from_dataframe(result_df)
                gb.configure_default_column(
                    wrapText=True,      # 文字換行
                    autoHeight=True     # 自動調整列高
                )
                grid_options = gb.build()
                AgGrid(
                    result_df,
                    gridOptions=grid_options,
                    fit_columns_on_grid_load=True,   # 載入時自動調整欄寬
                    enable_enterprise_modules=False,
                    height=200
                )
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
                        # AgGrid 顯示
                        gb_doc = GridOptionsBuilder.from_dataframe(doc_subset)
                        gb_doc.configure_default_column(
                            wrapText=True,
                            autoHeight=True
                        )
                        grid_options_doc = gb_doc.build()
                        AgGrid(
                            doc_subset,
                            gridOptions=grid_options_doc,
                            fit_columns_on_grid_load=True,
                            enable_enterprise_modules=False,
                            height=200
                        )
            else:
                st.success("此產品無需準備任何申請文件")
