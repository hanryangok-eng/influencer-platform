"""Independent industry judgments, campaign-wide query budget and merged export."""
from copy import deepcopy
from dataclasses import asdict, replace
import time
import buyer_core as core
from version import SCHEMA_VERSION
from industry_catalog import allocate, validate_groups


def collect_buyers(cfg, tavily_key, hunter_key="", progress=None, checkpoint=None,
                   resume_state=None, brave_key=""):
    if not cfg.industry_groups:
        return core.collect_buyers(cfg,tavily_key,hunter_key,progress,checkpoint,resume_state,brave_key)
    validate_groups(cfg.industry_groups)
    started=time.monotonic()
    state=deepcopy(resume_state or {})
    results=state.get("group_results",{})
    n=len(cfg.industry_groups); countries=cfg.countries or [cfg.region]
    candidate_goals=allocate(cfg.candidate_limit,n)
    email_goals=allocate(cfg.target_per_country,n)
    if min(candidate_goals)<1 or min(email_goals)<1:
        raise ValueError("업종별 기본 조사를 위해 국가별 이메일 목표와 전체 조사 목표를 선택 업종 수 이상으로 설정하세요.")
    budget=cfg.max_search_queries or sum(len(g["keywords"])*core.search_profile_count(cfg.search_mode)+18 for g in cfg.industry_groups)*len(countries)
    children=[]
    for i,g in enumerate(cfg.industry_groups):
        children.append(replace(cfg,industry=g["industry"],industry_groups=[],major_industry=g["major"],
            subcategories=g["subcategories"],product=", ".join(g["products"]),keywords=g["keywords"],
            base_keyword_count=g["base_keyword_count"],candidate_limit=candidate_goals[i],
            target_per_country=email_goals[i],verified_email_target=email_goals[i]*len(countries),
            qualified_candidate_target=email_goals[i]*len(countries),refill_enabled=False,
            max_search_queries=max(1,g["base_keyword_count"])*len(countries)))
    def used():
        return sum(r.get("discovery_summary",{}).get("queries",0) for r in results.values())
    def persist(active=None, child_cfg=None, child_state=None):
        if checkpoint:
            checkpoint(dict(schema_version=SCHEMA_VERSION,config=asdict(cfg),group_results=results,
                active_group=active,active_config=asdict(child_cfg) if child_cfg else None,
                active_state=child_state,progress_done=len(results),progress_total=n))
    def run(i, child, saved=None):
        def report(done,total,message):
            if progress: progress(done,total,children[i].major_industry+" · "+message)
        persist(i,child,saved)
        previous_elapsed=results.get(str(i),{}).get("summary",{}).get("elapsed_seconds",0)
        result=core.collect_buyers(child,tavily_key,hunter_key,report,
            lambda s:persist(i,child,s),saved,brave_key,shared_cache=True)
        result["summary"]["elapsed_seconds"]+=previous_elapsed
        results[str(i)]=result
        persist()
    core._RUN_PAGE_CACHE={}; core._RUN_PAGE_LOCKS={}
    try:
        active=state.get("active_group")
        if active is not None:
            run(active,core.CollectionConfig(**state["active_config"]),state.get("active_state"))
        # Every selected industry receives its base round before anyone uses the reserve.
        for i,child in enumerate(children):
            if str(i) in results: continue
            remaining=budget-used()
            if remaining<=0: break
            run(i,replace(child,max_search_queries=min(child.max_search_queries,remaining)))
        exhausted=set()
        while used()<budget and len(results)==n:
            merged=core.deduplicate_records([core.BuyerRecord(**r) for p in results.values() for r in p["records"]])
            from delivery_policy import approval_rows
            emails=approval_rows(merged,include_external=cfg.include_external_sendable)
            country_shortfall=max(max(0,cfg.target_per_country-sum(r.get('target_country')==country for r in emails)) for country in countries)
            qualified=sum(r.quality_decision=='적합' for r in merged)
            if len(merged)>=cfg.candidate_limit and len(emails)>=cfg.verified_email_target and not country_shortfall and qualified>=(cfg.qualified_candidate_target or cfg.target_per_country*len(countries)): break
            choices=[i for i in range(n) if i not in exhausted and results[str(i)].get("search_status")=="ok"]
            if not choices: break
            i=max(choices,key=lambda j:results[str(j)]["summary"]["sendable"]/max(1,results[str(j)]["discovery_summary"].get("queries",0)))
            previous=results[str(i)]
            old_calls=previous["discovery_summary"].get("queries",0)
            grant=min(budget-used(),3*len(countries))
            child=replace(children[i],refill_enabled=True,max_search_queries=old_calls+grant,
                candidate_limit=previous["summary"]["records"]+max(0,cfg.candidate_limit-len(merged)),
                target_per_country=children[i].target_per_country+max(country_shortfall,(cfg.verified_email_target-len(emails)+len(countries)-1)//len(countries)))
            saved={k:deepcopy(previous[k]) for k in ("records","access_holds","errors","discovery_summary")}
            run(i,child,saved)
            if results[str(i)]["discovery_summary"].get("queries",0)==old_calls:
                exhausted.add(i)
        stats={"queries":0,"api_response_log":[],"queries_by_country":{},"keyword_stats_by_country":{}}
        def add(dst,src):
            for k,v in src.items():
                if isinstance(v,bool): continue
                if isinstance(v,(int,float)): dst[k]=dst.get(k,0)+v
                elif isinstance(v,list): dst.setdefault(k,[]).extend(deepcopy(v))
                elif isinstance(v,dict): add(dst.setdefault(k,{}),v)
        for p in results.values():
            add(stats,{k:v for k,v in p["discovery_summary"].items() if k not in ("diagnostic","_prior_api_log")})
        stats["diagnostic"]=next((p["discovery_summary"].get("diagnostic",{}) for p in results.values() if p["search_status"]=="ok"),{})
        stats["campaign_query_budget"]=budget
        statuses=[p["search_status"] for p in results.values()]
        status="ok" if "ok" in statuses else (statuses[0] if statuses else "empty_after_search")
        records=[core.BuyerRecord(**r) for p in results.values() for r in p["records"]]
        holds=list({(r.get("website") or r.get("url"),r.get("target_country")):r for p in results.values() for r in p.get("access_holds",[])}.values())
        errors=[e for p in results.values() for e in p.get("errors",[])]
        payload=core.summarize_collection(cfg,records,holds,errors,stats,status,cfg.search_provider,started,bool(resume_state))
        payload["industry_summary"]=[dict(major=children[int(i)].major_industry,
            subcategories=children[int(i)].subcategories,initial_candidate_target=candidate_goals[int(i)],
            initial_email_target=email_goals[int(i)]*len(countries),search_status=p["search_status"],
            queries=p["discovery_summary"].get("queries",0),**p["summary"]) for i,p in results.items()]
        payload["group_results"]=results
        from subcategory_report import build_subcategory_summary
        payload["subcategory_summary"]=build_subcategory_summary(cfg,payload)
        payload["partial_industry_failure"]=len(results)<n or any(s!="ok" for s in statuses)
        return payload
    finally:
        core._RUN_PAGE_CACHE=None; core._RUN_PAGE_LOCKS={}
