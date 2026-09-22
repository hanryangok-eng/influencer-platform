COUNTRIES = {
    "Vietnam": ("아시아", "vn", "84", ["vietnam", "viet nam", "việt nam", "vietnamese", "ho chi minh", "hanoi", "hà nội"], ["nhà nhập khẩu", "nhà phân phối", "phân phối", "hệ thống phân phối", "đại lý"]),
    "Thailand": ("아시아", "th", "66", ["thailand", "thai", "bangkok"], ["ผู้นำเข้า", "ผู้จัดจำหน่าย", "ขายส่ง", "ตัวแทนจำหน่าย", "ร้านค้า"]),
    "Indonesia": ("아시아", "id", "62", ["indonesia", "indonesian", "jakarta"], ["importir", "distributor", "grosir", "agen", "pemasok"]),
    "Malaysia": ("아시아", "my", "60", ["malaysia", "malaysian", "kuala lumpur"], ["pengimport", "pengedar"]),
    "Singapore": ("아시아", "sg", "65", ["singapore", "singaporean"], ["importer", "distributor"]),
    "Philippines": ("아시아", "ph", "63", ["philippines", "philippine", "filipino", "manila"], ["importer", "distributor"]),
    "Japan": ("아시아", "jp", "81", ["japan", "japanese", "tokyo"], ["輸入", "輸入販売", "卸売", "販売代理店", "商社", "法人向け"]),
    "China": ("아시아", "cn", "86", ["china", "chinese", "beijing", "shanghai"], ["进口商", "经销商"]),
    "Taiwan": ("아시아", "tw", "886", ["taiwan", "taiwanese", "taipei"], ["韓國化妝品進口商", "韓國美妝代理商", "化妝品經銷商", "化妝品批發", "美妝通路"]),
    "Hong Kong": ("아시아", "hk", "852", ["hong kong", "hongkong"], ["進口商", "分銷商"]),
    "India": ("아시아", "in", "91", ["india", "indian", "new delhi", "mumbai"], ["importer", "distributor"]),
    "South Korea": ("아시아", "kr", "82", ["south korea", "korea", "korean", "seoul"], ["수입업체", "유통업체"]),
    "United States": ("북미", "us", "1", ["united states", "usa", "u.s.a", "american"], ["importer", "distributor"]),
    "Canada": ("북미", "ca", "1", ["canada", "canadian", "toronto", "vancouver"], ["importer", "distributor"]),
    "Mexico": ("북미", "mx", "52", ["mexico", "mexican", "méxico"], ["importador de cosméticos", "distribuidor de cosméticos", "mayorista de belleza", "cosmética coreana", "productos coreanos al mayoreo"]),
    "United Kingdom": ("유럽", "uk", "44", ["united kingdom", "uk", "british", "england", "london"], ["importer", "distributor"]),
    "Germany": ("유럽", "de", "49", ["germany", "german", "deutschland"], ["Importeur", "Vertrieb", "Großhandel", "Händler", "Warenimport"]),
    "France": ("유럽", "fr", "33", ["france", "french", "paris"], ["importateur", "distributeur", "grossiste", "revendeur", "marques distribuées"]),
    "Italy": ("유럽", "it", "39", ["italy", "italian", "italia"], ["importatore", "distributore"]),
    "Spain": ("유럽", "es", "34", ["spain", "spanish", "españa"], ["importador", "distribuidor"]),
    "Netherlands": ("유럽", "nl", "31", ["netherlands", "dutch", "holland"], ["importeur", "distributeur"]),
    "Belgium": ("유럽", "be", "32", ["belgium", "belgian", "belgië", "belgique"], ["importeur", "distributeur"]),
    "Poland": ("유럽", "pl", "48", ["poland", "polish", "polska"], ["importer", "dystrybutor"]),
    "Sweden": ("유럽", "se", "46", ["sweden", "swedish", "sverige"], ["importör", "distributör"]),
    "Switzerland": ("유럽", "ch", "41", ["switzerland", "swiss", "schweiz", "suisse"], ["importeur", "distributor"]),
    "Austria": ("유럽", "at", "43", ["austria", "austrian", "österreich"], ["importeur", "händler"]),
    "Czech Republic": ("유럽", "cz", "420", ["czech republic", "czechia", "czech"], ["dovozce", "distributor"]),
    "Romania": ("유럽", "ro", "40", ["romania", "romanian", "românia"], ["importator", "distribuitor"]),
    "Portugal": ("유럽", "pt", "351", ["portugal", "portuguese"], ["importador", "distribuidor"]),
    "Greece": ("유럽", "gr", "30", ["greece", "greek", "hellas"], ["εισαγωγέας", "διανομέας"]),
    "Denmark": ("유럽", "dk", "45", ["denmark", "danish", "danmark"], ["importør", "distributør"]),
    "Norway": ("유럽", "no", "47", ["norway", "norwegian", "norge"], ["importør", "distributør"]),
    "Finland": ("유럽", "fi", "358", ["finland", "finnish", "suomi"], ["maahantuoja", "jakelija"]),
    "Ireland": ("유럽", "ie", "353", ["ireland", "irish", "dublin"], ["importer", "distributor"]),
    "United Arab Emirates": ("중동", "ae", "971", ["united arab emirates", "uae", "dubai", "abu dhabi"], ["importer", "distributor", "Trading LLC", "General Trading", "FZCO", "GCC distributor"]),
    "Saudi Arabia": ("중동", "sa", "966", ["saudi arabia", "saudi", "riyadh", "jeddah"], ["مستورد", "موزع"]),
    "Qatar": ("중동", "qa", "974", ["qatar", "qatari", "doha"], ["مستورد", "موزع"]),
    "Kuwait": ("중동", "kw", "965", ["kuwait", "kuwaiti"], ["مستورد", "موزع"]),
    "Israel": ("중동", "il", "972", ["israel", "israeli", "tel aviv"], ["יבואן", "מפיץ"]),
    "Turkey": ("중동", "tr", "90", ["turkey", "türkiye", "turkish", "istanbul"], ["ithalatçı", "distribütör"]),
    "Brazil": ("중남미", "br", "55", ["brazil", "brazilian", "brasil"], ["importador", "distribuidor"]),
    "Argentina": ("중남미", "ar", "54", ["argentina", "argentine", "buenos aires"], ["importador", "distribuidor"]),
    "Chile": ("중남미", "cl", "56", ["chile", "chilean", "santiago"], ["importador", "distribuidor"]),
    "Colombia": ("중남미", "co", "57", ["colombia", "colombian", "bogotá", "bogota"], ["importador", "distribuidor"]),
    "Peru": ("중남미", "pe", "51", ["peru", "peruvian", "perú", "lima"], ["importador", "distribuidor"]),
    "Ecuador": ("중남미", "ec", "593", ["ecuador", "ecuadorian", "quito"], ["importador", "distribuidor"]),
    "Panama": ("중남미", "pa", "507", ["panama", "panamá", "panamanian"], ["importador", "distribuidor"]),
    "South Africa": ("아프리카", "za", "27", ["south africa", "south african", "johannesburg", "cape town"], ["importer", "distributor"]),
    "Egypt": ("아프리카", "eg", "20", ["egypt", "egyptian", "cairo"], ["مستورد", "موزع"]),
    "Morocco": ("아프리카", "ma", "212", ["morocco", "moroccan", "maroc", "casablanca"], ["importateur", "distributeur"]),
    "Nigeria": ("아프리카", "ng", "234", ["nigeria", "nigerian", "lagos"], ["importer", "distributor"]),
    "Kenya": ("아프리카", "ke", "254", ["kenya", "kenyan", "nairobi"], ["importer", "distributor"]),
    "Ghana": ("아프리카", "gh", "233", ["ghana", "ghanaian", "accra"], ["importer", "distributor"]),
    "Australia": ("오세아니아", "au", "61", ["australia", "australian", "sydney", "melbourne"], ["importer", "distributor"]),
    "New Zealand": ("오세아니아", "nz", "64", ["new zealand", "new zealander", "auckland"], ["importer", "distributor"]),
}

