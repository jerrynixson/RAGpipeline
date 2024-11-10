from llama_index.core import KnowledgeGraphIndex 
from llama_index.core import load_index_from_storage
from llama_index.core import StorageContext
from llama_index.core.graph_stores import SimpleGraphStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openai import OpenAI  # If you are using OpenAI LLMs
from llama_index.core import Settings  # If you are using the Settings class
import numpy as np
from sklearn.decomposition import PCA
from llama_index.core import Settings  # Import PCA
import os
class InformationRetriever:
 
    def __init__(self, knowledge_graph: KnowledgeGraphIndex):
        embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-base-en-v1.5")
        os.environ["OPENAI_API_KEY"] = ""
        llm = OpenAI(temperature=0.1, model="gpt-3.5-turbo-16k")
        Settings.llm = llm
        Settings.chunk_size = 1024
        Settings.embed_model = embed_model
        
        # Load the knowledge graph index
        graph_store = SimpleGraphStore()
        storage_context = StorageContext.from_defaults(persist_dir='/Users/sampa/Desktop/Project/RAG/projectFile/knowledge_graph_storage', graph_store=graph_store)
        
        # Load the index from storage
        self.index = load_index_from_storage(
            storage_context=storage_context,
            max_triplets_per_chunk=15,
            verbose=True,
        )
        


    def retrieve_information(self, query: str):

        query_engine = self.index.as_query_engine(
            include_text=True,
            response_mode="tree_summarize",
            embedding_mode="hybrid", #keyword
            similarity_top_k=7,
            verbose=True,
        )
        
        # Query the engine
        response = query_engine.query(query)
        return str(response)