from pathlib import Path
import pandas as pd
import networkx as nx

input_dir = Path("data/input/yt_comments_processed")
output_dir = Path("data/output/yt_graphs")
output_dir.mkdir(parents=True, exist_ok=True)

csv_files = list(input_dir.glob("yt_comments_*_processed.csv"))

if not csv_files:
    raise FileNotFoundError(f"Nenhum arquivo processado encontrado em {input_dir}")

for csv_file in csv_files:
    print(f"Gerando grafo para: {csv_file.name}")
    df = pd.read_csv(csv_file)

    G = nx.DiGraph()

    for _, row in df.iterrows():
        G.add_node(
            row["comment_id"],
            label=row["text"][:50],
            author=row["author"],
            like_count=row["like_count"],
            is_reply=row["is_reply"],
            transphobia_score=row["transphobia_score"],
            transphobia_label=row["transphobia_label"],
            color=row["color"],
            relevance=row["relevance"],
            is_main_comment=not row["is_reply"]
        )

    for _, row in df[df["reply_to"].notna()].iterrows():
        if row["reply_to"] in G.nodes:
            G.add_edge(row["reply_to"], row["comment_id"])

    graph_filename = csv_file.stem.replace("_processed", "") + ".graphml"
    graph_path = output_dir / graph_filename

    nx.write_graphml(G, graph_path)
    print(f"Grafo salvo em: {graph_path}")
