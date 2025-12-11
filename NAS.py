import streamlit as st
import pandas as pd

# 讀取主資料檔
df = pd.read_csv("toxic_NAS.csv")

st.title("🔍 毒化物成分查詢系統")

# 使用者輸入產品編號
prod_no = st.text_input("請輸入產品編號：")

# 定義毒化物欄位（G~N）
hazard_cols = df.columns[6:14]  # 確保是第7~14欄

if prod_no:
    # 查詢產品
    result = df[df["Product#"] == prod_no]

    if result.empty:
        st.warning("查無此產品編號")
    else:
        row = result.iloc[0]

        # 找出 G~N 欄位中值為 “Y” 的欄位表頭
        toxin_list = [col for col in hazard_cols if str(row[col]).strip().upper() == "Y"]

        # 判斷是否含毒化物
        if toxin_list:
            toxin_type = "、".join(toxin_list)
        else:
            toxin_type = "沒有毒化物成分"

        # 是否需要核可文件 → 等你給第二個檔案，我可幫你自動合併
        require_docs = ""

        # 濃度：直接使用 WeightConversion 欄位
        concentration = row["WeightConversion"]

        # 顯示結果
        st.subheader("查詢結果")

        st.write(f"**CAS Number：** {row['CAS#']}")
        st.write(f"**濃度 (WeightConversion)：** {concentration}")
        st.write(f"**毒化物類型：** {toxin_type}")
        st.write(f"**是否需要相關文件：** ")
        st.write(f"**備註：** {row['備註']}")
