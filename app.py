from flask import Flask, request, render_template, jsonify
import os
from graph_builder import GraphBuilder
from graph_updater import GraphUpdater
from information_retriever import InformationRetriever
from content_fetcher import ContentFetcher
from setEnvironment_variable import SetEnvironment_variable
app = Flask(__name__)

# Set environment variable and storage directory

STORAGE_DIR = SetEnvironment_variable()
# Initialize the knowledge graph
graph_builder = GraphBuilder(STORAGE_DIR)
graph = graph_builder.load_existing_graph()

@app.route('/')
def home():
    return render_template('index.html')  # Frontend page with form elements

@app.route('/create_graph', methods=['POST'])
def create_graph():
    url = request.json.get('url')
    content_fetcher = ContentFetcher(url)
    content = content_fetcher.fetch_content()

    if content:
        global graph
        graph = graph_builder.build_graph(content)
        return jsonify(message="Graph created and saved successfully!")
    else:
        return jsonify(message="Error: Could not fetch content."), 400

@app.route('/update_graph', methods=['POST'])
def update_graph():
    if graph:
        update_url = request.json.get('url')
        graph_updater = GraphUpdater(graph, STORAGE_DIR)
        result = graph_updater.update_graph_from_url(update_url)
        return jsonify(message=result)
    return jsonify(message="No existing graph to update."), 400

@app.route('/query_graph', methods=['POST'])
def query_graph():
    if graph:
        query = request.json.get('query')
        info_retriever = InformationRetriever(graph)
        result = info_retriever.retrieve_information(query)
        return jsonify(result=result)
    return jsonify(message="No existing graph to query."), 400

if __name__ == "__main__":
    app.run(debug=True)
