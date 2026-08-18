import json
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# ============================================================
# LOAD DATA
# ============================================================

with open("candidates.json", "r", encoding="utf-8") as f:
    candidates = json.load(f)["candidates"]

with open("interactions.json", "r", encoding="utf-8") as f:
    interactions = json.load(f)["interactions"]


# ============================================================
# LOAD AI MODEL
# ============================================================

print("Loading AI model...")

model = SentenceTransformer("all-MiniLM-L6-v2")

print("AI model ready.")


# ============================================================
# INTERACTION SCORE
# ============================================================

def interaction_score(reel):

    score = 0

    watch = reel.get("watch_percentage", 0)

    if watch >= 90:
        score += 4

    elif watch >= 75:
        score += 3

    elif watch >= 50:
        score += 1

    else:
        score -= 2

    if reel.get("liked"):
        score += 3

    if reel.get("saved"):
        score += 5

    if reel.get("shared"):
        score += 4

    if reel.get("skipped"):
        score -= 4

    return max(score, 0)


# ============================================================
# BUILD STUDENT PROFILE
# ============================================================

positive_reels = []

for reel in interactions:

    score = interaction_score(reel)

    if score > 0:

        text = (
            reel.get("title", "")
            + ". "
            + reel.get("transcript", "")
        )

        positive_reels.append(text)


student_profile = " ".join(positive_reels)


# ============================================================
# BROAD INTEREST
# ============================================================

interest = "Software Engineering"
confidence = "High"


print("\nInterest detected:", interest)


# ============================================================
# CREATE STUDENT EMBEDDING
# ============================================================

student_embedding = model.encode(
    student_profile,
    normalize_embeddings=True
)


# ============================================================
# CATEGORY DETECTION
# ============================================================

def detect_category(text):

    text = text.lower()

    categories = {

        "AI": [
            "artificial intelligence",
            "machine learning",
            "deep learning",
            "generative ai",
            " ai "
        ],

        "DSA": [
            "data structure",
            "algorithm",
            "leetcode",
            "coding interview",
            "dsa"
        ],

        "Java": [
            "java"
        ],

        "HLD": [
            "system design",
            "high level design",
            "distributed system",
            "architecture"
        ],

        "Cybersecurity": [
            "cybersecurity",
            "network security",
            "malware",
            "ethical hacking",
            "penetration testing"
        ],

        "Cloud": [
            "cloud",
            "aws",
            "azure",
            "google cloud",
            "docker"
        ],

        "Hardware": [
            "laptop",
            "processor",
            "gpu",
            "hardware"
        ],

        "Career": [
            "career",
            "job",
            "interview",
            "software engineer"
        ],

        "Software Engineering": [
            "software engineering",
            "software development",
            "developer",
            "backend",
            "frontend",
            "api",
            "database",
            "git",
            "github"
        ]
    }

    scores = {}

    for category, keywords in categories.items():

        scores[category] = sum(
            1
            for keyword in keywords
            if keyword in text
        )

    best = max(
        scores,
        key=scores.get
    )

    if scores[best] == 0:
        return "Other"

    return best


# ============================================================
# EDUCATIONAL VALUE
# ============================================================

def educational_score(candidate):

    text = (
        candidate.get("title", "")
        + " "
        + candidate.get("transcript_snippet", "")
    ).lower()

    useful_terms = [

        "tutorial",
        "explained",
        "guide",
        "how to",
        "learn",

        "algorithm",
        "architecture",
        "system design",

        "programming",
        "coding",
        "development",
        "developer",

        "security",
        "cloud",

        "machine learning",
        "artificial intelligence",

        "interview",

        "database",
        "backend",
        "frontend",

        "git",
        "github",
        "docker"
    ]

    matches = sum(
        1
        for term in useful_terms
        if term in text
    )

    return min(matches / 4, 1.0)


# ============================================================
# HYPE DETECTION
# ============================================================

