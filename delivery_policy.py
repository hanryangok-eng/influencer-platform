"""Separate retained contact evidence from approval candidates. Never sends mail."""
import csv
import re
from io import StringIO


def review_reasons(row, include_external=True):
    from buyer_core import company_name_review_reason, email_purpose
    reasons = []
    if row.get('priority') not in {'A', 'B'} or row.get('quality_decision') != '적합':
        reasons.append('업체 적합성 추가검토')
    if (not row.get('verified_country') or not row.get('target_country')
            or row.get('verified_country') != row.get('target_country')):
        reasons.append('목표국가 확인 필요')
    if not row.get('industry_score') or not row.get('buyer_role_score'):
        reasons.append('제품·바이어 역할 확인 필요')
    statuses = {'공식확인', '검증완료'} | ({'외부확인'} if include_external else set())
    if row.get('email_status') not in statuses or not row.get('email_source_url'):
        reasons.append('이메일 출처·상태 확인 필요')
    relationship_ok=(row.get('email_domain_status') in {'동일도메인', '공식페이지·공용메일'}
                     or row.get('email_relationship_verified') is True)
    if not relationship_ok:
        reasons.append('이메일 소유관계 확인 필요')
    if len(row.get('related_company_ids', [])) > 1:
        reasons.append('공유 이메일·회사 관계 확인 필요')
    if row.get('identity_review_reason'):
        reasons.append(row['identity_review_reason'])
    if re.search(r'<[^>]+>', str(row.get('company_name') or '')):
        reasons.append('회사명 HTML 정제·법인명 확인 필요')
    name_reason=company_name_review_reason(row.get('company_name', ''))
    if name_reason:
        reasons.append(name_reason)
    purpose=row.get('email_purpose') or email_purpose(row.get('company_email',''))
    if purpose == '채용':
        reasons.append('채용 전용 이메일·발송 승인 제외')
    elif purpose == '임대·입점':
        reasons.append('임대·입점 전용 이메일·담당부서 확인 필요')
    elif purpose == '개인정보·법무':
        reasons.append('개인정보·법무 전용 이메일·발송 승인 제외')
    return list(dict.fromkeys(reasons))


def delivery_partitions(records, include_external=True):
    from buyer_core import mailing_rows, email_variants, strip_html_text
    retained = mailing_rows(records, include_external=True, include_other_country=True, include_reference=True)
    owners = {}
    for record in records:
        for row in email_variants(record):
            owners.setdefault(row['company_email'], set()).add(row.get('company_id', ''))
    approved, review = [], []
    for row in retained:
        raw_name=str(row.get('company_name') or '')
        if re.search(r'<[^>]+>', raw_name):
            row['identity_review_reason']='; '.join(filter(None,[row.get('identity_review_reason',''),'회사명 HTML 정제·법인명 확인 필요']))
        row['company_name']=strip_html_text(raw_name)
        row['brand_name']=strip_html_text(row.get('brand_name',''))
        row['related_company_ids'] = sorted(owners.get(row['company_email'], set()) - {''})
        reasons = review_reasons(row, include_external)
        row['delivery_review_reason'] = '; '.join(reasons)
        row['delivery_status'] = '추가 검토' if reasons else '발송 승인 후보'
        (review if reasons else approved).append(row)
    return retained, approved, review


def approval_rows(records, include_external=True):
    return delivery_partitions(records, include_external)[1]


def approval_csv(records, include_external=True):
    fields = ['company_id', 'company_name', 'company_email', 'target_country',
              'email_status', 'email_source_url', 'delivery_status']
    output = StringIO(newline='')
    writer = csv.DictWriter(output, fieldnames=fields, extrasaction='ignore')
    writer.writeheader()
    for row in approval_rows(records, include_external):
        # CSV opened in spreadsheet applications must not execute scraped formulas.
        writer.writerow({k: "'" + str(row.get(k, '')) if str(row.get(k, '')).startswith(('=', '+', '-', '@'))
                         else row.get(k, '') for k in fields})
    return output.getvalue().encode('utf-8-sig')
