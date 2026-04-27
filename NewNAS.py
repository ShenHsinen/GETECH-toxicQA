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
    except UnicodeDecodeError:
        list_df = pd.read_csv("List_NAS.csv", encoding="cp950")
        doc_df = pd.read_csv("Document_NAS.csv", encoding="cp950")

    list_df.columns = list_df.columns.str.strip()
    doc_df.columns = doc_df.columns.str.strip()

    return list_df, doc_df


df, df_doc = load_data()


# -------------------- 基本欄位檢查 --------------------
required_cols = ["產品編號", "CAS NO", "成分名稱", "濃度", "單位", "申請文件類別", "產品包裝"]

missing_cols = [col for col in required_cols if col not in df.columns]

if missing_cols:
    st.error(f"List_NAS.csv 缺少欄位：{', '.join(missing_cols)}")
    st.stop()

if "參考" not in df_doc.columns:
    st.error("Document_NAS.csv 缺少欄位：參考")
    st.stop()


# 產品編號統一轉字串，避免數字格式查不到
df["產品編號"] = df["產品編號"].astype(str).str.strip()


# -------------------- 毒化物類別欄位設定 --------------------
# 依照你之前的需求：檢查 G~N 欄
# pandas 欄位索引從 0 開始，所以 G 欄是 index 6，N 欄是 index 13
if len(df.columns) < 14:
    st.error("List_NAS.csv 欄位數不足，無法檢查 G~N 欄")
    st.stop()

cols_to_check = df.columns[6:14]
G_COL = df.columns[6]


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

            # -------------------- 查毒化物成分 --------------------
            results = []

            for _, row in subset.iterrows():

                # 條件 A：G~N 欄是否有 Y
                has_y = any(
                    str(row[col]).strip().upper() == "Y"
                    for col in cols_to_check
                )

                # 條件 B：G 欄是否含「N 限值0.1-10%」
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

            # -------------------- 顯示毒化物結果 --------------------
            if results:
                result_df = pd.DataFrame(results).reset_index(drop=True)

                gb = GridOptionsBuilder.from_dataframe(result_df)
                gb.configure_default_column(
                    wrapText=True,
                    autoHeight=True
                )
                grid_options = gb.build()

                AgGrid(
                    result_df,
                    gridOptions=grid_options,
                    fit_columns_on_grid_load=True,
                    enable_enterprise_modules=False,
                    height=220,
                    key=f"result_grid_{pid}"
                )

            else:
                st.success("沒有毒化物成分")

            # -------------------- 查文件需求 --------------------
            doc_types = set()

            for r in results:
                doc_value = str(r.get("申請文件類別", "")).strip()

                if doc_value and doc_value.lower() != "nan":
                    for d in re.split("[、,，\n]", doc_value):
                        d = d.strip()
                        if d:
                            doc_types.add(d)

            if doc_types:
                st.subheader("📄 需準備的相關文件")

                doc_subset = df_doc[
                    df_doc["參考"].astype(str).str.strip().isin(doc_types)
                ]

                if doc_subset.empty:
                    st.info("找不到對應的文件需求資料")
                else:
                    doc_display = doc_subset.drop(columns=["參考"]).reset_index(drop=True)

                    gb_doc = GridOptionsBuilder.from_dataframe(doc_display)
                    gb_doc.configure_default_column(
                        wrapText=True,
                        autoHeight=True
                    )
                    grid_options_doc = gb_doc.build()

                    AgGrid(
                        doc_display,
                        gridOptions=grid_options_doc,
                        fit_columns_on_grid_load=True,
                        enable_enterprise_modules=False,
                        height=220,
                        key=f"doc_grid_{pid}"
                    )

            else:
                st.success("此產品無需準備任何申請文件")
