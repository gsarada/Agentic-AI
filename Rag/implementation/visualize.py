from langchain_huggingface import HuggingFaceEmbeddings
import tiktoken
from sklearn.manifold import TSNE
import plotly.graph_objects as go
import numpy as np


MODEL = "gpt-4.1-nano"
def get_tokens_count(knowledge_base):
    encoding = tiktoken.encoding_for_model(MODEL)
    tokens = encoding.encode(knowledge_base)
    token_count = len(tokens)
    print(f"Total tokens for {MODEL}: {token_count:,}")

def get_vector_count(vectorstore):
    collection = vectorstore._collection
    count = collection.count()

    sample_embedding = collection.get(limit=1, include=["embeddings"])["embeddings"][0]
    dimensions = len(sample_embedding)
    print(f"There are {count:,} vectors with {dimensions:,} dimensions in the vector store")

def visualize_2D(vectorstore):
    collection = vectorstore._collection
    result = collection.get(include=['embeddings', 'documents', 'metadatas'])
    vectors = np.array(result['embeddings'])
    documents = result['documents']
    metadatas = result['metadatas']
    doc_types = [metadata['doc_type'] for metadata in metadatas]
    colors = [['blue', 'green', 'red', 'orange'][['products', 'employees', 'contracts', 'company'].index(t)] for t in doc_types]
    tsne = TSNE(n_components=2, random_state=42) # set n_components=3 for 3D plot
    reduced_vectors = tsne.fit_transform(vectors)

    # Create the 2D scatter plot
    fig = go.Figure(data=[go.Scatter(
        #data=[go.Scatter3d( # for 3D visualization
        x=reduced_vectors[:, 0],
        y=reduced_vectors[:, 1],
        # z=reduced_vectors[:, 2], # for 3D visualization
        mode='markers',
        marker=dict(size=5, color=colors, opacity=0.8),
        text=[f"Type: {t}<br>Text: {d[:100]}..." for t, d in zip(doc_types, documents)],
        hoverinfo='text'
    )])

    fig.update_layout(title='2D Chroma Vector Store Visualization',
                      scene=dict(xaxis_title='x', yaxis_title='y'),
                      # scene=dict(xaxis_title='x', yaxis_title='y', zaxis_title='z'), # for 3D visualization
                      width=800,
                      height=600,
                      margin=dict(r=20, b=10, l=10, t=40)
                      )

    fig.show()
