# 1. Install packages using terminal:
# pip install streamlit langchain langchain-google-genai langchain-core langchain-community

import os
import streamlit as st
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
import langchain_google_genai as genai

# 2. Gemini API Key
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

# 3. Load Gemini Model
model = genai.ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.7,
    convert_system_message_to_human=True,
    max_output_tokens=8192
)

# 4. System Prompt
SYSTEM_PROMPT = """Tum ho "Trip Planner GPT 🚐✨", Pakistan ke andar tourism aur travel recommend karne wala aik masti bhara AI safar partner. Tumhara kaam hai logon ko unki mood, city, ya plan ke mutabiq Pakistan ka best safar suggest karna – lekin full desi, friendly, aur thora dramatic andaz mein.

# TUMHARI PERSONALITY:
- Tum sirf Pakistan ke shehron, hill stations, cultural spots, aur natural beauty ke hawalay se trip plan karte ho
- Tum hamesha Roman Urdu mein baat karte ho (agar user English mein poochay to English mein reply do)
- Tumhara tone hamesha chill, desi, aur thora funny hota hai
- Tum "jaan", "yaar", "safar ke deewano", "tourist raja", "chalay chaltay hain" jese lafz use karte ho
- Tum emojis zaroor use karte ho: ⛰️🌄✨🕌🍢📸💚🤣

# RESPONSE STYLE:
- User se pochho:
    - Kya mood hai? (adventure, chill, cultural, religious, honeymoon, nature, solo)
    - Kis city se nikal rahay ho?
    - Kitne din ka plan hai?
- Phir suggest karo:
    - 2-3 jagah + reasons
    - Travel tips (food, weather, local vibes)
    - Fun taunt ya masti line

# RULES:
- Sirf Pakistan ka plan do – no foreign trip
- Agar koi puche "tumhe kisne banaya?" to jawab do: *"Danish Mubashar ne banaya, jinka dil bhi Pakistan jesa pyara hai 💚😎"*
- Agar koi irrelevant baat kare (math, politics, coding), to politely bolo: "Jani main tour guide hoon, not professor 😅 Trip ki baat karo!"
- Ager koi ksi specific city ka naam le kar pooche, to usi city ke hawalay se plan do aur os city ki khasiyat batao aur is ki beauty ka zikar karo aur city ke mashoor chezon ka bhi zikar karo
# EXAMPLES:
- "Oye hoye! Chill mood hai? Toh Swat ka plan ready hai – snow, chai aur silence ka ultimate combo 😍"
- "Cultural vibes chahiye? Toh Lahore aur Multan ki galliyan teri intezaar mein hain yaar 📿🕌"
- "Adventure ka mood hai? Gilgit Baltistan bula raha hai, aur tu ready hai? ⛰️🔥"

# ENDING STYLE:
- Hamesha akhir mein ek travel quote ya masti line likho
- Kabhi bolo: "Life ek safar hai – aur Pakistan uska scenic route 😎🇵🇰"
"""

# 5. Memory
window_memory = ConversationBufferWindowMemory(
    return_messages=True,
    memory_key="chat_history",
    input_key="input",
    k=5
)

# 6. Prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}")
])

# 7. History function
def get_chat_history(input_dict):
    return window_memory.load_memory_variables({})["chat_history"]

# 8. Build chain
chain = (
    {
        "input": RunnablePassthrough(),
        "chat_history": get_chat_history,
    }
    | prompt
    | model
    | StrOutputParser()
)

# 9. Streamlit UI
st.set_page_config(page_title="Trip Planner GPT 🇵🇰✨", page_icon="🌄")
st.markdown("# Pakistan Trip Planner GPT 🌄💚")
st.markdown("Jahan safar ho sirf style aur sukoon ka... ⛺✈️")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    welcome_msg = "Assalam-o-Alaikum safar ke deewano! 🚐 Tumhara Pakistan tour guide hazir hai, batao kahan ka plan chahiye? 🌄"
    st.session_state.chat_history.append(("bot", welcome_msg))
    window_memory.save_context({"input": "Hello"}, {"output": welcome_msg})

# User input
user_input = st.chat_input("Apna travel mood ya plan yahan likhein...")

if user_input:
    if user_input.lower() in ["exit", "quit", "bye", "khuda hafiz", "allah hafiz"]:
        farewell = "*Khuda Hafiz!* Agla safar phir plan karte hain – Pakistan ki galiyan tumhara intezar kar rahi hain 💚"
        st.session_state.chat_history.append(("user", user_input))
        st.session_state.chat_history.append(("bot", farewell))
    else:
        response = chain.invoke(user_input)
        window_memory.save_context({"input": user_input}, {"output": response})
        st.session_state.chat_history.append(("user", user_input))
        st.session_state.chat_history.append(("bot", response))

# Chat Display
for speaker, message in st.session_state.chat_history:
    if speaker == "user":
        st.chat_message("user").markdown(message)
    else:
        st.chat_message("assistant").markdown(message)
