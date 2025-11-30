# app.py
import streamlit as st
import openai
import os
from typing import List, Tuple

# --------- Configuration ----------
MODEL = "gpt-3.5-turbo"  # reliable and inexpensive for demos
MAX_TOKENS = 500

# --------- Helpers ----------
def load_faq_items() -> List[Tuple[str, str]]:
    """
    Default FAQ items. You can also upload a plain-text file where each Q/A pair is separated by a blank line
    and Q and A are separated by a newline. Example file format:
    
    Q: What are the office working hours?
    A: Office hours are 9:30 AM - 6:30 PM, Monday to Friday.
    
    Q: How to reset my password?
    A: Visit https://intra.example/reset and follow instructions.
    """
    default = [
        ("What are the office working hours?", "Office hours are 9:30 AM - 6:30 PM, Monday to Friday."),
        ("How to contact IT support?", "Email IT at it-support@example.com or call ext. 1234."),
        ("How to apply for leave?", "Use the HR portal -> Leave Request. Contact hr@example.com for urgent help.")
    ]
    return default

def faq_match(question: str, faqs: List[Tuple[str, str]]) -> Tuple[str, float]:
    """
    Very simple matching:
    - If a FAQ question is a substring (or vice versa), return that answer with high score.
    - Otherwise return the best overlap score (token overlap).
    """
    q = question.lower().strip()
    best_score = 0.0
    best_answer = ""
    for fq, fa in faqs:
        fq_l = fq.lower()
        # exact/substring quick check
        if q in fq_l or fq_l in q:
            return fa, 0.99
        # token overlap
        q_tokens = set(q.split())
        fq_tokens = set(fq_l.split())
        if len(q_tokens) == 0:
            score = 0.0
        else:
            score = len(q_tokens & fq_tokens) / len(q_tokens)
        if score > best_score:
            best_score = score
            best_answer = fa
    return (best_answer, best_score)

