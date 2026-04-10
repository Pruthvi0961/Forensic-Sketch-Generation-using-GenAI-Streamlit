import streamlit as st
from huggingface_hub import InferenceClient
import unicodedata

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="Forensic Sketch Generator(Z-Image-Turbo)", layout="wide")

st.title("🕵️ Forensic Sketch Generation using GenAI")

# -----------------------------
# SAFE TEXT CLEANER (FIX ASCII ERROR)
# -----------------------------
def clean_text(text):
    if not text:
        return ""
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")

# -----------------------------
# SIDEBAR: HF TOKEN INPUT
# -----------------------------
st.sidebar.header("🔐 Hugging Face Settings")

hf_token = st.sidebar.text_input(
    "Enter Hugging Face Token",
    type="password",
    placeholder="hf_...",
)

if hf_token:
    st.session_state["hf_token"] = str(hf_token)

# -----------------------------
# INIT CLIENT
# -----------------------------
client = None

if "hf_token" in st.session_state:
    try:
        client = InferenceClient(
            provider="replicate",
            api_key=st.session_state["hf_token"].strip()
        )
        st.sidebar.success("✅ Connected to Replicate via HF")
    except Exception as e:
        st.sidebar.error("❌ Client init failed")
        st.sidebar.exception(e)

# -----------------------------
# MAIN UI (NO TABS USED)
# -----------------------------
st.header("Generate Forensic Sketch")

manual_prompt = st.text_area("Enter custom description")

st.subheader("Or use guided attributes")

col1, col2, col3 = st.columns(3)

with col1:
    gender = st.selectbox("Gender", ["", "male", "female"])
    eye_color = st.selectbox("Eye Color", ["", "brown", "blue", "green", "black", "hazel"])

with col2:
    skin_tone = st.selectbox("Skin Tone", ["", "fair", "medium", "dark"])
    hair_color = st.selectbox("Hair Color", ["", "black", "brown", "blonde", "grey"])

with col3:
    beard = st.selectbox("Beard", ["", "no beard", "light beard", "full beard"])
    age = st.selectbox("Age Group", ["", "child", "young adult", "middle-aged", "elderly"])

# -----------------------------
# BUILD PROMPT
# -----------------------------
guided_prompt_parts = [
    gender,
    age,
    skin_tone,
    f"{eye_color} eyes" if eye_color else "",
    f"{hair_color} hair" if hair_color else "",
    beard,
]

guided_prompt = " ".join([p for p in guided_prompt_parts if p])

final_prompt = manual_prompt if manual_prompt else guided_prompt

if final_prompt:
    final_prompt = (
        "highly detailed face, "
        f"{final_prompt}, "
        "front-facing view, neutral expression, looking at camera, "
        "plain grey background, harsh flat lighting, police mughsot photography style"
    )

# -----------------------------
# SHOW PROMPT
# -----------------------------
st.markdown("### 🧾 Final Prompt")
st.write(final_prompt if final_prompt else "No prompt generated yet")

# -----------------------------
# NEGATIVE PROMPT
# -----------------------------
negative_prompt = (
    "cgi, 3d, render, cartoon, anime, illustration, painting, blurry, smile, "
    "side view, hat, sunglasses, glowing, deformed, low quality, bad eyes, fake skin"
)

# -----------------------------
# GENERATE BUTTON
# -----------------------------
if st.button("Generate Sketch"):
    if client is None:
        st.error("Please enter a valid Hugging Face token in the sidebar.")
    elif not final_prompt:
        st.warning("Please enter a prompt or select attributes.")
    else:
        with st.spinner("Generating image..."):
            try:
                # FIX: ASCII-safe prompt to prevent encoding crash
                safe_prompt = clean_text(final_prompt)
                safe_negative = clean_text(negative_prompt)

                image = client.text_to_image(
                    prompt=safe_prompt,
                    negative_prompt=safe_negative,
                    model="Tongyi-MAI/Z-Image-Turbo",
                )

                st.image(image, caption="Generated Sketch", use_container_width=True)

            except Exception as e:
                st.exception(e)
