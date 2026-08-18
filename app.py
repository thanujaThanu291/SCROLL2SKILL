from flask import Flask, jsonify
from flask_cors import CORS
import subprocess
import re

app = Flask(__name__)
CORS(app)


@app.route("/")
def home():
    return "ReelWise AI Backend is Running"


@app.route("/api/recommend")
def recommend():

    try:

        result = subprocess.run(
            ["python3", "recommender.py"],
            capture_output=True,
            text=True
        )

        output = result.stdout

        # =====================================================
        # EXTRACT TOP 5 RECOMMENDATIONS
        # =====================================================

        recommendations = []

        pattern = re.compile(
            r"#(\d+)\s*"
            r"Title:\s*(.*?)\s*"
            r"Category:\s*(.*?)\s*"
            r"Semantic:\s*([0-9.]+)\s*"
            r"Educational:\s*([0-9.]+)\s*"
            r"Hype:\s*([0-9.]+)\s*"
            r"Final:\s*(-?[0-9.]+)",
            re.MULTILINE
        )

        matches = pattern.findall(output)

        for match in matches:

            recommendations.append({
                "rank": int(match[0]),
                "title": match[1].strip(),
                "category": match[2].strip(),
                "semantic": float(match[3]),
                "educational": float(match[4]),
                "hype": float(match[5]),
                "final": float(match[6])
            })


        # =====================================================
        # EXTRACT MAIN RESULT
        # =====================================================

        def extract_value(label):

            lines = output.splitlines()

            for i, line in enumerate(lines):

                if line.strip() == label:

                    if i + 1 < len(lines):
                        return lines[i + 1].strip()

            return ""


        current_reel = extract_value(
            "CURRENT REEL:"
        )

        interest = extract_value(
            "INTEREST DETECTED:"
        )

        recommended_reel = extract_value(
            "RECOMMENDED TECH REEL:"
        )

        category = extract_value(
            "CATEGORY:"
        )

        difficulty = extract_value(
            "DIFFICULTY:"
        )

        confidence = extract_value(
            "CONFIDENCE:"
        )


        # =====================================================
        # RETURN DATA TO FRONTEND
        # =====================================================

        return jsonify({

            "success": True,

            "output": output,

            "current_reel": current_reel,

            "interest": interest,

            "recommended_reel": recommended_reel,

            "category": category,

            "difficulty": difficulty,

            "confidence": confidence,

            "recommendations": recommendations,

            "error": result.stderr

        })


    except Exception as e:

        return jsonify({

            "success": False,

            "error": str(e)

        })


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )