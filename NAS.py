import streamlit as st
import pandas as pd

st.title("🔍 毒化物查詢表 自動產生工具（自動讀取檔案）")

# 直接讀取檔案（請確保檔名與路徑正確）
file_path = "標準品確認清單_NAS.xlsx"
df = pd.read_excel(file_path)


# 取 G~N 欄位（根據你提供的原始格式）
type_cols = df.columns[6:14]

# 建立毒化物類型
def build_toxin_types(row):
    types = []
    for col in type_cols:
        val = str(row[col]).strip().upper()
        if val == "Y":
            types.append(col.split("\n")[0])  # 取換行前名稱
    return ",".join(types) if types else ""

# 建立輸出 DataFrame
out = pd.DataFrame({
    "產品編號": df["Product#"].astype(str),
    "Cas No.": df["CAS#"].astype(str).replace("nan", ""),
    "毒化物類型": df.apply(build_toxin_types, axis=1),
    "是否需要核可文件": "",  # 之後可加入第二檔合併
    "濃度": df["Weight\nConversion"].apply(lambda x: "" if pd.isna(x) else str(x) + "%"),
    "備註": df["備註"].fillna("")
})

st.subheader("📋 毒化物查詢表（自動讀取檔案）")
st.dataframe(out, use_container_width=True)
