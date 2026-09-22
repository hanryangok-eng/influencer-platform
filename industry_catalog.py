"""Curated product taxonomy. Korean labels are not sent as English search terms."""
from keyword_generator import generate_keyword_plan

# label: (classification industry, {subcategory: Korean product -> English phrase})
CATALOG = {
    "화장품·스킨케어": ("화장품", {
        "스킨케어": {"세럼": "facial serum", "보습크림": "moisturizing cream", "선크림": "sunscreen", "클렌저": "facial cleanser", "시트마스크": "sheet masks"},
        "색조화장품": {"립스틱": "lipstick", "파운데이션": "foundation makeup", "아이섀도": "eye shadow", "마스카라": "mascara", "블러셔": "blush makeup"},
        "헤어·바디": {"샴푸": "shampoo", "컨디셔너": "hair conditioner", "바디워시": "body wash", "바디로션": "body lotion", "핸드크림": "hand cream"},
        "화장품 원료": {"화장품용 펩타이드": "cosmetic peptides", "히알루론산 원료": "cosmetic hyaluronic acid", "세라마이드 원료": "cosmetic ceramides", "화장품 식물추출물": "cosmetic botanical extracts", "화장품 유화제": "cosmetic emulsifiers"},
    }),
    "건강기능식품·다이어트": ("건강식품", {
        "영양제": {"비타민": "vitamin supplements", "유산균": "probiotic supplements", "오메가3": "omega 3 supplements", "홍삼": "red ginseng supplements", "콜라겐": "collagen supplements"},
        "다이어트·체중관리": {"식사대용 쉐이크": "meal replacement shakes", "체중관리 보충제": "weight management supplements", "저칼로리 간식": "low calorie snacks", "고단백 식사대용": "high protein meal replacements", "식이섬유 보충제": "dietary fiber supplements"},
        "스포츠 뉴트리션": {"단백질 파우더": "protein powder", "단백질바": "protein bars", "아미노산 보충제": "amino acid supplements", "전해질 보충제": "electrolyte supplements", "크레아틴": "creatine supplements"},
    }),
    "패션·의류·액세서리": ("패션·섬유", {
        "계절의류": {"티셔츠": "t shirts", "여름 원피스": "summer dresses", "니트웨어": "knitwear", "겨울 코트": "winter coats", "재킷": "jackets"},
        "스포츠웨어": {"레깅스": "sports leggings", "트레이닝복": "tracksuits", "요가복": "yoga apparel", "골프웨어": "golf apparel", "러닝웨어": "running apparel"},
        "가방·신발": {"핸드백": "handbags", "백팩": "backpacks", "운동화": "sneakers", "샌들": "sandals", "가죽 신발": "leather shoes"},
        "주얼리·액세서리": {"패션 주얼리": "fashion jewelry", "헤어 액세서리": "hair accessories", "스카프": "scarves", "벨트": "fashion belts", "모자": "fashion hats"},
    }),
    "산업기계·부품": ("산업", {
        "포장기계": {"충진기": "filling machines", "라벨링기": "labeling machines", "실링기": "sealing machines", "포장기": "wrapping machines", "카토닝기": "cartoning machines"},
        "CNC·공작기계": {"CNC 선반": "CNC lathes", "머시닝센터": "machining centers", "밀링머신": "milling machines", "연삭기": "grinding machines", "절삭공구": "cutting tools"},
        "펌프·밸브": {"원심펌프": "centrifugal pumps", "다이어프램펌프": "diaphragm pumps", "기어펌프": "gear pumps", "제어밸브": "control valves", "볼밸브": "ball valves"},
        "자동화·산업부품": {"PLC": "programmable logic controllers", "서보모터": "servo motors", "산업용 센서": "industrial sensors", "산업용 베어링": "industrial bearings", "산업용 로봇": "industrial robots"},
    }),
    "식품·음료": ("식품", {
        "간편식·스낵": {"라면": "instant noodles", "즉석밥": "ready to eat rice", "김스낵": "seaweed snacks", "쌀과자": "rice crackers", "냉동만두": "frozen dumplings"},
        "소스·조미료": {"고추장": "gochujang", "간장": "soy sauce", "바비큐소스": "barbecue sauce", "샐러드드레싱": "salad dressing", "조미료": "food seasonings"},
        "음료": {"과일주스": "fruit juice", "차음료": "ready to drink tea", "커피음료": "ready to drink coffee", "탄산음료": "soft drinks", "식물성음료": "plant based beverages"},
    }),
    "의료기기·헬스케어": ("의료기기", {
        "진단·모니터링": {"진단키트": "diagnostic test kits", "환자모니터": "patient monitors", "혈압계": "blood pressure monitors", "혈당측정기": "blood glucose meters", "산소포화도측정기": "pulse oximeters"},
        "의료소모품": {"의료용 장갑": "medical gloves", "주사기": "medical syringes", "상처드레싱": "wound dressings", "의료용 거즈": "medical gauze", "카테터": "medical catheters"},
        "재활·병원장비": {"재활운동기기": "rehabilitation equipment", "병원침대": "hospital beds", "휠체어": "wheelchairs", "보행보조기": "walking aids", "물리치료장비": "physiotherapy equipment"},
    }),
    "생활용품·소비재": ("생활용품", {
        "세정·위생": {"세탁세제": "laundry detergent", "주방세제": "dishwashing detergent", "물티슈": "wet wipes", "위생용품": "personal hygiene products", "청소용품": "household cleaning products"},
        "주방·수납": {"조리도구": "kitchen utensils", "밀폐용기": "food storage containers", "텀블러": "reusable tumblers", "수납용품": "home storage products", "식기": "tableware"},
    }),
    "뷰티 서비스·장비": ("뷰티", {
        "살롱·헤어장비": {"헤어드라이어": "professional hair dryers", "헤어고데기": "hair straighteners", "살롱의자": "salon chairs", "이발기": "hair clippers", "헤어스타일링도구": "hair styling tools"},
        "피부·네일장비": {"피부관리장비": "facial treatment equipment", "LED 미용기기": "LED beauty devices", "네일램프": "nail curing lamps", "네일드릴": "electric nail drills", "미용베드": "beauty treatment beds"},
    }),
    "전자·IT": ("전자·IT", {
        "소비자가전": {"공기청정기": "air purifiers", "소형가전": "small home appliances", "무선이어폰": "wireless earbuds", "스마트워치": "smart watches", "충전기": "electronic chargers"},
        "IT장비·전자부품": {"네트워크장비": "network equipment", "산업용 컴퓨터": "industrial computers", "반도체": "semiconductors", "전자커넥터": "electronic connectors", "PCB": "printed circuit boards"},
    }),
    "포장재·소재": ("산업", {
        "포장재": {"포장필름": "packaging films", "식품포장용기": "food packaging containers", "골판지상자": "corrugated boxes", "포장파우치": "packaging pouches", "화장품용기": "cosmetic packaging containers"},
        "산업소재": {"산업용 수지": "industrial resins", "산업용 접착제": "industrial adhesives", "고무소재": "industrial rubber materials", "부직포": "nonwoven fabrics", "금속소재": "industrial metal materials"},
    }),
}


