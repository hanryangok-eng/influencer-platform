import os
from datetime import datetime

import streamlit as st

from buyer_core import CollectionConfig, check_brave_connection, check_tavily_connection, email_is_sendable, mailing_candidate, registrable_domain, search_profile_count
from delivery_policy import approval_rows, approval_csv
from cl_generator import generate_cl_batch
from country_catalog import COUNTRIES, WORLD_BATCHES, continents, countries_by_continent, country_meta, country_name_ko
from excel_exporter import build_excel
from industry_catalog import CATALOG, make_group, product_options
from campaign_runner import collect_buyers
from job_store import list_jobs, load_checkpoint, load_result, mark_failed, new_job, save_checkpoint, save_result
from influencer_app import render_influencer_app
from version import APP_VERSION, SCHEMA_VERSION

st.set_page_config(page_title="GLOEUM — Connect Your Product to the World", page_icon="🌏", layout="wide")

st.markdown("""
<style>
.block-container {max-width: 1180px; padding-top: 2rem;}
.stButton button {background:#17365D;color:white;border-radius:8px;font-weight:700;}
.metric-card {background:#F4F7FB;border:1px solid #D9E2F3;border-radius:10px;padding:14px;}
</style>
""", unsafe_allow_html=True)

st.title("GLOEUM — Connect Your Product to the World")
st.caption(f"글로이음 · v{APP_VERSION} · 기업 바이어와 Instagram 인플루언서 발굴")

collection_mode=st.radio(
    "검색 모드",
    ["기업 바이어", "Instagram 인플루언서"],
    horizontal=True,
    help="기업 바이어 모드는 기존 기능을 그대로 사용하고, Instagram 모드는 공개 검색결과에서 크리에이터 후보를 찾습니다.",
)
if collection_mode=="Instagram 인플루언서":
    render_influencer_app()
    st.stop()

# 수집 실행 상태는 브라우저 세션에만 보관합니다. 완료 후에는 결과를
# 다운로드할 시간을 보장하기 위해 새 수집 준비를 누르기 전까지 시작을 잠급니다.
if "collection_ui_state" not in st.session_state:
    st.session_state.collection_ui_state = "ready"
collection_ui_state = st.session_state.collection_ui_state

def country_label(country: str) -> str:
    code=country_meta(country).get("tld","").upper()
    return f"{country_name_ko(country)} [{code}] · {country}" if code else f"{country_name_ko(country)} · {country}"

with st.sidebar:
    st.header("API 연결")
    search_provider = st.selectbox("검색엔진",["Brave (권장)","Brave → Tavily 자동전환","Tavily"],index=0,help="Brave를 기본으로 사용합니다. 자동전환은 Brave가 실패하거나 빈 결과일 때 Tavily를 사용합니다.")
    brave_key = st.text_input("Brave Search API Key", value=os.getenv("BRAVE_SEARCH_API_KEY", ""), type="password")
    tavily_key = st.text_input("Tavily API Key", value=os.getenv("TAVILY_API_KEY", ""), type="password")
    hunter_key = st.text_input("Hunter API Key", value=os.getenv("HUNTER_API_KEY", ""), type="password")
    st.caption("키는 브라우저 세션에서만 사용하며 결과 파일에 저장하지 않습니다.")
    st.caption("Brave를 기본 검색으로 사용하며 Tavily는 선택형 보조엔진으로 유지합니다.")
    use_hunter = st.toggle("Hunter 이메일 보강", value=bool(hunter_key))
    verify_hunter = st.toggle("Hunter 이메일 검증", value=bool(hunter_key))
    if st.button("선택 검색엔진 연결 테스트",use_container_width=True):
        test_brave=search_provider=="Brave (권장)" or (search_provider.startswith("Brave →") and bool(brave_key))
        test_key=brave_key if test_brave else tavily_key
        test_name="Brave" if test_brave else "Tavily"
        if not test_key:
            st.error(f"{test_name} API Key를 먼저 입력하세요.")
        else:
            check=check_brave_connection(brave_key) if test_brave else check_tavily_connection(tavily_key)
            if check.get("ok"):
                st.success(f"연결 정상 · 테스트 결과 {check.get('result_count',0)}개")
            else:
                st.error(f"연결 실패 · {check.get('message','빈 응답')}")
            st.caption(f"HTTP {check.get('http_status','-')} · 요청 ID {check.get('request_id') or '-'}")

