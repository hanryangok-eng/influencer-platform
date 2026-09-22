import re

INDUSTRY_OPTIONS = [
    "화장품, 스킨케어", "건강기능식품(다이어트용)", "패션(계절의류 및 악세서리)",
    "산업(제조품별 상이)", "국내 행사 바이어 모집", "식품·음료", "의료기기·헬스케어",
    "생활용품·소비재", "뷰티 서비스·장비", "전자·IT",
]

INDUSTRY_ALIASES = {
    "화장품, 스킨케어": "화장품", "화장품·스킨케어": "화장품", "스킨케어": "화장품",
    "건강기능식품·식품": "건강식품", "건강기능식품": "건강식품", "건강 보조 식품": "건강식품", "건강기능식품(다이어트용)": "건강식품", "다이어트 건강식품": "건강식품",
    "산업기계 및 부품": "산업기계·부품", "산업기계/부품": "산업기계·부품", "산업기계,부품": "산업기계·부품", "산업기계, 부품": "산업기계·부품", "산업기계· 부품": "산업기계·부품", "산업기계 부품": "산업기계·부품", "산업용기계": "산업기계·부품", "산업용 기계": "산업기계·부품", "기계부품": "산업기계·부품",
    "패션 의류": "패션·섬유", "의류·섬유": "패션·섬유", "패션/섬유": "패션·섬유",
    "패션(계절의류 및 악세서리)": "패션·섬유", "패션·계절의류·악세서리": "패션·섬유", "계절의류 및 악세서리": "패션·섬유",
    "산업(제조품별 상이)": "산업", "산업·제조품": "산업", "제조품": "산업",
    "국내 행사 바이어 모집": "행사바이어", "행사 바이어 모집": "행사바이어", "국내행사": "행사바이어",
    "식품·음료": "식품", "식품 및 음료": "식품", "의료기기·헬스케어": "의료기기",
    "생활용품·소비재": "생활용품", "뷰티 서비스·장비": "뷰티", "전자·IT": "전자·IT", "전자제품·IT": "전자·IT",
}

INDUSTRY_TERMS = {
    "화장품": ["skincare products", "makeup cosmetics", "K-beauty products", "facial masks", "personal care cosmetics"],
    "뷰티": ["professional beauty products", "salon cosmetics", "hair care products", "nail beauty products", "beauty equipment"],
    "식품": ["processed foods", "Korean snacks", "instant foods", "sauces and condiments", "non-alcoholic beverages"],
    "건강식품": ["dietary supplements", "vitamins and minerals", "probiotic supplements", "weight management foods", "meal replacement protein products"],
    "의료기기": ["diagnostic medical devices", "hospital medical equipment", "patient monitoring devices", "rehabilitation equipment", "medical consumables"],
    "생활용품": ["household cleaning products", "home care products", "kitchen household goods", "hygiene products", "daily consumer goods"],
    "산업기계": ["industrial machinery", "machine tools", "factory automation equipment", "industrial spare parts", "manufacturing equipment"],
    "산업기계·부품": ["industrial machinery", "machine tools", "factory automation equipment", "industrial spare parts", "manufacturing equipment"],
    "산업": ["industrial products", "manufacturing equipment", "industrial machinery", "industrial components", "factory automation equipment"],
    "패션·섬유": ["fashion apparel", "textile products", "garment accessories", "fashion wholesale", "clothing brands"],
    "패션": ["fashion apparel", "textile products", "garment accessories", "fashion wholesale", "clothing brands"],
    "행사바이어": ["trade show buyers", "exhibition buyers", "hosted buyer program", "business matching event", "trade fair participants"],
    "전자·IT": ["consumer electronics", "IT hardware", "smart devices", "software solutions", "electronic components"],
}

# 넓은 업종을 그대로 검색하면 제조사·서비스사·일반 상품이 섞이기 쉬우므로,
# 제품군이 분명한 업종은 첫 화면에서 바로 검색 가능한 대표군을 제안한다.
# 화장품·건강식품처럼 기존 사용자 결과와 호환성이 중요한 항목은
# INDUSTRY_TERMS를 그대로 사용한다.
PRODUCT_FAMILY_PRESETS = {
    "산업": ["CNC machine tools", "industrial pumps", "packaging machinery", "factory automation equipment", "industrial spare parts"],
    "식품": ["Korean snacks", "sauces and condiments", "instant foods", "non-alcoholic beverages", "health foods"],
    "의료기기": ["diagnostic kits", "patient monitoring devices", "rehabilitation equipment", "medical consumables", "hospital equipment"],
}

