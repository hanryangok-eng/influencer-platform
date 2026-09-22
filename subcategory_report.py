"""Observed search coverage and product evidence, not inferred buyer intent."""
from product_matching import aliases, phrase_present, subcategory_products


def build_subcategory_summary(cfg, payload):
    import buyer_core as core
    from delivery_policy import approval_rows
    approved=approval_rows(payload.get('records',[]),include_external=cfg.include_external_sendable)
    groups=cfg.industry_groups or [dict(major=cfg.major_industry,subcategories=cfg.subcategories,
                                      products=[p.strip() for p in cfg.product.split(',') if p.strip()])]
    countries=cfg.countries or [cfg.region]
    stats=payload.get('discovery_summary',{}).get('keyword_stats_by_country',{})
    result=[]
    for g in groups:
        mapping=subcategory_products(g['major'],g['subcategories'],g['products'])
        unassigned=[p for p in g['products'] if not any(p in ps for ps in mapping.values())]
        if unassigned: mapping['직접입력·세부업종 미지정']=unassigned
        for sub,products in mapping.items():
            for country in countries:
                keywords={k:v for k,v in stats.get(country,{}).items()
                          if any(phrase_present(k,a) for p in products for a in aliases(p,country))}
                searched=[p for p in products if any(v.get('calls',0)>0 and any(phrase_present(k,a) for a in aliases(p,country))
                                                    for k,v in keywords.items())]
                matched=[]
                for record in payload.get('records',[]):
                    assessment=next((a for a in record.get('industry_assessments',[])
                                     if a.get('major')==g['major'] and a.get('target_country')==country
                                     and any(p in a.get('product_hits',[]) for p in products)),None)
                    if assessment:
                        # A merged company's strongest other-country grade must not
                        # overwrite this country's specific assessment.
                        matched.append(dict(record,priority=assessment.get('priority',record.get('priority')),
                                            quality_decision=assessment.get('quality_decision',record.get('quality_decision')),
                                            target_country=country))
                matching_ids={r.get('company_id') for r in matched if r.get('priority') in {'A','B'} and r.get('quality_decision')=='적합'}
                approved_sub=[r for r in approved if r.get('company_id') in matching_ids and r.get('target_country')==country]
                result.append(dict(주업종=g['major'],세부업종=sub,국가=country,
                    선택제품수=len(products),검색실행제품수=len(searched),
                    검색호출수=sum(v.get('calls',0) for v in keywords.values()),
                    제품표현확인기업=len(matched),메일링대상기업=len({r.get('company_id') for r in approved_sub}),
                    수집이메일=len(approved_sub),
                    검색상태='선택 제품 없음' if not products else '미검색 제품 있음' if len(searched)<len(products)
                             else '제품 근거 미확보' if not matched else '제품 근거 확보'))
    return result
