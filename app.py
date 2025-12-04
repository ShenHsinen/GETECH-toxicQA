import streamlit as st
import pandas as pd
import requests
import json

st.title("🔍 毒化物查詢與智能判別（LM Studio 本地 AI）")

# 讀取資料
df = pd.read_csv("toxic_list.csv")
detail_df = pd.read_csv("toxic_detail.csv")

# LM Studio API 設定
LM_API_URL = "http://127.0.0.1:1234/v1/chat/completions"

def ask_lmstudio(prompt):
    payload = {
        "model": "local-model",  # LM Studio 會自動忽略這欄
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0
    }
    res = requests.post(LM_API_URL, json=payload)
    return res.json()["choices"][0]["message"]["content"]


# 使用者查詢
raw_text = st.text_area("請貼上產品成分、SDS、或 CAS No.：")

if st.button("開始智能判斷 + 查詢毒化物"):
    if raw_text.strip() == "":
        st.warning("請輸入文字。")
    else:
        st.info("⏳ 正在使用本地 AI（LM Studio）判讀內容…")

        # ✨ 叫 LM Studio 幫你萃取 CAS No.
        prompt = f"""
以下為原始內容：

{raw_text}

請從中提取出所有 CAS No.，格式輸出為純列表，例如：
50-00-0
75-52-5
100-41-4
"""

        cas_list_text = ask_lmstudio(prompt)
        cas_list = [line.strip() for line in cas_list_text.split("\n") if "-" in line]

        st.write("📌 AI 判斷出的 CAS No.：")
        st.write(cas_list)

        # 開始比對
        results = df[df["CAS No."].isin(cas_list)]

        if not results.empty:
            st.success("🎯 以下成分屬於毒化物：")
            st.dataframe(results)

            toxic_class = results.iloc[0]["毒化物類型"]
            detail = detail_df[detail_df["毒化物類型"] == toxic_class]

            if not detail.empty:
                d = detail.iloc[0]
                st.markdown("---")
                st.subheader(f"📘 相關申請與管理資訊 – {toxic_class}")
                st.write(f"**申請必需資料：** {d['申請必需資料']}")
                st.write(f"**注意事項：** {d['注意事項']}")
                st.write(f"**申請/申報端：** {d['申請、申報端']}")
                st.write(f"**審核時間：** {d['審核時間']}")
        else:
            st.warning("❌ 查無毒化物。可能不在你的資料清單中。")
