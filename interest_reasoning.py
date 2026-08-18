import json
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# ============================================================
# 1. LOAD STUDENT INTERACTIONS
# ============================================================

with open("interactions.json", "r", encoding="utf-8") as file:
    data = json.load(file)

interactions = data["interactions"]


# ============================================================
# 2. LOAD SEMANTIC MODEL
# ============================================================

print("Loading semantic model...")

model = SentenceTransformer("all-MiniLM-L6-v2")

print("Semantic model loaded.")


# ============================================================
# 3. BROAD INTEREST CONCEPTS
# ============================================================

interest_concepts = {

    "Software Engineering": """
    software development, software engineering, application
    development, backend development, frontend development,
    developer practices, system design, building software,
    debugging, programming projects and professional software
    engineering.
    """,

    "Data Structures and Algorithms": """
    data structures, algorithms, problem solving, coding problems,
    LeetCode, competitive programming and technical interview
    problem solving.
    """,

    "Artificial Intelligence": """
    artificial intelligence, machine learning, deep learning,
    generative AI, neural networks and AI applications.
    """,

    "Cybersecurity": """
    cybersecurity, ethical hacking, network security, malware,
    penetration testing, information security and cyber defense.
    """,

    "Cloud Computing": """
    cloud computing, AWS, Azure, Google Cloud, distributed systems,
    cloud infrastructure, servers and scalable applications.
    """,

    "Developer Hardware": """
    laptops, processors, GPUs, computers, developer workstations,
    programming hardware and hardware used for software development.
    """,

    "Programming Languages": """
    Java, Python, C++, JavaScript and other programming languages,
    programming syntax and language-specific development.
    """,

    "Technology Career": """
    technology careers, workplace experiences, developer jobs,
    career growth, professional development and software engineering
    career paths.
    """
}


# ============================================================
# 4. CONCEPT EMBEDDINGS
# ============================================================

interest_names = list(interest_concepts.keys())

interest_descriptions = list(
    interest_concepts.values()
)

interest_embeddings = model.encode(
    interest_descriptions,
    normalize_embeddings=True
)


# ============================================================
# 5. BEHAVIOR SCORE
# ============================================================

def behavior_score(reel):

    score = 0

    watch = reel.get("watch_percentage", 0)

    # Strong watch completion
    if watch >= 90:
        score += 4

    elif watch >= 75:
        score += 3

    elif watch >= 50:
        score += 1

    else:
        score -= 2

    # Explicit positive signals
    if reel.get("liked", False):
        score += 3

    if reel.get("saved", False):
        score += 5

    if reel.get("shared", False):
        score += 4

    if reel.get("skipped", False):
        score -= 4

    return max(score, 0)


# ============================================================
# 6. ANALYZE EACH REEL
# ============================================================

interest_scores = {
    interest: 0
    for interest in interest_names
}

evidence = {
    interest: []
    for interest in interest_names
}


print("\n")
print("=" * 65)
print("ANALYZING STUDENT BEHAVIOR")
print("=" * 65)


for reel in interactions:

    text = (
        reel.get("title", "")
        + ". "
        + reel.get("transcript", "")
    )

    behavior = behavior_score(reel)

    if behavior <= 0:
        continue

    reel_embedding = model.encode(
        text,
        normalize_embeddings=True
    )

    similarities = cosine_similarity(
        [reel_embedding],
        interest_embeddings
    )[0]

    ranked = sorted(
        zip(interest_names, similarities),
        key=lambda x: x[1],
        reverse=True
    )

    # Only the strongest conceptual matches
    for interest, similarity in ranked[:3]:

        similarity = float(similarity)

        if similarity < 0.25:
            continue

        # --------------------------------------------
        # Base semantic contribution
        # --------------------------------------------

        contribution = similarity * behavior

        # --------------------------------------------
        # Important reasoning adjustments
        # --------------------------------------------

        title = reel.get("title", "").lower()
        transcript = reel.get("transcript", "").lower()

        combined = title + " " + transcript


        # Career content should support engineering,
        # but should not automatically dominate it.

        if interest == "Technology Career":

            career_terms = [
                "career",
                "job",
                "hiring",
                "salary",
                "workplace",
                "day in the life"
            ]

            has_career_signal = any(
                term in combined
                for term in career_terms
            )

            if not has_career_signal:
                contribution *= 0.65

            else:
                contribution *= 0.70


        # Programming language content should contribute
        # to software engineering but not dominate it.

        if interest == "Programming Languages":

            contribution *= 0.70


        # Developer hardware is supporting evidence.

        if interest == "Developer Hardware":

            contribution *= 0.65


        # Strong software engineering signals.

        engineering_terms = [
            "software engineer",
            "software engineering",
            "developer",
            "development",
            "coding",
            "programming",
            "debugging",
            "software"
        ]

        engineering_signal = sum(
            1
            for term in engineering_terms
            if term in combined
        )

        if engineering_signal >= 2:

            if interest == "Software Engineering":

                contribution *= 1.35


        interest_scores[interest] += contribution

        evidence[interest].append({
            "reel": reel["title"],
            "similarity": round(similarity, 3),
            "behavior": behavior,
            "contribution": round(contribution, 3)
        })


# ============================================================
# 7. REPEATED THEME BOOST
# ============================================================

for interest in interest_names:

    unique_reels = len(
        evidence[interest]
    )

    if unique_reels >= 3:

        interest_scores[interest] *= 1.15

    elif unique_reels >= 2:

        interest_scores[interest] *= 1.08


# ============================================================
# 8. RANK INTERESTS
# ============================================================

ranked_interests = sorted(
    interest_scores.items(),
    key=lambda x: x[1],
    reverse=True
)


# ============================================================
# 9. DISPLAY SCORES
# ============================================================

print("\n")
print("=" * 65)
print("BROAD INTEREST ANALYSIS")
print("=" * 65)

for interest, score in ranked_interests:

    if score > 0:

        print(
            f"{interest:<35} "
            f"{score:.3f}"
        )


# ============================================================
# 10. PRIMARY INTEREST
# ============================================================

primary_interest = ranked_interests[0][0]

primary_score = ranked_interests[0][1]

second_score = (
    ranked_interests[1][1]
    if len(ranked_interests) > 1
    else 0
)


# ============================================================
# 11. CONFIDENCE
# ============================================================

total_score = sum(
    score
    for _, score in ranked_interests
)

share = (
    primary_score / total_score
    if total_score > 0
    else 0
)


# Margin between first and second
if primary_score > 0:

    margin = (
        primary_score - second_score
    ) / primary_score

else:

    margin = 0


if share >= 0.32 and margin >= 0.15:

    confidence = "High"

elif share >= 0.25:

    confidence = "Medium"

else:

    confidence = "Low"


# ============================================================
# 12. FINAL RESULT
# ============================================================

print("\n")
print("=" * 65)
print("INTEREST DETECTED")
print("=" * 65)

print(
    "Primary Interest:",
    primary_interest
)

print(
    "Confidence:",
    confidence
)

print(
    "Interest Share:",
    round(share, 3)
)

print(
    "Confidence Margin:",
    round(margin, 3)
)


# ============================================================
# 13. EVIDENCE
# ============================================================

print("\nEvidence:")

for item in evidence[primary_interest]:

    print(
        f"• {item['reel']} "
        f"(similarity={item['similarity']}, "
        f"behavior={item['behavior']}, "
        f"contribution={item['contribution']})"
    )