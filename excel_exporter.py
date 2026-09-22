from io import BytesIO

import xlsxwriter

from country_catalog import country_name_ko
from buyer_core import email_is_sendable, mailing_candidate, mailing_rows as build_mailing_rows, strip_html_text
from delivery_policy import delivery_partitions
from version import APP_VERSION


def customer_summary(value: str) -> str:
    """스크랩 원문에서 고객에게 불필요한 메뉴·반복 문구를 줄인다."""
    import re
    # business_description can contain literal markup copied from metadata or
    # JSON-LD even though company/brand fields are already cleaned upstream.
    text=strip_html_text(value)
    navigation=(
        r"skip to content|home|contact us|search for|see all results|previous slide|next slide|"
        r"see more|bỏ qua nội dung|chuyển đến phần nội dung|trang chủ|"
        r"danh mục sản phẩm|tìm kiếm(?: sản phẩm)?|đăng ký|đăng nhập|"
        r"giỏ hàng|menu|xem thêm"
    )
    customer_ui=(
        r"add anything here or just remove it(?:\.\.\.)?|"
        r"nhập email và mật khẩu(?: của bạn)?\s*:?|bạn quên mật khẩu\s*\??|"
        r"quên mật khẩu\s*\??|tạo tài khoản|khôi phục mật khẩu|"
        r"nhập email(?: của bạn)?\s*:?|mật khẩu\s*:?|tài khoản|"
        r"yêu thích\s*\(\s*0\s*sản phẩm\s*\)|"
        r"hiện chưa có sản phẩm(?:\s+sản phẩm)?|"
        r"chưa có sản phẩm(?: nào)?(?:\s+trong)?\s*\.?|"
        r"quay trở lại cửa hàng|giỏ hàng trống|tuyển dụng"
    )
    # Remove only UI-close labels. The ordinary Vietnamese word "đóng" must
    # remain inside product phrases such as "máy đóng gói".
    text=re.sub(r'(?i)["“”]\s*đóng\s*["“”]', " ", text)
    text=re.sub(r"(?i)\bđóng\b\s+(?=see\s+more\b)", " ", text)
    # A bare close-button label is commonly followed by an uppercase menu
    # section. Keep ordinary product phrases such as "máy đóng gói" intact.
    text=re.sub(r"\bĐóng\b(?=\s+[A-ZÀ-ỸĐ][A-ZÀ-ỸĐ0-9&/+\-]*(?:\s+[A-ZÀ-ỸĐ][A-ZÀ-ỸĐ0-9&/+\-]*){0,4})", " ", text)
    text=re.sub(rf"(?i)(?<!\w)(?:{customer_ui})(?!\w)", " ", text)
    text=re.sub(rf"(?i)\b(?:{navigation})\b", " ", text)
    text=re.sub(r"\s+", " ", text).strip(" ·|-")
    sentences=re.split(r"(?<=[.!?])\s+",text)
    useful=[s for s in sentences if len(s)>=35 and not re.search(r"(?i)privacy|cookie|career|recruit|login|sign in",s)]
    return " ".join((useful or sentences)[:2])[:360]


HEADERS=["번호","company_id","회사명","목표국가","확인국가","품질판정","업체등급","바이어유형","관련성점수","국가점수","업종점수","바이어역할점수","사이트유형","자동판정 근거","국가근거","업종·취급제품","공식 홈페이지","회사 이메일","이메일 도메인 관계","이메일 용도","담당자명","직책·부서","담당자 이메일","전화번호","원본 키워드","검색경로","후보점수","검색어","검색결과 URL","회사정보 출처 URL","이메일 출처 URL","이메일 상태","이메일등급","검증점수","근거 상태","제외·검토사유","수집깊이","수집일시"]
KEYS=[None,"company_id","company_name","target_country","verified_country","quality_decision","priority","buyer_type","relevance_score","country_score","industry_score","buyer_role_score","site_type","decision_evidence","country_evidence","business_description","website","company_email","email_domain_status","email_purpose","contact_name","contact_title","contact_email","phone","original_keyword","discovery_source","candidate_score","search_query","discovery_url","company_source_url","email_source_url","email_status","email_grade","verification_score","evidence_status","exclusion_reason","collection_depth","collected_at"]
WIDTHS=[7,20,30,18,18,12,10,16,12,10,10,14,18,46,24,38,28,30,20,16,18,20,30,18,24,16,10,42,36,36,36,14,10,12,14,34,16,20]
HEADERS += ['보조 바이어 역할','회사명 검토사항','브랜드명','등급판정 근거']
KEYS += ['secondary_buyer_type','identity_review_reason','brand_name','grade_reason']
WIDTHS += [24,40,26,44]


