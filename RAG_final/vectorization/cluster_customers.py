import os
import numpy as np
import pandas as pd
import chromadb
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

#config
CHROMA_DIR       = "./chroma"
RESP_TEXT_COLL   = "excel_respondents_text"  # same as in vector.py
N_CLUSTERS       = 6                         # you can change this to 5, 8, etc.
OUTPUT_DIR       = "./ml_outputs"            # where to save CSVs and plots
RANDOM_STATE     = 42



def load_respondent_embeddings():
    """
    Load all respondent-level embeddings from the Chroma collection.
    Returns:
        ids      : list of string ids
        X        : numpy array of shape (n_samples, n_dims)
        metadatas: list of dicts (one per id)
    """
    if not os.path.isdir(CHROMA_DIR):
        raise SystemExit(f"Chroma directory '{CHROMA_DIR}' not found. "
                         f"Run vector.py first to create embeddings.")

    client = chromadb.PersistentClient(path=CHROMA_DIR)
    coll = client.get_collection(RESP_TEXT_COLL)

    print(f"[INFO] Fetching embeddings from collection '{RESP_TEXT_COLL}'...")
    data = coll.get(include=["embeddings", "metadatas", "ids"])

    ids = data["ids"]
    embs = data["embeddings"]
    metas = data["metadatas"]

    if not ids:
        raise SystemExit(f"No embeddings found in collection '{RESP_TEXT_COLL}'. "
                         f"Did you run vector.py successfully?")

    X = np.array(embs, dtype=np.float32)
    print(f"[INFO] Loaded {len(ids)} embeddings with dimension {X.shape[1]}.")
    return ids, X, metas


def train_kmeans(ids, X, metadatas):
    """
    Train a K-Means clustering model on the embeddings X.
    Returns:
        labels: cluster labels for each sample
        model : fitted KMeans model
    """
    print(f"[INFO] Training KMeans with k={N_CLUSTERS}...")
    kmeans = KMeans(
        n_clusters=N_CLUSTERS,
        random_state=RANDOM_STATE,
        n_init="auto"
    )
    labels = kmeans.fit_predict(X)

    sil = silhouette_score(X, labels)
    print(f"[METRIC] Silhouette score: {sil:.4f}")

    # build a DataFrame with basic info
    rows = []
    for rid, lbl, meta in zip(ids, labels, metadatas):
        row = {
            "id": rid,
            "cluster": int(lbl),
            "source": meta.get("source", "unknown"),
        }
        
        rows.append(row)

    df_clusters = pd.DataFrame(rows)
    return df_clusters, kmeans, sil


def pca_plot(X, labels, out_path):
    """
    Reduce embeddings to 2D with PCA and save a scatter plot colored by cluster.
    """
    print("[INFO] Running PCA for 2D visualization...")
    pca = PCA(n_components=2, random_state=RANDOM_STATE)
    X_2d = pca.fit_transform(X)

    plt.figure(figsize=(8, 6))
    scatter = plt.scatter(X_2d[:, 0], X_2d[:, 1], c=labels, alpha=0.7)
    plt.title("Customer Segments (PCA projection)")
    plt.xlabel("PC1")
    plt.ylabel("PC2")
    plt.colorbar(scatter, label="Cluster")
    plt.tight_layout()
    plt.savefig(out_path, dpi=200)
    plt.close()
    print(f"[INFO] Saved PCA cluster plot to: {out_path}")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # loadd embeddings from Chroma
    ids, X, metas = load_respondent_embeddings()

    # train KMeans and compute silhouette
    df_clusters, kmeans, sil = train_kmeans(ids, X, metas)

    # save cluster assignments to CSV
    csv_path = os.path.join(OUTPUT_DIR, "customer_clusters.csv")
    df_clusters.to_csv(csv_path, index=False)
    print(f"[INFO] Saved cluster assignments to: {csv_path}")

    #save PCA-based visualization
    labels = df_clusters["cluster"].values
    plot_path = os.path.join(OUTPUT_DIR, "customer_clusters_pca.png")
    pca_plot(X, labels, plot_path)

    print("\n clustering finished.")
    print(f"   - Number of customers: {len(df_clusters)}")
    print(f"   - Number of clusters: {N_CLUSTERS}")
    print(f"   - Silhouette score:   {sil:.4f}")
    print(f"   - Cluster CSV:        {csv_path}")
    print(f"   - PCA plot:           {plot_path}")
    print("\nYou can now inspect which customers belong to each cluster and use the LLM "
          "to explain the characteristics of each segment.")


if __name__ == "__main__":
    main()
