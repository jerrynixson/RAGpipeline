from llama_index.core import Document, KnowledgeGraphIndex, StorageContext
from content_fetcher import ContentFetcher
from llama_index.core.graph_stores import SimpleGraphStore

class GraphUpdater:
    def __init__(self, knowledge_graph: KnowledgeGraphIndex, storage_dir: str):
        self.index = knowledge_graph
        self.storage_dir = storage_dir

    def update_graph_from_url(self, url: str) -> str:
        content_fetcher = ContentFetcher(url)
        content = content_fetcher.fetch_content()

        if content:
            # Convert fetched content into Document format
            documents = [Document(text=content)]  # Assuming a single document for the fetched content
            
            try:
                # Update the graph with the new document(s)
                for doc in documents:
                    self.index.update(document=doc)

                # Assuming we need a method to persist the index
                graph_store = SimpleGraphStore()
                storage_context = StorageContext.from_defaults(
                persist_dir=self.storage_dir, graph_store=graph_store
                )
                self.index.storage_context.persist(persist_dir=self.storage_dir)  # Replace persist with save or the appropriate method
                
                return "Graph updated successfully!"
            except Exception as e:
                return f"Error updating graph: {str(e)}"
        else:
            return "Failed to fetch content from the URL."