def call_openai_system(question: str, context_faq: str) -> str:
    """
    Call OpenAI ChatCompletion to get an answer. Uses a short system prompt to constrain output.
    Make sure OPENAI_API_KEY is set (Streamlit Secrets or environment).
    """
    if "OPENAI_API_KEY" in st.secrets:
        openai.api_key = st.secrets["OPENAI_API_KEY"]
    else:
        openai.api_key = os.getenv("OPENAI_API_KEY", "")

    if not openai.api_key:
        return "ERROR: OpenAI API key not found. Set OPENAI_API_KEY in Streamlit Secrets or env."

    messages = [
        {"role": "system", "content": (
            "You are a helpful support assistant. Answer briefly and precisely. "
            "If the question is technical (IT/hardware) recommend escalation to IT support. "
            "If the question is HR/policy, answer from FAQ if possible and mention escalation contact if unsure."
        )},
        {"role": "user", "content": f"FAQ context:\n{context_faq}\n\nUser question: {question}"}
    ]

    try:
        resp = openai.ChatCompletion.create(
            model=MODEL,
            messages=messages,
            max_tokens=MAX_TOKENS,
            temperature=0.2,
            n=1,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"ERROR: OpenAI API call failed: {e}"

def should_escalate(question: str, answer: str) -> bool:
    q_kw = ["broken", "not working", "urgent", "can't", "cannot", "failed", "error"]
    a_kw = ["i'm not sure", "i do not know", "i may be wrong", "please contact", "escalate"]
    if any(w in question.lower() for w in q_kw):
        return True
    if any(w in answer.lower() for w in a_kw):
        return True
    return False

# --------- Streamlit UI ----------
st.set_page_config(page_title="Support Assistant", layout="wide")
st.title("Support Assistant — FAQ & Escalation (Demo)")

st.markdown("A simple support assistant that answers FAQs and escalates complex issues to human support.")

# Sidebar for admin/upload
with st.sidebar:
    st.header("Admin / FAQ")
    uploaded = st.file_uploader("Upload FAQ (plain text)", type=["txt"])
    if uploaded is not None:
        raw = uploaded.read().decode("utf-8")
        st.text_area("Uploaded FAQ preview", raw, height=200)
        if st.button("Load uploaded FAQ"):
            # parse simple format: pairs separated by blank line; Q:... A:...
            lines = raw.splitlines()
            pairs = []
            cur_q, cur_a = "", ""
            mode = None
            for ln in lines:
                ln = ln.strip()
                if ln.lower().startswith("q:"):
                    if cur_q and cur_a:
                        pairs.append((cur_q, cur_a))
                        cur_q, cur_a = "", ""
                    cur_q = ln[2:].strip()
                    mode = "q"
                elif ln.lower().startswith("a:"):
                    cur_a = ln[2:].strip()
                    mode = "a"
                else:
                    if mode == "q":
                        cur_q += " " + ln
                    elif mode == "a":
                        cur_a += " " + ln
            if cur_q and cur_a:
                pairs.append((cur_q, cur_a))
            if pairs:
                st.session_state["faq_list"] = pairs
                st.success(f"Loaded {len(pairs)} FAQ pairs.")
            else:
                st.error("Couldn't parse FAQ file. Use Q: / A: format.")
    st.markdown("---")
    st.markdown("**Streamlit Secrets**\nMake sure `OPENAI_API_KEY` is set in Streamlit -> Settings -> Secrets.")
    st.info("Keep API key secret. Do not commit secrets to GitHub.")

# initialize FAQ list
if "faq_list" not in st.session_state:
    st.session_state["faq_list"] = load_faq_items()

# show FAQ
st.subheader("Loaded FAQ (editable)")
faq_expander = st.expander("View & edit FAQ")
with faq_expander:
    for i, (q, a) in enumerate(st.session_state["faq_list"]):
        new_q = st.text_input(f"Q{i+1}", q, key=f"q_{i}")
        new_a = st.text_area(f"A{i+1}", a, key=f"a_{i}", height=60)
        st.session_state["faq_list"][i] = (new_q, new_a)
    if st.button("Add empty FAQ row"):
        st.session_state["faq_list"].append(("New question", "New answer"))

# Main interaction area
st.subheader("Ask a question")
name = st.text_input("Enter your name:", value="")

col1, col2 = st.columns([4,1])
with col1:
    user_q = st.text_area("Enter your question or support query:", height=120)
with col2:
    if st.button("Submit"):
        st.session_state["submitted_q"] = user_q

# Quick test buttons
st.markdown("### Quick test buttons")
tcol1, tcol2 = st.columns(2)
with tcol1:
    if st.button("Run Test 1 — Simple FAQ"):
        st.session_state["submitted_q"] = "What are the office working hours?"
with tcol2:
    if st.button("Run Test 2 — Escalation"):
        st.session_state["submitted_q"] = "My computer is broken what should I do?"

# Process submission
if "submitted_q" in st.session_state and st.session_state["submitted_q"].strip():
    q = st.session_state["submitted_q"].strip()
    st.markdown(f"**Hello {name or 'User'}, I will help you with:** {q}")

    faqs = st.session_state["faq_list"]
    best_answer, score = faq_match(q, faqs)
    # build small context string for the LLM
    context_text = "\n".join([f"Q: {fq}\nA: {fa}" for fq, fa in faqs[:10]])
    if score >= 0.6:
        # confident FAQ match
        st.success("Answered from FAQ (high confidence).")
        st.write(best_answer)
    else:
        st.info("Asking LLM for answer (FAQ match low/confidence low).")
        llm_ans = call_openai_system(q, context_text)
        st.write(llm_ans)
        if should_escalate(q, llm_ans):
            st.warning("This looks like it should be escalated to human support.")
            st.markdown("**Escalation:** Please contact IT at `it-support@example.com` or open a ticket in the IT portal.")
else:
    st.info("Enter a question or use Quick test buttons to try the agent.")