PRODUCT_ALIASES = {
    "홍삼": "red ginseng supplements", "비타민": "vitamins and minerals", "프로바이오틱스": "probiotic supplements",
    "유산균": "probiotic supplements", "콜라겐": "collagen supplements", "건강보조식품": "dietary supplements",
    "산업기계": "industrial machinery", "기계": "industrial machinery", "기계부품": "industrial spare parts",
    "부품": "industrial spare parts", "자동화": "factory automation equipment", "공작기계": "machine tools",
    "의류": "fashion apparel", "패션": "fashion apparel", "섬유": "textile products", "원단": "textile fabrics",
    "의류부자재": "garment accessories", "다이어트식품": "weight management foods", "다이어트 식품": "weight management foods", "체중관리식품": "weight management foods", "체중 관리 식품": "weight management foods", "식사대용": "meal replacement products", "식사대용식품": "meal replacement products", "단백질": "protein supplements", "저칼로리식품": "low-calorie foods",
    "계절의류": "seasonal apparel", "악세서리": "fashion accessories", "액세서리": "fashion accessories", "제조품": "manufactured products", "산업제품": "industrial products", "행사": "trade show buyers",
}

LOCAL_BUYER_TERMS = {
    "japan": ["輸入販売", "卸売"],
    "germany": ["Importeur", "Vertrieb"],
    "vietnam": ["nhà nhập khẩu", "phân phối"],
    "united arab emirates": ["importer", "distributor"],
}

BUYER_TERMS = ["importer", "distributor", "wholesaler", "retail chain", "professional buyer"]
INDUSTRY_BUYER_TERMS = {
    "화장품": ["importer", "distributor", "beauty wholesaler", "cosmetics retail chain", "aesthetic clinic beauty salon"],
    "뷰티": ["importer", "distributor", "professional beauty wholesaler", "beauty retail chain", "beauty salon spa"],
    "식품": ["food importer", "food distributor", "food wholesaler", "supermarket chain", "grocery retailer"],
    "건강식품": ["supplement importer", "supplement distributor", "health products wholesaler", "pharmacy chain", "health store retailer"],
    "의료기기": ["medical device importer", "medical equipment distributor", "hospital supplier", "medical wholesaler", "clinic procurement"],
    "생활용품": ["consumer goods importer", "household distributor", "household wholesaler", "retail chain", "home care retailer"],
    "산업기계": ["industrial equipment importer", "machinery distributor", "machine tool wholesaler", "industrial parts distributor", "factory automation dealer"],
    "산업기계·부품": ["industrial equipment importer", "machinery distributor", "machine tool wholesaler", "industrial parts distributor", "factory automation dealer"],
    "산업": ["industrial importer", "industrial distributor", "manufacturing buyer", "industrial wholesaler", "factory procurement"],
    "패션·섬유": ["fashion importer", "apparel distributor", "textile wholesaler", "fashion retail chain", "clothing buyer"],
    "패션": ["fashion importer", "apparel distributor", "textile wholesaler", "fashion retail chain", "clothing buyer"],
    "행사바이어": ["trade show organizer", "hosted buyer recruiter", "exhibition business matching", "trade fair buyer program", "event partnership manager"],
    "전자·IT": ["electronics importer", "IT distributor", "technology wholesaler", "consumer electronics retailer", "enterprise technology buyer"],
}


def resolve_search_industry(industry: str, event_industry: str = "") -> str:
    """행사 초청은 수집 목적이며, 참가 대상의 실제 품목으로 검색한다."""
    value = str(industry or "").strip()
    if INDUSTRY_ALIASES.get(value, value) == "행사바이어":
        value = str(event_industry or "").strip()
        if not value or INDUSTRY_ALIASES.get(value, value) == "행사바이어":
            raise ValueError("행사 참가 대상 업종을 선택해 주세요.")
    return value


def suggest_products(industry: str) -> list[str]:
    """업종별 대표 세부제품을 제안한다. 화면에서 직접 제품을 더 추가할 수 있다."""
    industry = resolve_search_industry(industry)
    value = INDUSTRY_ALIASES.get(str(industry or "").strip(), str(industry or "").strip())
    if value in PRODUCT_FAMILY_PRESETS:
        return PRODUCT_FAMILY_PRESETS[value][:5]
    if value in INDUSTRY_TERMS:
        return INDUSTRY_TERMS[value][:5]
    base = value or "products"
    return [base, f"{base} products", f"Korean {base}", f"professional {base}", f"premium {base}"]


def _product_terms(industry: str, products: str | list[str] | tuple[str, ...]) -> list[str]:
    if isinstance(products, str):
        # 쉼표·줄바꿈·세미콜론·슬래시를 모두 구분자로 처리해
        # "machine,industrial product" 같은 비정상 결합을 막는다.
        raw = re.split(r"[,\n;|/]+", products)
    else:
        raw = list(products or [])
    cleaned = [str(value).strip() for value in raw if str(value).strip()]
    aliases={"skin care":"skincare", "facial mask":"sheet mask", "facial masks":"sheet mask", "k beauty":"k-beauty"}
    unique=[]; seen=set()
    for value in cleaned or suggest_products(industry):
        key=" ".join(value.lower().replace("-"," ").split())
        key=aliases.get(key,key)
        translated=PRODUCT_ALIASES.get(key, PRODUCT_ALIASES.get(value.strip(), ""))
        # 한국어 자유입력은 화면에 보존하지만 검색어는 알려진 영어 표준어로
        # 치환한다. 미등록 용어는 업종 표준어를 사용해 검색량 급락을 방지한다.
        if translated: value=translated; key=translated
        elif any("가" <= ch <= "힣" for ch in value):
            canonical=INDUSTRY_ALIASES.get(str(industry or "").strip(), str(industry or "").strip())
            value=(INDUSTRY_TERMS.get(canonical) or ["products"])[0]
            key=value.lower()
        if key not in seen:
            seen.add(key); unique.append(value)
    return unique[:10]


