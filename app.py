# Importación de bibliotecas necesarias
import os
import openai
import streamlit as st
import time

import streamlit as st
import openai

# Configuración de la página
st.set_page_config(
    page_title="JusTicIA",
    page_icon="🤖",
    layout="wide",
    menu_items={
        'Get Help': 'https://marduk.pro',
        'Report a bug': None,
        'About': "JusTicIA: Tu asistente de IA para entender la transformación digital del sistema judicial en Colombia. Obtén información sobre proyectos, herramientas y el futuro de la IA en la justicia."
    }
)

# Función para verificar si el archivo secrets.toml existe
def secrets_file_exists():
    secrets_path = os.path.join('.streamlit', 'secrets.toml')
    return os.path.isfile(secrets_path)

# Intentar obtener el ID del asistente de OpenAI desde st.secrets si el archivo secrets.toml existe
if secrets_file_exists():
    try:
        ASSISTANT_ID = st.secrets['ASSISTANT_ID']
    except KeyError:
        ASSISTANT_ID = None
else:
    ASSISTANT_ID = None

# Si no está disponible, pedir al usuario que lo introduzca
if not ASSISTANT_ID:
    ASSISTANT_ID = st.sidebar.text_input('Introduce el ID del asistente de OpenAI', type='password')

# Si aún no se proporciona el ID, mostrar un error y detener la ejecución
if not ASSISTANT_ID:
    st.sidebar.error("Por favor, proporciona el ID del asistente de OpenAI.")
    st.stop()

assistant_id = ASSISTANT_ID

# Inicialización del cliente de OpenAI
client = openai

st.title("Bienvenido a JusTicIA 🤖⚖️")

st.markdown("""
### 🤖 ¡Hola! Soy JusTicIA, tu agente de IA para la justicia colombiana!

Estoy aquí para ayudarte a comprender cómo la Inteligencia Artificial (IA) está transformando el sistema judicial en Colombia. 

#### ¿Qué te gustaría saber sobre la IA en la justicia? 🤔

Puedo:

* **Explicar** cómo la IA moderniza la justicia colombiana según el Plan Sectorial de Desarrollo 2023-2026 "Hacia una Justicia confiable, digital e incluyente".
* **Describir** los beneficios y desafíos de implementar la IA en la justicia, como la eficiencia, accesibilidad y transparencia.
* **Analizar** el impacto de las herramientas de IA en la eficiencia y la accesibilidad de la justicia.
* **Discutir** consideraciones éticas y legales del uso de la IA en la justicia, basándome en la Ley 1581 de 2012 y jurisprudencia relevante.
* **Explorar** el futuro de la IA en el sistema judicial colombiano y su potencial transformador.
* **Informar** sobre proyectos e iniciativas de IA en el sector judicial colombiano, incluyendo los del Concurso de Innovación de la Rama Judicial.
* **Ofrecer** orientación para que las firmas de abogados y los profesionales del derecho se adapten a la era digital.
* **Analizar** la automatización en el sector legal y proponer estrategias para la relevancia de los profesionales del derecho.
* **Proporcionar** información sobre la protección de datos en el contexto judicial.

**¡No dudes en preguntarme!**

*Recuerda: Soy una IA y no un abogado. Mi conocimiento está actualizado hasta abril de 2024. Para información específica y actualizada, consulta con un experto.*
""")

# Inicialización de variables de estado de sesión
st.session_state.start_chat = True
if "thread_id" not in st.session_state:
    st.session_state.thread_id = None

# Cargar la clave API de OpenAI
API_KEY = os.environ.get('OPENAI_API_KEY') or st.secrets.get('OPENAI_API_KEY')
if not API_KEY:
    API_KEY = st.sidebar.text_input('Introduce tu clave API de OpenAI', type='password')

if not API_KEY:
    st.sidebar.error("Por favor, proporciona una clave API para continuar.")
    st.stop()

openai.api_key = API_KEY

def process_message_with_citations(message):
    """Extraiga y devuelva solo el texto del mensaje del asistente."""
    if hasattr(message, 'content') and len(message.content) > 0:
        message_content = message.content[0]
        if hasattr(message_content, 'text'):
            nested_text = message_content.text
            if hasattr(nested_text, 'value'):
                return nested_text.value
    return 'No se pudo procesar el mensaje'

# Crear un hilo de chat inmediatamente después de cargar la clave API
if not st.session_state.thread_id:
    thread = client.beta.threads.create()
    st.session_state.thread_id = thread.id
    st.write("ID del hilo: ", thread.id)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("¿Cómo puedo ayudarte hoy?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("usuario"):
        st.markdown(prompt)

    # Enviar mensaje del usuario
    client.beta.threads.messages.create(
        thread_id=st.session_state.thread_id,
        role="user",
        content=prompt
    )

    # Crear una ejecución para el hilo de chat
    run = client.beta.threads.runs.create(
        thread_id=st.session_state.thread_id,
        assistant_id=assistant_id
    )

    while run.status != 'completed':
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(
            thread_id=st.session_state.thread_id,
            run_id=run.id
        )

    # Recuperar mensajes agregados por el asistente
    messages = client.beta.threads.messages.list(
    thread_id=st.session_state.thread_id
    )

    # Procesar y mostrar mensajes del asistente
    for message in messages:
        if message.run_id == run.id and message.role == "assistant":
            full_response = process_message_with_citations(message)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            with st.chat_message("assistant"):
                st.markdown(full_response)
                
# Footer
st.sidebar.markdown('---')
st.sidebar.subheader('Creado por:')
st.sidebar.markdown('Alexander Oviedo Fadul')
st.sidebar.markdown("[GitHub](https://github.com/bladealex9848) | [Website](https://alexanderoviedofadul.dev/) | [LinkedIn](https://www.linkedin.com/in/alexander-oviedo-fadul/) | [Instagram](https://www.instagram.com/alexander.oviedo.fadul) | [Twitter](https://twitter.com/alexanderofadul) | [Facebook](https://www.facebook.com/alexanderof/) | [WhatsApp](https://api.whatsapp.com/send?phone=573015930519&text=Hola%20!Quiero%20conversar%20contigo!%20)")