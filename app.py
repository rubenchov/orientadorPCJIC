import os
import time
import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title="Orientador Politécnico", page_icon="🎓")
st.title("🎓 Politécnico Colombiano Jaime Isaza Cadavid")
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
- Cuando un usuario pregunte por sus gustos, hazle preguntas clave para perfilarlos y sugerirle las mejores facultades o programas del Politécnico (como la Facultad de Ciencias Agrarias, Ingeniería, Administración, etc.).
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

    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_INSTRUCTION,
        temperature=0.7,
    )

    # Lista priorizada de modelos estables
    modelos_a_probar = ["gemini-2.5-flash", "gemini-1.5-flash"]

    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            exito = False
            
            for modelo in modelos_a_probar:
                # Intentar hasta 3 veces por cada modelo con pequeñas pausas (backoff)
                for intento in range(3):
                    try:
                        response = client.models.generate_content(
                            model=modelo,
                            contents=contents,
                            config=config
                        )
                        st.markdown(response.text)
                        st.session_state.messages.append({"role": "assistant", "content": response.text})
                        exito = True
                        break
                    except Exception:
                        time.sleep(1.5)  # Espera breve antes de reintentar
                
                if exito:
                    break
            
            if not exito:
                st.error("El servicio está recibiendo muchas consultas simultáneas. Por favor intenta enviar tu mensaje nuevamente en unos segundos.")
