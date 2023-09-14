# coding=utf-8

import os
import shutil
import re
import time
from langchain.vectorstores import FAISS
from langchain.document_loaders import UnstructuredPowerPointLoader, UnstructuredWordDocumentLoader, \
    UnstructuredPDFLoader, UnstructuredFileLoader
import logging
from langchain.embeddings import HuggingFaceEmbeddings
from chat import TPUChatglm
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List
from glob import glob

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)


class DocChatbot:
    llm: TPUChatglm
    embeddings: HuggingFaceEmbeddings
    files: str

    def __init__(self) -> None:
        # self.llm = TPUChatglm()
        self.llm = None
        self.vector_db = None
        self.embeddings = HuggingFaceEmbeddings(model_name='./embedding')
        print("chatbot init success!")

    def query_from_doc(self, query_string, k=1):
        results = self.vector_db.similarity_search(query_string, k=k)
        return results

    # split documents, generate embeddings and ingest to vector db
    def init_vector_db_from_documents(self, file_list: List[str]):
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=325, chunk_overlap=6,
                                                       separators=["\n\n", "\n", "。", "！", "，", " ", ""])
        docs = []
        for file in file_list:
            ext_name = os.path.splitext(file)[-1]
            if ext_name == ".pptx":
                loader = UnstructuredPowerPointLoader(file)
            elif ext_name == ".docx":
                loader = UnstructuredWordDocumentLoader(file)
            elif ext_name == ".pdf":
                loader = UnstructuredPDFLoader(file)
            else:
                loader = UnstructuredFileLoader(file)
            doc = loader.load()
            doc[0].page_content = filter_space(doc[0].page_content)
            doc = text_splitter.split_documents(doc)
            docs.extend(doc)

        # print([(len(x.page_content), count_chinese_chars(x.page_content)) for x in docs])
        # for item in docs:
        #     if len(item.page_content) / count_chinese_chars(item.page_content) > 1.5:
        #         print(len(item.page_content), item.page_content)
        if self.vector_db is None:
            self.files = ", ".join([item.split("/")[-1] for item in file_list])
            self.vector_db = FAISS.from_documents(docs, self.embeddings)
        else:
            self.files = self.files + ", " + ", ".join([item.split("/")[-1] for item in file_list])
            self.vector_db.add_documents(docs)
        return True

        # load vector db from local

    def load_vector_db_from_local(self, index_name: str):
        self.vector_db = FAISS.load_local(f"./data/db/{index_name}", self.embeddings, index_name)
        self.files = index_name

    def save_vector_db_to_local(self):
        FAISS.save_local(self.vector_db, "data/db/" + self.files, self.files)
        print("Vector db saved to local")

    def del_vector_db(self, file_name):
        shutil.rmtree("data/db/" + file_name)

    def get_vector_db(self):
        file_list = glob("./data/db/*")
        return (x.split("/")[-1] for x in file_list)


def stream_predict(query, history):
    history.append((query, ''))
    res = ''
    i = 0
    while i < 3:
        res += str(i)
        i += 1
        time.sleep(0.01)
        history[-1] = (query, res)
        yield res, history


def filter_space(string):
    result = ""
    count = 0
    for char in string:
        if char == " " or char == '\t':
            count += 1
            if count < 4:
                result += char
        else:
            result += char
            count = 0
    return result


def count_chinese_chars(string):
    pattern = re.compile(r'[\u4e00-\u9fa5]')
    chinese_chars = re.findall(pattern, string)
    return len("".join(chinese_chars))

# if __name__ == "__main__":
#     loader = UnstructuredWordDocumentLoader("./data/uploaded/北方航空科技 框架合同 1.docx")
#     doc = loader.load()
#     print(doc[0].page_content)
#     print(filter_space(doc[0].page_content))
#     text_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=0,
#                                                    separators=["\n\n", "\n", "。", "！", "，", " ", ""])
#     doc = text_splitter.split_documents(doc)
