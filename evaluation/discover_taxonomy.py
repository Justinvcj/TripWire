import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances_argmin_min

def run():
    print("Loading sample...")
    with open('data/taxonomy_sample.json', 'r', encoding='utf-8') as f:
        samples = json.load(f)
        
    texts = [s['customer_text'] for s in samples]
    
    print("Embedding texts...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode(texts, show_progress_bar=True)
    
    print("Clustering with k=6...")
    k = 6
    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(embeddings)
    
    # Get the closest texts to each centroid
    closest, _ = pairwise_distances_argmin_min(kmeans.cluster_centers_, embeddings)
    
    # Also grab top 15 closest for each cluster
    with open('data/taxonomy_clusters.md', 'w', encoding='utf-8') as f:
        f.write("# Taxonomy Discovery Clusters (k=6)\n\n")
        for i in range(k):
            f.write(f"## Cluster {i}\n")
            # Calculate distance of all points to this centroid
            distances = np.linalg.norm(embeddings - kmeans.cluster_centers_[i], axis=1)
            # Filter to points in this cluster
            in_cluster_idx = np.where(kmeans.labels_ == i)[0]
            # Sort by distance
            sorted_idx = in_cluster_idx[np.argsort(distances[in_cluster_idx])]
            
            f.write(f"**Total samples in cluster:** {len(in_cluster_idx)}\n\n")
            for idx in sorted_idx[:15]:
                f.write(f"- {texts[idx]}\n")
            f.write("\n")
            
    print("Wrote cluster analysis to data/taxonomy_clusters.md")

if __name__ == "__main__":
    run()
