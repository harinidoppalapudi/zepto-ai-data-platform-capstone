from ingestion import PolicyIndexer


if __name__ == "__main__":
    indexer = PolicyIndexer()
    indexer.build_index()