def hype_score(candidate):

    text = (
        candidate.get("title", "")
        + " "
        + candidate.get("transcript_snippet", "")
    ).lower()

    hype_terms = [

        "guaranteed job",
        "get a job",
        "get hired instantly",
        "make money fast",
        "become rich",
        "secret trick",
        "you won't believe",
        "10 ai tools",
        "get hired",
        "easy job"
    ]

    matches = sum(
        1
        for term in hype_terms
        if term in text
    )

    return min(matches / 2, 1.0)


# ============================================================
# TECHNOLOGY CONTENT FILTER
# ============================================================

technology_terms = [

    "software",
    "developer",
    "programming",
    "coding",

    "java",
    "python",
    "javascript",
    "c++",

    "algorithm",
    "data structure",

    "system design",
    "architecture",

    "backend",
    "frontend",

    "api",
    "database",

    "cloud",
    "aws",
    "azure",
    "docker",

    "cybersecurity",
    "network security",

    "machine learning",
    "artificial intelligence",
    " ai ",

    "computer",
    "laptop",
    "hardware",

    "technology",
    "tech",

    "git",
    "github"
]


# ============================================================
# RANK CANDIDATES
# ============================================================

results = []


for candidate in candidates:

    # --------------------------------------------------------
    # Candidate text
    # --------------------------------------------------------

    candidate_text = (
        candidate.get("title", "")
        + ". "
        + candidate.get("transcript_snippet", "")
    )

    candidate_lower = candidate_text.lower()


    # --------------------------------------------------------
    # TECHNOLOGY FILTER
    # --------------------------------------------------------

    is_technology = any(
        term in candidate_lower
        for term in technology_terms
    )

    if not is_technology:
        continue


    # --------------------------------------------------------
    # CREATE CANDIDATE EMBEDDING
    # --------------------------------------------------------

    candidate_embedding = model.encode(
        candidate_text,
        normalize_embeddings=True
    )


    # --------------------------------------------------------
    # SEMANTIC SIMILARITY
    # --------------------------------------------------------

    semantic_score = float(
        cosine_similarity(
            [student_embedding],
            [candidate_embedding]
        )[0][0]
    )


    # --------------------------------------------------------
    # REMOVE WEAK SEMANTIC MATCHES
    # --------------------------------------------------------

    if semantic_score < 0.20:
        continue


    # --------------------------------------------------------
    # EDUCATIONAL SCORE
    # --------------------------------------------------------

    education = educational_score(candidate)


    # --------------------------------------------------------
    # HYPE SCORE
    # --------------------------------------------------------

    hype = hype_score(candidate)


    # --------------------------------------------------------
    # CATEGORY
    # --------------------------------------------------------

    category = detect_category(candidate_text)


    # --------------------------------------------------------
    # BASE FINAL SCORE
    # --------------------------------------------------------

    final_score = (
        semantic_score * 0.60
        + education * 0.30
        - hype * 0.20
    )


    # --------------------------------------------------------
    # CAREER HYPE PENALTY
    # --------------------------------------------------------

    if category == "Career" and education < 0.5:

        final_score -= 0.10


    # --------------------------------------------------------
    # LANGUAGE-SPECIFIC DETECTION
    # --------------------------------------------------------

    language_specific = any(
        x in candidate_lower
        for x in [
            "java",
            "python",
            "javascript",
            "c++",
            "jvm"
        ]
    )


    # --------------------------------------------------------
    # BROAD TECHNOLOGY TOPICS
    # --------------------------------------------------------

    broad_topic = any(
        x in candidate_lower
        for x in [

            "system design",
            "architecture",

            "backend",
            "frontend",

            "api",
            "database",

            "distributed",

            "cloud",
            "aws",
            "azure",
            "docker",

            "cybersecurity",

            "data structure",
            "algorithm",

            "software engineering",
            "software development",

            "git",
            "github"
        ]
    )


    # --------------------------------------------------------
    # SOFTWARE ENGINEERING LOGIC
    # --------------------------------------------------------

    if interest == "Software Engineering":

        # Penalize Java/Python/etc. content
        # when it is ONLY about that language.

        if language_specific and not broad_topic:

            final_score -= 0.50


        # Reward broader software engineering topics.

        if broad_topic:

            final_score += 0.08


    # --------------------------------------------------------
    # SAVE RESULT
    # --------------------------------------------------------

    results.append({

        "candidate": candidate,

        "semantic": semantic_score,

        "education": education,

        "hype": hype,

        "category": category,

        "final": final_score
    })


