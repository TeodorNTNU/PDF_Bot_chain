import os
from dotenv import load_dotenv
from uuid import uuid4
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_astradb import AstraDBVectorStore
from langchain_openai import OpenAIEmbeddings
from astrapy import DataAPIClient

load_dotenv()
 
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ASTRA_TOKEN = os.getenv('ASTRA_TOKEN')
ASTRA_ENDPOINT = os.getenv('ASTRA_ENDPOINT')
ASTRA_NAMESPACE = os.getenv('ASTRA_NAMESPACE')

COLLECTION = 'text_qa_pdf'

def upload_pdf_to_vector_db(file_path):
    # Load PDF file
    loader = PyPDFLoader(file_path)

    # Extract and split content into pages
    pages = loader.load_and_split()

    # Initialize a text splitter with specified chunk size and overlap
    splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=1000, chunk_overlap=100
    )

    # Split the documents into chunks
    document_chunks = splitter.split_documents(pages)

    # Initialize the AstraDB client and vector store
    client = DataAPIClient(ASTRA_TOKEN)
    db = client.get_database_by_api_endpoint(ASTRA_ENDPOINT, namespace=ASTRA_NAMESPACE)
    embedding = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

    vstore = AstraDBVectorStore(
        embedding=embedding,
        namespace=ASTRA_NAMESPACE,
        collection_name=COLLECTION,
        token=ASTRA_TOKEN,
        api_endpoint=ASTRA_ENDPOINT
    )

    # Generate unique IDs for the document chunks
    uuids = [str(uuid4()) for _ in range(len(document_chunks))]

    # Add documents to the vector store
    inserted_ids = vstore.add_documents(documents=document_chunks, ids=uuids)

    print(f"\nInserted {len(inserted_ids)} documents.")
    return inserted_ids