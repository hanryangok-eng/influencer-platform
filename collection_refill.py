"""Bounded feedback loop: search one unused query, analyze only new domains, reassess."""
import math
import time


def refill_batches(cfg, provider, records, candidates, stats, progress=None):
    import buyer_core as core
    from delivery_policy import approval_rows
    countries=cfg.countries or [cfg.region]
    # No unbounded loop in full-search mode. This is a query limit, not paid credits.
    cap=cfg.max_search_queries or max(stats.get('queries',0),len(countries)*(len(cfg.keywords)*core.search_profile_count(cfg.search_mode)+18))
    per_country_cap=math.ceil(cap/len(countries))
    calls=stats.setdefault('queries_by_country',{})
    seen_queries={r.get('query','') for r in stats.get('api_response_log',[])}
    seen_queries.update(stats.get('executed_refill_queries',[]))
    seen={(core.registrable_domain(c.get('url','')),c.get('target_country') or cfg.region) for c in candidates}
    seen.update((core.registrable_domain(r.website),r.target_country) for r in records)
    seen.update(tuple(key.split('|',1)) for key in stats.get('completed_domain_keys',[]) if '|' in key)
    excluded=' '.join(f'-"{t}"' if ' ' in t else f'-{t}' for t in core.QUERY_EXCLUDE_TERMS)
    tasks=[]
    from product_matching import VI, subcategory_products
    products=[p.strip() for p in cfg.product.split(',') if p.strip()]
    sub_products=subcategory_products(cfg.major_industry,cfg.subcategories,products)
    counts={s:sum(any(p in a.get('product_hits',[]) for p in ps)
                  for r in records for a in r.industry_assessments if a.get('major')==cfg.major_industry)
            for s,ps in sub_products.items()}
    def evidence_count(product):
        return min((counts[s] for s,ps in sub_products.items() if product in ps),default=0)
    products.sort(key=evidence_count)
    # The base round has already covered English products. Spend the next calls on
    # local product phrases in under-evidenced subcategories, before repeating profiles.
    for product in products:
        for country in countries:
            if country=='Vietnam' and VI.get(product.casefold()):
                keyword=f'{VI[product.casefold()][0]} nhà phân phối'
                tasks.append((country,keyword,f'{country} {keyword} {excluded}'))
    profiles=core.SEARCH_PROFILES.get(cfg.search_mode,core.SEARCH_PROFILES['균형'])
    for i,keyword in enumerate(cfg.keywords):
        for country in countries:
            tasks.append((country,keyword,core.build_search_query(country,keyword,profiles[i%len(profiles)],excluded)))
    for profile in profiles:
        for keyword in cfg.keywords:
            for country in countries:
                tasks.append((country,keyword,core.build_search_query(country,keyword,profile,excluded)))
    # Local buyer terms stay specific to the selected product. No beauty-only fallback.
    for product in products:
        for country in countries:
            local=' '.join(core.country_meta(country).get('local_buyer',[])[:2]) or 'importer distributor'
            keyword=f'{product} {local}'
            tasks.append((country,keyword,f'{country} {keyword} {excluded}'))
    stats.setdefault('refill_queries',0)
    stats.setdefault('refill_log',[])
    for country,keyword,query in tasks:
        subset=[r for r in records if r.target_country==country]
        count=len({core.registrable_domain(r.website) for r in subset})
        addresses=len(approval_rows(records,include_external=cfg.include_external_sendable))
        country_addresses=sum(r.get('target_country')==country for r in approval_rows(records,include_external=cfg.include_external_sendable))
        qualified=sum(r.quality_decision=='적합' for r in subset)
        qualified_target=math.ceil((cfg.qualified_candidate_target or cfg.target_per_country*len(countries))/len(countries))
        if count>=math.ceil(cfg.candidate_limit/len(countries)) and country_addresses>=cfg.target_per_country and qualified>=qualified_target and addresses>=cfg.verified_email_target:
            continue
        if stats.get('queries',0)>=cap or stats.get('stop_reason'):
            break
        if calls.get(country,0)>=per_country_cap or query in seen_queries:
            continue
        seen_queries.add(query)
        stats.setdefault('executed_refill_queries',[]).append(query)
        stats['queries']=stats.get('queries',0)+1
        calls[country]=calls.get(country,0)+1
        stats['refill_queries']+=1
        if progress: progress(0,1,f'{country} 최종 부족분 보충 · 분석 {count}개 · 이메일 {addresses}개')
        stat=stats.setdefault('keyword_stats_by_country',{}).setdefault(country,{}).setdefault(keyword,
            dict(calls=0,raw_results=0,accepted_results=0,rejected_results=0))
        stat['calls']+=1
        try:
            items=provider.search(query,max_results=20,country='',minimal=False)
        except core.SearchPlanLimitError:
            stats['query_errors']=stats.get('query_errors',0)+1
            stats['stop_reason']='검색 공급자 사용 한도 초과'
            yield []
            break
        except Exception as exc:
            stats['query_errors']=stats.get('query_errors',0)+1
            stats.setdefault('query_error_details',[]).append(f'{country} · 보충검색 · {type(exc).__name__}')
            yield []
            continue
        stat['raw_results']+=len(items)
        stats['raw_results']=stats.get('raw_results',0)+len(items)
        batch=[]
        for item in items:
            ok,score,reason=core.candidate_prefilter(item,country,cfg,'자동보충')
            if not ok:
                stat['rejected_results']+=1
                stats['prefilter_rejected']=stats.get('prefilter_rejected',0)+1
                reasons=stats.setdefault('prefilter_reasons',{})
                reasons[reason]=reasons.get(reason,0)+1
                continue
            stat['accepted_results']+=1
            url=str(item.get('url') or '')
            key=(core.registrable_domain(url),country)
            if key in seen:
                stats['deduplicated']=stats.get('deduplicated',0)+1
                continue
            seen.add(key)
            batch.append(dict(url=url,root_url=core.root_url(url),keyword=keyword,query=query,
                description=str(item.get('content') or ''),title=str(item.get('title') or ''),
                target_country=country,discovery_source='최종부족분 보충',discovery_url=url,
                candidate_score=score,alternate_urls=[url]))
        stats['refill_log'].append(dict(country=country,keyword=keyword,new_domains=len(batch),
            analyzed_before=count,emails_before=addresses))
        # Checkpoint needs an up-to-date ledger, including failed and empty searches.
        prior=stats.get('_prior_api_log',[])
        stats['api_response_log']=prior+list(provider.response_log)
        time.sleep(cfg.request_delay)
        yield sorted(batch,key=lambda x:x['candidate_score'],reverse=True)
    stats['refill_stop_reason']='목표 충족 또는 실행 가능한 검색어·예산 소진'