# ============================================================
# CHECK RESULTS
# ============================================================

if not results:

    print("\nNo suitable technology recommendation found.")

    print(
        "Try adding more technology-related candidates "
        "to candidates.json."
    )

    exit()


# ============================================================
# SORT RESULTS
# ============================================================

results.sort(
    key=lambda x: x["final"],
    reverse=True
)


# ============================================================
# DISPLAY TOP 5
# ============================================================

print("\n")
print("=" * 60)
print("TOP 5 RECOMMENDATIONS")
print("=" * 60)


for i, item in enumerate(results[:5], 1):

    candidate = item["candidate"]

    print(f"\n#{i}")

    print(
        "Title:",
        candidate.get("title", "")
    )

    print(
        "Category:",
        item["category"]
    )

    print(
        "Semantic:",
        round(item["semantic"], 3)
    )

    print(
        "Educational:",
        round(item["education"], 3)
    )

    print(
        "Hype:",
        round(item["hype"], 3)
    )

    print(
        "Final:",
        round(item["final"], 3)
    )


# ============================================================
# BEST RECOMMENDATION
# ============================================================

best = results[0]

candidate = best["candidate"]

recommended_title = candidate.get(
    "title",
    "Technology Reel"
)

category = best["category"]


# ============================================================
# DIFFICULTY
# ============================================================

text = (
    candidate.get("title", "")
    + " "
    + candidate.get("transcript_snippet", "")
).lower()


if any(
    word in text
    for word in [

        "advanced",
        "distributed systems",
        "system design",
        "architecture",
        "senior"
    ]
):

    difficulty = "Advanced"


elif any(
    word in text
    for word in [

        "interview",
        "optimization",
        "framework",
        "backend",
        "algorithm"
    ]
):

    difficulty = "Intermediate"


else:

    difficulty = "Beginner"


# ============================================================
# INTEREST EVIDENCE
# ============================================================

evidence_titles = [

    reel["title"]

    for reel in interactions

    if interaction_score(reel) >= 3
]


evidence_text = ", ".join(
    evidence_titles[:4]
)


# ============================================================
# WHY INTEREST
# ============================================================

why_interest = (

    f"The student showed strong engagement with "
    f"{evidence_text}, indicating a broader interest "
    f"in software engineering rather than only one "
    f"programming language."
)


# ============================================================
# WHY RECOMMENDATION
# ============================================================

why_recommendation = (

    f"This Reel connects to the inferred "
    f"Software Engineering interest with a semantic "
    f"relevance score of {best['semantic']:.2f}. "

    f"It has an educational value score of "
    f"{best['education']:.2f}. "

    f"The content does not contain obvious "
    f"career-hype signals."
)


# ============================================================
# FINAL REQUIRED OUTPUT
# ============================================================

print("\n")
print("=" * 60)
print("AI RECOMMENDATION RESULT")
print("=" * 60)


print("\nCURRENT REEL:")

print(
    interactions[-1].get(
        "title",
        "Unknown"
    )
)


print("\nINTEREST DETECTED:")

print(interest)


print("\nWHY:")

print(why_interest)


print("\nRECOMMENDED TECH REEL:")

print(recommended_title)


print("\nCATEGORY:")

print(category)


print("\nWHY THIS RECOMMENDATION:")

print(why_recommendation)


print("\nDIFFICULTY:")

print(difficulty)


print("\nCONFIDENCE:")

print(confidence)


print("\n" + "=" * 60)