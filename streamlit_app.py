import html

import streamlit as st

from server import ANSWERS, DASHBOARD, answer_for


st.set_page_config(
    page_title="Ledger & Loom | Retail copilot",
    page_icon="L",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500;600;700&family=Fraunces:opsz,wght@9..144,600;9..144,700&display=swap');
    :root { --ink: #17211b; --muted: #68736b; --line: #dce3dc; --paper: #f5f7f2; --green: #2e6849; --orange: #c9683f; }
    .stApp { background: var(--paper); color: var(--ink); font-family: 'DM Sans', sans-serif; }
    [data-testid='stSidebar'] { background: #e8eee7; border-right: 1px solid var(--line); }
    h1, h2, h3 { font-family: 'Fraunces', serif !important; color: var(--ink) !important; }
    .eyebrow { color: var(--green); font: 500 0.72rem 'DM Mono', monospace; letter-spacing: .08em; text-transform: uppercase; }
    .metric { background: white; border: 1px solid var(--line); border-radius: 8px; padding: 18px 20px; min-height: 116px; }
    .metric-label { color: var(--muted); font-size: .83rem; }
    .metric-value { color: var(--ink); font: 700 1.9rem 'Fraunces', serif; margin: 6px 0; }
    .metric-change { color: var(--green); font: 500 .76rem 'DM Mono', monospace; }
    .attention { background: white; border-left: 4px solid var(--orange); border-top: 1px solid var(--line); border-right: 1px solid var(--line); border-bottom: 1px solid var(--line); border-radius: 6px; padding: 14px 16px; margin: 9px 0; }
    .attention-title { font-weight: 700; color: var(--ink); }
    .attention-meta { color: var(--muted); font-size: .88rem; margin-top: 4px; }
    .evidence { color: var(--green); font: .72rem 'DM Mono', monospace; margin-top: 9px; }
    .pulse { background: white; border: 1px solid var(--line); border-radius: 8px; padding: 14px 16px; margin-bottom: 10px; }
    .pulse-name { font-weight: 700; }
    .pulse-rate { color: var(--green); float: right; font: 500 .75rem 'DM Mono', monospace; }
    .bar { height: 7px; background: #e5ebe4; border-radius: 5px; margin-top: 10px; overflow: hidden; }
    .bar-fill { height: 100%; background: var(--green); }
    .answer { background: #fff; border: 1px solid var(--line); border-radius: 8px; padding: 22px; }
    .answer-label { color: var(--green); font: 500 .72rem 'DM Mono', monospace; text-transform: uppercase; letter-spacing: .06em; }
    .answer h3 { margin: 8px 0 10px; }
    .recommendation { background: #edf4ed; border-left: 3px solid var(--green); padding: 12px 14px; margin-top: 14px; }
    .recommendation strong { display: block; margin-bottom: 4px; }
    </style>
    """,
    unsafe_allow_html=True,
)


def render_answer(answer):
    if not answer:
        st.info("I do not have enough data to answer that yet. Try asking about stock-outs, overstock, sales drops, or product performance.")
        return

    rows = "".join(f"<tr><td>{html.escape(label)}</td><td>{html.escape(value)}</td></tr>" for label, value in answer["rows"])
    st.markdown(
        f"""
        <div class="answer">
          <div class="answer-label">Evidence-backed answer</div>
          <h3>{answer['title']}</h3>
          <p>{answer['body']}</p>
          <table><thead><tr><th>Measure</th><th>Value</th></tr></thead><tbody>{rows}</tbody></table>
          <div class="recommendation"><strong>Recommended next step</strong>{answer['recommendation']}</div>
          <p><small>{answer['assumption']}</small></p>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.sidebar.markdown("# L Ledger & Loom")
st.sidebar.caption("Retail operations copilot")
st.sidebar.divider()
st.sidebar.markdown("**Workspace**")
st.sidebar.selectbox("Viewing", ["All stores · 3", "High Street", "Riverside", "Station kiosk"], label_visibility="collapsed")
st.sidebar.divider()
st.sidebar.success(f"Data synced\n{DASHBOARD['syncedAt']}")
st.sidebar.caption("Python backend · Streamlit")

st.markdown('<div class="eyebrow">Saturday briefing · Live data</div>', unsafe_allow_html=True)
st.title("Good morning, Praveen Kumar N.")
st.write("Here is what deserves your attention across the shop floor today.")

metrics = DASHBOARD["metrics"]
metric_data = [
    ("Sales this month", metrics["sales"], f"↑ {metrics['salesChange']} vs. Aug 2026"),
    ("Units sold", metrics["units"], f"↑ {metrics['unitsChange']} vs. Aug 2026"),
    ("Stock value", metrics["stockValue"], f"→ {metrics['stockChange']} vs. last week"),
    ("Needs attention", f"{metrics['attention']} items", f"{metrics['urgent']} urgent across {DASHBOARD['stores']} stores"),
]
metric_columns = st.columns(4)
for column, (label, value, change) in zip(metric_columns, metric_data):
    with column:
        st.markdown(f'<div class="metric"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-change">{change}</div></div>', unsafe_allow_html=True)

st.divider()
main_column, right_column = st.columns([1.55, 1])
with main_column:
    st.markdown('<div class="eyebrow">Action queue</div>', unsafe_allow_html=True)
    st.header("Worth a look today")
    for item in DASHBOARD["attention"]:
        evidence = " · ".join(f"{label}: {value}" for label, value in item["evidence"])
        st.markdown(
            f'<div class="attention"><div class="attention-title">{item["product"]} <small>· {item["type"]}</small></div><div class="attention-meta">{item["store"]} · {item["summary"]}</div><div class="evidence">{evidence}</div></div>',
            unsafe_allow_html=True,
        )

with right_column:
    st.markdown('<div class="eyebrow">Ask your copilot</div>', unsafe_allow_html=True)
    st.header("What do you need to know?")
    question = st.text_area("Ask about sales, stock, or a product", placeholder="What might run out?", height=95)
    suggestions = ["What might run out?", "What is overstocked?", "How did the Matcha Starter Kit do this month?"]
    selected = st.selectbox("Quick questions", ["Choose a question..."] + suggestions, label_visibility="collapsed")
    if st.button("Ask copilot", type="primary", use_container_width=True):
        st.session_state["answer"] = answer_for(question.strip() or ("" if selected.startswith("Choose") else selected))
    if "answer" in st.session_state:
        render_answer(st.session_state["answer"])
    else:
        st.info("Ask a question to see the numbers behind the answer.")

st.divider()
st.markdown('<div class="eyebrow">Quick view</div>', unsafe_allow_html=True)
st.header("Store pulse")
pulse_columns = st.columns(3)
for column, store in zip(pulse_columns, DASHBOARD["pulse"]):
    with column:
        st.markdown(
            f'<div class="pulse"><span class="pulse-name">{store["store"]}</span><span class="pulse-rate">{store["status"]} · {store["rate"]}%</span><div class="bar"><div class="bar-fill" style="width:{store["rate"]}%"></div></div></div>',
            unsafe_allow_html=True,
        )