"""Public-search based Instagram creator discovery and outreach drafting.

This module never logs in to Instagram, fetches follower lists, bypasses access
controls, or sends messages.  It converts public search-engine results into a
review queue and prepares drafts for a human operator.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from html import unescape
import hashlib
import re
import time
import urllib.parse

from version import APP_VERSION, SCHEMA_VERSION


CATEGORY_KEYWORDS = {
    "뷰티·화장품": ["beauty", "skincare", "makeup", "cosmetics", "K-beauty"],
    "패션·잡화": ["fashion", "style", "accessories", "streetwear", "K-fashion"],
    "식품·건강": ["food", "wellness", "healthy lifestyle", "nutrition", "K-food"],
    "육아·키즈": ["parenting", "mom creator", "family lifestyle", "kids products"],
    "리빙·라이프스타일": ["lifestyle", "home decor", "living", "daily life"],
    "여행·지역": ["travel", "local guide", "travel creator", "city guide"],
}

COUNTRY_LOCAL_TERMS = {
    "Vietnam": ["Việt Nam", "Vietnam", "beauty blogger Vietnam", "KOC Vietnam"],
    "Thailand": ["Thailand", "Thai creator", "บิวตี้บล็อกเกอร์"],
    "Indonesia": ["Indonesia", "Indonesian creator", "beauty blogger Indonesia"],
    "Malaysia": ["Malaysia", "Malaysian creator"],
    "Philippines": ["Philippines", "Filipino creator"],
    "Japan": ["Japan", "Japanese creator", "美容インフルエンサー"],
    "United States": ["United States", "US creator"],
}

# v2.24.1: a bio containing the query country name anywhere is not proof the
# creator is actually based there (Brave/Tavily snippets can surface the word
# from unrelated context). Location is instead judged from an explicit,
# positive signal — a country flag emoji or a named city/country phrase — and
# checked for signals that point to a *different* country.
FLAG_EMOJI_COUNTRY = {
    "🇻🇳": "Vietnam", "🇹🇭": "Thailand", "🇮🇩": "Indonesia", "🇲🇾": "Malaysia",
    "🇵🇭": "Philippines", "🇯🇵": "Japan", "🇺🇸": "United States", "🇰🇷": "Korea",
    "🇳🇱": "Netherlands", "🇩🇪": "Germany", "🇲🇽": "Mexico", "🇬🇧": "United Kingdom",
    "🇫🇷": "France", "🇪🇸": "Spain", "🇮🇹": "Italy", "🇨🇦": "Canada",
    "🇦🇺": "Australia", "🇮🇳": "India", "🇧🇷": "Brazil", "🇨🇳": "China",
    "🇸🇬": "Singapore", "🇹🇼": "Taiwan", "🇹🇷": "Turkey", "🇦🇪": "UAE",
}
CITY_COUNTRY_HINTS = {
    "hanoi": "Vietnam", "ho chi minh": "Vietnam", "saigon": "Vietnam", "da nang": "Vietnam",
    "bangkok": "Thailand", "jakarta": "Indonesia", "kuala lumpur": "Malaysia",
    "manila": "Philippines", "tokyo": "Japan", "osaka": "Japan", "seoul": "Korea",
    "amsterdam": "Netherlands", "cincinnati": "United States", "new york": "United States",
    "los angeles": "United States", "berlin": "Germany", "mexico city": "Mexico",
    "london": "United Kingdom", "paris": "France", "madrid": "Spain",
}
MEDIA_BRAND_TERMS = (
    "magazine", "editorial", "media outlet", "official page", "official account",
    "news", "folio",
)
FIRST_PERSON_TERMS = ("i'm", "i am", "my ", "me •", "mom ", "wife ", "founder of")

CREATOR_TERMS = (
    "influencer", "content creator", "digital creator", "blogger", "vlogger",
    "reviewer", "koc", "kol", "ugc creator", "makeup artist", "beauty creator",
    "beauty blogger", "lifestyle creator", "travel creator", "creator",
)
COLLAB_TERMS = (
    "collab", "collaboration", "booking", "business inquiries", "business enquiry",
    "pr contact", "work with me", "brand partnership", "ugc", "review",
)
BUSINESS_TERMS = (
    "official store", "official shop", "company", "corporation", "clinic", "hospital",
    "shopping mall", "wholesale", "manufacturer", "distributor", "brand official",
)
RESERVED_PATHS = {
    "p", "reel", "reels", "tv", "stories", "explore", "accounts", "direct",
    "about", "developer", "legal", "press", "web", "challenge", "api", "privacy",
}
EMAIL_RE = re.compile(r"(?i)(?<![\w.+-])([a-z0-9][a-z0-9._%+-]{0,63}@[a-z0-9.-]+\.[a-z]{2,24})(?![\w.-])")
FOLLOWER_RE = re.compile(
    r"(?i)(\d{1,3}(?:[.,]\d{1,3})?|\d{1,9})\s*([kmb]?)\s*"
    r"(?:followers?|팔로워|người\s+theo\s+dõi|pengikut|ผู้ติดตาม)"
)


@dataclass
class InfluencerConfig:
    country: str
    category: str
    keywords: list[str]
    target_count: int = 20
    min_followers: int = 0
    max_followers: int = 0
    max_queries: int = 8
    request_delay: float = 0.2
    include_business_accounts: bool = False
    search_provider: str = "Brave"


def _plain(value: object, limit: int = 600) -> str:
    text=unescape(str(value or ""))
    text=re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()[:limit]


def default_keywords(category: str) -> list[str]:
    return list(CATEGORY_KEYWORDS.get(category, ["creator", "reviewer", "influencer"]))


def normalize_handle(url: str) -> str:
    """Return an Instagram profile handle, never a post/reel/system path."""
    try:
        parsed=urllib.parse.urlsplit(str(url or "").strip())
    except ValueError:
        return ""
    host=(parsed.hostname or "").lower().removeprefix("www.")
    if host not in {"instagram.com", "m.instagram.com"}:
        return ""
    parts=[part for part in parsed.path.split("/") if part]
    if not parts:
        return ""
    handle=parts[0].lstrip("@").lower()
    if handle in RESERVED_PATHS or not re.fullmatch(r"[a-z0-9._]{1,30}", handle):
        return ""
    return handle


def profile_url(handle: str) -> str:
    return f"https://www.instagram.com/{handle}/" if handle else ""


def parse_follower_count(text: str) -> int | None:
    match=FOLLOWER_RE.search(_plain(text, 1200))
    if not match:
        return None
    raw=match.group(1); suffix=match.group(2).lower()
    if suffix:
        number=float(raw.replace(",", "."))
    else:
        number=float(raw.replace(",", ""))
    multiplier={"":1, "k":1_000, "m":1_000_000, "b":1_000_000_000}[suffix]
    return int(number*multiplier)


def follower_label(value: int | None) -> str:
    if value is None:
        return "미확인"
    if value >= 1_000_000:
        return f"{value/1_000_000:.1f}M"
    if value >= 1_000:
        return f"{value/1_000:.1f}K"
    return f"{value:,}"


def extract_public_email(text: str) -> str:
    for email in EMAIL_RE.findall(_plain(text, 1600)):
        email=email.lower().strip(".,;:()[]{}<>")
        host=email.rsplit("@",1)[-1]
        if host not in {"instagram.com", "facebook.com", "example.com", "email.com"}:
            return email
    return ""


def clean_display_name(title: str, handle: str) -> str:
    text=_plain(title, 180)
    text=re.sub(r"(?i)\s*[·|\-–—]?\s*instagram(?:\s+photos\s+and\s+videos)?\s*$", "", text)
    text=re.sub(rf"(?i)\s*\(@?{re.escape(handle)}\)\s*", " ", text)
    text=re.sub(r"(?i)^instagram\s*[:\-–—|]\s*", "", text)
    text=re.sub(r"\s+", " ", text).strip(" ·|-–—")
    return (text if 1 <= len(text) <= 80 else "") or f"@{handle}"


def _term_hits(text: str, terms) -> list[str]:
    lowered=text.casefold()
    return [term for term in terms if term.casefold() in lowered]


def location_signal(text: str, target_country: str) -> tuple[str, str]:
    """Judge location from explicit signals only, never from a bare keyword hit.

    Returns (status, evidence) where status is one of:
    "확인"(target country flag/city found), "불일치"(a different country's
    flag/city found and no target signal), "미확인"(no usable signal).
    """
    lowered=text.casefold()
    found_flags=[emoji for emoji in FLAG_EMOJI_COUNTRY if emoji in text]
    target_flag_hit=any(FLAG_EMOJI_COUNTRY[e]==target_country for e in found_flags)
    if target_flag_hit:
        return "확인", "국기 일치"
    found_cities=[(city,country) for city,country in CITY_COUNTRY_HINTS.items() if city in lowered]
    target_city_hit=[c for c,co in found_cities if co==target_country]
    if target_city_hit:
        return "확인", f"도시명 일치({target_city_hit[0]})"
    other_flag=[e for e in found_flags if FLAG_EMOJI_COUNTRY[e]!=target_country]
    if other_flag:
        return "불일치", f"타국 국기({FLAG_EMOJI_COUNTRY[other_flag[0]]})"
    other_city=[(c,co) for c,co in found_cities if co!=target_country]
    if other_city:
        return "불일치", f"타국 도시명({other_city[0][0]})"
    return "미확인", ""


def build_queries(config: InfluencerConfig) -> list[str]:
    country=config.country.strip()
    keywords=list(dict.fromkeys(k.strip() for k in config.keywords if k.strip()))
    local=COUNTRY_LOCAL_TERMS.get(country, [country])
    queries=[]
    for index,keyword in enumerate(keywords):
        locality=local[index % len(local)] if local else country
        queries.extend((
            f'site:instagram.com {locality} "{keyword}" influencer creator',
            f'site:instagram.com {country} "{keyword}" blogger reviewer KOC KOL',
        ))
    queries.append(f'site:instagram.com {country} "{config.category}" "content creator"')
    return list(dict.fromkeys(queries))[:max(1, int(config.max_queries))]


def _candidate_from_result(item: dict, query: str, config: InfluencerConfig) -> tuple[dict | None, str]:
    url=str(item.get("url") or "")
    handle=normalize_handle(url)
    if not handle:
        return None, "Instagram 프로필 URL 아님"
    title=_plain(item.get("title"), 220)
    snippet=_plain(item.get("content") or item.get("description"), 900)
    combined=f"{title} {snippet} {handle}"
    lowered=combined.casefold()
    if any(token in lowered for token in ("instagram login", "log in • instagram", "sign up • instagram")):
        return None, "로그인·시스템 페이지"

    creator_hits=_term_hits(combined, CREATOR_TERMS)
    business_hits=_term_hits(combined, BUSINESS_TERMS+MEDIA_BRAND_TERMS)
    category_terms=list(dict.fromkeys(config.keywords+default_keywords(config.category)))
    category_hits=_term_hits(combined, category_terms)
    collab_hits=_term_hits(combined, COLLAB_TERMS)
    is_business=bool(business_hits) and not creator_hits
    if is_business and not config.include_business_accounts:
        return None, "기업·공식상점 계정"

    followers=parse_follower_count(combined)
    if followers is not None and config.min_followers and followers < config.min_followers:
        return None, "최소 팔로워 미달"
    if followers is not None and config.max_followers and followers > config.max_followers:
        return None, "최대 팔로워 초과"

    # High-follower accounts with no first-person creator language read more
    # like a brand/media page than a personal creator; this is a soft signal
    # (downgrade + flag for manual review), never an automatic exclusion.
    media_suspect=bool(followers) and followers>=50_000 and not any(t in lowered for t in FIRST_PERSON_TERMS)

    loc_status,loc_evidence=location_signal(combined, config.country)

    email=extract_public_email(combined)
    score=15
    score+=min(30, 15+len(creator_hits)*5) if creator_hits else 0
    score+=min(20, len(category_hits)*7)
    score+=10 if loc_status=="확인" else 0
    score-=25 if loc_status=="불일치" else 0
    score+=10 if followers is not None else 0
    score+=15 if email else 0
    score+=min(10, len(collab_hits)*5)
    score-=20 if is_business else 0
    score-=15 if media_suspect else 0
    score=max(0,min(100,score))
    grade="A" if score>=70 else "B" if score>=50 else "C"
    if loc_status=="불일치" and grade=="A":
        grade="B"  # never let an unconfirmed/conflicting location keep top grade
    profile_type="SNS 셀러·사업계정" if is_business else ("인플루언서·크리에이터" if creator_hits else "크리에이터 후보")
    if media_suspect and not is_business:
        profile_type="브랜드·미디어 의심(수동확인)"
    matched=category_hits or [k for k in config.keywords if k.casefold() in query.casefold()]
    return {
        "account_id":"INF-"+hashlib.sha256(handle.encode()).hexdigest()[:12].upper(),
        "handle":handle,
        "display_name":clean_display_name(title,handle),
        "profile_type":profile_type,
        "country":config.country,
        "location_status":loc_status,
        "location_evidence":loc_evidence,
        "category":config.category,
        "instagram_url":profile_url(handle),
        "followers":followers if followers is not None else "",
        "followers_display":follower_label(followers),
        "follower_status":"검색결과 공개표시" if followers is not None else "추가확인",
        "public_email":email,
        "email_status":"공개 검색결과 확인" if email else "미확보",
        "bio_summary":snippet[:360],
        "matched_keywords":", ".join(list(dict.fromkeys(matched))[:6]),
        "creator_evidence":", ".join(list(dict.fromkeys(creator_hits+collab_hits))[:8]),
        "score":score,
        "grade":grade,
        "discovery_query":query,
        "source_url":url,
        "source_title":title,
        "dm_status":"초안",
        "email_contact_status":"미발송",
        "collected_at":datetime.now(timezone.utc).isoformat(),
    }, ""


def _sender_label(sender: dict) -> str:
    return _plain(sender.get("brand_name") or sender.get("company_name"), 80)


def generate_outreach(record: dict, sender: dict, product: dict) -> dict:
    """Create honest drafts without claiming that a profile was deeply inspected."""
    brand=_sender_label(sender)
    company=_plain(sender.get("company_name"),80)
    contact=_plain(sender.get("contact_name"),60)
    website=_plain(sender.get("website"),180)
    product_name=_plain(product.get("product_name"),100)
    category=_plain(product.get("category") or record.get("category"),100)
    benefit=_plain(product.get("selling_points"),220)
    offer=_plain(product.get("collaboration_offer"),180)
    name=record.get("display_name") or f"@{record.get('handle','')}"
    ready=bool(brand and product_name)
    if not ready:
        return {
            **record,
            "dm_draft":"발신 브랜드명과 영문 제품명을 입력하면 맞춤 DM이 생성됩니다.",
            "email_subject":"",
            "email_body":"발신 브랜드명과 영문 제품명을 입력하면 맞춤 이메일이 생성됩니다.",
            "email_compose_url":"",
            "outreach_generation_status":"입력 필요",
        }

    intro=f"I'm {contact} from {brand}" if contact else f"I'm reaching out from {brand}"
    company_note=f" ({company})" if company and company.casefold()!=brand.casefold() else ""
    product_line=f"We would like to introduce {product_name}, a Korean {category or 'product'}."
    if benefit:
        product_line+=f" {benefit.rstrip('.')} .".replace(" .", ".")
    offer_line=offer or "Would you be open to receiving a short product introduction and discussing a possible collaboration?"
    dm=(
        f"Hi {name},\n\n"
        f"I found your public Instagram profile while researching {record.get('category','')} creators in {record.get('country','')}. "
        f"{intro}{company_note}. {product_line}\n\n{offer_line}\n\n"
        f"Best,\n{contact or brand}"
    )
    if website:
        dm+=f"\n{website}"
    subject=f"Collaboration inquiry from {brand} — {product_name}"
    body=(
        f"Hi {name},\n\n"
        f"I found your public Instagram profile while researching {record.get('category','')} creators in {record.get('country','')}. "
        f"{intro}{company_note}.\n\n{product_line}\n\n{offer_line}\n\n"
        f"Best regards,\n{contact or brand}"
    )
    if website:
        body+=f"\n{website}"
    email=record.get("public_email","")
    mailto=""
    if email:
        mailto=f"mailto:{email}?"+urllib.parse.urlencode({"subject":subject,"body":body})
    return {
        **record,
        "dm_draft":dm[:1600],
        "email_subject":subject[:180],
        "email_body":body[:2400],
        "email_compose_url":mailto,
        "outreach_generation_status":"초안 생성완료",
    }


def collect_influencers(config: InfluencerConfig, provider, sender: dict | None=None,
                        product: dict | None=None, progress=None) -> dict:
    started=time.monotonic()
    sender=sender or {}; product=product or {}
    queries=build_queries(config)
    pool={}; rejected={}; errors=[]; raw_results=0
    for index,query in enumerate(queries,1):
        if progress:
            progress(index-1,len(queries),f"Instagram 공개 검색 {index}/{len(queries)}")
        try:
            results=provider.search(query,max_results=20,country="",minimal=False)
        except Exception as exc:
            errors.append(f"{query} · {type(exc).__name__}: {str(exc)[:240]}")
            continue
        raw_results+=len(results)
        for item in results:
            candidate,reason=_candidate_from_result(item,query,config)
            if not candidate:
                rejected[reason]=rejected.get(reason,0)+1
                continue
            handle=candidate["handle"]
            existing=pool.get(handle)
            if not existing or candidate["score"]>existing["score"]:
                pool[handle]=candidate
            elif candidate.get("public_email") and not existing.get("public_email"):
                existing.update({k:candidate[k] for k in ("public_email","email_status")})
        if len(pool)>=config.target_count*2:
            break
        time.sleep(max(0,float(config.request_delay)))
    ranked=sorted(pool.values(),key=lambda row:(row["score"],row.get("followers") if isinstance(row.get("followers"),int) else -1),reverse=True)
    records=[]
    for rank,row in enumerate(ranked[:config.target_count],1):
        records.append(generate_outreach({**row,"rank":rank},sender,product))
    if progress:
        progress(len(queries),len(queries),"Instagram 후보 정리 완료")
    summary={
        "records":len(records),
        "tier_a":sum(r["grade"]=="A" for r in records),
        "tier_b":sum(r["grade"]=="B" for r in records),
        "tier_c":sum(r["grade"]=="C" for r in records),
        "public_emails":sum(bool(r.get("public_email")) for r in records),
        "dm_drafts":sum(r.get("outreach_generation_status")=="초안 생성완료" for r in records),
        "raw_results":raw_results,
        "unique_profiles":len(pool),
        "elapsed_seconds":round(time.monotonic()-started,2),
    }
    return {
        "schema_version":SCHEMA_VERSION,
        "app_version":APP_VERSION,
        "mode":"instagram_influencer",
        "config":asdict(config),
        "records":records,
        "summary":summary,
        "queries":queries,
        "rejected_reasons":rejected,
        "api_response_log":list(getattr(provider,"response_log",[])),
        "errors":errors,
        "sender_profile":sender,
        "product_profile":product,
        "safety":{
            "instagram_login_used":False,
            "follower_list_collected":False,
            "email_guessed":False,
            "automatic_dm_sent":False,
            "automatic_email_sent":False,
        },
    }

