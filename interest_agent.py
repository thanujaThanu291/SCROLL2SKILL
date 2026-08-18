import json


# --------------------------------------------------
# 1. Load student interaction history
# --------------------------------------------------

with open("interactions.json", "r", encoding="utf-8") as file:
    data = json.load(file)

interactions = data["interactions"]


# --------------------------------------------------
# 2. Calculate interaction strength
# --------------------------------------------------

def interaction_score(reel):
    score = 0

    # Watch percentage
    watch = reel.get("watch_percentage", 0)

    if watch >= 80:
        score += 3
    elif watch >= 50:
        score += 1
    else:
        score -= 2

    # User actions
    if reel.get("liked", False):
        score += 3

    if reel.get("saved", False):
        score += 5

    if reel.get("shared", False):
        score += 4

    if reel.get("skipped", False):
        score -= 3

    return score


# --------------------------------------------------
# 3. Analyze every interaction
# --------------------------------------------------

print("\n========== STUDENT INTERACTION ANALYSIS ==========\n")

for reel in interactions:

    score = interaction_score(reel)

    print(f"Reel: {reel['title']}")
    print(f"Watch: {reel['watch_percentage']}%")
    print(f"Interaction Score: {score}")
    print("-" * 50)


# --------------------------------------------------
# 4. Infer broader interests
# --------------------------------------------------

interest_scores = {
    "Software Engineering": 0,
    "Programming": 0,
    "Coding Interviews": 0,
    "Developer Hardware": 0,
    "Artificial Intelligence": 0,
    "Gaming": 0,
    "Entertainment": 0,
    "Sports": 0
}


# Keywords are used ONLY as supporting signals.
# Later we will replace this with semantic AI analysis.

interest_keywords = {

    "Software Engineering": [
        "software engineer",
        "software engineering",
        "developer",
        "development",
        "coding setup"
    ],

    "Programming": [
        "java",
        "python",
        "programming",
        "coding",
        "code"
    ],

    "Coding Interviews": [
        "coding interview",
        "leetcode",
        "interview"
    ],

    "Developer Hardware": [
        "laptop",
        "programming laptop",
        "developer hardware"
    ],

    "Artificial Intelligence": [
        "ai",
        "artificial intelligence",
        "machine learning"
    ],

    "Gaming": [
        "gaming",
        "game",
        "gamer"
    ],

    "Sports": [
        "cricket",
        "football",
        "sports"
    ]
}


# --------------------------------------------------
# 5. Score interests from user behavior
# --------------------------------------------------

for reel in interactions:

    text = (
        reel.get("title", "") + " " +
        reel.get("transcript", "")
    ).lower()

    score = interaction_score(reel)

    for interest, keywords in interest_keywords.items():

        for keyword in keywords:

            if keyword in text:
                interest_scores[interest] += score


# --------------------------------------------------
# 6. Sort interests
# --------------------------------------------------

ranked_interests = sorted(
    interest_scores.items(),
    key=lambda x: x[1],
    reverse=True
)


# --------------------------------------------------
# 7. Display inferred interests
# --------------------------------------------------

print("\n========== INFERRED STUDENT INTERESTS ==========\n")

for interest, score in ranked_interests:

    if score > 0:
        print(f"{interest}: {score}")


# --------------------------------------------------
# 8. Primary interest
# --------------------------------------------------

primary_interest = ranked_interests[0][0]
primary_score = ranked_interests[0][1]


print("\n==============================================")
print("PRIMARY INTEREST DETECTED")
print("==============================================")

print(f"Interest   : {primary_interest}")
print(f"Score      : {primary_score}")

if primary_score >= 15:
    confidence = "High"
elif primary_score >= 8:
    confidence = "Medium"
else:
    confidence = "Low"

print(f"Confidence : {confidence}")