COUNTRY_NAMES_KO = {
    "Vietnam": "베트남", "Thailand": "태국", "Indonesia": "인도네시아", "Malaysia": "말레이시아",
    "Singapore": "싱가포르", "Philippines": "필리핀", "Japan": "일본", "China": "중국",
    "Taiwan": "대만", "Hong Kong": "홍콩", "India": "인도", "South Korea": "대한민국",
    "United States": "미국", "Canada": "캐나다", "Mexico": "멕시코", "United Kingdom": "영국",
    "Germany": "독일", "France": "프랑스", "Italy": "이탈리아", "Spain": "스페인",
    "Netherlands": "네덜란드", "Belgium": "벨기에", "Poland": "폴란드", "Sweden": "스웨덴",
    "Switzerland": "스위스", "Austria": "오스트리아", "Czech Republic": "체코", "Romania": "루마니아",
    "Portugal": "포르투갈", "Greece": "그리스", "Denmark": "덴마크", "Norway": "노르웨이",
    "Finland": "핀란드", "Ireland": "아일랜드", "United Arab Emirates": "아랍에미리트",
    "Saudi Arabia": "사우디아라비아", "Qatar": "카타르", "Kuwait": "쿠웨이트", "Israel": "이스라엘",
    "Turkey": "튀르키예", "Brazil": "브라질", "Argentina": "아르헨티나", "Chile": "칠레",
    "Colombia": "콜롬비아", "Peru": "페루", "Ecuador": "에콰도르", "Panama": "파나마",
    "South Africa": "남아프리카공화국", "Egypt": "이집트", "Morocco": "모로코", "Nigeria": "나이지리아",
    "Kenya": "케냐", "Ghana": "가나", "Australia": "호주", "New Zealand": "뉴질랜드",
}

