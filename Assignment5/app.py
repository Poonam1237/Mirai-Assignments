import streamlit as st
from google import genai
import requests
from PIL import Image
from io import BytesIO
from gtts import gTTS
import tempfile,json,urllib.parse

st.set_page_config(page_title='AI Multi-Modal Visual Novel',page_icon='📖',layout='wide')

@st.cache_resource
def get_client():
    return genai.Client(api_key='MyAPIKey')

client=get_client()
st.sidebar.title('Story Settings')
genre=st.sidebar.selectbox('Story Genre',['Fantasy','Sci-Fi','Mystery','Horror','Adventure','Cyberpunk'])
art=st.sidebar.selectbox('Art Style',['Anime','Realistic','Pixel Art','Watercolor','Oil Painting','Comic'])

if 'history' not in st.session_state:
    st.session_state.history=[]

if 'chat' not in st.session_state:
    system_prompt='''You are a visual novel engine.
Genre: %s
Art Style: %s
Return ONLY valid JSON:
{"story_text":"...","image_prompt":"...","options":["...","...","..."]}'''%(genre,art)
    st.session_state.chat=client.chats.create(model='gemini-3-flash-preview',config={'system_instruction':system_prompt})

st.title('AI Multi-Modal Visual Novel')

def render(scene):
    st.write(scene['story_text'])
    try:
        url='https://image.pollinations.ai/prompt/'+urllib.parse.quote(scene['image_prompt'])
        r=requests.get(url,timeout=20)
        st.image(Image.open(BytesIO(r.content)),use_container_width=True)
    except:
        st.toast('Image server is busy, skipping visual...')
    try:
        t=gTTS(scene['story_text'])
        f=tempfile.NamedTemporaryFile(delete=False,suffix='.mp3')
        t.save(f.name)
        st.audio(f.name)
    except:
        st.toast('Audio unavailable')

if not st.session_state.history:
    if st.button('Start Adventure'):
        data=json.loads(st.session_state.chat.send_message('Begin the story.').text)
        st.session_state.history.append(data)
        st.rerun()

for i,s in enumerate(st.session_state.history,1):
    st.subheader(f'Scene {i}')
    render(s)

if st.session_state.history:
    for opt in st.session_state.history[-1]['options']:
        if st.button(opt,key=opt):
            data=json.loads(st.session_state.chat.send_message(opt).text)
            st.session_state.history.append(data)
            st.rerun()
