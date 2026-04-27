import re
import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder


st.set_page_config(
    page_title="毒化物查詢系統",
    layout="wide"
)

st.markdown(
    """
    <div style="
        display:flex;
        align-items:center;
        justify-content:space-between;
        margin-bottom: 1rem;
    ">
        <h1 style="margin:0;">🔍 毒化物查詢系統</h1>
        <a href="https://forms.cloud.microsoft/r/5GRAJn4Xry" target="_blank">
            <button style="
                background-color:#4CAF50;
                color:white;
                padding:8px 16px;
                border:none;
                border-radius:6px;
                font-size:14px;
                cursor:pointer;">
                📝 填寫使用回饋
            </button>
        </a>
    </div>
    """,
    unsafe_allow_html=True
)


# -------------------- 讀取資料 --------------------
@st.cache_data
def load_data():
    try:
        list_df = pd.read_csv("List_NAS.csv", encoding="utf-8-sig")
        doc_df = pd.read_csv("Document_NAS.csv", encoding="utf-8-sig")
    except:
        list_df = pd.read_csv("List_NAS.csv", encoding="cp950")
        doc_df = pd.read_csv("Document_NAS.csv", encoding="cp950")

    list_df.columns = list_df.columns.str.strip()
    doc_df.columns = doc_df.columns.str.strip()

    return list_df, doc_df


df, df_doc = load_data()


# -------------------- 基本清理 --------------------
df["產品編號"] = df["產品編號"].astype(str).str.strip()


# -------------------- 找 G~N 欄（用名稱，不用位置） --------------------
target_cols = []

for col in df.columns:
    col_clean = str(col).strip().upper()
    if col_clean in list("GHIJKLMN"):
        target_cols.append(col)

if not target_cols:
    st.error("找不到 G~N 欄，請確認欄位名稱")
    st.stop()

cols_to_check = target_cols
G_COL = target_cols[0]  # 第一個就是 G


# -------------------- 使用者輸入 --------------------
pids_input = st.text_area(
    "請輸入產品編號（可用逗號或換行分隔多個）"
)


# -------------------- 查詢 --------------------
if st.button("查詢"):
    if not pids_input.strip():
        st.warning("請先輸入產品編號")
    else:
        pids = [
            p.strip()
            for p in re.split("[,，\n]", pids_input)
            if p.strip()
        ]

        for pid in pids:
            st.subheader(f"產品編號：{pid}")

            subset = df[df["產品編號"] == pid]

            if subset.empty:
                st.warning("查無此產品編號")
                continue

            # -------------------- 查毒化物 --------------------
            results = []

            for _, row in subset.iterrows():

                # ⭐ 保留你原本可查的寫法（寬鬆）
                has_y = any(
                    "Y" in str(row[col]).upper()
                    for col in cols_to_check
                )

                # G欄限值判斷
                g_value = str(row[G_COL]).replace(" ", "").replace("–", "-")

                has_g_limit = (
                    "N" in g_value.upper()
                    and "限值" in g_value
                    and "0.1-10%" in g_value
                )

                if not (has_y or has_g_limit):
                    continue

                notes = []

                if has_g_limit:
                    notes.append("關注化學物質 限值0.1-10%")

                results.append({
                    "Cas No.": row.get("CAS NO", ""),
                    "成分名稱": row.get("成分名稱", ""),
                    "濃度": f"{row.get('濃度', '')}{row.get('單位', '')}",
                    "申請文件類別": row.get("申請文件類別", ""),
                    "產品包裝": row.get("產品包裝", ""),
                    "備註": "、".join(notes)
                })

            # -------------------- 顯示結果 --------------------
            if results:
                result_df = pd.DataFrame(results).reset_index(drop=True)

                gb = GridOptionsBuilder.from_dataframe(result_df)
                gb.configure_default_column(wrapText=True, autoHeight=True)
                grid_options = gb.build()

                AgGrid(
                    result_df,
                    gridOptions=grid_options,
                    fit_columns_on_grid_load=True,
                    enable_enterprise_modules=False,
                    height=220,
                    key=f"result_{pid}"
                )
            else:
                st.success("沒有毒化物成分")

            # -------------------- 文件需求 --------------------
            doc_types = set()

            for r in results:
                val = str(r.get("申請文件類別", "")).strip()

                if val and val.lower() != "nan":
                    for d in re.split("[、,，\n]", val):
                        if d.strip():
                            doc_types.add(d.strip())

            if doc_types:
                st.subheader("📄 需準備的相關文件")

                doc_subset = df_doc[
                    df_doc["參考"].astype(str).str.strip().isin(doc_types)
                ]

                if doc_subset.empty:
                    st.info("找不到對應文件")
                else:
                    doc_display = doc_subset.drop(columns=["參考"]).reset_index(drop=True)

                    gb_doc = GridOptionsBuilder.from_dataframe(doc_display)
                    gb_doc.configure_default_column(wrapText=True, autoHeight=True)
                    grid_options_doc = gb_doc.build()

                    AgGrid(
                        doc_display,  # ⭐ 修正這裡
                        gridOptions=grid_options_doc,
                        fit_columns_on_grid_load=True,
                        enable_enterprise_modules=False,
                        height=220,
                        key=f"doc_{pid}"
                    )
            else:
                st.success("此產品無需準備文件")
