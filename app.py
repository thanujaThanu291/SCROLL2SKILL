from flask import Flask, jsonify
from flask_cors import CORS
import subprocess
import re

app = Flask(__name__)
CORS(app)


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():
    return "Scroll2Skill AI Backend is Running"


# ============================================================
# RECOMMENDATION API
# ============================================================

@app.route("/api/recommend")
def recommend():

    try:

        # Run the AI recommender
        result = subprocess.run(
            ["python3", "recommender.py"],
            capture_output=True,
            text=True
        )

        output = result.stdout

        # If recommender.py failed
        if result.returncode != 0:

            return jsonify({
                "success": False,
                "error": result.stderr
            })


        # ====================================================
        # SECTION EXTRACTOR
        # ====================================================

        def extract(start, end):

            if start not in output:
                return ""

            text = output.split(start, 1)[1]

            if end in text:
                text = text.split(end, 1)[0]

            return text.strip()


        # ====================================================
        # EXTRACT RECOMMENDATION DATA
        # ====================================================

        current_reel = extract(
            "CURRENT REEL:",
            "INTEREST DETECTED:"
        )

        interest = extract(
            "INTEREST DETECTED:",
            "WHY:"
        )

        why_interest = extract(
            "WHY:",
            "RECOMMENDED TECH REEL:"
        )

        recommendation = extract(
            "RECOMMENDED TECH REEL:",
            "CATEGORY:"
        )

        category = extract(
            "CATEGORY:",
            "WHY THIS RECOMMENDATION:"
        )

        why_recommendation = extract(
            "WHY THIS RECOMMENDATION:",
            "DIFFICULTY:"
        )

        difficulty = extract(
            "DIFFICULTY:",
            "CONFIDENCE:"
        )

        confidence = extract(
            "CONFIDENCE:",
            "=" * 60
        )


        # ====================================================
        # SEMANTIC SCORE
        # ====================================================

        score_match = re.search(
            r"semantic relevance score of\s+([0-9]+(?:\.[0-9]+)?)",
            output,
            re.IGNORECASE
        )

        semantic_score = 0.0

        if score_match:

            semantic_score = float(
                score_match.group(1)
            )


        # ====================================================
        # CLEAN TEXT
        # ====================================================

        def clean(text):

            if not text:
                return ""

            return (
                text
                .replace("\r", "")
                .replace("\n", " ")
                .replace("=", "")
                .strip()
            )


        current_reel = clean(current_reel)
        interest = clean(interest)
        why_interest = clean(why_interest)
        recommendation = clean(recommendation)
        category = clean(category)
        why_recommendation = clean(why_recommendation)
        difficulty = clean(difficulty)
        confidence = clean(confidence)


        # ====================================================
        # RETURN JSON TO FRONTEND
        # ====================================================

        return jsonify({

            "success": True,

            "current_reel": current_reel,

            "interest": interest,

            "why_interest": why_interest,

            "recommendation": recommendation,

            "category": category,

            "why_recommendation": why_recommendation,

            "difficulty": difficulty,

            "confidence": confidence,

            "semantic_score": semantic_score,

            "semantic_percentage": round(
                semantic_score * 100
            )

        })


    except Exception as e:

        return jsonify({

            "success": False,

            "error": str(e)

        })


# ============================================================
# START FLASK
# ============================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )