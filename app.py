"""
인플루언서 발굴 프로그램 - 서버 (v0.2)
v0.1에서 추가된 것:
- 후보를 화면에서 직접 추가·수정·삭제할 수 있는 기능(API)
- 데이터는 data/influencers.csv 파일에 저장됨 (서버를 꺼도 남아 있음)
- CSV 불러오기(여러 건 한 번에 등록)와 "샘플로 되돌리기" 기능
지금 안 하는 것 (다음 단계):
- 실제 인스타그램 조회
- 이메일 실제 발송
"""
import csv
import os
import re
import uuid
from datetime import date

from flask import Flask, jsonify, request, send_from_directory

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DATA_FILE = os.path.join(DATA_DIR, "influencers.csv")          # 실제 사용 중인 저장소 (수정됨)
SEED_FILE = os.path.join(DATA_DIR, "influencers_seed.csv")     # "샘플로 되돌리기"용 원본 5건

# 저장소의 컬럼. 순서가 파일에 그대로 저장된다.
COLUMNS = [
    "후보ID", "데이터구분", "표시명", "핸들", "국가", "카테고리",
    "팔로워", "참여율", "계정유형", "수집방식",
    "프로필출처URL", "연락이메일", "이메일출처URL",
    "검증상태", "확인일자", "수신거부·동의상태", "연락처·발송규제",
]
# 화면에서 직접 추가할 때 반드시 있어야 하는 항목 (출처 없는 정보를 막기 위한 최소 원칙)
REQUIRED = ["표시명", "핸들", "국가", "프로필출처URL"]


def _read_csv(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def _write_csv(path, rows):
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in COLUMNS})


def load_candidates():
    return _read_csv(DATA_FILE)


def save_candidates(rows):
    _write_csv(DATA_FILE, rows)


def next_id(rows):
    """CAND-0001 형태의 새 ID를 만든다. 이미 쓰는 번호와 겹치지 않게 한다."""
    max_n = 0
    for r in rows:
        m = re.match(r"CAND-(\d+)$", r.get("후보ID", ""))
        if m:
            max_n = max(max_n, int(m.group(1)))
    return f"CAND-{max_n + 1:04d}"


def normalize(payload, rows, is_new):
    """화면에서 들어온 값을 저장 형식으로 다듬는다. 문제가 있으면 오류 메시지를 준다."""
    row = {c: str(payload.get(c, "")).strip() for c in COLUMNS}
    if is_new:
        missing = [c for c in REQUIRED if not row.get(c)]
        if missing:
            return None, f"필수 항목이 비어 있습니다: {', '.join(missing)}"
        row["후보ID"] = next_id(rows)
        row["데이터구분"] = row.get("데이터구분") or "실입력"
        row["수집방식"] = row.get("수집방식") or "수동입력"
        row["검증상태"] = row.get("검증상태") or "미확인"
        row["확인일자"] = row.get("확인일자") or date.today().isoformat()
        row["연락처·발송규제"] = row.get("연락처·발송규제") or "확인 필요(국가별)"
    row["핸들"] = row.get("핸들", "").lstrip("@")
    return row, None


app = Flask(__name__, static_folder="static")
app.json.ensure_ascii = False  # 응답에서 한글이 그대로 보이게 함 (Flask 3.1+)

# 서버가 처음 켜질 때 저장소 파일이 없으면 샘플 5건으로 만들어 둔다.
if not os.path.exists(DATA_FILE):
    seed = _read_csv(SEED_FILE)
    if seed:
        save_candidates(seed)


@app.get("/")
def home():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/api/health")
def health():
    return jsonify(status="ok")


@app.get("/api/candidates")
def list_candidates():
    rows = load_candidates()
    return jsonify(count=len(rows), source="저장된 데이터(csv)", candidates=rows)


@app.post("/api/candidates")
def create_candidate():
    rows = load_candidates()
    row, err = normalize(request.get_json(silent=True) or {}, rows, is_new=True)
    if err:
        return jsonify(error=err), 400
    rows.append(row)
    save_candidates(rows)
    return jsonify(candidate=row), 201


@app.post("/api/candidates/bulk")
def bulk_create_candidates():
    """CSV로 여러 건을 한 번에 등록한다. 표시명·핸들·국가가 없는 행은 건너뛴다."""
    items = request.get_json(silent=True) or []
    rows = load_candidates()
    added, skipped = [], 0
    for item in items:
        row, err = normalize(item, rows, is_new=True)
        if err:
            skipped += 1
            continue
        rows.append(row)
        added.append(row)
    save_candidates(rows)
    return jsonify(added=len(added), skipped=skipped, count=len(rows)), 201


@app.put("/api/candidates/<cand_id>")
def update_candidate(cand_id):
    rows = load_candidates()
    idx = next((i for i, r in enumerate(rows) if r.get("후보ID") == cand_id), None)
    if idx is None:
        return jsonify(error="해당 후보를 찾을 수 없습니다."), 404
    payload = request.get_json(silent=True) or {}
    merged = {**rows[idx], **{k: v for k, v in payload.items() if k in COLUMNS}}
    row, err = normalize(merged, rows, is_new=False)
    if err:
        return jsonify(error=err), 400
    row["후보ID"] = cand_id
    rows[idx] = row
    save_candidates(rows)
    return jsonify(candidate=row)


@app.delete("/api/candidates/<cand_id>")
def delete_candidate(cand_id):
    rows = load_candidates()
    new_rows = [r for r in rows if r.get("후보ID") != cand_id]
    if len(new_rows) == len(rows):
        return jsonify(error="해당 후보를 찾을 수 없습니다."), 404
    save_candidates(new_rows)
    return jsonify(deleted=cand_id)


@app.post("/api/candidates/reset")
def reset_candidates():
    """저장된 데이터를 지우고 원래 샘플 5건으로 되돌린다."""
    seed = _read_csv(SEED_FILE)
    save_candidates(seed)
    return jsonify(count=len(seed), source="샘플로 초기화됨")


if __name__ == "__main__":
    app.run(debug=True, port=5000)