def generate_keywords(region: str, industry: str, products: str | list[str] = "", limit: int = 8) -> list[str]:
    """제품과 구매자 역할을 골고루 섞은 검색 축을 만든다.

    제품 수를 그대로 API 호출 수로 바꾸지 않는다. 먼저 모든 제품이 최소 한 번
    노출되게 한 뒤, 수입·유통·도매·소매/전문채널 역할을 회전 배정한다.
    """
    industry = resolve_search_industry(industry)
    canonical_industry = INDUSTRY_ALIASES.get(str(industry or "").strip(), str(industry or "").strip())
    product_terms = _product_terms(canonical_industry, products)
    keywords = []
    effective_limit=max(3,min(int(limit or 8),12))
    buyer_terms = INDUSTRY_BUYER_TERMS.get(canonical_industry,BUYER_TERMS).copy()
    for idx in range(max(len(product_terms),len(buyer_terms))):
        buyer=buyer_terms[idx % len(buyer_terms)]
        item=product_terms[idx % len(product_terms)]
        keywords.append(f"{item} {buyer}")
    return list(dict.fromkeys(keywords))[:effective_limit]


EXPANSION_BUYER_TERMS = {
    "화장품": ["beauty products importer", "Korean cosmetics distributor", "personal care wholesaler"],
    "건강식품": ["dietary supplement importer", "nutraceutical distributor", "health food wholesaler"],
    "산업": ["equipment distributor", "importer", "wholesaler"],
    "산업기계": ["equipment distributor", "importer", "wholesaler"],
    "산업기계·부품": ["equipment distributor", "importer", "wholesaler"],
    "식품": ["food products importer", "grocery distributor", "FMCG wholesaler"],
    "의료기기": ["healthcare device importer", "hospital equipment buyer", "medical supply distributor"],
    "생활용품": ["consumer goods importer", "home care distributor", "household wholesaler"],
    "뷰티": ["professional beauty importer", "salon equipment distributor", "beauty supply wholesaler"],
    "전자·IT": ["electronics importer", "IT distributor", "technology wholesaler"],
    "패션·섬유": ["apparel importer", "fashion distributor", "textile wholesaler"],
    "패션": ["apparel importer", "fashion distributor", "textile wholesaler"],
}


def generate_expansion_keywords(region: str, industry: str, products: str | list[str] = "", limit: int = 3) -> list[str]:
    """후보 풀이 부족할 때만 사용하는 추가 검색축을 만든다.

    기본 검색 5개와 역할이 겹치지 않도록 수입·유통·조직자 등 확장 역할을
    사용한다. ``region``은 API 호출 시 국가가 붙는 동일 인터페이스를 유지하기
    위해 받지만, 국가명은 검색어에 중복 삽입하지 않는다.
    """
    industry = resolve_search_industry(industry)
    canonical_industry = INDUSTRY_ALIASES.get(str(industry or "").strip(), str(industry or "").strip())
    buyer_terms = EXPANSION_BUYER_TERMS.get(canonical_industry, ["product importer", "product distributor", "product wholesaler"])
    product_terms = _product_terms(canonical_industry, products)
    effective_limit = max(0, min(int(limit or 0), 3))
    if not effective_limit:
        return []
    seen = {" ".join(k.casefold().split()) for k in generate_keywords(region, industry, product_terms, 10)}
    keywords = []
    for offset in range(len(buyer_terms)):
        for index, item in enumerate(product_terms):
            keyword = f"{item} {buyer_terms[(index + offset) % len(buyer_terms)]}"
            key = " ".join(keyword.casefold().split())
            if key not in seen:
                keywords.append(keyword)
                seen.add(key)
                if len(keywords) >= effective_limit:
                    return keywords
    return keywords


def generate_keyword_plan(region: str, industry: str, products: str | list[str] = "") -> tuple[list[str], list[str]]:
    """기본은 5개. 사용자가 6~10개 제품을 선택하면 모든 제품을 기본 검색에 포함한다."""
    industry = resolve_search_industry(industry)
    terms = _product_terms(industry, products)
    base = generate_keywords(region, industry, terms, max(5, len(terms)))
    return base, generate_expansion_keywords(region, industry, terms, 3)
