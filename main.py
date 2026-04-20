import streamlit as st
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings
import base64

# ── 配置（原样保留）────────────────────────────────────────
VOICE_ID = "MpFj36VyP4TvI7fd8mQA"
MODEL_ID = "eleven_v3"
STABILITY_VAL = 0.85
DEEPSEEK_API_KEY = "sk-46f5736e30f544288284d6b7d7641393"
ELEVENLABS_API_KEY = "sk_57e57c67990c2b1a1a5b44c018cf81b0564cc1cc777b7de8"

client_el = ElevenLabs(api_key=ELEVENLABS_API_KEY)

# ── 预设问答（原样保留）────────────────────────────────────
SPECIFIC_RESPONSES = {
    "朗读《红楼梦》的书评":
        "《红楼梦》不仅是一部描写封建家族衰落的小说，更是一部关于生命幻灭与悲剧美学的史诗。作者曹雪芹通过复杂的意象和精妙的谶语，勾勒出了一个大观园式的理想国。这种从繁华到荒凉的剧烈转变揭示了传统社会中人性与礼教之间不可调和的矛盾。",
    "朗读《三国演义》的书评":
        "《三国演义》以宏大的视野展现了近一个世纪的军事斗争。作品成功塑造了曹操的性格和诸葛亮的智者形象。体现了民间叙事中对'义'与'智'的高度崇拜其战争描写不仅具备文学张力，更包含了深刻的权谋策略与地缘政治考量。",
    "朗读《西游记》的书评":
        "《西游记》通过一场充满奇幻色彩的取经之旅，构建了一个神魔交织、妙趣横生的童话世界。孙悟空的叛逆与成长，实际上象征着人类心灵在面对困境时的顽强生命力。这部作品以浪漫主义的手法，探讨了意志、信仰以及个人与社会规则之间的博弈。",
    "朗读《水浒传》的书评":
        "《水浒传》是施耐庵创作的中国四大名著之一。讲述了108位梁山好汉反抗腐败官府、为民除暴的传奇故事。全书人物众多,每个角色都有鲜明的个性和背景,如忠诚勇敢的宋江、义气深重的武松、深藏不露的林冲等。",
}

