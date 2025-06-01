from pathlib import Path
import pandas as pd
from transformers import pipeline

# Caminhos
input_path = Path("data/input/yt_comments_20250531173412.csv")
output_path = Path("data/input/yt_comments_processed.csv")

# Leitura do CSV original
df = pd.read_csv(input_path)

# Inicializa coluna reply_to como None
df["reply_to"] = None

# Atribui replies com base na ordem e total_reply_count
main_comments = df[df["is_reply"] == False].reset_index()
reply_index = 0

for idx, row in main_comments.iterrows():
    total_replies = row["total_reply_count"]
    replies = df[(df["is_reply"] == True)].iloc[reply_index:reply_index + total_replies]
    df.loc[replies.index, "reply_to"] = row["comment_id"]
    reply_index += total_replies

# Classificação de toxicidade
classifier = pipeline("text-classification", model="unitary/toxic-bert", top_k=None)
toxicity_results = classifier(df["text"].tolist(), truncation=True)

toxicity_scores = []
toxicity_labels = []

for result in toxicity_results:
    toxic_score = next((r["score"] for r in result if r["label"] == "toxic"), 0)
    toxicity_scores.append(toxic_score)
    toxicity_labels.append("tóxico" if toxic_score > 0.5 else "não tóxico")

df["toxicity_score"] = toxicity_scores
df["toxicity_label"] = toxicity_labels

# Converte score em cor
def toxicity_to_color(score):
    if score > 0.6:
        return "#ff4d4d"  # vermelho
    elif score < 0.4:
        return "#4dff4d"  # verde
    else:
        return "#ffff4d"  # amarelo

df["color"] = df["toxicity_score"].apply(toxicity_to_color)

# Calcula atributo de relevância
df["relevance"] = df["total_reply_count"] + df["like_count"]

# Salva CSV processado
df.to_csv(output_path, index=False, encoding="utf-8")
print(f"Arquivo processado salvo em {output_path}")
