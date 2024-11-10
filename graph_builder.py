import os
from llama_index.core import Document, StorageContext
from llama_index.core.graph_stores import SimpleGraphStore
from llama_index.core import KnowledgeGraphIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openai import OpenAI
import json 
from llama_index.core.graph_stores import SimpleGraphStore
from llama_index.core import Settings
from pyvis.network import Network
from llama_index.core import load_index_from_storage

DEFAULT_PROMPT_TEMPLATE_PREFIX = (
    "You are an AI assistant helping users with their queries.\n"
    "Some text is provided below. Given the text, extract up to "
    "{max_knowledge_triplets} knowledge triplets in the form of (subject, "
    "predicate, object). Avoid stopwords.\n"
    "---------------------\n"
)

DEFAULT_PROMPT_INJECTION = """
-- When you encounter entities that look similar but are differently spelled (e.g., John Doe and J. Doe),
use one name for all entities, when extracting them from text.
-- The text provided can be incomplete and does not include any information about the entity as it appears in the text.
-- Try to extract triplets from the text that make a mixture of sparse-dense well-connected knowledge graphs.
-- Review the triplets and remove duplicates if needed.
"""

DEFAULT_PROMPT_TEMPLATE_SUFFIX = """
---------------------\n
Text: {text}

Triplets:
"""

MAX_TRIPLETS_PER_CHUNK = 1

class GraphBuilder:
    def __init__(self, storage_dir: str):
        self.storage_dir = storage_dir
        self.index = None
        os.makedirs(self.storage_dir, exist_ok=True)  # Ensure storage directory exists
        self.documents = None  # define in __init__
        self.edge_types = ["relationship"]
        self.rel_prop_names = ["relationship"]
        self.tags = ["entity"]
        self.prompt = DEFAULT_PROMPT_TEMPLATE_PREFIX + DEFAULT_PROMPT_INJECTION + DEFAULT_PROMPT_TEMPLATE_SUFFIX


    def build_graph(self, content: str):

        # Set up the embedding model and language model
        embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-base-en-v1.5")
        os.environ["OPENAI_API_KEY"] = ""
        llm = OpenAI(temperature=0.1, model="gpt-3.5-turbo-16k")
        Settings.llm = llm
        Settings.chunk_size = 1024
        Settings.embed_model = embed_model
        
        # Prepare the document and graph storage
        text_list = [content]
        documents = [Document(text=t) for t in text_list]
        edge_types, rel_prop_names = ["relationship"], ["relationship"]
        tags = ["entity"]  # default, could be omit if create from an empty kg
        graph_store = SimpleGraphStore()
        
        prompt = DEFAULT_PROMPT_TEMPLATE_PREFIX + DEFAULT_PROMPT_INJECTION + DEFAULT_PROMPT_TEMPLATE_SUFFIX
        
        # Create the index (knowledge graph)
        self.index = KnowledgeGraphIndex.from_documents(
                    documents=documents,
                    # storage_context=storage_context,
                    max_triplets_per_chunk=MAX_TRIPLETS_PER_CHUNK,
                    include_embeddings=True,
                    show_progress=True,
                    edge_types=edge_types,
                    rel_prop_names=rel_prop_names,
                    tags=tags,
                    # prompt injection for refined triplet extraction
                    prompt_template=prompt,
                    embedding_model=embed_model,
                )
# Retrieve the networkx graph from the index
        try:
            g = self.index.get_networkx_graph()
        except AttributeError:
            print("Error: `index` does not support `get_networkx_graph`.")
            g = None

        if g:
            # Create a PyVis Network object
            net = Network(notebook=True, cdn_resources="in_line", directed=True)

            # Load the networkx graph into the PyVis network
            net.from_nx(g)

            # Define the output file
            output_file = "example.html"
            
            # Write to HTML with UTF-8 encoding
            try:
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(net.html)
                print(f"Graph saved and displayed in {output_file}")
            except UnicodeEncodeError as e:
                print(f"Unicode error: {e}")
        else:
            print("Unable to generate the graph; please check the index and graph conversion method.")

        
        # Save the graph after building it
        self.index.storage_context.persist(persist_dir=self.storage_dir)
        print(f"Graph data has been saved to: {self.storage_dir}")
        
        return self.index


    def load_existing_graph(self):
        # Check if the storage directory and necessary files exist
        os.makedirs(self.storage_dir, exist_ok=True)
        print(f"Loading graph from directory: {self.storage_dir}")

        # List available files in the storage directory
        available_files = os.listdir(self.storage_dir)
        print(f"Available files in storage: {available_files}")


        try:
            graph_store = SimpleGraphStore()
            storage_context = StorageContext.from_defaults(
                persist_dir=self.storage_dir, graph_store=graph_store
            )

            # Load the index from storage based on user selection
            graph_index = load_index_from_storage(
                storage_context=storage_context,
                max_triplets_per_chunk=15,
                verbose=True,
            )
            print("Graph loaded successfully.")
            return graph_index
        except Exception as e:
            print(f"Error loading graph: {e}")
            return None