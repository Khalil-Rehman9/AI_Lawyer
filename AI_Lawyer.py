import streamlit as st
import pickle
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain.callbacks import get_openai_callback
import os

def main():
    st.header("AI Lawyer ⚖️👨‍⚖️📄")

    # Option to choose the jurisdiction
    jurisdiction = st.sidebar.selectbox("Select Jurisdiction:", ["US Law", "India Law", "UK Law", "PAKISTAN Law"])

    if jurisdiction == "US Law":
        pdf_path = "US.pdf"
    elif jurisdiction == "India Law":
        pdf_path = "india.pdf"
    elif jurisdiction == "UK Law":
        pdf_path = "UK.pdf"
    elif jurisdiction == "PAKISTAN Law":
        pdf_path = "Pakistan.pdf"
    else:
        pdf_path = None

    if pdf_path:
        pdf_reader = PdfReader(pdf_path)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = text_splitter.split_text(text=text)

        store_name = jurisdiction.replace(" ", "_").lower()
        st.write(f'Jurisdiction: {jurisdiction}')

        if os.path.exists(f"{store_name}.pkl"):
            with open(f"{store_name}.pkl", "rb") as f:
                VectorStore = pickle.load(f)
        else:
            embeddings = OpenAIEmbeddings(openai_api_key="OPEN_AI_API")
            VectorStore = FAISS.from_texts(chunks, embedding=embeddings)
            with open(f"{store_name}.pkl", "wb") as f:
                pickle.dump(VectorStore, f)

        query = st.text_input("Ask questions about the legal jurisdiction:")
        
        if query:
            docs = VectorStore.similarity_search(query=query, k=3)
            llm = OpenAI(openai_api_key="OPEN_AI_API")
            chain = load_qa_chain(llm=llm, chain_type="stuff")
            with get_openai_callback() as cb:
                response = chain.run(input_documents=docs, question=query, max_tokens= 2000)
            st.write(response)

if __name__ == '__main__':
    main()
