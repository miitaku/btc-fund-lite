# -*- coding: utf-8 -*-
import streamlit as st
import requests
from datetime import datetime
from PIL import Image
import base64
import os # ★ osモジュールをインポート

# --- Secretsから取得 ---
CRYPTO_API_KEY = st.secrets["cryptopanic"]["api_key"]
DEEPL_API_KEY = st.secrets["deepl"]["api_key"]

# --- ページ設定 ---
st.set_page_config(page_title="BTCファンダレーダー", layout="wide")

# --- ホーム画像にリンクを付ける ---
def add_logo_with_link(image_path, link_url, width=80):
    # エラーハンドリングを追加して、もしファイルが見つからなかった場合にメッセージを表示
    try:
        with open(image_path, "rb") as f:
            data = f.read()
            encoded = base64.b64encode(data).decode()
        st.markdown(
            f"""
            <a href="{link_url}">
                <img src="data:image/png;base64,{encoded}" width="{width}">
            </a>
            """,
            unsafe_allow_html=True
        )
    except FileNotFoundError:
        st.error(f"エラー: 画像ファイルが見つかりません。パスを確認してください: {image_path}")
        st.write("---") # エラー表示と区切り

# --- ヘッダー：ロゴ＋タイトルを1行にレイアウト ---
col_logo, col_title = st.columns([1, 8])
with col_logo:
    # ★ ここから修正箇所 ★
    # 現在のスクリプト (app.py) のディレクトリパスを取得
    # 例: /mount/src/btc-fund-lite/btc-fund-plus/
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 画像ファイルへのフルパスを構築
    # /mount/src/btc-fund-lite/btc-fund-plus/assets/hiroalufa8001.png
    image_full_path = os.path.join(current_script_dir, "assets", "hiroalufa8001.png")
    
    # 構築したフルパスを関数に渡す
    add_logo_with_link(image_full_path, link_url="/")
    # ★ 修正ここまで ★

with col_title:
    st.markdown(
        "<h2 style='margin-bottom: 0px; line-height: 1;'>BTCファンダレーダー</h2>"
        "<p style='font-size: 14px; color: gray; margin-top: 4px;'>"
        "暗号通貨ビットコインに関する価格、心理指数、ニュースを1ページで一括チェックできるレーダーアプリです。</p>",
        unsafe_allow_html=True
    )

st.markdown("---")


# --- BTC価格取得 ---
def get_btc_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd,jpy"
    res = requests.get(url).json()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 取得時刻
    return res["bitcoin"]["usd"], res["bitcoin"]["jpy"], now

usd, jpy, updated_time = get_btc_price()
st.markdown("### 💰 BTC価格", unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    st.metric(label="USD価格", value=f"${usd:,}")
with col2:
    st.metric(label="JPY価格", value=f"¥{jpy:,}")
st.caption(f"※ データ取得時刻：{updated_time}（ローカル時間）")
st.markdown("")

# --- Fear & Greed Index取得 ---
def get_fear_greed_index():
    url = "https://api.alternative.me/fng/"
    res = requests.get(url).json()
    index = int(res['data'][0]['value'])
    state = res['data'][0]['value_classification']
    return index, state

index, state = get_fear_greed_index()
st.subheader("🚦 売買判断の目安（Fear & Greed Index）")
if index <= 25:
    comment = "🟢 恐怖（買い傾向）"
    advice = "現在は市場に恐怖が広がっています。買いのチャンスかもしれません。"
elif index >= 75:
    comment = "🔴 欲望（売り傾向）"
    advice = "市場が強気すぎる状態です。利確や警戒が必要かもしれません。"
else:
    comment = "🟡 中立（様子見）"
    advice = "市場は比較的落ち着いています。状況を見ながら戦略を立てましょう。"
st.markdown(f"**現在の指数：{index}（{comment}）**")

# 🔽 開閉式説明パネルを追加
with st.expander("🔎 Fear & Greed Indexとは？"):
    st.markdown("""
- 投資家の心理を「恐怖（Fear）」と「欲望（Greed）」の度合いで数値化した指標です。
- 数値が **0に近いほど恐怖**, **100に近いほど強欲**。
- 一般的に「25以下」は**買い時**、「75以上」は**売り時**の目安とされています。
""")

# 💬 コメントを枠付きで表示（ライト・ダーク両モード対応）
st.markdown(
    f"""<div style='
        border-left: 6px solid #2E86C1;
        padding: 10px;
        background-color: rgba(46,134,193,0.1);
        color: inherit;
        font-size: 16px;
    '>
    <strong style='color: inherit;'>市場分析：</strong> {advice}
    </div>""",
    unsafe_allow_html=True
)

st.markdown("&nbsp;", unsafe_allow_html=True)
st.markdown("&nbsp;", unsafe_allow_html=True)

# --- CryptoPanicニュース取得 ---
def get_btc_news():
    url = f"https://cryptopanic.com/api/v1/posts/?auth_token={CRYPTO_API_KEY}&currencies=BTC"
    res = requests.get(url)
    if res.status_code == 200:
        return res.json().get("results", [])
    else:
        st.error(f"ニュース取得失敗（Status: {res.status_code}）")
        return []

# --- DeepL翻訳 ---
def translate_to_japanese(text):
    url = "https://api-free.deepl.com/v2/translate"
    params = {
        "auth_key": DEEPL_API_KEY,
        "text": text,
        "target_lang": "JA"
    }
    res = requests.post(url, data=params)
    if res.status_code == 200:
        return res.json()["translations"][0]["text"]
    else:
        return text + "（翻訳失敗）"

# --- ニュース表示 ---
st.subheader("📰 BTC関連ニュース・イベント")
posts = get_btc_news()

if posts:
    for post in posts[:5]:
        dt = post.get('published_at', '')[:10]
        title_en = post.get('title', '')
        title_ja = translate_to_japanese(title_en)
        url = post.get('url', '')
        
        st.markdown(f"📅 {dt}")
        st.markdown(f"**{title_ja}**")
        
        if url:
            st.markdown(f"📎 [情報元リンクはこちら]({url})")
        else:
            st.markdown("（リンクなし）")
        
        st.write("---")
else:
    st.warning("ニュースが取得できませんでした。")

# --- フッター：利用規約・免責事項 ---
st.markdown("---")
st.markdown("### 📄 ご利用にあたって")

with st.expander("🔐 利用規約（Terms of Use）"):
    st.markdown("""
このサービスは、情報提供のみを目的としており、金融商品の売買を勧誘・推奨するものではありません。  
掲載されている情報の正確性・完全性について保証するものではなく、内容に基づいて発生したいかなる損失についても責任を負いかねます。  
ご利用者様ご自身の判断と責任においてご活用ください。
    """)

with st.expander("⚠️ 免責事項（Disclaimer）"):
    st.markdown("""
本アプリにおける価格情報や指標、ニュース等は外部APIに依存しています。  
取得元の変更や仕様の不具合等により、正確な情報が提供されない可能性があります。  
また、情報の解釈・活用はすべてご利用者の責任において行ってください。  
本サービス運営者は、当アプリ利用に関連して生じたいかなる損害についても一切の責任を負いません。
    """)