col1, col2 = st.columns([1, 1])
with col1:
    region_mode = st.selectbox("지역 선택 방식", ["국가 직접선택", "대륙에서 선택", "전 세계 배치"])
    if region_mode=="국가 직접선택":
        countries=st.multiselect("수집 국가 · 1회 최대 5개",list(COUNTRIES),default=[],max_selections=5,format_func=country_label,placeholder="국가를 선택하세요",key="country_direct_v2210")
    elif region_mode=="대륙에서 선택":
        selected_continent=st.selectbox("대륙",continents())
        countries=st.multiselect("수집 국가 · 1회 최대 5개",countries_by_continent(selected_continent),default=[],max_selections=5,format_func=country_label,placeholder="국가를 선택하세요",key="country_continent_v2210")
    else:
        batch_name=st.selectbox("전 세계 수집 배치",list(WORLD_BATCHES))
        countries=WORLD_BATCHES[batch_name]
        st.caption("선택 배치: "+", ".join(country_name_ko(country) for country in countries))
    custom_country = st.text_input("목록에 없는 국가 직접입력 · 1개",value="",help="영문 국가명을 입력하면 선택 국가 대신 해당 국가를 조사합니다.")
    if custom_country.strip(): countries=[custom_country.strip()]
    if countries: st.code("실제 검색국가: "+", ".join(countries),language=None)
    collection_purpose = st.selectbox("1단계 · 수집 목적", ["수출 바이어 발굴", "국내 행사 바이어 모집"])
    selected_majors = [st.selectbox("2단계 · 주 업종 선택", list(CATALOG), key="major_v2236")]
    industry_groups = []
    group_errors = []
    for major in selected_majors:
        with st.expander(major + " · 세부업종과 제품", expanded=True):
            subs = st.multiselect("3단계 · 세부업종 복수선택", list(CATALOG[major][1]),
                default=[next(iter(CATALOG[major][1]))], key="subs_"+major)
            options = product_options(major, subs)
            # Round-robin defaults give every selected subcategory product coverage.
            defaults = list(dict.fromkeys(p for row in zip(*[list(CATALOG[major][1][s]) for s in subs]) for p in row))[:10] if subs else []
            product_key = "products_"+major
            signature = tuple(subs)
            if st.session_state.get("product_signature_"+major) != signature or product_key not in st.session_state:
                st.session_state[product_key] = defaults
                st.session_state["product_signature_"+major] = signature
            chosen = st.multiselect("4단계 · 자동 추천 제품 · 수정 가능", list(options),
                key=product_key, max_selections=10)
            extra = st.text_input("추가 제품 영어 입력 · 쉼표 구분", key="extra_"+major)
            products = list(dict.fromkeys([options[p] for p in chosen] + [p.strip() for p in extra.split(",") if p.strip()]))
            try:
                group = make_group(major, subs, products)
                industry_groups.append(group)
                st.caption("실제 검색 제품: " + ", ".join(products))
            except ValueError as exc:
                group_errors.append(str(exc))
                st.warning(str(exc))
    selected_industry = " | ".join(selected_majors)
    product_terms = list(dict.fromkeys(p for g in industry_groups for p in g["products"]))
    product_search = ", ".join(product_terms)
    target_per_country = st.select_slider("국가별 수집 이메일 목표", options=[5, 10, 20, 30], value=5)
    total_target=target_per_country*len(countries)
    candidate_target = st.number_input(
        "전체 후보기업 조사 목표",
        min_value=5,
        max_value=500,
        value=max(20,total_target*4),
        step=5,
        help="선택한 주 업종의 전체 조사 목표입니다. 이메일 목표와 별개이며, 마지막 검색 묶음의 결과는 목표보다 많아도 보존합니다.",
    )
