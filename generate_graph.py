import pandas as pd
import networkx as nx
from transformers import pipeline
from pathlib import Path
import matplotlib.colors as mcolors

# # Caminhos
# input_path = Path("data/input/yt_comments_20250531173412.csv")
# output_path = Path("data/output/yt_graph.graphml")

# # Leitura do CSV
# df = pd.read_csv(input_path)

# # Preenchendo replies fictícias com base na ordem de comentários (já que não há reply_to_comment_id)
# # Agrupa os comentários principais e associa respostas em sequência
# df["reply_to"] = None
# main_comments = df[df["is_reply"] == False].reset_index()
# reply_index = 0

# for idx, row in main_comments.iterrows():
#     # Conta quantos replies esse comentário principal teve
#     total_replies = row["total_reply_count"]
#     replies = df[(df["is_reply"] == True)].iloc[reply_index:reply_index + total_replies]
#     df.loc[replies.index, "reply_to"] = row["comment_id"]
#     reply_index += total_replies

# # Classificação de toxicidade
# classifier = pipeline("text-classification", model="unitary/toxic-bert", top_k=None)
# toxicity_results = classifier(df["text"].tolist())

# # Processar resultados
# toxicity_scores = []
# toxicity_labels = []

# for result in toxicity_results:
#     # procura pela pontuação de toxicidade
#     toxic_score = next((r["score"] for r in result if r["label"] == "toxic"), 0)
#     toxicity_scores.append(toxic_score)
#     toxicity_labels.append("tóxico" if toxic_score > 0.5 else "não tóxico")

# df["toxicity_score"] = toxicity_scores
# df["toxicity_label"] = toxicity_labels

# # Função para converter toxicidade em cor
# def toxicity_to_color(score):
#     if score > 0.6:
#         return "#ff4d4d"  # vermelho
#     elif score < 0.4:
#         return "#4dff4d"  # verde
#     else:
#         return "#ffff4d"  # amarelo

# df["color"] = df["toxicity_score"].apply(toxicity_to_color)

# # Construção do grafo
# G = nx.DiGraph()

# # Adiciona nós
# for _, row in df.iterrows():
#     G.add_node(
#         row["comment_id"],
#         label=row["text"][:50],
#         author=row["author"],
#         like_count=row["like_count"],
#         is_reply=row["is_reply"],
#         toxicity_score=row["toxicity_score"],
#         toxicity_label=row["toxicity_label"],
#         color=row["color"],
#         is_main_comment=not row["is_reply"]
#     )

# # Adiciona arestas com base em reply_to
# for _, row in df[df["reply_to"].notna()].iterrows():
#     if row["reply_to"] in G.nodes:
#         G.add_edge(row["reply_to"], row["comment_id"])

# # Exporta para GraphML
# nx.write_graphml(G, output_path)

import pandas as pd
import networkx as nx
from pathlib import Path

# Caminhos
input_path = Path("data/input/yt_comments_processed.csv")
output_path = Path("data/output/yt_graph.graphml")

# Leitura do CSV já processado
df = pd.read_csv(input_path)

# Cria grafo direcionado
G = nx.DiGraph()

# Adiciona nós
for _, row in df.iterrows():
    G.add_node(
        row["comment_id"],
        label=row["text"][:50],
        author=row["author"],
        like_count=row["like_count"],
        is_reply=row["is_reply"],
        toxicity_score=row["toxicity_score"],
        toxicity_label=row["toxicity_label"],
        color=row["color"],
        relevance=row["relevance"],
        is_main_comment=not row["is_reply"]
    )

# Adiciona arestas
for _, row in df[df["reply_to"].notna()].iterrows():
    if row["reply_to"] in G.nodes:
        G.add_edge(row["reply_to"], row["comment_id"])

# Salva em formato GraphML
output_path.parent.mkdir(parents=True, exist_ok=True)
nx.write_graphml(G, output_path)
print(f"Grafo salvo em {output_path}")