def build_excel(payload: dict) -> bytes:
    out=BytesIO(); wb=xlsxwriter.Workbook(out,{"in_memory":True,"strings_to_formulas":False})
    version_text=f"v{APP_VERSION}"
    title=wb.add_format({"bold":True,"font_color":"white","bg_color":"#17365D","font_size":16,"valign":"vcenter"})
    header=wb.add_format({"bold":True,"font_color":"white","bg_color":"#17365D","border":1,"text_wrap":True,"valign":"vcenter"})
    pale=wb.add_format({"bg_color":"#EAF2F8","font_color":"#44546A","text_wrap":True})
    wrap=wb.add_format({"border":1,"border_color":"#D9E2F3","text_wrap":True,"valign":"top"})
    green=wb.add_format({"border":1,"bg_color":"#E2F0D9","font_color":"#375623"})
    blue=wb.add_format({"border":1,"bg_color":"#DDEBF7","font_color":"#1F4E78"})
    amber=wb.add_format({"border":1,"bg_color":"#FFF2CC","font_color":"#7F6000"})
    gray=wb.add_format({"border":1,"bg_color":"#E7E6E6","font_color":"#595959"})
    red=wb.add_format({"border":1,"bg_color":"#FCE4D6","font_color":"#9C0006"})
    records=[]
    for source in payload.get("records",[]):
        row=dict(source)
        row['company_name']=strip_html_text(row.get('company_name',''))
        row['brand_name']=strip_html_text(row.get('brand_name',''))
        records.append(row)

    def make_customer_sheet(selected):
        """내부 검색/API 정보 없이 고객에게 바로 보여줄 수 있는 간편 결과표."""
        ws=wb.add_worksheet("00_고객용결과"); ws.hide_gridlines(2)
        ws.set_landscape(); ws.set_paper(9); ws.fit_to_pages(1,0)
        customer_headers=["번호","등급","회사명","브랜드명","국가","바이어유형","취급제품·회사소개","홈페이지","이메일","이메일 용도","전화번호","판정 근거","등급판정 근거","검토사항"]
        ws.merge_range(0,0,0,len(customer_headers)-1,f"GLOEUM 글로이음 고객용 결과 · {version_text}",title); ws.set_row(0,28)
        ws.merge_range(1,0,1,len(customer_headers)-1,"A·B·C 및 전략후보만 표시 · 발송 전 이메일과 CL 수동 검수 필요",pale)
        ws.write_row(3,0,customer_headers,header); ws.freeze_panes(4,3)
        for idx,r in enumerate(selected,1):
            values=[idx,r.get("priority",""),r.get("company_name",""),r.get("brand_name",""),country_name_ko(r.get("verified_country") or r.get("target_country","")),r.get("buyer_type",""),customer_summary(r.get("business_description","")),r.get("website",""),r.get("company_email",""),r.get("email_purpose",""),r.get("phone",""),r.get("decision_evidence",""),r.get("grade_reason",""),r.get("exclusion_reason","")]
            ws.write_row(idx+3,0,values,wrap)
        if selected: ws.autofilter(3,0,3+len(selected),len(customer_headers)-1)
        for i,width in enumerate([7,9,34,24,16,18,48,30,30,16,18,48,44,38]): ws.set_column(i,i,width)

    def make_all_company_sheet(selected):
        name="01_전체업체목록"
        grade_counts={grade:sum(r.get("priority")==grade for r in selected) for grade in ("A","B","C","전략","타국가","참고","보류","제외")}
        subtitle=" · ".join(f"{grade} {count}개" for grade,count in grade_counts.items())+f" | 전체 {len(selected)}개"
        ws=wb.add_worksheet(name); ws.hide_gridlines(2)
        ws.set_landscape(); ws.set_paper(9); ws.fit_to_pages(1,0); ws.set_margins(left=0.25,right=0.25,top=0.5,bottom=0.5)
        ws.repeat_rows(0,3)
        ws.merge_range(0,0,0,len(HEADERS)-1,f"GLOEUM 글로이음 수집 결과 · {version_text}",title); ws.set_row(0,28)
        ws.merge_range(1,0,1,len(HEADERS)-1,"업체등급 필터로 전체 수집 결과를 한 번에 확인 | "+subtitle,pale)
        ws.write_row(3,0,HEADERS,header); ws.freeze_panes(4,3)
        if selected: ws.autofilter(3,0,3+len(selected),len(HEADERS)-1)
        for row_idx,r in enumerate(selected,4):
            values=[row_idx-3]+[r.get(key,"") if key else "" for key in KEYS[1:]]
            values[3]=country_name_ko(values[3]); values[4]=country_name_ko(values[4]) if values[4] else ""
            for col_idx,value in enumerate(values):
                grade=r.get("priority","")
                grade_fmt={"A":green,"B":blue,"C":amber,"전략":blue,"타국가":amber,"참고":gray,"보류":amber,"제외":red}.get(grade,wrap)
                fmt=grade_fmt if HEADERS[col_idx] in {"품질판정","업체등급"} else wrap
                if HEADERS[col_idx]=="이메일 상태": fmt=green if value in {"공식확인","검증완료"} else amber
                ws.write(row_idx,col_idx,value,fmt)
        for i,width in enumerate(WIDTHS): ws.set_column(i,i,width)

    tier_a=[r for r in records if r.get("priority")=="A"]
    tier_b=[r for r in records if r.get("priority")=="B"]
    tier_c=[r for r in records if r.get("priority")=="C"]
    strategic=[r for r in records if r.get("priority")=="전략"]
    other_country=[r for r in records if r.get("quality_decision")=="타국가후보"]
    reference=[r for r in records if r.get("quality_decision")=="참고기업"]
    excluded=[r for r in records if r.get("quality_decision")=="제외"]
    access_holds=[]
    for source in payload.get("access_holds",[]):
        row=dict(source)
        row['company_name']=strip_html_text(row.get('company_name',''))
        row['brand_name']=strip_html_text(row.get('brand_name',''))
        access_holds.append(row)
    grade_order={"A":0,"B":1,"C":2,"전략":3,"타국가":4,"참고":5,"보류":6,"제외":7}
    all_companies=records+access_holds
    all_companies.sort(key=lambda r:(grade_order.get(r.get("priority",""),9),-int(r.get("relevance_score") or 0),str(r.get("company_name") or "").lower()))
    customer_rows=[r for r in all_companies if r.get("priority") in {"A","B","C","전략"}]
    make_customer_sheet(customer_rows)
    make_all_company_sheet(all_companies)

    # 외부 메일 서비스로 넘길 수 있는 원본 주소 목록이다. 자동 발송은 하지 않으며,
    # 업체등급은 우선순위로만 표시하고 A/B/C/전략의 유효 이메일을 모두 보존한다.
    mailing_rows, approved_rows, review_rows=delivery_partitions(records,include_external=payload.get("config",{}).get("include_external_sendable",True))
    mailing=wb.add_worksheet("메일_전체확보"); mailing.hide_gridlines(2)
    mailing.set_landscape(); mailing.set_paper(9); mailing.fit_to_pages(1,0); mailing.repeat_rows(0,3)
    mailing_headers=["번호","company_id","국가","업체등급","회사명","바이어유형","이메일","이메일 용도","이메일 상태","이메일등급","공식 홈페이지","이메일 출처 URL","도메인 관계","메일링 검토","CL 검수 상태","연관 업체ID"]
    mailing.merge_range(0,0,0,len(mailing_headers)-1,"전체 확보 이메일 · 보관용 · 일괄 발송 금지",title); mailing.set_row(0,28)
    mailing.merge_range(1,0,1,len(mailing_headers)-1,"공식 홈페이지·검증 과정에서 확보한 유효 이메일을 등급과 무관하게 제공 | 외부 메일 서비스에서 담당자 최종 검수 후 사용",pale)
    mailing.write_row(3,0,mailing_headers,header); mailing.freeze_panes(4,4)
    for i,r in enumerate(mailing_rows,1):
        values=[i,r.get("company_id",""),country_name_ko(r.get("verified_country") or r.get("target_country","")),r.get("priority",""),r.get("company_name",""),r.get("buyer_type",""),r.get("company_email",""),r.get("email_purpose",""),r.get("email_status",""),r.get("email_grade",""),r.get("website",""),r.get("email_source_url",""),r.get("email_domain_status",""),"검토대상", "CL 검수대기",", ".join(r.get("related_company_ids",[]))]
        if r.get("quality_decision")=="타국가후보":
            values[2]=country_name_ko(r["verified_country"]) if r.get("verified_country") else "국가 미확인"
            values[13]="선택국가 외·국가 확인 필요"
            values[14]="국가 확인 후 CL 작성"
        elif r.get("quality_decision")=="참고기업":
            values[2]=country_name_ko(r["verified_country"]) if r.get("verified_country") else "국가 미확인"
            values[13]="참고후보·업체유형 확인 필요"
            values[14]="업체 적합성 확인 후 CL 작성"
        else:
            draft=next((c for c in payload.get("cl_records",[]) if c.get("company_id")==r.get("company_id")),{})
            values[14]=draft.get("review_status","CL 입력대기")
        values[13]=r['delivery_status']+(' · '+r['delivery_review_reason'] if r['delivery_review_reason'] else ' · 최종 수동 승인 필요')
        for col,value in enumerate(values):
            grade=r.get("priority","")
            fmt={"A":green,"B":blue,"C":amber,"전략":blue}.get(grade,wrap) if col==3 else wrap
            mailing.write(i+3,col,value,fmt)
    if mailing_rows: mailing.autofilter(3,0,3+len(mailing_rows),len(mailing_headers)-1)
    for idx,width in enumerate([8,20,16,10,30,18,34,18,14,12,32,45,22,14,16,32]): mailing.set_column(idx,idx,width)

    summary=dict(payload.get("summary",{})); discovery=payload.get("discovery_summary",{}); diagnostic=discovery.get("diagnostic",{})
    summary['sendable']=len(approved_rows)
    ws=wb.add_worksheet("02_수집성과"); ws.hide_gridlines(2); ws.set_landscape(); ws.set_paper(9); ws.fit_to_pages(1,0); ws.set_margins(left=0.25,right=0.25,top=0.5,bottom=0.5); ws.merge_range("A1:M1","수집 성과 및 서비스 등급 요약",title)
    selected_country_names=", ".join(country_name_ko(c) for c in payload.get("config",{}).get("countries",[])) or payload.get("config",{}).get("region","")
    rows=[
        ["항목","결과"],["프로그램 버전",version_text],["결과 스키마",payload.get("schema_version",APP_VERSION)],["선택 국가",selected_country_names],["검색 상태",payload.get("search_status","ok")],["검색 모드",payload.get("config",{}).get("search_mode","균형")],["검색 조합 운영",payload.get("config",{}).get("search_strategy","적응형 최적화")],
        ["전체 후보기업 조사 목표",payload.get("config",{}).get("candidate_limit",0)],["발송 승인 후보 이메일 목표",payload.get("config",{}).get("verified_email_target",0)],
        ["수집 목표 달성 상태",payload.get("collection_status","-")],["전체 조사 목표 부족분",summary.get("candidate_shortfall",0)],["적합후보 목표",summary.get("qualified_target",0)],["적합후보 목표 부족분",summary.get("qualified_shortfall",0)],["이메일 목표 부족분",summary.get("email_shortfall",0)],
        ["공식사이트 분석 완료",summary.get("records",0)],["엑셀 전체 업체(접속보류 포함)",summary.get("records",0)+summary.get("access_holds",discovery.get("access_holds",0))],["고객 제공 리스트(A+B+C+전략)",summary.get("customer_list",summary.get("tier_a",0)+summary.get("tier_b",0)+summary.get("tier_c",0)+summary.get("strategic",0))],
        ["A 핵심바이어",summary.get("tier_a",0)],["B 잠재바이어",summary.get("tier_b",0)],["C 추가검토",summary.get("tier_c",0)],
        ["전략후보",summary.get("strategic",0)],["타국가 후보",summary.get("other_country",0)],["시장참고기업",summary.get("reference",0)],["완전제외",summary.get("excluded",0)],["접속보류 후보",summary.get("access_holds",discovery.get("access_holds",0))],["전체 발견 이메일",summary.get("emails_found",0)],
        ["이메일 확보 A·B 기업 수",summary.get("qualified_emails_found",0)],["자동응답·형식 제외 이메일",summary.get("blocked_email_purpose",0)],["발송 승인 후보 이메일",len(approved_rows)],["이메일 미확보",summary.get("missing_email",0)],
        ["원시 검색결과",discovery.get("raw_results",0)],["사전 제외",discovery.get("prefilter_rejected",0)],["검색 중복제거",discovery.get("deduplicated",0)],["접속 대체 URL 보관",discovery.get("alternate_urls_stored",0)],
        ["검색 공급자",payload.get("search_provider",payload.get("config",{}).get("search_provider",""))],["API 사용 모드",payload.get("config",{}).get("api_usage_mode","전체 실검색")],["검색 전 제외어","jobs · career · news · directory · marketplace · buying leads · lead platform · Yelp · Lemon8 · D&B"],["캐시 재사용",sum(row.get("http_status")=="CACHE" for row in discovery.get("api_response_log",[]))],
        ["접속·파싱 실패",discovery.get("scrape_skipped",0)],["공식기업 접속보류",discovery.get("access_holds",0)],["비기업 보류 제외",discovery.get("access_hold_discarded",0)],["홈페이지만 확인",discovery.get("homepage_only",0)],["홈페이지에서 완료",discovery.get("homepage_complete",0)],["연락처 심층탐색",discovery.get("deep_contact_review",0)],["검색 API 사용량",discovery.get("api_credits_used",0)],["적응형 확장 검색 호출",discovery.get("adaptive_expansion_queries",0)],["API 1회당 분석기업",summary.get("candidates_per_api_call",0)],["API 1회당 발송 승인 후보",summary.get("sendable_per_api_call",0)],["기업당 평균시간(초)",summary.get("seconds_per_analyzed_company",0)],["검색 API 오류",discovery.get("query_errors",0)],["수집 처리 오류",summary.get("errors",0)],["전체 오류",discovery.get("query_errors",0)+summary.get("errors",0)],["수집 중단 사유",discovery.get("stop_reason","")],["소요시간(초)",summary.get("elapsed_seconds",0)],["저장 후보에서 재개", "예" if discovery.get("resumed_from_checkpoint") else "아니오"],
    ]
    rows.extend([["발송 승인 후보 기업 수",len({r.get('company_id') for r in approved_rows})],
                 ["발송 승인 후보 이메일 수",len(approved_rows)],
                 ["추가 검토 이메일 수",len(review_rows)],
                 ["최종 부족분 보충 검색 호출",discovery.get("refill_queries",0)],
                 ["수집 목적",payload.get("config",{}).get("collection_purpose","수출 바이어 발굴")],
                 ["전체 이메일 보유 업체",len({r.get("company_id") for r in mailing_rows})],
                 ["전체 확보 이메일 수",len(mailing_rows)],
                 ["참고기업 이메일",sum(r.get("quality_decision")=="참고기업" for r in mailing_rows)],
                 ["선택국가 외·국가확인 필요 이메일",sum(r.get("quality_decision")=="타국가후보" or not r.get("verified_country") for r in mailing_rows)]])
    for i,row in enumerate(rows,3): ws.write_row(i,0,row,header if i==3 else wrap)
    ws.set_column("A:A",34); ws.set_column("B:B",64)
    ws.write_row(3,3,["국가","수집","A","B","C","전략","타국가","참고","제외","발송 승인 후보"],header)
    for i,row in enumerate(payload.get("country_summary",[]),4):
        ws.write_row(i,3,[country_name_ko(row.get("country","")),row.get("records",0)+row.get("access_holds",0),row.get("tier_a",0),row.get("tier_b",0),row.get("tier_c",0),row.get("strategic",0),row.get("other_country",0),row.get("reference",0),row.get("excluded",0),row.get("sendable",0)],wrap)
    ws.set_column("D:D",20); ws.set_column("E:M",12)

    evidence=wb.add_worksheet("03_검색근거"); evidence.hide_gridlines(2); evidence.set_landscape(); evidence.set_paper(9); evidence.fit_to_pages(1,0); evidence.set_margins(left=0.25,right=0.25,top=0.5,bottom=0.5); evidence.repeat_rows(0,3); evidence.merge_range("A1:I1","검색·판정 근거 및 API 진단",title)
    evidence.write_row("A4",["구분","번호","공급자·단계","키워드/사유","건수","HTTP","요청 ID","응답시간","오류"],header)
    erow=4
    keyword_stats=discovery.get("keyword_stats",{})
    for country in payload.get("config",{}).get("countries",[]) or [payload.get("config",{}).get("region","")]:
        for idx,keyword in enumerate(payload.get("generated_keywords",[]),1):
            country_stats=discovery.get("keyword_stats_by_country",{}).get(country)
            stat=country_stats.get(keyword,{}) if country_stats is not None else keyword_stats.get(keyword,{})
            note=(f"채택 {stat.get('accepted_results',0)} · 제외 {stat.get('rejected_results',0)} · 호출 {stat.get('calls',0)}회"
                   if stat else "실행기록 없음")
            evidence.write_row(erow,0,["검색키워드",idx,country_name_ko(country),keyword,stat.get("raw_results",0),"","", "",note],wrap); erow+=1
    for country,count in discovery.get("adaptive_expansion_by_country",{}).items():
        evidence.write_row(erow,0,["확장검색","",country_name_ko(country),"후보 부족 시 추가 키워드",count,"","","",discovery.get("search_stop_by_country",{}).get(country,"")],wrap); erow+=1
    for reason,count in sorted(discovery.get("prefilter_reasons",{}).items(),key=lambda item:item[1],reverse=True):
        evidence.write_row(erow,0,["사전제외","","검색결과",reason,count,"","","",""],wrap); erow+=1
    for reason,count in sorted(discovery.get("quality_exclusion_reasons",{}).items(),key=lambda item:item[1],reverse=True):
        evidence.write_row(erow,0,["판정사유","","공식사이트",reason,count,"","","",""],wrap); erow+=1
    for idx,row in enumerate(discovery.get("api_response_log",[]),1):
        evidence.write_row(erow,0,["API",idx,f'{row.get("provider","")} · {row.get("request_mode","")}'.strip(" ·"),row.get("query",""),row.get("result_count",0),row.get("http_status",""),row.get("request_id",""),row.get("response_time",""),row.get("error","")],wrap); erow+=1
    evidence.write_row(erow,0,["진단","",payload.get("search_status",""),diagnostic.get("query",""),diagnostic.get("result_count",0),diagnostic.get("http_status",""),diagnostic.get("request_id",""),diagnostic.get("response_time",""),diagnostic.get("message","")],wrap)
    for idx,width in enumerate([14,8,20,75,12,10,38,14,55]): evidence.set_column(idx,idx,width)
    evidence.freeze_panes(4,2)

    cl=wb.add_worksheet("04_CL발송목록"); cl.hide_gridlines(2); cl.set_landscape(); cl.set_paper(9); cl.fit_to_pages(1,0); cl.set_margins(left=0.25,right=0.25,top=0.5,bottom=0.5); cl.repeat_rows(0,3); cl.merge_range("A1:R1","메일링 후보 및 맞춤 CL 초안 (A/B/C/전략 · 수동 검수·승인 필요)",title)
    cl_headers=["번호","등급","company_id","바이어 회사","수신자","이메일","이메일 상태","도메인 관계","영문 제목","영문 본문","한국어 검수본","홈페이지","이메일 근거 URL","개인화 근거 URL","개인화 적용 문장","첨부 자료","생성 상태","최종 검수 상태"]
    cl.write_row("A4",cl_headers,header); cl.freeze_panes(4,3)
    cl_by_id={row.get("company_id"):row for row in payload.get("cl_records",[])}
    config=payload.get("config",{})
    sendable=approved_rows
    for i,r in enumerate(sendable,1):
        c=cl_by_id.get(r.get("company_id"),{})
        cl_missing=not bool(c)
        cl.write_row(i+3,0,[i,r.get("priority",""),r.get("company_id",""),r.get("company_name",""),c.get("recipient",r.get("contact_name","")),r.get("company_email",""),r.get("email_status",""),r.get("email_domain_status",""),c.get("subject_en",""),c.get("body_en",""),c.get("body_ko",""),r.get("website",""),r.get("email_source_url",""),c.get("personalization_evidence",r.get("company_source_url","")),c.get("personalization_sentence",""),c.get("attachment_name",""),c.get("generation_status","입력대기" if cl_missing else ""),c.get("review_status","CL 회사·제품정보 입력 필요" if cl_missing else "검수대기")],wrap)
    for idx,width in enumerate([8,8,20,30,20,30,14,20,45,85,70,32,40,40,60,28,14,16]): cl.set_column(idx,idx,width)


    industry_sheet=wb.add_worksheet("05_세부업종별성과")
    fields=["주업종","세부업종","국가","선택제품수","검색실행제품수","검색호출수","제품표현확인기업","메일링대상기업","수집이메일","검색상태"]
    industry_sheet.write_row(0,0,fields,header)
    for i,r in enumerate(payload.get("subcategory_summary",[]),1):
        industry_sheet.write_row(i,0,[r.get(k,"") for k in fields],wrap)
    industry_sheet.set_column(0,1,32); industry_sheet.set_column(2,9,22)
    industry_sheet.freeze_panes(1,2)
    industry_sheet.write(len(payload.get("subcategory_summary",[]))+3,0,"제품표현 확인은 구매 의사 확인이 아닙니다. 공통 업체·검색은 여러 세부업종에 집계될 수 있습니다. 직접입력 제품은 미지정 행에 표시합니다.",wrap)
    if "subcategory_summary" not in payload:
        industry_sheet.write(2,0,"이전 버전 결과: 세부업종별 검색 집계 없음",wrap)
    detail=wb.add_worksheet("06_업종별판정")
    detail.write_row(0,0,["company_id","회사명","브랜드명","선택 대분류","선택 세부업종","목표국가","업체등급","품질판정","확인된 제품명","세부제품 근거상태","판정 근거","등급판정 근거","공식 출처","제품 확인 세부업종","일치한 제품표현(정규화)"],header)
    rownum=1
    for r in records:
        for a in r.get("industry_assessments",[]):
            detail.write_row(rownum,0,[r.get("company_id",""),r.get("company_name",""),r.get("brand_name",""),a.get("major",""),
                ", ".join(a.get("subcategories",[])),a.get("target_country",""),a.get("priority",""),
                a.get("quality_decision",""),", ".join(a.get("product_hits",[])),
                a.get("product_evidence_status",""),a.get("evidence",""),r.get("grade_reason",""),a.get("source_url",""),
                ", ".join(a.get("matched_subcategories",[])),
                "; ".join(p+": "+", ".join(terms) for p,terms in a.get("product_alias_hits",{}).items())],wrap)
            rownum+=1
    detail.set_column(0,0,20); detail.set_column(1,4,32); detail.set_column(5,7,16); detail.set_column(8,14,45)
    detail.freeze_panes(1,2)
    detail.autofilter(0,0,max(1,rownum-1),14)
    for name, selected in (("메일_발송승인후보",approved_rows),("메일_추가검토",review_rows)):
        sheet=wb.add_worksheet(name); sheet.hide_gridlines(2)
        cols=['회사명','이메일','등급','목표국가','확인국가','상태','검토사유','이메일 출처','연관 업체ID']
        sheet.merge_range(0,0,0,8,name+' · 자동 발송 없음 · 최종 수동 승인 필요',title)
        sheet.write_row(3,0,cols,header); sheet.freeze_panes(4,2)
        for i,r in enumerate(selected,4):
            sheet.write_row(i,0,[r.get('company_name',''),r.get('company_email',''),r.get('priority',''),
                r.get('target_country',''),r.get('verified_country',''),r['delivery_status'],r['delivery_review_reason'],
                r.get('email_source_url',''),', '.join(r['related_company_ids'])],wrap)
        sheet.set_column(0,1,32); sheet.set_column(2,5,18); sheet.set_column(6,8,48)
        if selected: sheet.autofilter(3,0,3+len(selected),8)
    wb.close(); return out.getvalue()