with col2:
    st.markdown("**5단계 · 업종별 자동생성 키워드**")
    for group in industry_groups:
        major = group["major"]
        key = "keywords_"+major
        signature = tuple(group["products"])
        if st.session_state.get("keyword_signature_"+major) != signature or key not in st.session_state:
            st.session_state[key] = "\n".join(group["keywords"])
            st.session_state["keyword_signature_"+major] = signature
        text = st.text_area(major, key=key, height=150)
        group["keywords"] = list(dict.fromkeys(line.strip() for line in text.splitlines() if line.strip()))
        group["base_keyword_count"] = min(len(group["keywords"]), group["base_keyword_count"])
        if not group["keywords"]:
            group_errors.append(major + ": 검색어를 1개 이상 입력하세요.")
    entered_keywords = list(dict.fromkeys(k for g in industry_groups for k in g["keywords"]))
    keywords_text = "\n".join(entered_keywords)
    base_keyword_count = sum(g["base_keyword_count"] for g in industry_groups)
    saving_budget_per_country = sum(max(1,g["base_keyword_count"])+3 for g in industry_groups)
    st.caption("선택 제품의 기본 검색을 먼저 실행합니다. 수량이 부족하면 제품 근거가 적은 세부업종부터 남은 예산으로 보충합니다. 목표는 세부업종별 할당량이 아닌 전체 합계입니다.")
    search_strategy = st.selectbox("검색 조합 운영",["적응형 최적화", "수동 입력 그대로"],help="적응형은 제품·구매자역할·현지어를 분산 배치해 적은 API 호출로 발송 승인 후보 바이어 확보율을 높입니다.")
    st.caption("제조·생산공장, 리드 플랫폼, 미디어 등은 내부 규칙으로 자동 판정합니다. 클리닉·살롱·스파는 잠재 바이어로 포함합니다.")
    search_mode = st.selectbox(
        "검색 범위",
        ["정확도 우선", "균형", "최대수집"],
        index=1,
        help="정확도 우선은 공식기업 검색, 균형은 현지시장 검색 추가, 최대수집은 전시회·협회 검색까지 추가합니다.",
    )
    api_usage_mode=st.selectbox(
        "API 사용 모드",
        ["개발 검증 · 캐시만",f"절약수집 · 국가당 최대 {saving_budget_per_country}회","전체 실검색"],
        index=1,
        help="절약수집은 기본 키워드를 먼저 검색하고 중복 제거한 사전 후보가 부족할 때만 추가 검색합니다. 전체 실검색은 여유 후보와 추가 검색 조합까지 탐색합니다.",
    )
    if api_usage_mode=="개발 검증 · 캐시만":
        st.warning("캐시만 모드에서는 저장된 동일 검색결과가 없으면 실제 검색을 실행하지 않습니다.")
    fallback_estimate={"정확도 우선":12,"균형":18,"최대수집":25}[search_mode]
    estimated_queries=len(countries)*sum(len(g["keywords"])*search_profile_count(search_mode)+fallback_estimate for g in industry_groups)
    effective_queries=0 if api_usage_mode.startswith("개발") else min(saving_budget_per_country*len(countries),estimated_queries) if api_usage_mode.startswith("절약") else estimated_queries
    st.info(f"선택 국가 {len(countries)}개 · 세부제품 {len(product_terms)}개 · 전체 조사 목표 {int(candidate_target)}개 · 적합후보 목표 {total_target}개 · 이메일 목표 {total_target}개 · 검색어 실행 예산 최대 {effective_queries}회")

st.subheader("CL 발신기업·제품자료")
with st.expander("CL 자동생성 정보 입력", expanded=False):
    a1,a2=st.columns(2)
    with a1:
        sender_company=st.text_input("영문 회사명")
        sender_contact=st.text_input("영문 담당자명")
        sender_title=st.text_input("영문 직책")
        sender_email=st.text_input("회신 이메일")
        sender_website=st.text_input("영문 홈페이지")
    with a2:
        cl_product_name=st.text_input("영문 제품명")
        cl_category=st.text_input("영문 제품 카테고리", help="예: skincare product, hair care product")
        cl_description=st.text_area("제품 설명")
        cl_differentiator=st.text_area("핵심 차별점")
        cl_origin=st.text_input("원산지",value="Republic of Korea")
        cl_certifications=st.text_input("인증·시험자료")
        cl_moq=st.text_input("MOQ (첫 CL에는 미포함)")
        cl_lead_time=st.text_input("납기 (첫 CL에는 미포함)")
        cl_catalog=st.text_input("카탈로그 또는 제품페이지 URL")

