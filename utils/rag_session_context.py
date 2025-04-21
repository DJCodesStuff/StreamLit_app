import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import TextLoader

# Configuration
MENTAL_DIR = "mental_docs"
PHYSICAL_DIR = "physical_docs"
MENTAL_INDEX = "index_mental.faiss"
PHYSICAL_INDEX = "index_physical.faiss"
SUPPORTED_EXTENSIONS = [".txt"]

MODEL_PATH = "./models/all-MiniLM-L6-v2"
if os.path.exists(MODEL_PATH):
    print("Loading embedding model from local directory")
    embedding_model = HuggingFaceEmbeddings(model_name="./models/all-MiniLM-L6-v2")

else:
    print("Falling back to online model (requires internet)")
    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


def load_and_embed(file_path):
    loader = TextLoader(file_path)
    docs = loader.load()
    if not docs:
        print(f"[Warning] No documents loaded from {file_path}")
        return None
    return FAISS.from_documents(docs, embedding_model)

class DirectoryWatcher(FileSystemEventHandler):
    def __init__(self, category, directory):
        self.category = category
        self.directory = directory
        self.store_path = f"index_{category}.faiss"
        if os.path.exists(self.store_path):
            self.vectordb = FAISS.load_local(self.store_path, embedding_model, allow_dangerous_deserialization=True)
        else:
            self.vectordb = None
            print(f"[{self.category}] No existing vectorstore found. It will be created when files are added.")

        self.initialize_vectorstore_with_existing_files()

    def initialize_vectorstore_with_existing_files(self):
        all_files = [os.path.join(self.directory, f) for f in os.listdir(self.directory)
                     if os.path.isfile(os.path.join(self.directory, f)) and os.path.splitext(f)[1].lower() in SUPPORTED_EXTENSIONS]
        if not all_files:
            return

        print(f"[{self.category}] Initializing vectorstore with existing files: {all_files}")
        documents = []
        for file_path in all_files:
            loader = TextLoader(file_path)
            documents.extend(loader.load())

        if documents:
            self.vectordb = FAISS.from_documents(documents, embedding_model)
            self.vectordb.save_local(self.store_path)
            print(f"[{self.category}] Vectorstore initialized and saved with existing documents.")

    def on_created(self, event):
        self.process(event)

    def on_modified(self, event):
        self.process(event)

    def process(self, event):
        if event.is_directory:
            return
        ext = os.path.splitext(event.src_path)[1].lower()
        if ext not in SUPPORTED_EXTENSIONS:
            return

        print(f"[{self.category}] File change detected: {event.src_path}")
        new_vectorstore = load_and_embed(event.src_path)

        if new_vectorstore:
            if self.vectordb:
                self.vectordb.merge_from(new_vectorstore)
            else:
                self.vectordb = new_vectorstore

            print(f"[{self.category}] Saving vectorstore to {self.store_path}")
            self.vectordb.save_local(self.store_path)
            print(f"[{self.category}] Vectorstore updated.")


def monitor_directory(path, category):
    event_handler = DirectoryWatcher(category, path)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()
    print(f"Started monitoring '{path}' for category '{category}'")
    return observer

def get_vectorstore(category):
    store_path = f"index_{category}.faiss"
    if os.path.exists(store_path):
        return FAISS.load_local(store_path, embedding_model, allow_dangerous_deserialization=True)
    else:
        print(f"[get_vectorstore] No vectorstore found for category '{category}' at {store_path}.")
        return None

def retrieve_context_from_store(query: str, category: str, k: int = 5):
    store = get_vectorstore(category)
    if store:
        return "\n".join([doc.page_content for doc in store.similarity_search(query, k=k)])
    return ""

def start_monitoring():
    os.makedirs(MENTAL_DIR, exist_ok=True)
    os.makedirs(PHYSICAL_DIR, exist_ok=True)

    mental_observer = monitor_directory(MENTAL_DIR, "mental")
    physical_observer = monitor_directory(PHYSICAL_DIR, "physical")

    try:
        while True:
            time.sleep(1000)
    except KeyboardInterrupt:
        print("Stopping monitoring...")
        mental_observer.stop()
        physical_observer.stop()

    mental_observer.join()
    physical_observer.join()

if __name__ == "__main__":
    start_monitoring()
