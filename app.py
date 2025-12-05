import streamlit as st
import pandas as pd

st.title("🔍 毒化物查詢與應對問答系統")

# 讀取資料
df = pd.read_csv("toxic_list.csv")
detail_df = pd.read_csv("toxic_detail.csv")  # 詳細資訊檔案

# 查詢區
query = st.text_area(
    "請輸入產品名稱或 CAS No.（可多筆，用逗號或換行分隔）", 
    placeholder="例如：50-00-0, 75-07-0\n或輸入：甲醛, 乙醛"
)

# 查詢按鈕
if st.button("🔍 查詢"):
    if query.strip():
        # 分割輸入內容
        queries = [q.strip().lower() for q in query.replace("\n", ",").split(",") if q.strip()]

        # 找出哪些查詢看起來像 CAS No.（格式含 '-'）
        cas_queries = [q for q in queries if "-" in q]

        # --- ① 先試完全比對 CAS No. ---
        exact_results = pd.DataFrame()

        if cas_queries:
            exact_results = df[df["CAS No."].str.lower().isin(cas_queries)]

        # 如果有完全比對結果 → 只顯示這些結果
        if not exact_results.empty:
            result = exact_results
        else:
            # --- ② 沒有完全比對才使用原本的模糊搜尋 ---
            result = df[df.apply(
                lambda row: any(q in str(row.values).lower() for q in queries),
                axis=1
            )]

        # --- 顯示結果 ---
        if not result.empty:
            st.success(f"✅ 查到 {len(result)} 筆結果：")
            st.dataframe(result)

            # 顯示毒化物類型
            toxic_classes = result["毒化物類型"].unique()

            for toxic_class in toxic_classes:
                st.markdown("---")
                st.subheader(f"📋 {toxic_class} - 申請與管理資訊")

                detail = detail_df[detail_df["毒化物類型"] == toxic_class]
                if not detail.empty:
                    d = detail.iloc[0]
                    st.write(f"**申請必需資料：** {d['申請必需資料']}")
                    st.write(f"**注意事項：** {d['注意事項']}")
                    st.write(f"**申請、申報端：** {d['申請、申報端']}")
                    st.write(f"**審核時間：** {d['審核時間']}")
                else:
                    st.warning(f"⚠️ 查無「{toxic_class}」的詳細資料。")
        else:
            st.warning("❌ 查無任何符合的物質，請確認名稱或 CAS No. 是否正確。\n查詢新化學物質 https://csnn.osha.gov.tw/content/home/Substance_Home.aspx")
    else:
        st.info("請先輸入至少一項查詢內容再按下『查詢』。")
