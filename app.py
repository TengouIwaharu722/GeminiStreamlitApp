"""
実行は「ターミナル」で下記を打ち込みます
cd F:\Python_home\GeminiStreamlitApp
streamlit run app.py
終了するにはターミナルで「CTRL+C」を入力です。
https://geministreamlitapp.onrender.com/
"""
import streamlit as st
import os
import time
import json
from dotenv import load_dotenv
import google.generativeai as genai
import google.api_core.exceptions

# base_pathはこのファイルのある場所
base_path = os.path.dirname(__file__)
module_path = os.path.join(base_path, "Module")

# .envファイルからAPIキーを読み込む
env_path = os.path.join(module_path, ".env")
load_dotenv(dotenv_path=env_path)
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# 履歴ファイルのパス（Moduleフォルダ内の chat_history.json を使用）
history_path = os.path.join(module_path, "chat_history.json")

# 履歴を読み込む（存在しない場合は空リスト）
if os.path.exists(history_path):
    with open(history_path, "r", encoding="utf-8") as file:
        history = json.load(file)
else:
    history = []

# モデルを初期化してチャット開始（履歴を渡す）
model = genai.GenerativeModel("models/gemini-2.5-pro")
chat = model.start_chat(history=history)

# Streamlit UI
st.header("就職支援ソフト【ナベちゃん】")
st.markdown("""
<h4 class="custom-h4">プロが教えてさしあげます</h4>
""", unsafe_allow_html=True)


st.markdown("""
<style>
@media screen and (max-width: 768px) {
    h1, h2, h3, h4 {
        font-size: 1.3em !important;
        font-family: "Yu Gothic", "Meiryo", "Hiragino Kaku Gothic ProN", sans-serif;
    }
    .custom-h4 {
        font-size: 1.1em !important;
        font-family: "Yu Gothic", "Meiryo", "Hiragino Kaku Gothic ProN", sans-serif;
        letter-spacing: 0.05em;
    }
    p, div, span {
        font-size: 1em !important;
    }
}
</style>
""", unsafe_allow_html=True)

# セッションステート初期化
for key, default in {
    "question_input": "",
    "last_answer": "",
    "saved": None,
    "last_question": "",  # 送信された質問を保持
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# 質問入力欄
st.text_area("質問を入力してください：", key="question_input", height=100)

# 送信処理
if st.button("送信"):
    question = st.session_state.question_input.strip()
    if question == "":
        st.warning("質問を入力してください。")
    else:
        if question.lower() in ["テスト","テスト2"]:
            answer = "（モック応答）これはテスト用の回答です。"
        else:
            try:
                response = chat.send_message(question)
                answer = response.text
            except google.api_core.exceptions.ResourceExhausted:
                st.error("❌ Gemini APIの無料リクエスト上限に達しました。しばらく待って再試行してください。")
                st.stop()
        st.session_state.last_question = question
        st.session_state.last_answer = answer
        st.session_state.saved = None  # 新しい回答なので保存ボタンを再び有効にする
        st.rerun()

# 回答表示と保存ボタン
if st.session_state.last_answer:
    st.markdown("### 回答")
    st.write(st.session_state.last_answer)

    # いいねボタン（保存）
    if st.session_state.saved is not True:
        if st.button("👍 いいねして保存"):
            # 保存処理
            history.append({"role": "user", "parts": [st.session_state.last_question]})
            history.append({"role": "model", "parts": [st.session_state.last_answer]})
            with open(history_path, "w", encoding="utf-8") as file:
                json.dump(history, file, ensure_ascii=False, indent=2)
            st.session_state.saved = True
            st.success("✅ 回答を保存しました。")
    else:
        st.info("👍 この回答はすでに保存されています。")