# ── 读取背景图并转为 base64 ────────────────────────────────
def get_bg_base64(image_path: str) -> str:
    with open(image_path, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    return data

# ⚠️ 把图片放在与 app.py 同一目录，文件名改短
BG_BASE64 = get_bg_base64("bg.png")

# ── 页面配置 ──────────────────────────────────────────────
st.set_page_config(page_title="生成式 AI 声音研究", layout="centered")

st.markdown(f"""
<style>
/* ── 全局背景 ── */
.stApp {{
    background-image: url("data:image/png;base64,{BG_BASE64}");
    background-size: cover;
    background-position: center top;
    background-attachment: fixed;
    font-family: -apple-system, 'PingFang SC', 'Helvetica Neue', sans-serif;
}}

/* 背景加深色蒙版，保证文字可读 */
.stApp::before {{
    content: "";
    position: fixed;
    inset: 0;
    background: rgba(10, 18, 14, 0.55);
    z-index: 0;
    pointer-events: none;
}}

/* 所有内容层级在蒙版之上 */
.stApp > * {{ position: relative; z-index: 1; }}

header {{ visibility: hidden; }}

/* ── 固定顶部标题栏 ── */
.fixed-header {{
    position: fixed; top: 0; left: 0; width: 100%;
    background: rgba(10, 22, 16, 0.75);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-bottom: 0.5px solid rgba(80, 200, 140, 0.25);
    padding: 12px 16px 10px;
    display: flex; align-items: center; gap: 10px;
    z-index: 1000;
}}
.header-icon {{
    width: 32px; height: 32px; border-radius: 10px;
    background: rgba(46, 139, 106, 0.3);
    border: 0.5px solid rgba(80, 200, 140, 0.4);
    display: flex; align-items: center; justify-content: center;
    font-size: 15px; flex-shrink: 0;
}}
.header-title {{ font-size: 14px; font-weight: 500; color: #e8f5ee; }}
.header-sub {{ font-size: 10px; color: rgba(180,220,200,0.6); margin-top: 1px; }}

/* ── 聊天内容区 ── */
.chat-outer {{ padding-top: 68px; padding-bottom: 108px; }}

/* ── 用户气泡 ── */
.bubble-user {{
    background: rgba(46, 139, 106, 0.85);
    color: #e8f5ee;
    border: 0.5px solid rgba(80, 200, 140, 0.4);
    border-radius: 16px 16px 4px 16px;
    padding: 10px 14px;
    max-width: 80%;
    font-size: 14px; line-height: 1.6;
    margin-left: auto; margin-bottom: 12px;
    display: table;
    backdrop-filter: blur(6px);
}}

/* ── AI 气泡 ── */
.bubble-ai-wrap {{
    display: flex; align-items: flex-start;
    gap: 8px; margin-bottom: 12px;
}}
.ai-avatar {{
    width: 30px; height: 30px; border-radius: 50%;
    background: rgba(46, 139, 106, 0.25);
    border: 0.5px solid rgba(80, 200, 140, 0.35);
    flex-shrink: 0;
    display: flex; align-items: center; justify-content: center;
    font-size: 14px;
}}
.bubble-ai {{
    background: rgba(15, 28, 20, 0.72);
    border: 0.5px solid rgba(80, 200, 140, 0.2);
    border-radius: 4px 16px 16px 16px;
    padding: 10px 14px;
    max-width: 80%;
    font-size: 14px; line-height: 1.7; color: #d4ede2;
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
}}

/* ── 音频播放器 ── */
section.main audio {{
    width: 100%;
    max-width: 280px;
    height: 36px;
    margin-top: 8px;
    border-radius: 10px;
    filter: invert(0.85) hue-rotate(100deg);
}}

/* ── 固定底部控制栏 ── */
.fixed-footer {{
    position: fixed; bottom: 0; left: 0; width: 100%;
    background: rgba(10, 22, 16, 0.80);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border-top: 0.5px solid rgba(80, 200, 140, 0.2);
    padding: 10px 16px 20px;
    z-index: 1000;
}}
.footer-hint {{
    font-size: 11px; color: rgba(160, 210, 180, 0.6);
    margin-bottom: 7px;
}}

/* ── 下拉框 ── */
div[data-baseweb="select"] > div {{
    border-radius: 10px !important;
    border-color: rgba(80, 200, 140, 0.3) !important;
    background: rgba(15, 30, 20, 0.7) !important;
    color: #c8e8d8 !important;
    font-size: 13px !important;
    min-height: 38px !important;
}}
div[data-baseweb="select"] span {{
    color: #c8e8d8 !important;
}}

/* ── 发送按钮 ── */
.stButton > button {{
    background: rgba(46, 139, 106, 0.9) !important;
    color: #e8f5ee !important;
    border: 0.5px solid rgba(80, 200, 140, 0.5) !important;
    border-radius: 10px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    height: 38px;
    padding: 0 16px !important;
    backdrop-filter: blur(6px);
}}
.stButton > button:hover {{
    background: rgba(29, 110, 80, 0.95) !important;
}}
</style>

<div class="fixed-header">
    <div class="header-icon">🎙️</div>
    <div>
        <div class="header-title">生成式 AI 声音研究</div>
        <div class="header-sub">Generative Voice Study</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Session State ──────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── 渲染聊天历史 ──────────────────────────────────────────
st.markdown('<div class="chat-outer">', unsafe_allow_html=True)

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(
            f'<div class="bubble-user">{msg["content"]}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="bubble-ai-wrap">'
            f'<div class="ai-avatar">🤖</div>'
            f'<div class="bubble-ai">{msg["content"]}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        if "audio" in msg:
            st.audio(msg["audio"], format="audio/mp3")

st.markdown('</div>', unsafe_allow_html=True)

# ── 底部输入区（原逻辑完全保留）────────────────────────────
with st.container():
    st.markdown('<div class="fixed-footer">', unsafe_allow_html=True)

    col_sel, col_btn = st.columns([4, 1])
    options = ["请点击选择一个问题进行咨询..."] + list(SPECIFIC_RESPONSES.keys())
    selected_option = col_sel.selectbox("Q", options, label_visibility="collapsed")
    send_trigger = col_btn.button("发送", use_container_width=True, type="primary")

    st.markdown('</div>', unsafe_allow_html=True)

# ── 交互逻辑（原样保留）──────────────────────────────────
if send_trigger and selected_option != "请点击选择一个问题进行咨询...":
    st.session_state.messages.append({"role": "user", "content": selected_option})
    answer_text = SPECIFIC_RESPONSES[selected_option]

    try:
        with st.spinner("正在生成语音…"):
            audio_gen = client_el.text_to_speech.convert(
                voice_id=VOICE_ID,
                text=answer_text,
                model_id=MODEL_ID,
                voice_settings=VoiceSettings(
                    stability=STABILITY_VAL,
                    similarity_boost=0.8,
                    use_speaker_boost=True,
                ),
            )
            audio_bytes = b"".join(list(audio_gen))
            st.session_state.messages.append({
                "role": "assistant",
                "content": answer_text,
                "audio": audio_bytes,
            })
            st.rerun()
    except Exception as e:
        st.error(f"语音生成出错：{str(e)}")