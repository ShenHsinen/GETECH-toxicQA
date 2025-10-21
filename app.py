import streamlit as st
import pandas as pd

st.title("🔍 毒化物查詢與應對問答系統")

# 讀取毒化物清單
df = pd.read_csv("管制性化學品清單.csv")

# 查詢區
query = st.text_input("請輸入產品名稱或 CAS No.（例如：甲醛 或 50-00-0）")

if query:
    # 模糊搜尋中文名、英文名或 CAS No.
    result = df[df.apply(lambda row: query.lower() in str(row.values).lower(), axis=1)]

    if not result.empty:
        st.success("✅ 查詢結果如下：")
        st.dataframe(result)
        # 產生簡易回應
        toxic_class = result.iloc[0]["特定化學物質類別"]
        st.info(f"此物質屬於 **{toxic_class} 毒化物**，建議確認是否需申請相關文件或許可證。")
    else:
        st.warning("❌ 查無此物質，請確認名稱或 CAS No. 是否正確。")

