import streamlit as st
import pandas as pd

st.title("🔍 產品毒化物查詢系統")

# 固定讀取 Excel（請確認檔案放在同資料夾）
    df = pd.read_excel("toxic_NAS.xlsx")


# G 至 N 欄位 = 毒化物類別
type_cols = df.columns[6:14]

# 計算毒化物類型
def get_toxin_types(row):
    types = []
    for col in type_cols:
        if str(row[col]).strip().upper() == "Y":
            types.append(col.split("\n")[0])  # 取換行前
    return ",".join(types) if types else ""

# 建立查詢資料表
df["毒化物類型"] = df.apply(get_toxin_types, axis=1)

# 查詢輸入欄位
product_input = st.text_input("請輸入產品編號（Product#）")

if product_input:
    result = df[df["Product#"].astype(str) == product_input]

    if result.empty:
        st.warning("⚠️ 查無此產品編號，請確認輸入是否正確。")
    else:
        st.subheader("📌 查詢結果")

        # 產品是否含毒化物
        toxin_type = result["毒化物類型"].iloc[0]

        if toxin_type == "":
            st.success("✅ 此產品 **不含毒化物**")
        else:
            st.error(f"❗ 此產品 **含毒化物**：{toxin_type}")

        # 顯示資料詳細內容
        st.write("產品詳細資料：")
        st.dataframe(result, use_container_width=True)