WORLD_BATCHES = {
    "01 아시아 동남부": ["Vietnam", "Thailand", "Indonesia", "Malaysia", "Singapore"],
    "02 아시아 동북부": ["Japan", "China", "Taiwan", "Hong Kong", "South Korea"],
    "03 아시아 남부": ["Philippines", "India"],
    "04 북미": ["United States", "Canada", "Mexico"],
    "05 유럽 서부": ["United Kingdom", "Germany", "France", "Netherlands", "Belgium"],
    "06 유럽 남부": ["Italy", "Spain", "Portugal", "Greece", "Switzerland"],
    "07 유럽 북·동부": ["Poland", "Sweden", "Austria", "Czech Republic", "Romania"],
    "08 북유럽": ["Denmark", "Norway", "Finland", "Ireland"],
    "09 중동 1": ["United Arab Emirates", "Saudi Arabia", "Qatar", "Kuwait", "Israel"],
    "10 중동 2": ["Turkey"],
    "11 중남미 1": ["Brazil", "Argentina", "Chile", "Colombia", "Peru"],
    "12 중남미 2": ["Ecuador", "Panama"],
    "13 아프리카": ["South Africa", "Egypt", "Morocco", "Nigeria", "Kenya"],
    "14 아프리카·오세아니아": ["Ghana", "Australia", "New Zealand"],
}


def country_meta(country: str) -> dict:
    raw=COUNTRIES.get(country)
    if not raw:
        return {"continent":"직접입력","tld":"","dial":"","aliases":[country.lower()],"local_buyer":["importer","distributor"]}
    continent,tld,dial,aliases,local_buyer=raw
    return {"continent":continent,"tld":tld,"dial":dial,"aliases":aliases,"local_buyer":local_buyer}


def country_name_ko(country: str) -> str:
    """화면·Excel용 한글 국가명. 검색 로직에서는 영문 키를 유지한다."""
    return COUNTRY_NAMES_KO.get(country, country)


def countries_by_continent(continent: str) -> list[str]:
    return [name for name,raw in COUNTRIES.items() if raw[0]==continent]


def continents() -> list[str]:
    return list(dict.fromkeys(raw[0] for raw in COUNTRIES.values()))
