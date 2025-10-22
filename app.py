import streamlit as st
import pandas as pd

st.title("🔍 毒化物查詢與應對問答系統")

# 讀取資料
df = pd.read_csv("toxic_list.csv")
detail_df = pd.read_csv("toxic_detail.csv")  # 新增的詳細資訊檔案

# 查詢區
query = st.text_input("請輸入產品名稱或 CAS No.（例如：甲醛 或 50-00-0）")

if query:
    # 模糊搜尋中文名、英文名或 CAS No.
    result = df[df.apply(lambda row: query.lower() in str(row.values).lower(), axis=1)]

    if not result.empty:
        st.success("✅ 查詢結果如下：")
        st.dataframe(result)

        # 取出該筆的毒化物類型
        toxic_class = result.iloc[0]["毒化物類型"]
        st.info(f"此物質屬於 **{toxic_class}**，建議確認是否需申請相關文件或許可證。")

        # 依據毒化物類型查找對應資訊
        detail = detail_df[detail_df["毒化物類型"] == toxic_class]

        if not detail.empty:
            d = detail.iloc[0]

            st.markdown("---")
            st.subheader(f"📋 {toxic_class} - 申請與管理資訊")

            st.write(f"**申請必需資料：** {d['申請必需資料']}")
            st.write(f"**注意事項：** {d['注意事項']}")
            st.write(f"**申請、申報端：** {d['申請、申報端']}")
            st.write(f"**審核時間：** {d['審核時間']}")
        else:
            st.warning("⚠️ 查無此毒化物類型的詳細資料。")

    else:
        st.warning("❌ 查無此物質，請確認名稱或 CAS No. 是否正確。")