with st.expander("세부 설정"):
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        max_pages = st.number_input("회사별 최대 탐색 페이지", min_value=2, max_value=10, value=4)
    with c2:
        request_delay = st.number_input("요청 간격(초)", min_value=0.2, max_value=3.0, value=0.35, step=0.05)
    with c3:
        include_external = st.toggle("외부확인 이메일을 승인 후보에 포함", value=True)
    with c4:
        include_cross_domain = st.toggle(
            "교차도메인 이메일도 전체 목록에 보존",
            value=True,
            disabled=True,
            help="주소는 보존합니다. 소유관계가 불명확하면 승인 후보 CSV에는 넣지 않고 추가 검토로 분리합니다.",
        )
    with c5:
        worker_count = st.number_input("동시 조사 기업",min_value=1,max_value=12,value=8,help="무료 서버는 5~8개, 유료 서버는 8~12개를 권장합니다.")

st.subheader("최근 수집 결과")
jobs=list_jobs(20)
completed_jobs=[row for row in jobs if row.get("status")=="completed"]
recoverable_jobs=[row for row in jobs if row.get("status") in {"running","interrupted"}]
continue_completed_clicked=False; continue_completed_job_id=""
if completed_jobs:
    completed_labels={f"{row.get('updated_at','')[:16]} · {row.get('records',0)}개 · 발송 {row.get('sendable',0)}개 · {row['job_id']}":row for row in completed_jobs}
    selected_completed=st.selectbox("저장된 완료 결과",list(completed_labels),key="completed_job")
    saved=completed_labels[selected_completed]
    saved_payload,saved_excel=load_result(saved["job_id"])
    if saved_excel:
        st.download_button("저장된 Excel 다시 다운로드",saved_excel,file_name=saved.get("filename","GLOEUM_해외바이어.xlsx"),mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",use_container_width=True,on_click="ignore")
    if saved_payload:
        st.download_button('저장 결과의 발송 승인 후보 CSV',approval_csv(saved_payload.get('records',[]),
            saved_payload.get('config',{}).get('include_external_sendable',True)),
            file_name='GLOEUM_발송승인후보.csv',mime='text/csv',on_click='ignore',key='saved_approval_csv')
    continue_completed_clicked=st.button("이 결과의 부족분만 이어서 수집",use_container_width=True,help="기존 업체는 다시 조사하지 않고 저장된 검색 캐시와 미실행 검색어를 이용해 부족분을 보충합니다.")
    continue_completed_job_id=saved["job_id"]
else:
    st.caption("아직 저장된 완료 결과가 없습니다.")
resume_clicked=False; resume_job_id=""
if recoverable_jobs:
    recover_labels={f"{row.get('updated_at','')[:16]} · 진행 {row.get('progress_done',0)}/{row.get('progress_total',0)} · {row['job_id']}":row for row in recoverable_jobs}
    selected_recover=st.selectbox("중단·진행 작업",list(recover_labels),key="recover_job")
    resume_job_id=recover_labels[selected_recover]["job_id"]
    resume_clicked=st.button("마지막 저장지점부터 이어서 수집",use_container_width=True)

keywords = entered_keywords
exclude_keywords = []

state_col1, state_col2 = st.columns([3, 1])
with state_col1:
    if collection_ui_state == "running":
        st.info("수집 중입니다. 현재 실행이 끝날 때까지 수집 시작 버튼이 잠깁니다.")
    elif collection_ui_state == "completed":
        st.success("수집 완료 · 결과를 다운로드한 뒤 새로고침을 누르면 다음 수집을 시작할 수 있습니다.")
    elif collection_ui_state == "error":
        st.warning("수집이 중단되었습니다. 설정을 확인한 뒤 새로고침으로 다시 준비할 수 있습니다.")
with state_col2:
    refresh_clicked = st.button(
        "새로고침 · 새 수집 준비",
        use_container_width=True,
        disabled=collection_ui_state == "running",
        help="현재 화면의 실행 잠금을 해제하고 다음 수집을 준비합니다. 저장된 완료 결과는 최근 수집 결과에서 다시 다운로드할 수 있습니다.",
    )
if refresh_clicked:
    st.session_state.collection_ui_state = "ready"
    st.rerun()

start_clicked=st.button(
    "수집 중…" if collection_ui_state == "running" else ("수집 완료" if collection_ui_state == "completed" else "수집 시작"),
    type="primary",
    use_container_width=True,
    disabled=collection_ui_state in {"running", "completed"},
    help="완료 후에는 '새로고침 · 새 수집 준비'를 눌러야 다시 시작할 수 있습니다.",
)
if start_clicked or resume_clicked or continue_completed_clicked:
    provider_key_ok=(bool(brave_key) if search_provider=="Brave (권장)" else bool(tavily_key) if search_provider=="Tavily" else bool(brave_key or tavily_key))
    if not provider_key_ok and api_usage_mode!="개발 검증 · 캐시만" and not resume_clicked:
        st.error("선택한 검색엔진의 API Key가 필요합니다. API 키 없이 가짜 기업을 생성하지 않습니다.")
        st.stop()
    if start_clicked and (not industry_groups or any(not 1 <= len(g["keywords"]) <= 13 for g in industry_groups)):
        st.error("대분류를 선택하고 업종별 키워드를 1~13개 입력하세요.")
        st.stop()
    if start_clicked and not countries:
        st.error("수집할 국가를 1개 이상 선택해야 합니다.")
        st.stop()
    if start_clicked and not product_terms:
        st.error("검색할 세부제품을 1개 이상 선택하거나 입력해야 합니다.")
        st.stop()
    if start_clicked and len(countries)>5:
        st.error("무료 서버의 안정성을 위해 한 번에 최대 5개 국가만 실행할 수 있습니다.")
        st.stop()
    if group_errors and not (resume_clicked or continue_completed_clicked):
        st.error(" / ".join(group_errors))
        st.stop()
    if use_hunter and not hunter_key:
        st.warning("Hunter API Key가 없어 공식 홈페이지 공개 이메일만 수집합니다.")
    if not sender_company or not cl_product_name:
        st.warning("CL 영문 회사명 또는 영문 제품명이 비어 있어 수집은 계속하지만 Excel의 CL 문안은 'CL 미생성'으로 표시됩니다.")

    if continue_completed_clicked:
        previous_payload,_=load_result(continue_completed_job_id)
        if not previous_payload:
            st.session_state.collection_ui_state = "error"
            st.error("이어갈 완료 결과를 불러오지 못했습니다.")
            st.stop()
        old_config=dict(previous_payload.get("config",{}))
        cfg=CollectionConfig(**{k:v for k,v in old_config.items() if k in CollectionConfig.__dataclass_fields__})
        cfg.api_usage_mode=api_usage_mode
        cfg.search_provider=search_provider.replace(" (권장)","")
        new_budget=sum(max(1,g["base_keyword_count"])+3 for g in cfg.industry_groups)*len(cfg.countries or [cfg.region]) if cfg.industry_groups else (max(5,cfg.base_keyword_count)+3)*len(cfg.countries or [cfg.region])
        cfg.max_search_queries=previous_payload.get("discovery_summary",{}).get("queries",0)+new_budget
        old_records=previous_payload.get("records",[])
        resume_state={"schema_version":SCHEMA_VERSION,"config":cfg.__dict__,"records":old_records,"completed_domains":sorted({registrable_domain(row.get("website", "")) for row in old_records if registrable_domain(row.get("website", ""))}),"access_holds":previous_payload.get("access_holds",[]),"errors":previous_payload.get("errors",[]),"discovery_summary":previous_payload.get("discovery_summary",{})}
        if cfg.industry_groups:
            resume_state={"group_results": previous_payload.get("group_results",{})}
        job_id=new_job(cfg.__dict__)
        countries=cfg.countries or [cfg.region]; keywords=cfg.keywords
        candidate_target=cfg.candidate_limit; total_target=cfg.verified_email_target
        st.info(f"기존 {len(old_records)}개 업체를 유지하고 부족분 보충수집을 시작합니다.")
    elif resume_clicked:
        resume_state=load_checkpoint(resume_job_id)
        if not resume_state:
            st.session_state.collection_ui_state = "error"
            st.error("복구할 중간 저장 데이터가 없습니다.")
            st.stop()
        cfg=CollectionConfig(**resume_state["config"])
        cfg.search_provider=search_provider.replace(" (권장)","")
        job_id=resume_job_id
        countries=cfg.countries or [cfg.region]
        keywords=cfg.keywords
        candidate_target=cfg.candidate_limit
        total_target=cfg.verified_email_target
        st.info(f"작업 {job_id}를 {resume_state.get('progress_done',0)}/{resume_state.get('progress_total',0)} 지점부터 재개합니다.")
    else:
        resume_state=None
        cfg = CollectionConfig(
            region=", ".join(countries),keywords=keywords,industry=selected_industry,product=product_search,
            verified_email_target=total_target,candidate_limit=int(candidate_target),exclude_keywords=exclude_keywords,
            countries=countries,target_per_country=target_per_country,request_delay=float(request_delay),
            max_pages_per_company=int(max_pages),worker_count=int(worker_count),
            use_hunter=bool(use_hunter and hunter_key),verify_hunter=bool(verify_hunter and hunter_key),
            include_external_sendable=include_external,include_cross_domain_sendable=include_cross_domain,search_mode=search_mode,
            api_usage_mode=api_usage_mode,search_provider=search_provider.replace(" (권장)",""),max_search_queries=saving_budget_per_country*len(countries) if api_usage_mode.startswith("절약수집") else 0,
            search_strategy=search_strategy,
            qualified_candidate_target=total_target,
            base_keyword_count=base_keyword_count,
            collection_purpose=collection_purpose,
            industry_groups=industry_groups,
        )
        job_id=new_job(cfg.__dict__)
    st.session_state.collection_ui_state = "running"
    progress = st.progress(0, text="검색을 준비하고 있습니다.")
    status_box = st.empty()

    def on_progress(done: int, total: int, message: str):
        progress.progress(min(done / max(total, 1), 1.0), text=message)
        status_box.caption(f"진행 {done}/{total}")

    run_status = st.status("수집 중", expanded=True)
    run_status.write("검색·접속·이메일 판정을 진행하고 있습니다.")
    try:
        payload = collect_buyers(cfg,tavily_key,hunter_key,on_progress,
                                 checkpoint=lambda state: save_checkpoint(job_id,state),resume_state=resume_state,brave_key=brave_key)
    except Exception as exc:
        st.session_state.collection_ui_state = "error"
        run_status.update(label="수집 중단", state="error", expanded=False)
        mark_failed(job_id,f"{type(exc).__name__}: {exc}")
        st.error(f"수집이 중단되었습니다: {type(exc).__name__}: {exc}")
        st.stop()

    records = payload["records"]
    payload["generated_keywords"] = keywords
    payload["sender_profile"] = {"company_name":sender_company,"contact_name":sender_contact,"contact_title":sender_title,"email":sender_email,"website":sender_website}
    payload["product_profile"] = {"product_name":cl_product_name,"category":cl_category,"description":cl_description,"differentiator":cl_differentiator,"origin":cl_origin,"certifications":cl_certifications,"moq":cl_moq,"lead_time":cl_lead_time,"catalog_url":cl_catalog}
    cl_source=approval_rows(records, include_external=include_external)
    payload["cl_records"] = generate_cl_batch(cl_source,payload["sender_profile"],payload["product_profile"]) if sender_company and cl_product_name else []
    payload["cl_generation_status"] = "생성완료" if sender_company and cl_product_name else "미생성: 영문 회사명·제품명 확인 필요"
    summary = payload["summary"]
    discovery=payload.get("discovery_summary",{})
    search_status=payload.get("search_status","ok")
    if search_status!="ok":
        st.session_state.collection_ui_state = "completed"
        run_status.update(label="수집 완료 · API 진단 결과", state="complete", expanded=False)
        progress.progress(1.0,text="검색 API 진단 결과에 따라 수집을 안전하게 중단했습니다.")
        diagnostic=discovery.get("diagnostic",{})
        if search_status=="diagnostic_failed":
            st.error("선택한 검색엔진의 최소조건 진단검색이 빈 결과 또는 오류를 반환하여 본 검색을 실행하지 않았습니다.")
        else:
            st.error("진단검색은 통과했지만 본 검색 원시결과가 0개여서 수집을 중단했습니다.")
        st.write({"진단 검색어":diagnostic.get("query",""),"HTTP 상태":diagnostic.get("http_status",""),"결과 수":diagnostic.get("result_count",0),"요청 ID":diagnostic.get("request_id",""),"응답시간":diagnostic.get("response_time",""),"사용 크레딧":discovery.get("api_credits_used",0),"메시지":diagnostic.get("message","")})
        with st.expander("검색 API 요청 진단기록"):
            st.dataframe(discovery.get("api_response_log",[]),use_container_width=True,hide_index=True)
        excel=build_excel(payload)
        payload["job_id"]=job_id
        payload["download_filename"]=f"GLOEUM_검색API진단_{datetime.now():%Y%m%d_%H%M}.xlsx"
        save_result(job_id,payload,excel)
        st.download_button("API 진단 Excel 다운로드",excel,file_name=f"GLOEUM_검색API진단_{datetime.now():%Y%m%d_%H%M}.xlsx",mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",use_container_width=True,on_click="ignore")
        st.stop()
    if payload.get("collection_status")=="목표달성":
        progress.progress(1.0, text="수집과 Excel 생성이 완료되었습니다. 목표를 달성했습니다.")
    else:
        progress.progress(1.0, text="수집은 종료되었으나 설정한 목표에는 미달했습니다.")
        st.warning(
            f"목표 미달 · 후보 {summary.get('candidate_results',0)}/{int(candidate_target)}개 "
            f"(부족 {summary.get('candidate_shortfall',0)}개) · 발송 승인 후보 이메일 "
            f"{summary.get('sendable',0)}/{total_target}개 (부족 {summary.get('email_shortfall',0)}개)"
        )
    st.session_state.collection_ui_state = "completed"
    run_status.update(label="수집 완료", state="complete", expanded=False)
    m1, m2, m3, m4, m5, m6, m7, m8, m9 = st.columns(9)
    m1.metric("수집기업", summary["records"])
    m2.metric("A 핵심", summary.get("tier_a",0))
    m3.metric("B 잠재", summary.get("tier_b",0))
    m4.metric("C 검토", summary.get("tier_c",0))
    m5.metric("전략후보", summary.get("strategic",0))
    m6.metric("타국가", summary.get("other_country",0))
    m7.metric("시장참고", summary.get("reference",0))
    m8.metric("발송 승인 후보", summary["sendable"])
    st.download_button("발송 승인 후보 CSV 다운로드",approval_csv(records,include_external),
        file_name="GLOEUM_발송승인후보.csv",mime="text/csv",on_click="ignore")
    m9.metric("완전제외", summary["excluded"])
    st.caption(f"전체업체목록 {summary['records']+summary.get('access_holds',0)}개 = 분석완료 {summary['records']}개 + 접속보류 {summary.get('access_holds',0)}개 · 자동응답/형식 제외 이메일 {summary.get('blocked_email_purpose',0)}개 · 자동 발송 없음")
    st.caption(f"효율지표 · API 1회당 분석 {summary.get('candidates_per_api_call',0)}개 · API 1회당 발송 승인 후보 {summary.get('sendable_per_api_call',0)}개 · 기업당 평균 {summary.get('seconds_per_analyzed_company',0)}초")

    diagnostic=discovery.get("diagnostic",{})
    st.success(f"{diagnostic.get('provider',payload.get('search_provider','검색 API'))} 진단검색 정상 · 결과 {diagnostic.get('result_count',0)}개 · 요청 ID {diagnostic.get('request_id') or '-'}")
    st.caption(
        f"검색 {discovery.get('queries',0)}회 · 발견목표 {discovery.get('discovery_target',0)}개 "
        f"({discovery.get('oversample_factor',1)}배) · 후보풀 {discovery.get('candidate_pool_size',0)}개 · "
        f"원시결과 {discovery.get('raw_results',0)}개 · "
        f"사전제외 {discovery.get('prefilter_rejected',0)}개 · 중복제거 {discovery.get('deduplicated',0)}개 · "
        f"접속·파싱 실패 {discovery.get('scrape_skipped',0)}개 · 공식기업 접속보류 {discovery.get('access_holds',0)}개 · "
        f"비기업 보류제외 {discovery.get('access_hold_discarded',0)}개 · "
        f"홈페이지 종료 {discovery.get('homepage_only',0)}개 · 홈페이지 완결 {discovery.get('homepage_complete',0)}개 · 연락처 심층 {discovery.get('deep_contact_review',0)}개 · "
        f"협회·전시회 출처 {discovery.get('source_pages_visited',0)}개 → 공식사이트 {discovery.get('source_links_found',0)}개"
    )
    top_reasons=sorted(discovery.get("prefilter_reasons",{}).items(),key=lambda item:item[1],reverse=True)[:3]
    if top_reasons:
        st.caption("주요 사전제외: "+" · ".join(f"{reason} {count}건" for reason,count in top_reasons))
    if discovery.get("query_errors",0):
        st.error(f"검색 API 오류 {discovery['query_errors']}건이 발생했습니다. 아래 내용을 확인하세요.")
        for detail in discovery.get("query_error_details",[]): st.code(detail)
    if discovery.get("stop_reason"):
        st.warning(f"검색 안전중단: {discovery['stop_reason']} · 현재까지 확보된 결과는 저장되었습니다.")

    if payload.get("subcategory_summary"):
        st.subheader("세부업종별 검색·제품 확인 결과")
        st.dataframe(payload["subcategory_summary"], use_container_width=True, hide_index=True)
        st.caption("제품 확인은 공개 페이지의 제품 표현이 일치했다는 뜻입니다. 구매 의사나 이메일 수신 여부를 검증한 수치는 아닙니다. 공통 업체는 여러 세부업종에 집계될 수 있습니다.")
    elif payload.get("industry_summary"):
        st.subheader("이전 버전 업종별 수집 결과")
        st.dataframe(payload["industry_summary"], use_container_width=True, hide_index=True)
    if payload.get("partial_industry_failure"):
        st.warning("일부 업종 검색이 완료되지 않았습니다. 업종별 상태를 확인하세요.")
    st.dataframe(records, use_container_width=True, hide_index=True)
    if payload["cl_records"]:
        st.subheader("기업별 CL 미리보기")
        st.dataframe(payload["cl_records"],use_container_width=True,hide_index=True)
    else:
        st.info("CL 정보의 영문 회사명과 영문 제품명을 입력하면 기업별 CL이 함께 생성됩니다.")
    excel = build_excel(payload)
    region_label=countries[0] if len(countries)==1 else f"{len(countries)}개국"
    filename = f"GLOEUM_해외바이어_{region_label}_{datetime.now():%Y%m%d_%H%M}.xlsx"
    payload["job_id"]=job_id
    payload["download_filename"]=filename
    save_result(job_id,payload,excel)
    st.success(f"결과가 자동 저장되었습니다. 작업 ID: {job_id}")
    st.download_button("Excel 다운로드", excel, file_name=filename,
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                       use_container_width=True, on_click="ignore")
    if payload["errors"]:
        with st.expander(f"실행 참고사항 {len(payload['errors'])}건"):
            for error in payload["errors"]:
                st.write("-", error)

st.divider()
st.caption("공개 업무정보만 수집하며 로그인·CAPTCHA·robots.txt·접근제한을 우회하지 않습니다. 추정 이메일은 생성하지 않습니다.")
