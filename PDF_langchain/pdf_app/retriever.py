import os
from dotenv import load_dotenv
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_astradb import AstraDBVectorStore
from astrapy import DataAPIClient

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ASTRA_TOKEN = os.getenv('ASTRA_TOKEN')
ASTRA_ENDPOINT = os.getenv('ASTRA_ENDPOINT')
ASTRA_NAMESPACE = os.getenv('ASTRA_NAMESPACE')

COLLECTION = 'text_qa_pdf'

llm = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0, streaming=True)


embedding = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

client = DataAPIClient(ASTRA_TOKEN)
db = client.get_database_by_api_endpoint(ASTRA_ENDPOINT, namespace=ASTRA_NAMESPACE)

vstore = AstraDBVectorStore(
    embedding=embedding,
    namespace=ASTRA_NAMESPACE,
    collection_name=COLLECTION,
    token=ASTRA_TOKEN,
    api_endpoint=ASTRA_ENDPOINT
)

# Define the retriever with similarity search
retriever = vstore.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={"k": 3, "score_threshold": 0.5},
)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    ("user", "{input}")
])

output_parser = StrOutputParser()

chain = prompt | llm.with_config({"run_name": "model"}) | output_parser.with_config({"run_name": "Assistant"})

# Incorporate the retriever into a question-answering chain.
system_prompt = (
    "You are an assistant for question-answering tasks. "
    "Use the following pieces of retrieved context to answer "
    "the question. If you don't know the answer, say that you "
    "don't know. Use three sentences maximum and keep the "
    "answer concise."
    "\n\n"
    "{context}"
)

PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{input}"),
    ]
)

question_answer_chain = create_stuff_documents_chain(llm, PROMPT)
rag_chain = create_retrieval_chain(retriever, question_answer_chain)
