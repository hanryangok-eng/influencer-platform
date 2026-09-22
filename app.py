"""
인플루언서 발굴 프로그램 - 서버 뼈대 (v0.1)
지금은 아래만 합니다:
1) 화면(static/index.html) 보여주기
2) 후보 목록을 데이터 파일(csv)에서 읽어 화면에 전달하기
나중 단계에서 실제 인스타그램 조회, 저장 방식 등을 추가합니다.
"""
import csv
import os
from flask import Flask, jsonify, send_from_directory

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data", "influencers_sample.csv")

app = Flask(__name__, static_folder="static")
app.json.ensure_ascii = False  # 응답에서 한글이 그대로 보이게 함 (Flask 3.1+)


def load_candidates():
    """csv 파일에서 후보 목록을 읽는다. 파일이 없으면 빈 목록을 준다."""
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


@app.get("/")
def home():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/api/health")
def health():
    """프로그램이 정상 작동하는지 확인하는 용도"""
    return jsonify(status="ok")


@app.get("/api/candidates")
def candidates():
    """후보 목록을 화면에 전달한다. 지금은 샘플 데이터다."""
    rows = load_candidates()
    return jsonify(count=len(rows), source="샘플(csv)", candidates=rows)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
