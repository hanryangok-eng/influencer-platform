from __future__ import annotations

import re


def _clean(value: object, limit: int = 240) -> str:
    return " ".join(str(value or "").split())[:limit]


def _features(product: dict) -> list[str]:
    raw = product.get("features") or product.get("differentiator") or ""
    if isinstance(raw, (list, tuple)):
        values = [str(item).strip(" •-\t") for item in raw]
    else:
        values = re.split(r"[\n,;|]+", str(raw))
        values = [item.strip(" •-\t") for item in values]
    return [item for item in values if item][:3]


def generate_cl(record: dict, sender: dict, product: dict) -> dict:
    """Generate an editable, fact-only first-contact CL.

    MOQ, price, lead time, certifications, efficacy, origin and other claims
    are omitted unless explicitly supplied by the customer. This is an interest
    check, not a quotation.
    """
    buyer = _clean(record.get("company_name"), 160) or "your company"
    recipient = _clean(record.get("contact_name"), 100) or "Business Development Team"
    country = _clean(record.get("verified_country") or record.get("target_country"), 80)
    buyer_type = _clean(record.get("buyer_type"), 100)
    buyer_basis = buyer_type or _clean(record.get("business_description"), 180)
    company = _clean(sender.get("company_name"), 160) or "our company"
    sender_name = _clean(sender.get("contact_name"), 100)
    sender_title = _clean(sender.get("contact_title"), 100)
    email = _clean(sender.get("email"), 160)
    website = _clean(sender.get("website"), 240)
    product_name = _clean(product.get("product_name"), 160) or "our product"
    category = _clean(product.get("category"), 120)
    description = _clean(product.get("description"), 500)
    differentiator = _clean(product.get("differentiator"), 300)
    catalog = _clean(product.get("catalog_url"), 240)
    features = _features(product)
    subject_category = category or "product"

    personalization = f"We noticed that {buyer} works with {buyer_basis}." if buyer_basis else f"We came across {buyer}."
    if country:
        personalization = personalization.rstrip(".") + f" in {country}."

    lines = [
        f"Hello {recipient},", "", personalization, "",
        f"We are {company}. We would like to introduce {product_name}, a {subject_category} product.",
    ]
    if description:
        lines += ["", description]
    if differentiator or features:
        lines += ["", "The product information provided to us highlights:"]
        for item in features:
            lines.append(f"- {item}")
        if differentiator and not features:
            lines.append(f"- {differentiator}")
    if catalog:
        lines += ["", f"Product information: {catalog}"]
    lines += [
        "", "We believe this product may be relevant to your portfolio. Would you be open to receiving a short product introduction or catalog for your review?", "",
        "Best regards,", sender_name, sender_title, company, website, email, "",
        "If this is not relevant to your business, please let us know and we will not follow up.",
    ]
    body_en = "\n".join(lines).strip()

    ko_lines = [
        f"수신: {buyer} / {recipient}", "", "개인화 적용 문장:", personalization, "",
        f"{company}가 {product_name}을 소개하고 제품소개자료 수신 의향을 묻는 첫 연락 초안입니다.",
    ]
    if description:
        ko_lines += ["제품 설명(입력값):", description]
    if differentiator or features:
        ko_lines += ["핵심 강점(입력값):", *(f"- {item}" for item in (features or [differentiator]))]
    ko_lines += ["", "검수 메모: 발송 전 수신자·개인화 근거·제품 사실을 확인하세요."]

    return {
        "company_id": record.get("company_id", ""), "buyer_company": buyer, "recipient": recipient,
        "recipient_email": record.get("contact_email") or record.get("company_email") or "",
        "subject_en": f"Introducing {product_name} – {subject_category} for {buyer}",
        "body_en": body_en, "body_ko": "\n".join(ko_lines).strip(),
        "personalization_sentence": personalization, "personalization_evidence": record.get("company_source_url", ""),
        "attachment_name": _clean(product.get("attachment_name"), 160), "generation_status": "초안",
        "review_status": "검수대기", "edit_note": "",
    }


def generate_cl_batch(records: list[dict], sender: dict, product: dict) -> list[dict]:
    return [generate_cl(record, sender, product) for record in records if record.get("company_email") or record.get("contact_email")]
