import os
import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title="Orientador Politécnico", page_icon="🎓")
st.title("🎓 Orientador Vocacional - Politécnico Jaime Isaza Cadavid")
st.write("Pregúntame sobre tus gustos e intereses y te orientaré sobre la oferta académica.")

# Obtener la API Key
api_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))
client = genai.Client(api_key=api_key)

SYSTEM_INSTRUCTION = """
Eres un Orientador Vocacional Inteligente del Politécnico Colombiano Jaime Isaza Cadavid.

Tu objetivo:
1. Ayudar a los aspirantes a descubrir qué carrera estudiar según sus intereses, habilidades y gustos.
2. Proporcionar información detallada y precisa sobre las carreras, facultades, planes de estudio, enfoques y alternativas del Politécnico.
3. Responder de forma empática, clara, motivadora y formal.

Reglas de comportamiento:
- Cuando un usuario pregunte por sus gustos, hazle preguntas clave para perfilarlos y sugerirle las mejores facultades o programas del Politécnico (como la Facultad de Ciencias Agrarias, Ingeniería, etc.).
- Utiliza la información institucional del Politécnico Colombiano Jaime Isaza Cadavid para guiar la consulta de manera precisa.
"""

if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar el historial de conversación
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Capturar la entrada del usuario
if prompt := st.chat_input("Escribe tu consulta o tus gustos aquí..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Formatear el historial para la API
    contents = []
    for msg in st.session_state.messages:
        role = "user" if msg["role"] == "user" else "model"
        contents.append(types.Content(role=role, parts=[types.Part.from_text(text=msg["content"])]))

    # Configuración del modelo con System Instruction limpia
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_INSTRUCTION,
        temperature=0.7,
    )

    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            try:
                response = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=contents,
                    config=config
                )
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Error en el servicio: {str(e)}")
