"""Excel export for the Instagram influencer discovery workflow."""

from io import BytesIO

import xlsxwriter

from version import APP_VERSION


def build_influencer_excel(payload: dict) -> bytes:
    out=BytesIO()
    wb=xlsxwriter.Workbook(out,{
        "in_memory":True,
        "strings_to_formulas":False,
        "strings_to_urls":False,
    })
    title=wb.add_format({"bold":True,"font_color":"white","bg_color":"#833AB4","font_size":16,"valign":"vcenter"})
    header=wb.add_format({"bold":True,"font_color":"white","bg_color":"#405DE6","border":1,"text_wrap":True,"valign":"vcenter"})
    wrap=wb.add_format({"border":1,"border_color":"#D9E2F3","text_wrap":True,"valign":"top"})
    link=wb.add_format({"border":1,"font_color":"#0563C1","underline":1,"valign":"top"})
    green=wb.add_format({"border":1,"bg_color":"#E2F0D9","font_color":"#375623"})
    blue=wb.add_format({"border":1,"bg_color":"#DDEBF7","font_color":"#1F4E78"})
    amber=wb.add_format({"border":1,"bg_color":"#FFF2CC","font_color":"#7F6000"})
    pale=wb.add_format({"bg_color":"#F3EAF8","font_color":"#4C2A5E","text_wrap":True})
    records=list(payload.get("records",[]))

    ws=wb.add_worksheet("00_인플루언서결과")
    headers=["순위","등급","점수","계정명","표시명","계정유형","국가","위치확인","위치근거","분야","팔로워","팔로워근거","공개 이메일","이메일상태","Instagram","일치 키워드","크리에이터 근거","공개 소개요약","DM 상태","이메일 연락상태","검색어","검색결과 출처","수집일시"]
    ws.merge_range(0,0,0,len(headers)-1,f"GLOEUM Instagram 인플루언서 검색 · v{APP_VERSION}",title)
    ws.merge_range(1,0,1,len(headers)-1,"공개 검색결과 기반 후보 · 팔로워·이메일은 원본 프로필에서 최종 확인 · 자동 발송 없음",pale)
    ws.write_row(3,0,headers,header); ws.freeze_panes(4,5); ws.autofilter(3,0,max(3,3+len(records)),len(headers)-1)
    for row_idx,r in enumerate(records,4):
        values=[r.get("rank",""),r.get("grade",""),r.get("score",0),r.get("handle",""),r.get("display_name",""),r.get("profile_type",""),r.get("country",""),r.get("location_status",""),r.get("location_evidence",""),r.get("category",""),r.get("followers_display",""),r.get("follower_status",""),r.get("public_email",""),r.get("email_status",""),"Instagram 열기",r.get("matched_keywords",""),r.get("creator_evidence",""),r.get("bio_summary",""),r.get("dm_status",""),r.get("email_contact_status",""),r.get("discovery_query",""),r.get("source_url",""),r.get("collected_at","")]
        for col,value in enumerate(values):
            fmt={"A":green,"B":blue,"C":amber}.get(r.get("grade"),wrap) if col in {1,2} else wrap
            if col==14 and r.get("instagram_url"):
                ws.write_url(row_idx,col,r["instagram_url"],link,string="Instagram 열기")
            elif col==21 and r.get("source_url"):
                ws.write_url(row_idx,col,r["source_url"],link,string=r["source_url"][:120])
            else:
                ws.write(row_idx,col,value,fmt)
    widths=[8,8,8,24,28,22,16,12,20,20,12,18,30,18,18,30,32,58,14,18,55,40,22]
    for idx,width in enumerate(widths): ws.set_column(idx,idx,width)

    dm=wb.add_worksheet("01_DM초안")
    dm_headers=["순위","등급","계정명","표시명","Instagram","맞춤 DM 초안","생성상태","DM 상태","최종 검수"]
    dm.merge_range(0,0,0,len(dm_headers)-1,"Instagram DM 초안 · 복사 후 담당자가 직접 검수·발송",title)
    dm.merge_range(1,0,1,len(dm_headers)-1,"임의 계정 자동발송 없음 · 사실과 다른 개인화 문구를 추가하지 말 것",pale)
    dm.write_row(3,0,dm_headers,header); dm.freeze_panes(4,4)
    for row_idx,r in enumerate(records,4):
        values=[r.get("rank",""),r.get("grade",""),r.get("handle",""),r.get("display_name",""),"Instagram 열기",r.get("dm_draft",""),r.get("outreach_generation_status",""),r.get("dm_status",""),"검수대기"]
        for col,value in enumerate(values):
            if col==4 and r.get("instagram_url"):
                dm.write_url(row_idx,col,r["instagram_url"],link,string="Instagram 열기")
            else:
                dm.write(row_idx,col,value,wrap)
    for idx,width in enumerate([8,8,24,28,18,95,18,16,16]): dm.set_column(idx,idx,width)

    email=wb.add_worksheet("02_이메일연락")
    email_headers=["순위","등급","계정명","표시명","공개 이메일","메일 작성","영문 제목","영문 본문","이메일 상태","연락 상태","근거 URL","최종 검수"]
    email.merge_range(0,0,0,len(email_headers)-1,"공개 이메일 연락 초안 · 클릭하면 기본 메일 앱의 작성창이 열립니다",title)
    email.merge_range(1,0,1,len(email_headers)-1,"검색결과에 공개된 주소만 표시 · 이메일 추정 생성 없음 · 실제 발송 전 수신주소와 본문 확인",pale)
    email.write_row(3,0,email_headers,header); email.freeze_panes(4,4)
    email_records=[r for r in records if r.get("public_email")]
    for row_idx,r in enumerate(email_records,4):
        values=[r.get("rank",""),r.get("grade",""),r.get("handle",""),r.get("display_name",""),r.get("public_email",""),"메일 작성",r.get("email_subject",""),r.get("email_body",""),r.get("email_status",""),r.get("email_contact_status",""),r.get("source_url",""),"검수대기"]
        for col,value in enumerate(values):
            if col==5 and r.get("email_compose_url"):
                try:
                    email.write_url(row_idx,col,r["email_compose_url"],link,string="메일 작성")
                except ValueError:
                    email.write(row_idx,col,"메일 앱에서 주소 입력",wrap)
            elif col==10 and r.get("source_url"):
                email.write_url(row_idx,col,r["source_url"],link,string=r["source_url"][:120])
            else:
                email.write(row_idx,col,value,wrap)
    for idx,width in enumerate([8,8,24,28,32,16,48,95,20,16,42,16]): email.set_column(idx,idx,width)

    evidence=wb.add_worksheet("03_검색근거")
    evidence.merge_range("A1:I1","공개 검색 근거·안전 기준",title)
    evidence.write_row("A4",["구분","번호","공급자","검색어·항목","결과수","HTTP","요청ID","응답시간","오류·비고"],header)
    row=4
    for index,query in enumerate(payload.get("queries",[]),1):
        evidence.write_row(row,0,["검색어",index,payload.get("config",{}).get("search_provider",""),query,"","","","",""],wrap); row+=1
    for index,item in enumerate(payload.get("api_response_log",[]),1):
        evidence.write_row(row,0,["API",index,item.get("provider",""),item.get("query",""),item.get("result_count",0),item.get("http_status",""),item.get("request_id",""),item.get("response_time",""),item.get("error","")],wrap); row+=1
    for reason,count in sorted(payload.get("rejected_reasons",{}).items(),key=lambda x:x[1],reverse=True):
        evidence.write_row(row,0,["제외","", "",reason,count,"","","",""],wrap); row+=1
    safety=payload.get("safety",{})
    safety_rows=[
        ("Instagram 로그인 사용","아니오" if not safety.get("instagram_login_used") else "예"),
        ("팔로워 목록 수집","아니오" if not safety.get("follower_list_collected") else "예"),
        ("이메일 추정 생성","아니오" if not safety.get("email_guessed") else "예"),
        ("DM 자동 발송","아니오" if not safety.get("automatic_dm_sent") else "예"),
        ("이메일 자동 발송","아니오" if not safety.get("automatic_email_sent") else "예"),
    ]
    for label,value in safety_rows:
        evidence.write_row(row,0,["안전기준","","",label,"","","","",value],wrap); row+=1
    summary=payload.get("summary",{})
    evidence.write_row(row+1,0,["성과","","","프로그램 버전","","","","",f"v{APP_VERSION}"],wrap)
    for label,key in (("원시 검색결과","raw_results"),("고유 프로필","unique_profiles"),("최종 후보","records"),("공개 이메일","public_emails"),("DM 초안","dm_drafts"),("소요시간(초)","elapsed_seconds")):
        row+=1; evidence.write_row(row+1,0,["성과","","",label,summary.get(key,0),"","","",""],wrap)
    for idx,width in enumerate([14,8,18,72,12,10,36,14,58]): evidence.set_column(idx,idx,width)
    evidence.freeze_panes(4,3)

    wb.close()
    return out.getvalue()

