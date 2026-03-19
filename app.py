import streamlit as st
import yt_rag

# variables innitialize at first

def set_status_false(): # call by restart button
    st.session_state.db_status = False
    st.session_state['messages'] = []       # clear chat history

if 'db_status' not in st.session_state:
    st.session_state.db_status = False     # used for input chat disable/enable

if 'messages' not in st.session_state:
    st.session_state['messages'] = []

@st.cache_data(show_spinner=False)
def get_data_in_db(video_id):
    # get text
    with st.spinner('wait..', show_time=True):
        try:
            transcripts = yt_rag.get_video_transcript(video_id=video_id)
        except Exception as e:
            st.error(body = 'Video not found\nPlease give valid video id', icon='🚨')
            st.write(e)# remove this line layer its for debugging
            return False
            
        # create chunks
        docs = yt_rag.split_text(transcripts)
        
        # store in db 
        # create new collection (previous store data erases)
        yt_rag.client.recreate_collection( 
            collection_name="sample_collection_3072",

            vectors_config={"size": 3072, "distance": "Cosine"}
            
            )

        yt_rag.vector_store.add_documents(docs)
        st.success('Done')
        return True

def get_reponse(query):
    result = yt_rag.agent.invoke(
        {"messages": [{"role": "user", "content": query}]}
    )

    return result['messages'][-1].text

col1, col2 = st.columns([3, 1], vertical_alignment = 'bottom')
col1.title('YouTube Chat')
col2.button('New chat', help='Add new video', on_click=set_status_false)

if not st.session_state.db_status:
    with st.form('form1', clear_on_submit=False):
        video_id = st.text_input('Enter Video ID')
        submitted = st.form_submit_button('Send')
        if submitted:
            if not video_id.strip():
                st.error("Video ID is required")
            else:
                st.session_state.db_status = get_data_in_db(video_id)
                if st.session_state.db_status: # rerun when db_status is true
                    st.rerun()

# print all previous chat
chat_box = st.container(border=True, height=400)
for message in st.session_state['messages']: # st.session_state['messages']  must conatain [{'role':'role_name', 'content':'message'}]
    with chat_box.chat_message(name=message['role']):
        st.write(message['content'])

user_input = st.chat_input('ask something', disabled=not st.session_state.db_status) # if db_status is false - no input, else sb_status True - take input

if user_input:
#    st.session_state.db_state = False # set temporary false


    with chat_box.chat_message(name='human'):
        st.write(user_input)
        st.session_state['messages'].append({'role':'human', 'content':user_input})
    
    with chat_box.chat_message(name='ai'):
        with st.spinner('Thinking...', show_time=True):
            ai_message = get_reponse(user_input)
            st.markdown(ai_message)
            st.session_state['messages'].append({'role':'ai', 'content':ai_message})

#    st.session_state.db_state = True
#    st.rerun()