def product_options(major, subcategories):
    options = {}
    for sub in subcategories:
        if sub not in CATALOG[major][1]:
            raise ValueError(f"알 수 없는 세부업종: {sub}")
        options.update(CATALOG[major][1][sub])
    return options


def make_group(major, subcategories, products):
    """No silent truncation or unknown-Korean fallback to an unrelated broad term."""
    if major not in CATALOG or not subcategories:
        raise ValueError("대분류와 세부업종을 선택하세요.")
    product_options(major, subcategories)
    if not products or len(products) > 10:
        raise ValueError(f"{major}: 세부제품은 1~10개를 선택하세요.")
    if any(any("가" <= c <= "힣" for c in p) for p in products):
        raise ValueError("추가 제품은 영어 검색어로 입력하세요. 미등록 한글은 임의로 치환하지 않습니다.")
    canonical = CATALOG[major][0]
    base, expansion = generate_keyword_plan("", canonical, products)
    # Machinery buyers need dealers and importers, not a vague manufacturing buyer.
    if major == "산업기계·부품":
        roles = ("equipment distributor", "machinery importer", "equipment dealer", "industrial wholesaler", "system integrator")
        base = [f"{p} {roles[i % len(roles)]}" for i,p in enumerate(products)]
        expansion = [f"{p} {roles[(i+1) % len(roles)]}" for i,p in enumerate(products[:3])]
    elif major == "포장재·소재":
        roles = ("importer", "distributor", "wholesaler", "industrial supplier", "packaging distributor")
        base = [f"{p} {roles[i % len(roles)]}" for i,p in enumerate(products)]
        expansion = [f"{p} importer distributor" for p in products[:3]]
    return dict(major=major, industry=canonical, subcategories=list(subcategories),
                products=list(products), keywords=base+expansion, base_keyword_count=len(base))


def validate_groups(groups):
    if not 1 <= len(groups) <= 3 or len({g['major'] for g in groups}) != len(groups):
        raise ValueError("서로 다른 대분류를 1~3개 선택하세요.")
    for group in groups:
        make_group(group['major'], group['subcategories'], group['products'])
        if not group.get('keywords'):
            raise ValueError("업종별 검색어를 1개 이상 입력하세요.")


def allocate(total, count):
    """Exact integer totals, deterministic ordering, no per-industry multiplication."""
    q, r = divmod(int(total), count)
    return [q + int(i < r) for i in range(count)]
