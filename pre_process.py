from pathlib import Path
import pandas as pd
from transformers import pipeline

input_dir = Path("data/input/yt_comments")
output_dir = Path("data/input/yt_comments_processed")
output_dir.mkdir(parents=True, exist_ok=True)

classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli", device=0)

labels = [
    "hate speech against trans women",
    "hate speech against trans men",
    "transphobic",
    "transphobic comment",
    "transphobia",
    "trans erasure",
    "transphobic insult",
    "denial of trans identity",
    "neutral",
    "uninformative",
    "irrelevant",
    "general discussion",
    "supportive of trans people",
    "affirming trans identities",
    "defending trans rights",
    "calling out transphobia",
    "allyship with trans people"
]

hateful_labels = {
    "hate speech against trans women",
    "hate speech against trans men",
    "transphobic",
    "transphobic comment",
    "transphobia",
    "trans erasure",
    "transphobic insult",
    "denial of trans identity"
}

supportive_labels = {
    "supportive of trans people",
    "affirming trans identities",
    "defending trans rights",
    "calling out transphobia",
    "allyship with trans people"
}

neutral_labels = {
    "neutral",
    "uninformative",
    "irrelevant",
    "general discussion"
}

def categorize_label(label):
    if label in hateful_labels:
        return "hateful"
    elif label in supportive_labels:
        return "supportive"
    elif label in neutral_labels:
        return "neutral"
    else:
        return "uncategorized"

def transphobia_to_color(category, score):
    if category == "hateful":
        if score > 0.4:
            return "#ff4d4d"  # vermelho forte
        elif score > 0.2:
            return "#ffcc00"  # laranja
        else:
            return "#cccccc"  # fraco, cinza
    elif category == "supportive":
        return "#4dff4d"  # verde
    elif category == "neutral":
        return "#cccccc"  # cinza
    else:
        return "#999999"  # cinza escuro fallback

csv_files = list(input_dir.glob("yt_comments_*.csv"))
if not csv_files:
    raise FileNotFoundError(f"Nenhum arquivo encontrado em {input_dir} com padrão yt_comments_*.csv")

for csv_file in csv_files:
    print(f"Processando: {csv_file.name}")
    df = pd.read_csv(csv_file)

    df["reply_to"] = None
    main_comments = df[df["is_reply"] == False].reset_index()
    reply_index = 0

    for idx, row in main_comments.iterrows():
        total_replies = row["total_reply_count"]
        replies = df[(df["is_reply"] == True)].iloc[reply_index:reply_index + total_replies]
        df.loc[replies.index, "reply_to"] = row["comment_id"]
        reply_index += total_replies

    texts = df["text"].tolist()
    batch_size = 8
    batched_results = classifier(texts, candidate_labels=labels, batch_size=batch_size)

    trans_labels = [r["labels"][0] for r in batched_results]
    trans_scores = [r["scores"][0] for r in batched_results]
    df["transphobia_label"] = trans_labels
    df["transphobia_score"] = trans_scores

    df["transphobia_category"] = df["transphobia_label"].apply(categorize_label)
    df["color"] = [transphobia_to_color(cat, score) for cat, score in zip(df["transphobia_category"], df["transphobia_score"])]

    df["relevance"] = df["total_reply_count"] + df["like_count"]

    output_path = output_dir / csv_file.name.replace(".csv", "_processed.csv")
    df.to_csv(output_path, index=False, encoding="utf-8")
    print(f"Salvo: {output_path}")
