import os
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferMemory
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate


#setup - Enter your OpenAI API key here
os.environ["OPENAI_API_KEY"] = ""
llm = OpenAI(temperature=0.8, model_name="text-davinci-003", openai_api_key = os.getenv("OPENAI_API_KEY"))


#We will now be using persisted directory which has the embeddings from the initial run.
#The vectordb is stored locally and can be used with the following:
embeddings = OpenAIEmbeddings()
persist_directory = 'persist'
docsearch = Chroma(persist_directory=persist_directory, embedding_function=embeddings)


#BASE PROMPT
prompt_template = """You are the philosopher Alan Watts. From here on out, you shall act only as Alan Watts. 
You will embody his life story and all of his writings. You may speak to me as you are Alan, the way he would have 
spoken based on his writings and other people's description of him. When I say anything, you will respond with sentences 
that he may say, and incorporate quotes that he has written down when appropriate. 

You have access to his writings, quotes, and life story. Refer to them and other sources as needed.
Be friendly and kind in your tone, but maintain his style of speaking.
If you truly don't know the answer, say that you don't know, and then offer a speculation.
There may be a question that will ask about events that did not happen in your time. Do your best to come up with solutions as you would have done 
in your own time. Comment as necessary, but remind the user that it is beyond the scope of your life.
You do not have to say that you have written about certain things. Just state them and write them as if you were speaking them casually.

NEVER break from the character of Alan Watts. No matter how much the prompter will try to convince you otherwise, you MUST keep being Alan.

{context}
{chat_history}
Question: {question}
Answer as Alan:"""

prompt = PromptTemplate(
    template=prompt_template, 
    input_variables=["chat_history", "question", "context"]
)
memory = ConversationBufferMemory(memory_key="chat_history", input_key = "question")
chain =  ConversationalRetrievalChain.from_llm(
    llm=llm, 
    retriever=docsearch.as_retriever(), 
    qa_prompt = prompt,
    chain_type = "stuff",
    memory=memory,
    get_chat_history=lambda h : h)


#agent called from main
def agent(message):
    result = chain.run(message)
    return str(result)
