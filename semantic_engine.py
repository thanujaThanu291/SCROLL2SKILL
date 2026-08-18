from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# Load semantic embedding model
print("Loading AI semantic model...")

model = SentenceTransformer("all-MiniLM-L6-v2")

print("Semantic model loaded.")


def create_embedding(text):
    """
    Convert text into a semantic vector.
    """

    return model.encode(
        text,
        normalize_embeddings=True
    )


def similarity(text1, text2):
    """
    Calculate semantic similarity between two pieces of text.
    """

    embedding1 = create_embedding(text1)
    embedding2 = create_embedding(text2)

    score = cosine_similarity(
        [embedding1],
        [embedding2]
    )[0][0]

    return float(score)


if __name__ == "__main__":

    text1 = """
    Software engineering, programming,
    coding interviews and developer careers
    """

    text2 = """
    How developers design real-world
    software applications
    """

    score = similarity(text1, text2)

    print("\nSemantic Similarity:", round(score, 3))