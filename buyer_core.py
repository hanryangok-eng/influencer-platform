from __future__ import annotations

import hashlib
import html as html_lib
import json
import os
import re
import time
import threading
import urllib.parse
import urllib.robotparser
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass, field, replace
from functools import lru_cache
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Callable

import requests

from version import APP_VERSION, SCHEMA_VERSION

from country_catalog import country_meta
from keyword_generator import INDUSTRY_ALIASES

# Offline IANA root-zone snapshot 2026091300 (2026-09-13).
# Source: https://data.iana.org/TLD/tlds-alpha-by-domain.txt
# Syntax/TLD validation only; never claims DNS or mailbox delivery verification.
IANA_TLDS = frozenset("""
aaa aarp abb abbott abbvie abc able abogado abudhabi ac academy accenture
accountant accountants aco actor ad ads adult ae aeg aero aetna af
afl africa ag agakhan agency ai aig airbus airforce airtel akdn al
alibaba alipay allfinanz allstate ally alsace alstom am amazon americanexpress americanfamily amex
amfam amica amsterdam analytics android anquan anz ao aol apartments app apple
aq aquarelle ar arab aramco archi army arpa art arte as asda
asia associates at athleta attorney au auction audi audible audio auspost author
auto autos aw aws ax axa az azure ba baby baidu banamex
band bank bar barcelona barclaycard barclays barefoot bargains baseball basketball bauhaus bayern
bb bbc bbt bbva bcg bcn bd be beats beauty beer berlin
best bestbuy bet bf bg bh bharti bi bible bid bike bing
bingo bio biz bj black blackfriday blockbuster blog bloomberg blue bm bms
bmw bn bnpparibas bo boats boehringer bofa bom bond boo book booking
bosch bostik boston bot boutique box br bradesco bridgestone broadway broker brother
brussels bs bt build builders business buy buzz bv bw by bz
bzh ca cab cafe cal call calvinklein cam camera camp canon capetown
capital capitalone car caravan cards care career careers cars casa case cash
casino cat catering catholic cba cbn cbre cc cd center ceo cern
cf cfa cfd cg ch chanel channel charity chase chat cheap chintai
christmas chrome church ci cipriani circle cisco citadel citi citic city ck
cl claims cleaning click clinic clinique clothing cloud club clubmed cm cn
co coach codes coffee college cologne com commbank community company compare computer
comsec condos construction consulting contact contractors cooking cool coop corsica country coupon
coupons courses cpa cr credit creditcard creditunion cricket crown crs cruise cruises
cu cuisinella cv cw cx cy cymru cyou cz dad dance data
date dating datsun day dclk dds de deal dealer deals degree delivery
dell deloitte delta democrat dental dentist desi design dev dhl diamonds diet
digital direct directory discount discover dish diy dj dk dm dnp do
docs doctor dog domains dot download drive dtv dubai dupont durban dvag
dvr dz earth eat ec eco edeka edu education ee eg email
emerck energy engineer engineering enterprises epson equipment er ericsson erni es esq
estate et eu eurovision eus events exchange expert exposed express extraspace fage
fail fairwinds faith family fan fans farm farmers fashion fast fedex feedback
ferrari ferrero fi fidelity fido film final finance financial fire firestone firmdale
fish fishing fit fitness fj fk flickr flights flir florist flowers fly
fm fo foo food football ford forex forsale forum foundation fox fr
free fresenius frl frogans frontier ftr fujitsu fun fund furniture futbol fyi
ga gal gallery gallo gallup game games gap garden gay gb gbiz
gd gdn ge gea gent genting george gf gg ggee gh gi
gift gifts gives giving gl glass gle global globo gm gmail gmbh
gmo gmx gn godaddy gold goldpoint golf goodyear goog google gop got
gov gp gq gr grainger graphics gratis green gripe grocery group gs
gt gu gucci guge guide guitars guru gw gy hair hamburg hangout
haus hbo hdfc hdfcbank health healthcare help helsinki here hermes hiphop hisamitsu
hitachi hiv hk hkt hm hn hockey holdings holiday homedepot homegoods homes
homesense honda horse hospital host hosting hot hotels hotmail house how hr
hsbc ht hu hughes hyatt hyundai ibm icbc ice icu id ie
ieee ifm ikano il im imamat imdb immo immobilien in inc industries
infiniti info ing ink institute insurance insure int international intuit investments io
ipiranga iq ir irish is ismaili ist istanbul it itau itv jaguar
java jcb je jeep jetzt jewelry jio jll jm jmp jnj jo
jobs joburg jot joy jp jpmorgan jprs juegos juniper kaufen kddi ke
kerryhotels kerryproperties kfh kg kh ki kia kids kim kindle kitchen kiwi
km kn koeln komatsu kosher kp kpmg kpn kr krd kred kuokgroup
kw ky kyoto kz la lacaixa lamborghini lamer land landrover lanxess lasalle
lat latino latrobe law lawyer lb lc lds lease leclerc lefrak legal
lego lexus lgbt li lidl life lifeinsurance lifestyle lighting like lilly limited
limo lincoln link live living lk llc llp loan loans locker locus
lol london lotte lotto love lpl lplfinancial lr ls lt ltd ltda
lu lundbeck luxe luxury lv ly ma madrid maif maison makeup man
management mango map market marketing markets marriott marshalls mattel mba mc mckinsey
md me med media meet melbourne meme memorial men menu merck merckmsd
mg mh miami microsoft mil mini mint mit mitsubishi mk ml mlb
mls mm mma mn mo mobi mobile moda moe moi mom monash
money monster mormon mortgage moscow moto motorcycles mov movie mp mq mr
ms msd mt mtn mtr mu museum music mv mw mx my
mz na nab nagoya name navy nba nc ne nec net netbank
netflix network neustar new news next nextdirect nexus nf nfl ng ngo
nhk ni nico nike nikon ninja nissan nissay nl no nokia norton
now nowruz nowtv np nr nra nrw ntt nu nyc nz obi
observer office okinawa olayan olayangroup ollo om omega one ong onl online
ooo open oracle orange org organic origins osaka otsuka ott ovh pa
page panasonic paris pars partners parts party pay pccw pe pet pf
pfizer pg ph pharmacy phd philips phone photo photography photos physio pics
pictet pictures pid pin ping pink pioneer pizza pk pl place play
playstation plumbing plus pm pn pnc pohl poker politie porn post pr
praxi press prime pro prod productions prof progressive promo properties property protection
pru prudential ps pt pub pw pwc py qa qpon quebec quest
racing radio re read realestate realtor realty recipes red redumbrella rehab reise
reisen reit reliance ren rent rentals repair report republican rest restaurant review
reviews rexroth rich richardli ricoh ril rio rip ro rocks rodeo rogers
room rs rsvp ru rugby ruhr run rw rwe ryukyu sa saarland
safe safety sakura sale salon samsclub samsung sandvik sandvikcoromant sanofi sap sarl
sas save saxo sb sbi sbs sc scb schaeffler schmidt scholarships school
schule schwarz science scot sd se search seat secure security seek select
sener services seven sew sex sexy sfr sg sh shangrila sharp shell
shia shiksha shoes shop shopping shouji show si silk sina singles site
sj sk ski skin sky skype sl sling sm smart smile sn
sncf so soccer social softbank software sohu solar solutions song sony soy
spa space sport spot sr srl ss st stada staples star statebank
statefarm stc stcgroup stockholm storage store stream studio study style su sucks
supplies supply support surf surgery suzuki sv swatch swiss sx sy sydney
systems sz tab taipei talk taobao target tatamotors tatar tattoo tax taxi
tc tci td tdk team tech technology tel temasek tennis teva tf
tg th thd theater theatre tiaa tickets tienda tips tires tirol tj
tjmaxx tjx tk tkmaxx tl tm tmall tn to today tokyo tools
top toray toshiba total tours town toyota toys tr trade trading training
travel travelers travelersinsurance trust trv tt tube tui tunes tushu tv tvs
tw tz ua ubank ubs ug uk unicom university uno uol ups
us uy uz va vacations vana vanguard vc ve vegas ventures verisign
versicherung vet vg vi viajes video vig viking villas vin vip virgin
visa vision viva vivo vlaanderen vn vodka volvo vote voting voto voyage
vu wales walmart walter wang wanggou watch watches weather weatherchannel web webcam
weber website wed wedding weibo weir wf whoswho wien wiki williamhill win
windows wine winners wme woodside work works world wow ws wtc wtf
xbox xerox xihuan xin xn--11b4c3d xn--1ck2e1b xn--1qqw23a xn--2scrj9c xn--30rr7y xn--3bst00m xn--3ds443g xn--3e0b707e
xn--3hcrj9c xn--3pxu8k xn--42c2d9a xn--45br5cyl xn--45brj9c xn--45q11c xn--4dbrk0ce xn--4gbrim xn--54b7fta0cc xn--55qw42g xn--55qx5d xn--5su34j936bgsg
xn--5tzm5g xn--6frz82g xn--6qq986b3xl xn--80adxhks xn--80ao21a xn--80aqecdr1a xn--80asehdb xn--80aswg xn--8y0a063a xn--90a3ac xn--90ae xn--90ais
xn--9dbq2a xn--9et52u xn--9krt00a xn--b4w605ferd xn--bck1b9a5dre4c xn--c1avg xn--c2br7g xn--cck2b3b xn--cckwcxetd xn--cg4bki xn--clchc0ea0b2g2a9gcd xn--czr694b
xn--czrs0t xn--czru2d xn--d1acj3b xn--d1alf xn--e1a4c xn--eckvdtc9d xn--efvy88h xn--fct429k xn--fhbei xn--fiq228c5hs xn--fiq64b xn--fiqs8s
xn--fiqz9s xn--fjq720a xn--flw351e xn--fpcrj9c3d xn--fzc2c9e2c xn--fzys8d69uvgm xn--g2xx48c xn--gckr3f0f xn--gecrj9c xn--gk3at1e xn--h2breg3eve xn--h2brj9c
xn--h2brj9c8c xn--hxt814e xn--i1b6b1a6a2e xn--imr513n xn--io0a7i xn--j1aef xn--j1amh xn--j6w193g xn--jlq480n2rg xn--jvr189m xn--kcrx77d1x4a xn--kprw13d
xn--kpry57d xn--kput3i xn--l1acc xn--lgbbat1ad8j xn--mgb9awbf xn--mgba3a3ejt xn--mgba3a4f16a xn--mgba7c0bbn0a xn--mgbaam7a8h xn--mgbab2bd xn--mgbah1a3hjkrd xn--mgbai9azgqp6j
xn--mgbayh7gpa xn--mgbbh1a xn--mgbbh1a71e xn--mgbc0a9azcg xn--mgbca7dzdo xn--mgbcpq6gpa1a xn--mgberp4a5d4ar xn--mgbgu82a xn--mgbi4ecexp xn--mgbpl2fh xn--mgbt3dhd xn--mgbtx2b
xn--mgbx4cd0ab xn--mix891f xn--mk1bu44c xn--mxtq1m xn--ngbc5azd xn--ngbe9e0a xn--ngbrx xn--node xn--nqv7f xn--nqv7fs00ema xn--nyqy26a xn--o3cw4h
xn--ogbpf8fl xn--otu796d xn--p1acf xn--p1ai xn--pgbs0dh xn--pssy2u xn--q7ce6a xn--q9jyb4c xn--qcka1pmc xn--qxa6a xn--qxam xn--rhqv96g
xn--rovu88b xn--rvc1e0am3e xn--s9brj9c xn--ses554g xn--t60b56a xn--tckwe xn--tiq49xqyj xn--unup4y xn--vermgensberater-ctb xn--vermgensberatung-pwb xn--vhquv xn--vuq861b
xn--w4r85el8fhu5dnra xn--w4rs40l xn--wgbh1c xn--wgbl6a xn--xhq521b xn--xkc2al3hye2a xn--xkc2dl3a5ee0h xn--y9a3aq xn--yfro4i67o xn--ygbi2ammx xn--zfr164b xxx
xyz yachts yahoo yamaxun yandex ye yodobashi yoga yokohama you youtube yt
yun za zappos zara zero zip zm zone zuerich zw
""".split())

USER_AGENT = f"KBPBuyerResearchBot/{APP_VERSION} (+public-business-research; respects robots.txt)"
EMAIL_RE = re.compile(r"[A-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[^\s<>()\[\]{}\"',;:!?/=\\]+", re.I)
PHONE_RE = re.compile(r"(?:\+?\d[\d\s().-]{7,}\d)")
CONTACT_HINTS = ("contact", "about", "team", "company", "sales", "import", "purchase", "partner", "vendor", "supplier", "lien-he", "gioi-thieu", "hop-tac")
BLOCKED_DOMAINS = {
    "facebook.com", "instagram.com", "linkedin.com", "youtube.com", "tiktok.com", "amazon.com",
    "wikipedia.org", "pinterest.com", "x.com", "twitter.com", "tradekey.com", "alibaba.com",
    "globalsources.com", "petsglobal.com", "pagefly.io", "cosmeticsbusiness.com", "procureradar.com",
    "brainly.com", "indiamart.com", "tradeindia.com", "exporthub.com", "go4worldbusiness.com",
    "scribd.com", "slideshare.net", "issuu.com", "yumpu.com", "academia.edu", "researchgate.net",
    "medium.com", "blogspot.com", "wordpress.com",
    "tradeholding.com", "chinatradeholding.com", "indotrading.com", "globalcosmeticsnews.com",
    "careerlink.vn", "careerviet.vn", "huggingface.co", "kaggle.com", "github.com", "gitlab.com",
    "d7leadfinder.com", "expolume.com", "sourceready.com", "asiapro-distribution.com",
    "vietdata.vn", "mekongcapital.com", "dewsia.com", "sblaw.vn", "lawyer24h.net",
    "hptoancau.com", "meiyume.com", "trueen.com", "zipleaf.us", "eventseye.com",
    "tradeimex.in", "vietnambusinessgateway.com", "consultingroom.com", "trade.gov",
    "whatclinic.com",
    "yellowpages.com.vn", "ensun.io", "studocu.vn", "b2btradeshows.net", "topfranchise.com",
    "ec21.com", "marketinsidedata.com", "bestfoodimporters.com", "turkishexporter.com.tr",
    "vietnamia.org", "europages.co.uk", "volza.com", "cosmeticindex.com", "b2bmap.com",
    "market.us", "themeforest.net", "templatemonster.com", "pro.makeup", "pinterest.ca",
    "pinterest.at", "statista.com", "researchandmarkets.com", "expertmarketresearch.com",
    "goldsupplier.com", "everychina.com", "brandcrowd.com", "rocketreach.co",
    "informamarkets-info.com", "bizhwy.com",
    "personalcare1.com", "vietnam.travel", "sunshine-events.co.il",
    "listcompany.org", "tradewheel.com", "secomm.vn",
    "globaltradeplaza.com", "trangvangvietnam.com", "ecomeye.com", "silverlandhotels.com",
    "banchaidanhrangnano.com", "yelp.com", "dnb.com", "lemon8-app.com",
    "classpass.com", "companydata.com", "abraa.com", "inaexport.id", "manufacturers.com.tw",
    "quora.com", "listofcompaniesin.com",
}
BLOCKED_EMAIL_PARTS = ("example.com", "sentry.io", "wixpress.com", "cloudflare.com", "email.com", "domain.com", "messages.contact",
    ".png", ".jpg", ".jpeg", ".svg", ".webp", ".gif")
BUYER_TERMS = (
    "importer", "import and distribution", "import & distribution", "exclusive distributor", "distributor",
    "distribution company", "wholesaler", "wholesale", "retail chain", "retailer", "buyer", "procurement",
    "nhà nhập khẩu", "nhap khau", "phân phối", "phan phoi", "bán buôn", "ban buon", "bán lẻ", "ban le",
    "aesthetic clinic", "beauty clinic", "dermatology clinic", "beauty salon", "professional salon", "spa",
    "thẩm mỹ viện", "phòng khám da liễu", "spa làm đẹp", "salon làm đẹp",
)
PLATFORM_TERMS = (
    "buying leads directory", "b2b sourcing platform", "global buyer leads", "marketplace", "submit your requirement",
    "signing up", "select industry", "quote now", "software platform", "news and analysis", "trade publication",
    "lead finder", "find business leads", "ai-powered sourcing platform", "find suppliers", "supplier database",
    "search for leads", "verified leads", "company database", "export leads", "sales intelligence",
    "buying demand", "selling demand", "business opportunity", "all projects", "project listing",
    "post a project", "investment projects", "buyer request board", "seller request board",
    "add new company listing", "free company listing", "list of companies",
)
# 검색엔진 단계에서만 제외한다. 제조·수출·공급업체는 전략 후보로 보존해야
# 하므로 검색어에서 일괄 제외하지 않는다.
QUERY_EXCLUDE_TERMS = (
    "jobs", "job", "career", "recruitment", "news", "directory",
    "marketplace", "buying leads", "lead platform", "yelp", "lemon8", "d&b",
)
CONTENT_SOURCE_TERMS = (
    "news", "magazine", "academy", "university", "training course", "blog", "document library",
    "market report", "industry report", "price list", "review article", "tin tức", "học viện", "đào tạo",
)
NON_COMPANY_TITLE_TERMS = (
    "job", "jobs", "career", "recruitment", "hiring", "directory", "marketplace", "buying leads",
    "market report", "industry report", "news", "academy", "training", "verifying", "cookie required",
    "tuyển dụng", "việc làm", "danh bạ", "tin tức",
)
NON_COMPANY_PATH_TERMS = (
    "/job/", "/jobs/", "/career/", "/careers/", "/recruitment/", "/news/", "/blog/", "/article/",
    "/directory", "/buying-lead", "/market-report", "/industry-report",
)
STRONG_BUYER_TERMS = (
    "importer", "exclusive distributor", "authorized distributor", "wholesaler", "wholesale distributor",
    "retail chain", "distribution company", "nhà nhập khẩu", "nhà phân phối", "bán buôn", "bán lẻ",
)
PACKAGING_ONLY_TERMS = (
    "cosmetic packaging", "beauty packaging", "packaging supplier", "packaging manufacturer",
    "bao bì mỹ phẩm", "chai lọ mỹ phẩm", "bottle packaging", "container packaging",
)
MANUFACTURER_TERMS = (
    "we manufacture", "our factory", "manufacturing facility", "production plant", "production factory",
    "we are a manufacturer", "manufacturer of", "manufacturer", "we produce", "producer of", "contract manufacturer",
    "oem manufacturer", "odm manufacturer", "oem/odm", "private label manufacturer",
    "nhà máy sản xuất", "cơ sở sản xuất", "gia công mỹ phẩm", "sản xuất mỹ phẩm", "nhà sản xuất", "xưởng sản xuất",
    "trực tiếp thiết kế và chế tạo", "thiết kế và chế tạo", "tự chủ hoàn toàn khâu thiết kế",
    "gia công và tự động hóa", "năng lực gia công cơ khí",
)
NEGATED_DISTRIBUTOR_TERMS = (
    "không phải đơn vị phân phối", "không phải nhà phân phối",
    "not a distributor", "we are not a distributor",
)
SUPPLIER_BUYER_TERMS = (
    "chuyên cung cấp", "nhà cung cấp", "cung cấp các loại", "cung cấp máy",
    "officially imported", "authorized supplier", "industrial equipment supplier",
)
BUYER_IDENTITY_TERMS = (
    "importer", "distributor", "wholesale", "we import", "imports and distributes", "import and distribute", "import and distribution",
    "importing and distributing", "specializing in the import", "exclusive distributor",
    "authorized distributor", "distribution company", "wholesale distributor", "wholesaler",
    "retail chain", "wholesale supplier", "beauty supplier", "cosmetics supplier", "aesthetic clinic", "beauty clinic", "dermatology clinic", "beauty salon",
    "professional salon", "nhà nhập khẩu", "nhap khau", "nhập khẩu và phân phối",
    "nhap khau va phan phoi", "nhà phân phối", "phân phối", "phan phoi", "cung ứng và phân phối",
    "cung ung va phan phoi", "hệ thống phân phối", "he thong phan phoi", "phân phối độc quyền",
    "đại lý", "dai ly", "bán buôn", "bán lẻ",
    "aesthetic clinic", "beauty clinic", "dermatology clinic", "skin clinic", "cosmetic clinic",
    "beauty salon", "professional salon", "medical spa", "beauty spa", "thẩm mỹ viện",
    "thẩm mỹ", "phòng khám", "phong kham", "phòng khám da liễu", "spa làm đẹp", "salon làm đẹp",
    "cửa hàng mỹ phẩm", "cửa hàng phân phối", "hệ thống cửa hàng", "tìm cửa hàng",
)
INVESTMENT_TERMS = (
    "private equity", "venture capital", "investment firm", "investment fund", "growth capital",
    "portfolio companies", "portfolio by sectors", "investment criteria", "asset management",
)
LEGAL_TERMS = (
    "law firm", "lawyers", "legal services", "legal consulting", "law office", "trademark registration",
    "dispute resolution", "employment law", "intellectual property law",
)
LOGISTICS_TERMS = (
    "logistics company", "logistics service", "international shipping", "freight forwarding",
    "freight service", "customs service", "customs broker", "customs brokerage", "customs declaration",
    "cargo transportation", "import procedure service", "shipping service", "fulfillment", "warehouse management",
    "warehousing", "last-mile delivery", "last mile delivery", "order processing",
)
STRONG_RESEARCH_MEDIA_TERMS = (
    "market research", "industry research", "company research", "economic data", "macro database",
    "editorial platform", "editorials & analysis", "news editorials", "consumer guides",
    "industry publication", "media platform", "magazine", "e-magazine",
    "newspaper", "news portal", "báo điện tử", "tạp chí điện tử",
    "bao dien tu", "tap chi dien tu", "thời báo", "thoi bao", "tạp chí", "tap chi", "đài truyền hình",
    "dai truyen hinh", "cơ quan trung ương", "co quan trung uong", "tòa soạn", "toa soan",
    "ban biên tập", "ban bien tap", "phóng viên", "phong vien",
    "news & review", "news and review", "digital cover", "subscribe to the newsletter",
)
KNOWN_MEDIA_DOMAINS = {
    "vietcetera.com", "vietnamnet.vn", "vietnamnews.vn", "vtv.vn", "cafef.vn", "nguoiduatin.vn",
    "thuonghieucongluan.com.vn", "the-shiv.com", "kenh14.vn",
}
EXHIBITION_IDENTITY_TERMS = (
    "international trade exhibition", "trade exhibition",
    "triển lãm thương mại", "trien lam thuong mai", "triển lãm quốc tế", "trien lam quoc te",
    "hội chợ thương mại", "hoi cho thuong mai",
)
WEAK_RESEARCH_MEDIA_TERMS = ("brand news", "product reviews", "news", "academy", "blog")
AGENCY_TERMS = (
    "company registration", "market entry service", "business consulting", "business advisory",
    "licensing service", "regulatory consulting", "consulting service", "incorporation & compliance",
    "business setup", "corporate amendments", "product registration service",
)
KNOWN_DIRECTORY_DOMAINS = {"infoisinfo-ca.com", "infoisinfo.com", "listcompany.org", "tradewheel.com", "timnhaphanphoi.vn", "top10tphcm.com"}
EQUIPMENT_ONLY_TERMS = (
    "medical equipment", "aesthetic equipment", "ophthalmic equipment", "beauty equipment",
    "medical device", "aesthetic device", "laser equipment", "surgical equipment",
)
SOFTWARE_SERVICE_TERMS = (
    "spa and salon software", "salon software", "clinic software", "booking software",
    "appointment software", "point of sale software", "pos software", "business management software",
    "sales management software", "omnichannel management", "ecommerce software", "e-commerce software",
    "phần mềm quản lý bán hàng", "phần mềm bán hàng", "phần mềm quản lý", "nhanh.pos", "nhanh.ship",
)
# These are service identities, not incidental words such as 'software' or 'import'.
SERVICE_IDENTITY_GROUPS = {
    "임상시험·연구대행": (
        "contract research organization", "clinical trials cro", "clinical research organization",
        "clinical trials", "feasibility assessments", "ba/be studies",
    ),
    "소프트웨어·IT서비스": (
        "shoppable media", "where to buy tools", "commerce intelligence", "commerce orchestration",
        "commerce enablement platform", "commerce enable commerce everywhere",
    ),
    "업무대행·콜센터": (
        "live answering service", "virtual receptionist", "salon outsourcing", "medspa outsourcing",
        "virtual salesforce", "call center services",
    ),
}
TOURISM_TERMS = (
    "official tourism website", "tourism authority", "tourism board", "tourism office",
    "national tourism", "travel guide", "tourist information", "visit vietnam",
)
GAMBLING_SPAM_TERMS = (
    "online casino", "casino games", "sports betting", "sportsbook", "slot games",
    "slot88", "topslot", "betting site", "jackpot",
)
FULFILLMENT_CORE_TERMS = (
    "fulfillment", "warehouse management", "order processing", "last-mile delivery", "last mile delivery",
)
RETAIL_OWN_BRAND_TERMS = (
    "shopping cart", "add to cart", "flash sale", "free shipping", "retail price", "shop now",
    "giỏ hàng", "mua hàng", "mua online", "đặt hàng", "ưu đãi", "cửa hàng", "tìm cửa hàng",
    "miễn phí giao hàng", "sản phẩm yêu thích",
)
MULTIBRAND_RETAIL_TERMS = (
    "multi-brand", "multibrand", "shop by brand", "brands we carry", "authorized retailer",
    "authorized dealer", "official retailer", "official dealer", "genuine cosmetics",
    "mỹ phẩm chính hãng", "hàng chính hãng", "đại lý chính hãng", "giấy chứng nhận đại lý",
    "các thương hiệu", "nhiều thương hiệu", "chuỗi cửa hàng", "hệ thống cửa hàng",
)
FIRST_PARTY_BRAND_TERMS = (
    "our brand", "our own brand", "our products are", "brand story", "official brand website",
    "câu chuyện thương hiệu", "thương hiệu của chúng tôi", "sản phẩm của chúng tôi",
)
CORPORATE_BRAND_OWNER_TERMS = (
    "our brands", "brand portfolio", "brand owner", "global brands", "house of brands",
    "investors & shareholders", "investors and shareholders", "annual report", "corporate governance",
    "groupe", "our purpose", "research & innovation", "research and innovation",
)
HIGH_CONFIDENCE_DISTRIBUTION_TERMS = (
    "importer", "we import", "imports and distributes", "exclusive distributor", "authorized distributor",
    "distribution company", "wholesale distributor", "nhà nhập khẩu", "nhập khẩu và phân phối",
    "nhà phân phối", "phân phối độc quyền", "hệ thống phân phối",
    "nhập khẩu chính hãng", "xuất nhập khẩu", "xuat nhap khau",
    "chuyên cung cấp", "nhà cung cấp", "cung cấp các loại", "cung cấp máy",
)
EXPORT_SELLER_TERMS = (
    "wholesale exporter", "source for importers", "destination for importers", "we export",
    "export products", "exporting products", "oversea clients", "overseas clients",
    "products from vietnam", "source goods from vietnam", "export partner", "export supplier",
    "supplier for importers", "for overseas buyers", "serving overseas buyers",
    "products from thailand", "products from indonesia", "products from japan", "products from taiwan",
    "products from germany", "products from france", "products from mexico", "products from uae",
    "made in thailand", "made in indonesia", "made in japan", "made in taiwan", "made in mexico",
    "exportación", "exportacion", "exportateur", "exporteur", "exporter of",
)
INBOUND_IMPORT_TERMS = (
    "importer", "imported brands", "we import", "imports and distributes", "import and distribute", "import and distribution",
    "importing and distributing", "specializing in the import", "our import products",
    "nhà nhập khẩu", "nhập khẩu", "xuất nhập khẩu", "xuat nhap khau", "xnk", "công ty nhập khẩu",
    "nhập khẩu và phân phối", "nhap khau va phan phoi",
)
ECOSYSTEM_SOURCE_TERMS = (
    "exhibitor", "exhibitors", "exhibition", "expo", "trade fair", "member directory",
    "member companies", "association", "show directory", "danh sách doanh nghiệp", "hiệp hội",
)
SEARCH_PROFILES = {
    "정확도 우선": ("공식기업",),
    "균형": ("공식기업", "현지시장"),
    "최대수집": ("공식기업", "현지시장", "전시회·협회"),
}
DISCOVERY_OVERSAMPLE = {"정확도 우선": 1.8, "균형": 2.5, "최대수집": 3.0}
KNOWN_COUNTRY_TLDS = {"vn","jp","th","id","tw","de","fr","mx","ae","au","uk","sg","my","ph","tr","il","us","ca","cn","in","kr"}
INDUSTRY_TERMS = {
    "화장품": ("cosmetic", "cosmetics", "skincare", "skin care", "beauty", "makeup", "personal care", "nail", "nail care", "nailbox", "manicure", "gel polish", "móng", "chăm sóc móng", "mỹ phẩm", "my pham", "chăm sóc da"),
    "뷰티": ("beauty", "cosmetic", "cosmetics", "skincare", "skin care", "makeup", "hair care", "personal care", "nail", "nail care", "nailbox", "manicure", "gel polish", "móng", "chăm sóc móng", "mỹ phẩm", "làm đẹp"),
    "식품": ("food", "foods", "beverage", "grocery", "groceries", "snack", "processed food", "thực phẩm", "đồ uống"),
    "건강식품": ("health food", "supplement", "nutraceutical", "functional food", "vitamin", "dietary", "thực phẩm chức năng"),
    "의료기기": ("medical device", "medical equipment", "diagnostic", "healthcare equipment", "hospital equipment", "thiết bị y tế"),
    "생활용품": ("household", "home care", "consumer goods", "daily necessities", "cleaning product", "personal care", "hàng tiêu dùng"),
}
LOCAL_BUSINESS_MARKERS = {
    "Vietnam": ("công ty", "trang chủ", "liên hệ", "sản phẩm", "hệ thống phân phối", "phân phối", "cửa hàng"),
    "Japan": ("株式会社", "会社概要", "お問い合わせ", "販売店", "輸入", "卸売"),
    "Thailand": ("บริษัท", "ติดต่อ", "จำหน่าย", "นำเข้า", "ผู้จัดจำหน่าย"),
    "Indonesia": ("perusahaan", "hubungi kami", "distributor", "impor", "grosir"),
    "Germany": ("unternehmen", "kontakt", "impressum", "großhandel", "importeur"),
    "France": ("société", "contact", "distributeur", "importateur", "grossiste"),
    "Taiwan": ("公司", "聯絡我們", "進口", "代理", "經銷", "批發"),
    "Mexico": ("empresa", "contacto", "importador", "distribuidor", "mayorista"),
    "United Arab Emirates": ("trading llc", "general trading", "fzco", "dubai", "distribution"),
}

GENERIC_PRODUCT_TERMS = {
    "product", "products", "personal", "care", "professional", "premium", "korean",
    "goods", "item", "items", "company", "brand", "brands",
}
LOCATION_HINTS = (
    "address", "head office", "headquarters", "registered office", "located", "based in",
    "office in", "địa chỉ", "dia chi", "trụ sở", "tru so",
)
PHONE_HINTS = (
    "phone", "telephone", "tel", "hotline", "mobile", "call us", "điện thoại", "dien thoai",
    "số điện thoại", "so dien thoai", "liên hệ", "lien he",
)
NON_PHONE_HINTS = (
    "business code", "registration number", "registration no", "company number", "tax code", "tax id",
    "enterprise code", "license number", "mã số doanh nghiệp", "ma so doanh nghiep", "mã số thuế",
    "ma so thue", "đkkd", "gpkd", "giấy cnđkdn", "cnđkdn", "giay cndkdn", "cndkdn",
)
CONTACT_PATH_HINTS = (
    "contact", "contact-us", "lien-he", "lienhe", "kontakt", "contato", "contacto", "contacts",
    "reach-us", "support", "customer-service",
)
COMMON_CONTACT_PATHS = (
    "contact", "contact-us", "contacts", "lien-he", "lien-he/", "lienhe",
    "hoi-dap/lien-he", "pages/contact", "pages/lien-he", "gioi-thieu/lien-he",
    "support", "customer-service",
)
EMAIL_PURPOSES = {
    "recruitment": "채용", "recruit": "채용", "career": "채용", "hiring": "채용", "jobs": "채용", "hr": "채용",
    "tuyendung": "채용", "nhansu": "채용", "vieclam": "채용", "toasoan": "언론·편집",
    "sales": "B2B·영업", "business": "B2B·제휴", "partner": "B2B·제휴", "partnership": "B2B·제휴",
    "vendor": "B2B·구매", "purchase": "B2B·구매", "procurement": "B2B·구매", "export": "B2B·영업",
    "info": "일반문의", "contact": "일반문의", "hello": "일반문의", "admin": "일반문의",
    "support": "고객지원", "cskh": "고객지원", "care": "고객지원",
    "leasing": "임대·입점", "lease": "임대·입점", "cho-thue": "임대·입점", "chothue": "임대·입점",
    "privacy": "개인정보·법무", "legal": "개인정보·법무", "abuse": "개인정보·법무",
}
NON_SENDABLE_EMAIL_LOCALS = {"hr","humanresources","recruit","recruitment","career","careers","job","jobs","hiring",
    "support","help","helpdesk","customer","customerservice","service","cskh","cs","press","media","editor","newsroom",
    "privacy","legal","grievance","billing","accounting","webmaster","noreply","no-reply",
    "tuyendung","nhansu","vieclam","toasoan"}
# 공식 홈페이지에서 확인한 주소는 개인명·부서·대표메일을 구분하지 않고
# 메일링 후보로 보존한다. 다만 실제 수신이 불가능한 자동응답 주소만 제외한다.
NON_MAILING_EMAIL_LOCALS = {"noreply", "no-reply", "donotreply", "do-not-reply"}
MAILING_EMAIL_STATUSES = {"공식확인", "검증완료", "외부확인", "검증필요"}
MAILING_PRIORITIES = {"A", "B", "C", "전략"}


@dataclass
class CollectionConfig:
    region: str
    keywords: list[str]
    industry: str
    product: str
    verified_email_target: int
    candidate_limit: int
    exclude_keywords: list[str]
    countries: list[str] = field(default_factory=list)
    target_per_country: int = 10
    request_delay: float = 0.35
    max_pages_per_company: int = 4
    worker_count: int = 8
    use_hunter: bool = True
    verify_hunter: bool = True
    include_external_sendable: bool = True
    include_cross_domain_sendable: bool = False
    search_mode: str = "균형"
    api_usage_mode: str = "전체 실검색"
    search_provider: str = "Brave"
    max_search_queries: int = 0
    search_strategy: str = "적응형 최적화"
    qualified_candidate_target: int = 0
    base_keyword_count: int = 5
    collection_purpose: str = "수출 바이어 발굴"
    industry_groups: list[dict] = field(default_factory=list)
    major_industry: str = ""
    subcategories: list[str] = field(default_factory=list)
    refill_enabled: bool = True


@dataclass
class BuyerRecord:
    company_id: str
    company_name: str
    country_region: str
    business_description: str
    website: str
    brand_name: str = ""
    target_country: str = ""
    verified_country: str = ""
    company_email: str = ""
    email_candidates: list[dict] = field(default_factory=list)
    discovered_countries: list[str] = field(default_factory=list)
    country_assessments: list[dict] = field(default_factory=list)
    contact_name: str = ""
    contact_title: str = ""
    contact_email: str = ""
    phone: str = ""
    original_keyword: str = ""
    search_query: str = ""
    discovery_source: str = ""
    discovery_url: str = ""
    candidate_score: int = 0
    company_source_url: str = ""
    email_source_url: str = ""
    email_status: str = "미확보"
    email_domain_status: str = "미확보"
    email_grade: str = "D"
    verification_score: int | None = None
    evidence_status: str = "추가확인"
    country_evidence: str = ""
    country_score: int = 0
    industry_score: int = 0
    buyer_role_score: int = 0
    relevance_score: int = 0
    site_type: str = "기업후보"
    buyer_type: str = "미분류"
    secondary_buyer_type: str = ""
    identity_review_reason: str = ""
    grade_reason: str = ""
    priority: str = "C"
    decision_evidence: str = ""
    email_purpose: str = ""
    quality_decision: str = "추가검토"
    exclusion_reason: str = ""
    collection_depth: str = ""
    selected_industries: str = ""
    selected_subcategories: str = ""
    matched_industries: str = ""
    industry_assessments: list[dict] = field(default_factory=list)
    collected_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.text=[]; self.links=[]; self.href=""; self.anchor=[]; self.site_name=""; self.title=[]; self.hidden_depth=0; self.in_title=False
    def handle_starttag(self, tag, attrs):
        tag=tag.lower()
        if tag in {"script","style","noscript","svg","template"}:
            self.hidden_depth+=1
            return
        if self.hidden_depth: return
        values=dict(attrs)
        if tag=="title": self.in_title=True
        if tag=="a": self.href=values.get("href") or ""; self.anchor=[]
        if tag=="meta":
            label=(values.get("property") or values.get("name") or "").lower()
            if label in {"og:site_name","application-name"} and values.get("content"): self.site_name=values["content"]
    def handle_data(self, data):
        if self.hidden_depth: return
        value=" ".join(data.split())
        if value:
            self.text.append(value)
            if self.in_title: self.title.append(value)
            if self.href: self.anchor.append(value)
    def handle_endtag(self, tag):
        tag=tag.lower()
        if tag in {"script","style","noscript","svg","template"}:
            self.hidden_depth=max(0,self.hidden_depth-1)
            return
        if self.hidden_depth: return
        if tag=="title": self.in_title=False
        if tag=="a" and self.href:
            self.links.append((self.href," ".join(self.anchor))); self.href=""; self.anchor=[]


def domain(url: str) -> str:
    return (urllib.parse.urlsplit(url).hostname or "").lower().removeprefix("www.")


def registrable_domain(url_or_host: str) -> str:
    host=domain(url_or_host) if "://" in url_or_host else url_or_host.lower().removeprefix("www.")
    parts=host.split(".")
    if len(parts)<=2: return host
    multi={"com.vn","co.uk","com.au","co.jp","com.sg","com.my","co.id","co.th","com.ph","com.tr","co.il"}
    return ".".join(parts[-3:]) if ".".join(parts[-2:]) in multi else ".".join(parts[-2:])


def root_url(url: str) -> str:
    if not urllib.parse.urlsplit(url).scheme: url="https://"+url
    p=urllib.parse.urlsplit(url)
    return urllib.parse.urlunsplit((p.scheme,p.netloc,"/","",""))


def make_id(host: str) -> str:
    return "CMP-"+hashlib.sha256(host.encode()).hexdigest()[:12].upper()


@lru_cache(maxsize=8192)
def normalize_email(raw: str) -> str:
    """Validate one extracted address locally; do not invent or test a mailbox."""
    value=html_lib.unescape(urllib.parse.unquote(str(raw or ""))).strip()
    if value.lower().startswith("mailto:"):
        value=value[7:].split("?",1)[0]
    value=value.strip(" \t\r\n<>\"'").rstrip(".,;:")
    if not EMAIL_RE.fullmatch(value) or value.count("@")!=1: return ""
    local,host=value.lower().split("@",1)
    try: host=host.encode("idna").decode("ascii")
    except UnicodeError: return ""
    labels=host.split(".")
    if (len(local)>64 or len(value)>254 or local.startswith(".") or local.endswith(".") or ".." in local
            or len(labels)<2 or labels[-1] not in IANA_TLDS
            or any(not re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?",label) for label in labels)):
        return ""
    email=local+"@"+host
    if any(part in email for part in BLOCKED_EMAIL_PARTS): return ""
    return email


def decode_obfuscated_emails(text: str) -> str:
    value=html_lib.unescape(str(text or ""))
    # Never replace 'at' inside 'international', 'contact' or literal mail addresses.
    # Only decode complete address-shaped spans, not arbitrary prose.
    at=r"(?:\s*\[\s*at\s*\]\s*|\s*\(\s*at\s*\)\s*|\s*\[골뱅이\]\s*)"
    dot=r"(?:\s*\[\s*dot\s*\]\s*|\s*\(\s*dot\s*\)\s*|\s*\[점\]\s*|\.)"
    pattern=rf"([A-Z0-9._%+-]+){at}([A-Z0-9-]+(?:{dot}[A-Z0-9-]+)+)"
    def decode(match):
        address=match[1]+"@"+re.sub(dot,".",match[2],flags=re.I)
        return normalize_email(address) or match[0]
    value=re.sub(pattern,decode,value,flags=re.I)
    return value


def email_purpose(email: str) -> str:
    local=str(email or "").split("@",1)[0].lower()
    return next((label for token,label in EMAIL_PURPOSES.items() if token in local),"업무용·용도확인")


def email_is_sendable(email: str) -> bool:
    """형식상 유효하고 실제 수신함을 가리키는 주소인지 확인한다.

    역할 주소(support/info/HR 포함)는 우선순위·용도 정보로만 남기고,
    회사 공식 홈페이지에서 공개된 주소라면 메일링 후보에서 임의로 제거하지 않는다.
    """
    local=str(email or "").split("@",1)[0].lower().strip()
    compact=re.sub(r"[^a-z0-9]+","",local)
    host=str(email or "").rsplit("@",1)[-1].lower().strip()
    placeholder = host in {"addresshere.com", "example.com", "example.org", "example.net", "yourdomain.com"}
    return bool(local) and not placeholder and compact not in NON_MAILING_EMAIL_LOCALS and bool(normalize_email(email))


def mailing_candidate(record: BuyerRecord | dict, include_external: bool = True, include_other_country: bool = False, include_reference: bool = False) -> bool:
    """A/B/C/전략 등급의 유효 이메일을 외부 메일링용으로 제공한다.

    등급은 우선순위이지 발송 자격이 아니다. 단, 플랫폼·미디어 등 완전 제외와
    명백한 자동응답·검증실패 주소는 제외한다. 실제 발송 여부는 외부 메일 서비스와
    담당자의 최종 검수에서 결정한다.
    """
    getter = record.get if isinstance(record, dict) else lambda key, default="": getattr(record, key, default)
    status = getter("email_status", "")
    other_country = (include_other_country and getter("quality_decision", "") == "타국가후보"
                     and getter("industry_score", 0) > 0
                     and bool(getter("email_source_url", "")))
    reference = (include_reference and getter("quality_decision", "") == "참고기업"
                 and getter("industry_score", 0) > 0
                 and status == "공식확인" and bool(getter("email_source_url", "")))
    if status == "외부확인" and not include_external:
        return False
    return (
        (getter("priority", "") in MAILING_PRIORITIES or other_country or reference)
        and status in MAILING_EMAIL_STATUSES
        and email_is_sendable(getter("company_email", ""))
        and getter("email_grade", "") != "제외"
        and getter("quality_decision", "") != "제외"
        and (getter("quality_decision", "") != "참고기업" or reference)
    )


def company_name_key(value: str) -> str:
    """국가별 도메인이 달라도 동일 회사 표기를 비교할 수 있게 정규화한다."""
    return re.sub(r"[^\w]+", "", (value or "").casefold(), flags=re.UNICODE)


EMAIL_FIELDS = ("company_email", "email_source_url", "email_status", "email_domain_status",
                "email_grade", "email_purpose", "verification_score")


def email_variants(record: BuyerRecord | dict) -> list[dict]:
    """Backwards-compatible address views; email metadata never overrides company quality."""
    row=asdict(record) if isinstance(record,BuyerRecord) else dict(record)
    choices=[{key:row.get(key,"") for key in EMAIL_FIELDS}]
    choices.extend(row.get("email_candidates") or [])
    by_email={}
    for choice in choices:
        email=normalize_email(str(choice.get("company_email") or ""))
        if not email: continue
        view={**row, **{key:choice[key] for key in EMAIL_FIELDS if key in choice}, "company_email":email}
        # Newly preserved extra addresses must carry their own discovery source.
        if choice is not choices[0] and not choice.get("email_source_url"): continue
        current=by_email.get(email)
        if current is None or contact_source_priority(view.get("email_source_url", ""))>contact_source_priority(current.get("email_source_url", "")):
            by_email[email]=view
    return list(by_email.values())


def mailing_rows(records: list, include_external: bool=True, include_other_country: bool=False,
                 include_reference: bool=False) -> list[dict]:
    """One normalized address per row, even when multiple companies share an address."""
    selected={}
    grade_rank={"A":0,"B":1,"C":2,"전략":3,"타국가":4,"참고":5}
    ordered=sorted(records,key=lambda r:(grade_rank.get((r.get("priority") if isinstance(r,dict) else r.priority),9),
                                         (r.get("company_id","") if isinstance(r,dict) else r.company_id)))
    for record in ordered:
        for row in email_variants(record):
            if not mailing_candidate(row,include_external,include_other_country,include_reference): continue
            email=row["company_email"]
            if email not in selected:
                selected[email]=dict(row,related_company_ids=[],email_source_urls=[])
            saved=selected[email]
            for key,value in (("related_company_ids",row.get("company_id","")),("email_source_urls",row.get("email_source_url",""))):
                if value and value not in saved[key]: saved[key].append(value)
    return list(selected.values())


def record_rank(record: BuyerRecord) -> tuple:
    # Completion timing must not determine which country/identity survives.
    grades={"A":7,"B":6,"전략":5,"C":4,"타국가":3,"참고":2,"제외":0}
    return (grades.get(record.priority,1), bool(record.verified_country), record.country_score,
            record.relevance_score, bool(normalize_email(record.company_email)), record.candidate_score,
            record.company_id, record.target_country)


def country_assessment(record: BuyerRecord) -> dict:
    return {key:getattr(record,key) for key in ("target_country","verified_country","country_score",
            "country_evidence","quality_decision","priority","discovery_url")}


def deduplicate_records(records: list[BuyerRecord]) -> list[BuyerRecord]:
    """Merge repeated companies without losing better country evidence or extra emails."""
    seen_hosts={}
    seen_name_email={}
    unique: list[BuyerRecord] = []
    for record in sorted(records,key=record_rank,reverse=True):
        host=domain(record.website)
        email_host=registrable_domain(record.company_email.split("@")[-1]) if record.company_email else ""
        alias=(str(record.target_country or "").casefold(),company_name_key(record.company_name),email_host)
        existing=(seen_hosts.get(host) if host else None) or (seen_name_email.get(alias) if email_host and alias[1] else None)
        if existing is not None:
            for field_name in ("selected_industries", "selected_subcategories", "matched_industries"):
                values = (getattr(existing, field_name) + " | " + getattr(record, field_name)).split(" | ")
                setattr(existing, field_name, " | ".join(dict.fromkeys(v for v in values if v)))
            assessments = existing.industry_assessments + record.industry_assessments
            existing.industry_assessments = list({json.dumps(a,sort_keys=True,ensure_ascii=False):a for a in assessments}.values())
            existing.discovered_countries=sorted(set(existing.discovered_countries+record.discovered_countries+[record.target_country])-{''})
            assessments=existing.country_assessments+(record.country_assessments or [country_assessment(record)])
            existing.country_assessments=list({json.dumps(item,sort_keys=True,ensure_ascii=False):item for item in assessments}.values())
            # Excluded identities cannot add addresses to an otherwise valid company.
            if record.quality_decision!="제외":
                variants=email_variants(existing)+email_variants(record)
                existing.email_candidates=[{key:v.get(key,"") for key in EMAIL_FIELDS} for v in variants if v.get("email_source_url")]
                if not normalize_email(existing.company_email):
                    recovered=next((v for v in variants if email_is_sendable(v["company_email"])),None)
                    if recovered:
                        for key in EMAIL_FIELDS: setattr(existing,key,recovered.get(key,""))
            seen_hosts[host]=existing
        else:
            if not record.discovered_countries: record.discovered_countries=[record.target_country] if record.target_country else []
            if not record.country_assessments: record.country_assessments=[country_assessment(record)]
            unique.append(record)
            if host: seen_hosts[host]=record
            if email_host and alias[1]: seen_name_email[alias]=record
    return unique


def finalize_email_delivery_grade(record: BuyerRecord) -> None:
    """회사 적합성과 이메일 발송 적합성을 혼동하지 않도록 최종 등급을 보정한다."""
    if record.company_email and not email_is_sendable(record.company_email):
        record.email_grade="용도제외"
        record.evidence_status="발송제외·"+(record.evidence_status or "용도확인")


def email_candidate_sort_key(email: str, source_rank: int=0) -> tuple:
    """발송 가능 여부와 실제 해외영업·제휴 적합도를 함께 반영한다.

    sales/export/partner 같은 담당 주소를 info/admin 등의 일반 대표주소보다
    먼저 선택하되, 채용·고객지원 주소는 계속 최하위로 둔다.
    """
    purpose=email_purpose(email)
    local=str(email or "").split("@",1)[0].lower()
    role_rank=(
        0 if any(token in local for token in ("export","oversea","international","foreign","global","partner","partnership","business","bd","sales"))
        else 1 if purpose.startswith("B2B")
        else 2 if purpose=="일반문의"
        else 3
    )
    return (0 if email_is_sendable(email) else 1,role_rank,-source_rank,email)


def valid_email(raw: str) -> bool:
    return bool(normalize_email(raw))


def is_blocked_domain(host: str) -> bool:
    base=registrable_domain(host)
    return any(base==x or base.endswith("."+x) for x in BLOCKED_DOMAINS)


def clean_phone(raw: str, country: str) -> str:
    value=" ".join(str(raw or "").split()).strip(" .-()")
    value=re.sub(r"^\+(\d+)\)\s*",r"+\1 ",value)
    value=re.sub(r"^(\d+)\)\s*",r"\1 ",value)
    digits=re.sub(r"\D","",value)
    if len(digits)<9 or len(digits)>15: return ""
    if country=="Vietnam" and digits.startswith("0") and not digits.startswith(("02","03","05","07","08","09","18","19")):
        return ""
    dial=country_meta(country)["dial"]
    if dial and not (value.startswith("+"+dial) or digits.startswith(dial) or digits.startswith("0")): return ""
    return value


@lru_cache(maxsize=2048)
def _term_regex(term: str):
    return re.compile(rf"(?<![a-z0-9]){re.escape(term)}(?![a-z0-9])")


def term_present(text: str, term: str) -> bool:
    text=(text or "").lower(); term=(term or "").lower().strip()
    if not term: return False
    if term.isascii():
        return bool(_term_regex(term).search(text))
    return term in text


def extract_phone_candidates(text: str) -> list[str]:
    """전화 문맥을 우선하고 사업자·세금·등록번호 문맥은 제거한다."""
    ranked=[]
    for match in PHONE_RE.finditer(text or ""):
        raw=match.group(0).strip()
        prefix=text[max(0,match.start()-100):match.start()].lower()
        suffix=text[match.end():min(len(text),match.end()+100)].lower()
        phone_pos=max((prefix.rfind(term) for term in PHONE_HINTS),default=-1)
        non_phone_pos=max((prefix.rfind(term) for term in NON_PHONE_HINTS),default=-1)
        phone_after=min((suffix.find(term) for term in PHONE_HINTS if term in suffix),default=-1)
        non_phone_after=min((suffix.find(term) for term in NON_PHONE_HINTS if term in suffix),default=-1)
        has_phone_hint=phone_pos>=0 or phone_after>=0
        if non_phone_pos>phone_pos or (non_phone_after>=0 and (phone_after<0 or non_phone_after<phone_after)):
            continue
        ranked.append((1 if has_phone_hint else 0,match.start(),raw))
    ranked.sort(key=lambda row:(-row[0],row[1]))
    return list(dict.fromkeys(raw for _,_,raw in ranked))[:10]


def contact_source_priority(url: str) -> int:
    parsed=urllib.parse.urlsplit(url or "")
    path=f"{parsed.path} {parsed.query}".lower()
    if any(term in path for term in ("partner", "partnership", "cooperation", "business", "export", "international", "oversea", "vendor", "supplier", "doi-tac", "hop-tac")): return 5
    if any(term in path for term in CONTACT_PATH_HINTS): return 4
    if any(term in path for term in ("about", "company", "gioi-thieu")): return 2
    if any(term in path for term in ("news", "blog", "article", "academy", "course", "report")): return 0
    return 1


def explicit_contact_urls(base_url: str) -> list[str]:
    root=root_url(base_url)
    return [urllib.parse.urljoin(root,path) for path in COMMON_CONTACT_PATHS]


def buyer_type_from_text(text: str, company_name: str="") -> str:
    name=(company_name or "").lower()
    clinic_terms=("clinic","spa","salon","thẩm mỹ viện","tham my vien","phòng khám","phong kham")
    if any(term_present(name,term) for term in clinic_terms):
        return "클리닉·살롱"
    checks=(
        ("수입·유통사",("importer","we import","imports and distributes","nhà nhập khẩu","nhập khẩu",
                     "nhập khẩu chính hãng","xuất nhập khẩu","xuat nhap khau","nhập khẩu và phân phối")),
        ("유통사",("exclusive distributor","authorized distributor","distribution company","distributor","nhà phân phối","phân phối","phan phoi","cung ứng và phân phối","hệ thống phân phối","phân phối độc quyền","đại lý")+SUPPLIER_BUYER_TERMS),
        ("도매사",("wholesaler","wholesale distributor","wholesale","bán buôn")),
        ("소매체인",("retail chain","retailer","bán lẻ","cửa hàng mỹ phẩm","cửa hàng phân phối","hệ thống cửa hàng","tìm cửa hàng")),
        ("클리닉·살롱",("aesthetic clinic","beauty clinic","dermatology clinic","skin clinic","cosmetic clinic","beauty salon","professional salon","medical spa","beauty spa","thẩm mỹ viện","thẩm mỹ","phòng khám","phong kham")),
    )
    normalized=(text or "").lower()
    return next((label for label,terms in checks if any(term_present(normalized,term) for term in terms)),"미분류")


def strip_html_text(value: str) -> str:
    """Remove scraped markup before a value can reach Excel or a CL draft."""
    text=html_lib.unescape(str(value or ""))
    text=re.sub(r"(?is)<(?:br|hr)\s*/?>", " ", text)
    text=re.sub(r"(?is)<[^>]+>", " ", text)
    return " ".join(text.split()).strip()


def industry_terms(cfg: CollectionConfig) -> tuple[str,...]:
    from product_matching import aliases
    base=list(INDUSTRY_TERMS.get(INDUSTRY_ALIASES.get(cfg.industry,cfg.industry),()))
    product_phrases=[value.strip().lower() for value in cfg.product.split(",") if value.strip()]
    for phrase in product_phrases:
        if phrase not in GENERIC_PRODUCT_TERMS and phrase not in base: base.append(phrase)
        for alias in aliases(phrase, cfg.region):
            if alias not in base: base.append(alias)
    return tuple(base)


def search_profile_count(mode: str) -> int:
    return len(SEARCH_PROFILES.get(mode, SEARCH_PROFILES["균형"]))


def build_search_query(country: str, keyword: str, profile: str, excluded: str) -> str:
    local_terms=country_meta(country).get("local_buyer", [])
    if profile=="현지시장":
        lowered=keyword.lower()
        role_index=0 if "import" in lowered else 1 if any(x in lowered for x in ("distribut","wholesale","retail","clinic","salon","spa")) else 0
        local=local_terms[min(role_index,len(local_terms)-1)] if local_terms else "distributor"
        query=f'{country} {keyword} {local}'
    elif profile=="전시회·협회":
        query=f'{country} {keyword} exhibitor association'
    else:
        query=f'{country} {keyword} company'
    query=" ".join(query.split())
    if excluded:
        query=f"{query} {excluded}"
    return " ".join(query.split())


def candidate_prefilter(item: dict,country: str,cfg: CollectionConfig,profile: str) -> tuple[bool,int,str]:
    url=str(item.get("url") or ""); host=domain(url)
    if not host or is_blocked_domain(host): return False,0,"차단 도메인"
    if registrable_domain(host) in KNOWN_DIRECTORY_DOMAINS | KNOWN_MEDIA_DOMAINS:
        return False,0,"확인된 디렉터리·미디어 출처"
    path=urllib.parse.urlsplit(url).path.lower()
    if re.search(r"\.(pdf|docx?|xlsx?|pptx?)(?:$|[?#])",path): return False,0,"문서 파일"
    if any(term in path for term in NON_COMPANY_PATH_TERMS): return False,0,"채용·뉴스·디렉터리 URL"
    text=" ".join(str(item.get(key) or "") for key in ("title","content","url")).lower()
    title=str(item.get("title") or "").lower()
    if any(term in title for term in NON_COMPANY_TITLE_TERMS): return False,0,"기업이 아닌 검색결과"
    industry_hits={term for term in industry_terms(cfg) if term and term.lower() in text}
    buyer_terms=BUYER_TERMS+STRONG_BUYER_TERMS+tuple(country_meta(country).get("local_buyer", []))
    buyer_hits={term for term in buyer_terms if term and term.lower() in text}
    content_hits={term for term in CONTENT_SOURCE_TERMS if term in text}
    if not industry_hits and not buyer_hits: return False,0,"업종·바이어 근거 모두 없음"
    if len(content_hits)>=2 and not (industry_hits and buyer_hits): return False,0,"뉴스·교육·콘텐츠 페이지"
    aliases=country_meta(country).get("aliases", [])
    country_hit=any(alias and alias in text for alias in aliases)
    tld=country_meta(country).get("tld","")
    tld_hit=bool(tld and (host.endswith("."+tld) or host.endswith(".com."+tld)))
    host_suffix=host.rsplit(".",1)[-1] if "." in host else ""
    foreign_tld=bool(tld and host_suffix in KNOWN_COUNTRY_TLDS and host_suffix!=tld)
    score=min(8,len(industry_hits)*3)+min(8,len(buyer_hits)*3)+(3 if country_hit else 0)
    score+=4 if tld_hit else 0
    score-=8 if foreign_tld else 0
    score-=3 if not (country_hit or tld_hit) else 0
    score-=4 if not industry_hits else 0
    score-=4 if not buyer_hits else 0
    score+=round(float(item.get("score") or 0)*5)
    score+=3 if profile=="공식기업" else 2 if profile=="현지시장" else 1
    score-=len(content_hits)*3
    return True,max(score,0),""


def is_ecosystem_source(item: dict,cfg: CollectionConfig) -> bool:
    title=str(item.get("title") or "").lower()
    path=urllib.parse.urlsplit(str(item.get("url") or "")).path.lower()
    text=" ".join(str(item.get(key) or "") for key in ("title","content")).lower()
    if not any(term in text for term in industry_terms(cfg)): return False
    source_hits=sum(term in text for term in ECOSYSTEM_SOURCE_TERMS)
    source_path=any(term in path for term in ("exhibitor","member","directory","association","expo"))
    source_title=any(term in title for term in ("exhibitor","exhibition","expo","association","member directory"))
    return source_hits>=2 or source_path or source_title


def external_company_links(source_url: str,limit: int=10) -> list[str]:
    if not robots_allowed(source_url): return []
    page_html,resolved=fetch_html(source_url)
    if not page_html: return []
    parser=PageParser(); parser.feed(page_html)
    source_base=registrable_domain(resolved); found=[]
    for href,anchor in parser.links:
        absolute=urllib.parse.urljoin(resolved,href)
        parsed=urllib.parse.urlsplit(absolute)
        if parsed.scheme not in {"http","https"}: continue
        target_base=registrable_domain(absolute)
        if not target_base or target_base==source_base or is_blocked_domain(target_base): continue
        if re.search(r"\.(pdf|docx?|xlsx?|pptx?|jpe?g|png|gif|svg|zip)(?:$|[?#])",parsed.path.lower()): continue
        label=f"{href} {anchor}".lower()
        if any(term in label for term in ("privacy","terms","ticket","register","login","media partner","powered by")): continue
        official=root_url(absolute)
        if official not in found: found.append(official)
        if len(found)>=limit: break
    return found


COMPANY_NAME_NOISE_RE = re.compile(
    r"(?i)\s+(?:facebook|twitter|youtube|instagram|tiktok|linkedin|"
    r"mục\s+danh\s+sách(?:\s*#?\d+)?|danh\s+mục\s+sản\s+phẩm|"
    r"tìm\s+kiếm\s+sản\s+phẩm|skip\s+to\s+content|"
    r"chuyển\s+đến\s+phần\s+nội\s+dung|see\s+more|"
    r"đăng\s+nhập|giỏ\s+hàng|search\s+products?|product\s+categories)\b.*$"
)


def strip_company_name_noise(value: str) -> str:
    """Remove flattened navigation/social labels appended to an identity."""
    text=strip_html_text(value)
    text=COMPANY_NAME_NOISE_RE.sub("",text)
    return " ".join(text.split()).strip(" .,:;|-")


def company_name_review_reason(value: str) -> str:
    """Return a delivery-gate reason for unresolved page-title contamination."""
    text=strip_html_text(value)
    if not text:
        return "회사명 확인 필요"
    if COMPANY_NAME_NOISE_RE.search(" "+text):
        return "회사명 메뉴·SNS 문구 정제 필요"
    legal_markers=re.findall(r"(?i)\b(?:công ty|cong ty)\b",text)
    if len(legal_markers)>1:
        return "복수 법인명 혼입·법인명 확인 필요"
    normalized=text.casefold()
    marketing=("giá tốt", "cao cấp", "giá rẻ", "uy tín", "chất lượng cao")
    if len(text)>150 or len(text.split())>25:
        return "회사명 과다 길이·법인명 확인 필요"
    if any(token in normalized for token in marketing) and not re.match(
            r"(?i)^\s*(?:công ty|cong ty)\s+(?:tnhh|cp\b|cổ phần|co phan|trách nhiệm hữu hạn)",text):
        return "회사명 홍보문구·법인명 확인 필요"
    return ""


def clean_company_name(site_name: str,title: str,host: str,jsonld_name: str="",body: str="") -> str:
    """Return a buyer-facing company name, never a theme/navigation/page label."""
    # 일부 테마는 Organization.name에 회사명 대신 하위도메인/호스트를 넣는다.
    # 도메인 모양의 구조화 이름은 버리고 사이트명·제목·호스트 순으로 복구한다.
    domain_name_pattern=re.compile(r"^(?:https?://)?(?:www\.)?[a-z0-9-]+(?:\.[a-z0-9-]+){1,3}/?$",re.I)
    candidates=[strip_company_name_noise(jsonld_name),strip_company_name_noise(site_name),strip_company_name_noise(title)]
    strong_legal_pattern=re.compile(
        r'(?i)\b(?:công ty|cong ty)\s+(?:tnhh|cp\b|cổ phần|co phan|trách nhiệm hữu hạn)\b')
    metadata_strong_legal=[]
    parts=[]
    for candidate in candidates:
        raw=strip_company_name_noise(candidate)
        if not raw or domain_name_pattern.fullmatch(raw): continue
        # Preserve hyphens inside a legal name (for example "Thương Mại - Kỹ
        # Thuật").  Generic title splitting below is still useful for brands,
        # but must not destroy a legal identity found later in a marketing title.
        legal_matches=list(strong_legal_pattern.finditer(raw))
        if legal_matches:
            legal_tail=raw[legal_matches[-1].start():]
            # Hyphens and en/em dashes can be part of Vietnamese legal names
            # (for example "DƯỢC – MỸ PHẨM TTH"), so only unambiguous title
            # separators are allowed to terminate a strong legal identity.
            legal_tail=re.split(r"\s+(?:\||::)\s+",legal_tail,1)[0]
            legal_tail=strip_company_name_noise(legal_tail).strip(" .,:;|")
            if 8<=len(legal_tail)<=150 and 2<=len(legal_tail.split())<=25:
                metadata_strong_legal.append(legal_tail)
        candidate_parts=[raw]
        for separator in (" | "," — "," – "," :: "," - "):
            candidate_parts=[piece for part in candidate_parts for piece in part.split(separator)]
        parts.extend(candidate_parts)
    parts=[re.sub(r'(?i)(?:\s*\btrang chủ\b)+\s*$', '',part).strip() for part in parts if part.strip()]
    metadata_parts=set(parts)
    # Read bounded legal-name spans, never the rest of a flattened page.
    legal_pattern=r'(?i)\b(?:công ty|cong ty)\b'
    clean_body=strip_html_text(body)[:8000]
    operator_legal=[]
    body_legal=[]
    operator_terms=(
        "phân phối độc quyền bởi", "được phân phối bởi", "đơn vị phân phối", "đơn vị chủ quản",
        "vận hành bởi", "operated by", "distributed by", "exclusive distributor",
    )
    for match in re.finditer(legal_pattern,clean_body):
        span=clean_body[match.start():match.start()+220]
        next_legal=strong_legal_pattern.search(span,max(1,match.end()-match.start()))
        if next_legal:
            span=span[:next_legal.start()]
        span=re.split(r'(?i)\s*(?:[|\n]|trang chủ|giới thiệu|hotline|địa chỉ|điện thoại|email|bỏ qua|mst\s*:|mã số thuế|sđt\s*:|copyright|facebook|twitter|youtube|instagram|mục\s+danh\s+sách|danh\s+mục\s+sản\s+phẩm|tìm\s+kiếm\s+sản\s+phẩm)\s*',span)[0].strip(" .,:;|-")
        span=strip_company_name_noise(span)
        if 8<=len(span)<=150 and 2<=len(span.split())<=25:
            body_legal.append(span)
            context=clean_body[max(0,match.start()-120):match.start()].lower()
            if any(term in context for term in operator_terms): operator_legal.append(span)
    import unicodedata
    def identity_token(value):
        value=unicodedata.normalize('NFKD', value.lower().replace('đ','d'))
        return re.sub(r'[^a-z0-9]', '', value)
    domain_token=identity_token(registrable_domain(host).split(".")[0])
    generic_terms={"home","homepage","official site","trang chủ","welcome","my blog","blog","about us","contact","shop","store","flatsome","hazo","wordpress","website","untitled","top","site blueprint","website blueprint"}
    def usable(part: str) -> bool:
        normalized=" ".join(part.lower().split()).strip(" -|:·")
        if not normalized or normalized in generic_terms: return False
        if any(token in normalized for token in ("flatsome","my blog","wordpress theme")): return False
        if any(term_present(normalized,term) for term in ("skip to content","đăng nhập","giỏ hàng")): return False
        if re.match(legal_pattern,part): return len(part)<=150 and len(part.split())<=25
        return len(part)<=90 and len(part.split())<=9
    parts=[strip_html_text(part) for part in parts if usable(strip_html_text(part))]
    body_legal=[part for part in body_legal if usable(part)]
    strong_legal=[part for part in body_legal if strong_legal_pattern.match(part)]
    matched=[part for part in parts if domain_token and domain_token in identity_token(part)]
    concise=[part for part in parts if 1<=len(part.split())<=7 and len(part)<=70]
    legal=[part for part in parts if re.match(legal_pattern,part)]
    # Prefer a legal title when corroborated by the site's domain or body.
    corroborated=[part for part in legal if part in matched or (part in metadata_parts and body and identity_token(part) in identity_token(body))]
    # A footer legal name may be longer than a shortened metadata title. Accept it
    # when the metadata begins with the same legal identity, or when the page says
    # the brand is operated/distributed by that company.
    expanded_legal=[candidate for candidate in body_legal if any(
        identity_token(candidate).startswith(identity_token(meta))
        for meta in legal if len(identity_token(meta))>=8
    )]
    # A body-only partner name must not replace the site's own metadata.
    parts=[part for part in parts if part in metadata_parts or part in matched]
    concise=[part for part in concise if part in parts]
    # A strong legal-form match is safer than a marketing title beginning with
    # the generic words "Công ty" (for example "Công ty máy ... giá tốt").
    # The site's own strong legal metadata outranks unrelated company names in
    # article/product body text. A body expansion is accepted only when it
    # extends that same metadata identity.
    metadata_expanded=[candidate for candidate in expanded_legal if any(
        identity_token(candidate).startswith(identity_token(meta))
        for meta in metadata_strong_legal if len(identity_token(meta))>=8
    )]
    preferred_legal=operator_legal or metadata_expanded or metadata_strong_legal or corroborated
    if not preferred_legal and len(strong_legal)==1:
        preferred_legal=strong_legal
    if preferred_legal:
        name=max(preferred_legal,key=lambda value:(len(value.split()),len(value)))
    else:
        name=(matched or concise or parts or [""])[0]
    canonical_domain_names={
        "kolmarvietnam":"Kolmar Vietnam",
        "kprivatelabel":"KPrivateLabel",
        "eliintl":"ELI INTERNATIONAL",
        "peroma":"Peroma",
    }
    if domain_token in canonical_domain_names:
        name=canonical_domain_names[domain_token]
    if not name:
        if domain_token in canonical_domain_names:
            name=canonical_domain_names[domain_token]
        else:
            token=registrable_domain(host).split(".")[0].replace("-"," ")
            name=" ".join(word.upper() if len(word)<=3 else word.capitalize() for word in token.split())
    return strip_company_name_noise(name)[:160]


def clean_brand_name(site_name: str,title: str,company_name: str,host: str) -> str:
    """Keep a concise consumer brand when the official legal company differs."""
    legal_key=company_name_key(company_name)
    for raw in (site_name,title):
        text=strip_html_text(raw)
        for separator in (" | "," — "," – "," :: "," - "):
            text=text.split(separator,1)[0].strip()
        text=re.sub(r'(?i)(?:\s*\btrang chủ\b)+\s*$', '',text).strip(" .,:;|-")
        key=company_name_key(text)
        if (not text or len(text)>80 or len(text.split())>9 or key==legal_key
                or text.lower() in {"home","homepage","official site","trang chủ","shop","store"}
                or re.match(r'(?i)^\s*(?:công ty|cong ty)\b',text)):
            continue
        if key and key not in legal_key and legal_key not in key:
            return text
    return ""


def apply_quality(record: BuyerRecord,cfg: CollectionConfig,official_text: str,target_country: str="",identity_text: str="") -> None:
    from product_matching import product_evidence, subcategory_products
    _apply_quality(record,cfg,official_text,target_country,identity_text)
    # An exhibitor's article must not turn the fair owner into a distributor.
    name=record.company_name.casefold()
    identity=(identity_text or official_text).casefold()
    fair_name=bool(re.search(r"\b(?:trade fair|industrial.*fair|manufacturing fair|exhibition organizer|exhibition centre)\b", name))
    fair_navigation=sum(t in identity for t in ("book a stand","for exhibitors","exhibitor registration","hosted buyer program"))>=2
    if fair_name or fair_navigation:
        record.site_type="협회·전시회 출처"
        record.quality_decision="제외"; record.priority="제외"; record.email_grade="제외"
        record.exclusion_reason="행사 주최사이트: 소개된 참가기업의 공식 홈페이지 별도 확인 필요"
    if cfg.major_industry:
        record.selected_industries=cfg.major_industry
        record.selected_subcategories=" | ".join(cfg.subcategories)
        text=" ".join((identity_text or official_text).lower().split())
        products=[p.strip() for p in cfg.product.split(',') if p.strip()]
        evidence=product_evidence(text,products,target_country or record.target_country or cfg.region)
        hits=list(evidence)
        sub_products=subcategory_products(cfg.major_industry,cfg.subcategories,products)
        # The broader industry match remains useful, but is not proof of a specific product.
        record.matched_industries=cfg.major_industry if record.industry_score>0 and record.quality_decision!='제외' else ''
        record.industry_assessments=[dict(major=cfg.major_industry,subcategories=cfg.subcategories,
            target_country=record.target_country,priority=record.priority,quality_decision=record.quality_decision,
            product_hits=hits,product_alias_hits=evidence,
            matched_subcategories=[s for s,ps in sub_products.items() if any(p in hits for p in ps)],
            product_evidence_status="제품명 확인" if hits else "세부제품 추가확인",
            evidence=record.decision_evidence,source_url=record.company_source_url or record.website)]


def _apply_quality(record: BuyerRecord,cfg: CollectionConfig,official_text: str,target_country: str="",identity_text: str="") -> None:
    text=" ".join(official_text.lower().split())
    identity=" ".join((identity_text or official_text).lower().split())
    identity_with_name=f"{record.company_name.lower()} {identity}"
    host=domain(record.website); country=target_country or record.target_country or cfg.region
    meta=country_meta(country); aliases=meta["aliases"]
    country_hits=[x for x in aliases if x and x in identity]
    tld=meta["tld"]
    tld_match=bool(tld and (host.endswith("."+tld) or host.endswith(".com."+tld)))
    dial=meta["dial"]
    phone_match=bool(dial and ("+"+dial in identity or re.search(rf"\b{re.escape(dial)}[ .()-]?\d{{7,12}}\b",identity)))
    address_match=False
    for alias in country_hits:
        if any(re.search(rf"{re.escape(hint)}[^.;|]{{0,120}}\b{re.escape(alias)}\b",identity) for hint in LOCATION_HINTS):
            address_match=True
        if address_match: break
    presence_terms=("contact","hotline","store","stores","branch","branches","cửa hàng","hệ thống")
    local_presence=any(
        re.search(rf"(?:{re.escape(alias)}[^.;|]{{0,100}}(?:{'|'.join(map(re.escape,presence_terms))})|(?:{'|'.join(map(re.escape,presence_terms))})[^.;|]{{0,100}}{re.escape(alias)})",identity)
        for alias in country_hits
    )
    local_business_match=any(
        re.search(rf"{re.escape(alias)}[^.;|]{{0,80}}(?:importer|distributor|wholesaler|retail chain|clinic|salon|spa|company|nhà nhập khẩu|nhà phân phối|bán lẻ)",identity)
        for alias in country_hits
    )
    local_marker_hits=sum(term_present(identity,term) for term in LOCAL_BUSINESS_MARKERS.get(country,()))
    local_language_match=local_marker_hits>=2
    local_market_identity=any(
        re.search(rf"(?:based|located|headquartered|office|operations?|distributor|importer|retailer|stores?)\s+(?:in|across)\s+{re.escape(alias)}\b",identity)
        or re.search(rf"\b{re.escape(alias)}(?:ese)?\s+(?:market|company|distributor|importer|retailer|stores?|operations?)\b",identity)
        for alias in country_hits
    )
    city_markers={
        "Vietnam":("ho chi minh","hanoi","ha noi","da nang","can tho","hai phong"),
        "Japan":("tokyo","osaka","yokohama","nagoya","fukuoka","sapporo"),
        "Thailand":("bangkok","chiang mai","phuket","chonburi"),
        "Indonesia":("jakarta","surabaya","bandung","medan","bali"),
        "Germany":("berlin","hamburg","munich","münchen","frankfurt","cologne"),
        "France":("paris","lyon","marseille","toulouse","nice"),
    }
    city_address_match=any(city in identity for city in city_markers.get(country,())) and bool(
        re.search(r"\b(?:address|contact|office|store|stores|hotline|headquarters|located|location)\b",identity)
    )
    # 국가명과 distributor가 검색결과 문맥에서 우연히 붙은 것만으로 현지기업으로
    # 확정하지 않는다. 도메인·전화·주소·현지어 또는 명시적 현지시장 문장이 필요하다.
    strong_country=bool(tld_match or phone_match or address_match or city_address_match or local_language_match or local_market_identity)
    record.country_score=min(3,(2 if tld_match else 0)+(2 if phone_match else 0)+(2 if address_match else 0)+(2 if city_address_match else 0)+(1 if local_presence and strong_country else 0)+(1 if local_business_match and strong_country else 0)+(2 if local_language_match else 0)+(2 if local_market_identity else 0))
    record.country_evidence="; ".join(([f"도메인 .{tld}"] if tld_match else [])+(["현지 주소 문맥"] if address_match else [])+(["현지 주요도시·연락처 문맥"] if city_address_match else [])+(["국가 전화코드"] if phone_match else [])+(["현지 영업망 문맥"] if local_presence and strong_country else [])+(["현지 기업 본업 문맥"] if local_business_match and strong_country else [])+(["현지어 기업페이지"] if local_language_match else [])+(["명시적 현지시장 문맥"] if local_market_identity else []))
    record.target_country=country
    record.verified_country=country if strong_country else ""
    record.country_region=record.verified_country or "미확인"
    # 기사·블로그 원문은 발견 단서로만 사용한다. 최종 업종 판정은 홈페이지·회사소개·
    # 연락처 등 공식 본업 문맥(identity_text)에서 확인된 내용으로 제한한다.
    from product_matching import product_evidence
    i_hits=[term for term in industry_terms(cfg) if term_present(identity,term)]
    local_product_hits=product_evidence(identity,[p.strip() for p in cfg.product.split(',') if p.strip()],country)
    i_hits=list(dict.fromkeys(i_hits+list(local_product_hits)))
    garment_context=any(term_present(identity_with_name,term) for term in (
        "garment factory","clothing factory","sewing factory","apparel manufacturer",
        "cut & sew","ready-to-wear","women's wear","womenswear","knit fabric","garments we produce",
        "ppe","n95","ffp2","surgical mask","disposable mask","respirator",
    ))
    mask_only=bool(i_hits) and all(hit in {"mask","masks","facial mask","facial masks"} for hit in i_hits)
    if cfg.industry in {"화장품","뷰티"} and garment_context and mask_only:
        i_hits=[]
    buyer_terms=BUYER_IDENTITY_TERMS+SUPPLIER_BUYER_TERMS+("nhập khẩu chính hãng","xuất nhập khẩu","xuat nhap khau")+tuple(meta["local_buyer"])
    b_hits=list(dict.fromkeys(term for term in buyer_terms if term_present(identity_with_name,term)))
    record.buyer_type=buyer_type_from_text(identity,record.company_name)
    explicit_not_distributor=any(term_present(identity_with_name,term) for term in NEGATED_DISTRIBUTOR_TERMS)
    if explicit_not_distributor:
        generic_distribution={
            "distributor","distribution company","nhà phân phối","phân phối","phan phoi",
            "hệ thống phân phối","he thong phan phoi","đại lý","dai ly",
        }
        b_hits=[hit for hit in b_hits if hit not in generic_distribution]
        if record.buyer_type=="유통사": record.buyer_type="미분류"
    retail_signal_hits=sum(term_present(identity,term) for term in RETAIL_OWN_BRAND_TERMS)
    multibrand_retail_hits=sum(term_present(identity,term) for term in MULTIBRAND_RETAIL_TERMS)
    first_party_brand_hits=sum(term_present(identity,term) for term in FIRST_PARTY_BRAND_TERMS)
    discovery_path=urllib.parse.urlsplit(record.discovery_url or "").path.lower()
    verified_dealer_path=any(token in discovery_path for token in ("giay-chung-nhan-dai-ly","authorized-dealer","authorized-retailer"))
    if verified_dealer_path: multibrand_retail_hits+=1
    distribution_identity=any(term_present(identity_with_name,term) for term in HIGH_CONFIDENCE_DISTRIBUTION_TERMS)
    # 장바구니·무료배송만으로 자사 브랜드몰을 바이어로 승격하지 않는다.
    # 정품 멀티브랜드·공식대리점·매장망 근거가 함께 있을 때만 소매 바이어로 복원한다.
    if (not b_hits and i_hits and (retail_signal_hits>=2 or verified_dealer_path) and multibrand_retail_hits>=1
            and not first_party_brand_hits):
        b_hits=["멀티브랜드·공식소매 근거"]
        if record.buyer_type=="미분류": record.buyer_type="소매체인"
    if not b_hits and record.buyer_type=="클리닉·살롱":
        b_hits=["회사명·공식페이지의 클리닉/살롱 근거"]
    record.industry_score=0 if not i_hits else 2 if len(i_hits)==1 else 3
    record.buyer_role_score=0 if not b_hits else 2 if len(b_hits)==1 else 3
    platform=is_blocked_domain(host) or registrable_domain(host) in KNOWN_DIRECTORY_DOMAINS or sum(term_present(identity,term) for term in PLATFORM_TERMS)>=2
    # Explicit directory identity, not a shop's ordinary "find a distributor" menu.
    platform=platform or sum(term_present(identity,term) for term in (
        "business directory", "list your business", "claim your listing", "danh bạ doanh nghiệp",
        "đăng tin tìm nhà phân phối", "kết nối nhà cung cấp và nhà phân phối"))>=2
    listing_actions=sum(term_present(identity,term) for term in (
        'tin rao vặt','báo giá đăng tin','báo giá banner','đăng tin tìm đại lý'))
    directory_identity=any(term_present(identity_with_name,term) for term in (
        'tìm đại lý','tìm nhà cung cấp','nhận làm đại lý'))
    platform=platform or (directory_identity and listing_actions>=2)
    content_hits=sum(term_present(identity,term) for term in CONTENT_SOURCE_TERMS)
    strong_company=record.industry_score>0 and record.buyer_role_score>0
    investment_hits=sum(term_present(identity_with_name,term) for term in INVESTMENT_TERMS)
    investment_name=any(term_present(record.company_name.lower(),term) for term in ("capital","investment","ventures","private equity"))
    investment=investment_name or investment_hits>=2
    legal_hits=sum(term_present(identity_with_name,term) for term in LEGAL_TERMS)
    legal_name=any(term_present(record.company_name.lower(),term) for term in ("law","lawyer","legal","attorney"))
    legal=legal_name or legal_hits>=2
    cosmetic_product_evidence=any(term_present(identity,term) for term in ("cosmetics","skincare","skin care","makeup","personal care","mỹ phẩm","chăm sóc da"))
    clinic_product_trade_hits=sum(term_present(identity,term) for term in (
        "products we use","professional products","purchasing and using","purchase professional",
        "product portfolio","product range","shop products",
        "retail products","authorized retailer","stockist","brand distributor","distributes brands",
        "cửa hàng mỹ phẩm","sản phẩm phân phối","phân phối mỹ phẩm","đại lý mỹ phẩm","bán lẻ mỹ phẩm",
    ))
    logistics_hits=sum(term_present(identity_with_name,term) for term in LOGISTICS_TERMS)
    fulfillment_core=any(term_present(identity_with_name,term) for term in FULFILLMENT_CORE_TERMS)
    # 화장품 도매몰에도 배송·창고 안내는 흔하다. 물류 단어 하나만으로 본업을
    # 물류회사로 단정하지 않고, 바이어 근거가 약하거나 물류 근거가 복수일 때만 제외한다.
    explicit_logistics_hits=sum(term_present(identity_with_name,term) for term in (
        "logistics company","logistics service","freight forwarding","customs service",
        "customs broker","customs declaration","international shipping","trucking",
    ))
    importer_of_record=any(term_present(identity_with_name,term) for term in ("importer of record","exporter of record","customs clearance"))
    logistics=explicit_logistics_hits>=2 or (importer_of_record and not cosmetic_product_evidence) or (fulfillment_core and not cosmetic_product_evidence) or (logistics_hits>=2 and not strong_company)
    strong_media_hits=sum(term_present(identity_with_name,term) for term in STRONG_RESEARCH_MEDIA_TERMS)
    weak_media_hits=sum(term_present(identity_with_name,term) for term in WEAK_RESEARCH_MEDIA_TERMS)
    known_media=registrable_domain(host) in KNOWN_MEDIA_DOMAINS
    explicit_media_identity=any(term_present(identity_with_name,term) for term in (
        "tạp chí điện tử","tap chi dien tu","báo điện tử","bao dien tu",
        "news portal","newspaper","editorial platform","cơ quan trung ương","co quan trung uong",
    ))
    research_media=bool(known_media or explicit_media_identity or strong_media_hits>=2 or (term_present(identity_with_name,"market research") and not record.buyer_role_score) or (weak_media_hits>=2 and not strong_company))
    agency_hits=sum(term_present(identity_with_name,term) for term in AGENCY_TERMS)
    agency=agency_hits>=2 or (agency_hits>=1 and not strong_company)
    content_source=research_media or (content_hits>=2 and not strong_company)
    source_name=record.company_name.lower()
    site_path=urllib.parse.urlsplit(record.website).path.lower()
    exhibition_identity=any(term_present(identity_with_name,term) for term in EXHIBITION_IDENTITY_TERMS)
    ecosystem_page=(exhibition_identity
                    or any(term_present(source_name,term) for term in ("association","exhibition","expo","trade fair","hiệp hội"))
                    or any(re.search(rf"(?:^|/){re.escape(term)}(?:/|$)",site_path) for term in ("exhibitor","member-directory","association","expo")))
    # 전시회 홈페이지의 뉴스·행사 콘텐츠는 미디어 본업이 아니다.
    if exhibition_identity:
        research_media=False
        content_source=False
    packaging_only=cfg.industry in {"화장품","뷰티"} and any(term_present(identity,term) for term in PACKAGING_ONLY_TERMS)
    manufacturer_hits=sum(term_present(identity_with_name,term) for term in MANUFACTURER_TERMS)
    # 블로그·시술 설명에 등장하는 생산 단어 하나 때문에 클리닉이 제조사로
    # 빠지지 않도록 복수의 명확한 제조 근거를 요구한다.
    manufacturer_name=any(term_present(record.company_name.lower(),term) for term in ("factory","manufacturer","manufacturing","nhà máy","sản xuất"))
    first_party_manufacturing=any(term_present(identity_with_name,term) for term in (
        "our factory","we manufacture","we are a manufacturer","manufacturing facility",
        "production factory","manufacturer of","manufacturer and distributor","oem/odm","oem manufacturer","odm manufacturer","nhà máy sản xuất",
        "nhà sản xuất và","xưởng sản xuất oem","xưởng sản xuất odm","cơ sở sản xuất của chúng tôi",
        "trực tiếp thiết kế và chế tạo","thiết kế và chế tạo","tự chủ hoàn toàn khâu thiết kế",
        "gia công và tự động hóa","năng lực gia công cơ khí",
    ))
    manufacturer=(manufacturer_name and manufacturer_hits>=1) or first_party_manufacturing or (
        manufacturer_hits>=3 and any(term_present(identity_with_name,term) for term in ("private label","contract manufacturing","oem","odm"))
    )
    corporate_brand_hits=sum(term_present(identity_with_name,term) for term in CORPORATE_BRAND_OWNER_TERMS)
    direct_inbound_import=(
        any(term_present(record.company_name,term) for term in ("importer","nhà nhập khẩu","xuất nhập khẩu","xuat nhap khau","xnk"))
        or any(term_present(identity,term) for term in (
            "importer","imported brands","we import","imports and distributes","import and distribute","importing and distributing",
            "specializing in the import","our import products","nhà nhập khẩu","công ty nhập khẩu",
            "nhập khẩu chính hãng","nhập khẩu và phân phối","nhap khau va phan phoi",
            "máy được nhập khẩu chính hãng","các máy kiểm tra được nhập khẩu","xnk",
        ))
    )
    inbound_import=direct_inbound_import
    authoritative_inbound_import=(
        any(term_present(record.company_name,term) for term in ("importer","nhà nhập khẩu","xuất nhập khẩu","xuat nhap khau","xnk"))
        or any(term_present(identity,term) for term in (
            "we import", "imports and distributes", "import and distribute", "importing and distributing",
            "specializing in the import", "nhà nhập khẩu", "công ty nhập khẩu",
            "nhập khẩu và phân phối", "nhap khau va phan phoi",
        ))
    )
    # A first-party manufacturer explicitly saying it is not a distributor must
    # not become a buyer because an unrelated product/menu sentence contains an
    # imported-goods phrase. Only a direct company import assertion can override.
    if explicit_not_distributor and manufacturer and not authoritative_inbound_import:
        inbound_import=False
    known_brand_owner=registrable_domain(host) in {
        "loreal.com", "laboratoriosbabe.com.vn", "moicosmetics.vn",
    } or record.company_name.lower().strip() in {"l'oréal", "laboratorios babé", "m.o.i cosmetics"}
    brand_owner=bool(
        cfg.industry in {"화장품","뷰티"}
        and (known_brand_owner or corporate_brand_hits>=2)
        and not inbound_import
        and multibrand_retail_hits==0
    )
    authoritative_media=bool(known_media or explicit_media_identity)
    # OEM·ODM·공장 등 명시적인 1차 제조근거가 있으면 Blog/News 메뉴 같은 약한
    # 콘텐츠 신호보다 제조사 판정을 우선한다. 언론사 고유 정체성은 계속 우선한다.
    if manufacturer and not authoritative_media:
        research_media=False
        content_source=False
    # 제품 제조 정체성이 명확한 경우 배송·통관 안내 문구보다 제조사 판정을 우선한다.
    if manufacturer and (manufacturer_name or first_party_manufacturing): logistics=False
    equipment_hits=sum(term_present(identity_with_name,term) for term in EQUIPMENT_ONLY_TERMS)
    software_hits=sum(term_present(identity_with_name,term) for term in SOFTWARE_SERVICE_TERMS)
    software_name=bool(re.search(r"(?<![a-z0-9])(?:software|soft|saas|cloud|pos)(?![a-z0-9])",record.company_name.lower()))
    # 본문 하단의 제휴·추천 문구 한 건 때문에 실제 도매업체가 IT서비스로 빠지지 않도록
    # 복수 제품근거 또는 회사명 자체의 소프트웨어 정체성을 요구한다.
    vietnamese_software_name=any(term_present(record.company_name,term) for term in ('phần mềm','phan mem'))
    software_product_context=any(term_present(identity,term) for term in ('phần mềm dms','phan mem dms','giải pháp phần mềm','tích hợp erp'))
    software_service=software_name or software_hits>=2 or vietnamese_software_name or (
        software_product_context and sum(term_present(identity,term) for term in ('quản lý khách hàng','quản lý đơn hàng','ứng dụng di động','dms ai','saas'))>=2)
    service_identity=next((label for label,terms in SERVICE_IDENTITY_GROUPS.items()
                           if sum(term_present(identity_with_name,term) for term in terms)>=1),"")
    cleanroom_service=cfg.industry in {"화장품","뷰티"} and any(term_present(identity_with_name,t) for t in (
        "cleanroom", "clean room", "thiết bị phòng sạch", "thi công phòng sạch"
    )) and not local_product_hits and (not cosmetic_product_evidence or sum(term_present(identity_with_name,t) for t in (
        "cleanroom equipment", "cleanroom construction", "thiết bị phòng sạch", "thi công phòng sạch"))>=2)
    tourism_hits=sum(term_present(identity_with_name,term) for term in TOURISM_TERMS)
    tourism_name=any(term_present(record.company_name.lower(),term) for term in ("tourism","tourist","travel guide","travel","tours"))
    # 병원·클리닉 사이트의 환자용 travel guide 같은 부가 문구는 본업이 아니다.
    tourism=(tourism_hits>=2 and not strong_company) or (tourism_name and record.buyer_type!="클리닉·살롱")
    gambling_spam=any(term_present(identity_with_name,term) for term in GAMBLING_SPAM_TERMS)
    equipment_only=cfg.industry in {"화장품","뷰티"} and cfg.major_industry!="뷰티 서비스·장비" and equipment_hits>=1 and not cosmetic_product_evidence and record.buyer_type!="클리닉·살롱"
    high_confidence_distribution=any(term_present(identity_with_name,term) for term in HIGH_CONFIDENCE_DISTRIBUTION_TERMS)
    # A negative distributor statement and first-party manufacturing evidence
    # override incidental historic/menu uses of the word "distribution".
    if explicit_not_distributor and manufacturer and not inbound_import:
        high_confidence_distribution=False
        b_hits=[hit for hit in b_hits if hit not in {
            "phân phối","phan phoi","nhà phân phối","distributor",
            "nhập khẩu chính hãng","officially imported",
        }]
        record.buyer_role_score=0 if not b_hits else 2 if len(b_hits)==1 else 3
        record.buyer_type="제조사"
    retail_own_brand_hits=sum(term_present(identity,term) for term in RETAIL_OWN_BRAND_TERMS)
    first_party_brand_store=bool(first_party_brand_hits and retail_own_brand_hits>=2 and not distribution_identity)
    export_seller=any(term_present(identity_with_name,term) for term in EXPORT_SELLER_TERMS) and not inbound_import
    if platform: record.site_type="플랫폼/디렉터리"
    elif gambling_spam: record.site_type="도박·스팸"
    elif tourism: record.site_type="관광·여행"
    elif investment: record.site_type="투자·금융사"
    elif legal: record.site_type="법률·전문서비스"
    elif logistics: record.site_type="물류·통관사"
    elif cleanroom_service: record.site_type="산업설비·클린룸"
    elif software_service: record.site_type="소프트웨어·IT서비스"
    elif service_identity: record.site_type=service_identity
    elif ecosystem_page: record.site_type="협회·전시회 출처"
    elif authoritative_media: record.site_type="리서치·미디어"
    elif manufacturer: record.site_type="생산공장·제조사"
    elif brand_owner: record.site_type="브랜드 본사·자사제품사"
    elif content_source: record.site_type="리서치·미디어"
    elif agency: record.site_type="컨설팅·대행사"
    elif equipment_only: record.site_type="미용·의료장비사"
    elif packaging_only: record.site_type="포장재·부자재업체"
    elif export_seller: record.site_type="수출·판매사"
    else: record.site_type="기업 공식사이트"
    record.relevance_score=round((record.country_score/3)*30+(record.industry_score/3)*35+(record.buyer_role_score/3)*35)
    evidence=[]
    if country_hits or strong_country: evidence.append(record.country_evidence or f"{country} 문맥")
    if i_hits: evidence.append("업종: "+", ".join(i_hits[:3]))
    if b_hits: evidence.append("바이어역할: "+", ".join(b_hits[:3]))
    record.decision_evidence=" | ".join(evidence)[:500]
    hard_reasons=[]
    if platform: hard_reasons.append("플랫폼·디렉터리")
    if gambling_spam: hard_reasons.append("도박·스팸")
    if tourism: hard_reasons.append("관광·여행")
    if investment: hard_reasons.append("투자·금융사")
    if legal: hard_reasons.append("법률·전문서비스")
    if logistics: hard_reasons.append("물류·통관사")
    if software_service: hard_reasons.append("소프트웨어·IT서비스")
    if service_identity and not high_confidence_distribution: hard_reasons.append(service_identity)
    if cleanroom_service: hard_reasons.append("산업설비·클린룸")
    if equipment_only: hard_reasons.append("미용·의료장비사")
    if content_source: hard_reasons.append("리서치·미디어")
    if agency: hard_reasons.append("컨설팅·대행사")
    # 제조·수출 단어 자체는 배제 사유가 아니다. 목표국가에 실제 사업기반이 있고
    # 선택 업종을 다루는 현지 제조/OEM/수출사는 별도 전략후보로 보존한다.
    # 수입·유통을 함께 하는 제조사는 제조사라는 이유로 A/B 승격을 막지 않는다.
    hybrid_buyer=bool(inbound_import or high_confidence_distribution)
    record.secondary_buyer_type="제조·OEM·ODM" if manufacturer and hybrid_buyer else ""
    strategic_operator=bool(
        record.country_score and record.industry_score
        and (manufacturer or export_seller)
        and not hybrid_buyer
        and not any((ecosystem_page, packaging_only, brand_owner, first_party_brand_store))
    )
    reference_reasons=[]
    if ecosystem_page: reference_reasons.append("협회·전시회·시장 생태계 출처")
    if packaging_only: reference_reasons.append("포장재·부자재업체")
    if manufacturer and not hybrid_buyer and not strategic_operator: reference_reasons.append("생산공장·제조사")
    if brand_owner: reference_reasons.append("브랜드 본사·자사제품사")
    if export_seller and not hybrid_buyer and not strategic_operator: reference_reasons.append("수출·판매사")
    if first_party_brand_store: reference_reasons.append("자사 브랜드몰·직접판매사")
    review_reasons=[]
    if not record.country_score: review_reasons.append(f"{country} 소재 근거 추가확인")
    if not record.buyer_role_score: review_reasons.append("바이어 역할 근거 추가확인")
    if record.relevance_score<65: review_reasons.append("관련성 점수 65점 미만")

    reference_override=bool(reference_reasons) and not any(
        reason in hard_reasons for reason in ("플랫폼·디렉터리","투자·금융사","법률·전문서비스","물류·통관사","소프트웨어·IT서비스","산업설비·클린룸","리서치·미디어","컨설팅·대행사")
    )
    # 현지어만 있는 페이지는 국가 추정에는 유용하지만 A등급의 법인·영업거점 확정
    # 근거로는 부족하다. A는 도메인·전화·주소·도시 연락처·명시적 현지시장 근거가 필요하다.
    a_country_confidence=bool(tld_match or phone_match or address_match or city_address_match or local_market_identity)
    if (hard_reasons and not reference_override) or not record.industry_score:
        primary_reason={"플랫폼/디렉터리":"플랫폼·디렉터리"}.get(record.site_type,record.site_type)
        reasons=([f"{country} 소재 근거 없음·타국가 캠페인 재검토"] if not record.country_score else [])+([primary_reason] if hard_reasons else [])
        if not record.industry_score: reasons.append(f"{cfg.industry} 관련성 없음")
        record.quality_decision="제외"; record.priority="제외"; record.email_grade="제외"
        record.exclusion_reason="; ".join(dict.fromkeys(reasons))
        record.evidence_status="추가확인"
        record.grade_reason="제외: 비기업·비대상 사이트 또는 선택 업종 근거 없음"
    elif strategic_operator:
        record.quality_decision="전략후보"; record.priority="전략"
        role="생산·OEM·ODM" if manufacturer else "수출·판매"
        record.exclusion_reason=f"현지 {role} 사업자 · 한국 제품·원료·브랜드 제휴 가능성 검토"
        record.evidence_status="전략검토"; record.email_grade="전략"
        record.grade_reason="전략: 현지 제조·OEM·수출 사업자이며 직접 바이어 근거 미확인"
    elif reference_reasons:
        record.quality_decision="참고기업"; record.priority="참고"
        record.exclusion_reason="; ".join(dict.fromkeys(reference_reasons))
        record.evidence_status="시장참고"; record.email_grade="참고"
        record.grade_reason="참고: 시장 관련성은 있으나 직접 바이어 대상이 아님"
    elif not record.country_score:
        record.quality_decision="타국가후보"; record.priority="타국가"
        record.exclusion_reason=f"{country} 소재 근거 없음·타국가 캠페인 재검토"
        record.evidence_status="타국가후보"; record.email_grade="보류"
        record.grade_reason="타국가: 목표국가 소재 근거 미확인"
    elif review_reasons:
        record.quality_decision="추가검토"; record.priority="C"
        record.exclusion_reason="; ".join(dict.fromkeys(review_reasons))
        record.evidence_status="추가확인"
        record.grade_reason="C: 국가·업종·바이어 역할 중 필수 근거 추가확인"
    elif (record.buyer_type in {"수입·유통사","유통사"} and record.relevance_score>=75
          and inbound_import and high_confidence_distribution and record.industry_score>=2
          and a_country_confidence and not (retail_own_brand_hits>=2 and not inbound_import)):
        record.quality_decision="적합"; record.exclusion_reason=""
        record.priority="A"
        record.grade_reason="A: 목표국가·선택 업종과 명시적인 수입·유통 역할이 확인됨"
    elif record.buyer_type=="클리닉·살롱" and not clinic_product_trade_hits:
        record.quality_decision="추가검토"; record.priority="C"
        record.exclusion_reason="클리닉·살롱 확인 · 제품 구매·판매·브랜드 취급 근거 추가확인"
        record.evidence_status="추가확인"
        record.grade_reason="C: 클리닉·살롱의 제품 구매·판매·브랜드 취급 근거 추가확인"
    elif record.buyer_type in {"도매사","소매체인","클리닉·살롱","유통사"} or record.relevance_score>=70:
        record.quality_decision="적합"; record.exclusion_reason=""
        record.priority="B"
        missing=[]
        if record.country_score<3: missing.append("국가")
        if record.industry_score<3: missing.append("업종")
        if record.buyer_role_score<3: missing.append("바이어 역할")
        if not inbound_import: missing.append("명시적 수입")
        if not high_confidence_distribution: missing.append("강한 유통")
        record.grade_reason="B: "+("·".join(dict.fromkeys(missing))+" 근거 보완 필요" if missing else "적합 후보이나 A등급 확정조건 보완 필요")
    else:
        record.quality_decision="추가검토"; record.priority="C"
        record.exclusion_reason="핵심 바이어 역할 추가확인"
        record.evidence_status="추가확인"
        record.grade_reason="C: 핵심 바이어 역할 추가확인"


# One lazily-created connection pool per company task, never shared across workers.
_WEBSITE_HTTP = threading.local()


def _website_get(url: str, **kwargs):
    if not getattr(_WEBSITE_HTTP, "active", False):
        return requests.get(url, **kwargs)
    session = getattr(_WEBSITE_HTTP, "session", None)
    if session is None:
        session = requests.Session()
        _WEBSITE_HTTP.session = session
    # Preserve stateless crawling while reusing TCP/TLS connections.
    session.cookies.clear()
    return session.get(url, **kwargs)


_ROBOTS_CACHE: dict[str, urllib.robotparser.RobotFileParser | bool] = {}
_RUN_PAGE_CACHE: dict[str,tuple[str,str]] | None = None
_RUN_PAGE_LOCKS: dict[str,threading.Lock] = {}
_RUN_PAGE_LOCK_GUARD = threading.Lock()


def robots_allowed(url: str) -> bool:
    p=urllib.parse.urlsplit(url); origin=urllib.parse.urlunsplit((p.scheme,p.netloc,"","",""))
    cached=_ROBOTS_CACHE.get(origin)
    if isinstance(cached,bool): return cached
    if cached is not None: return cached.can_fetch(USER_AGENT,url)
    robot=origin+"/robots.txt"
    try:
        response=_website_get(robot,headers={"User-Agent":USER_AGENT},timeout=(2.5,4),allow_redirects=True)
        if response.status_code>=400:
            _ROBOTS_CACHE[origin]=True; return True
        rp=urllib.robotparser.RobotFileParser(); rp.set_url(robot)
        rp.parse(response.text[:250_000].splitlines()); _ROBOTS_CACHE[origin]=rp
        return rp.can_fetch(USER_AGENT,url)
    except Exception:
        _ROBOTS_CACHE[origin]=True; return True


def fetch_html(url: str) -> tuple[str,str]:
    global _RUN_PAGE_CACHE
    key=urllib.parse.urldefrag(url).geturl().rstrip("/") or url
    lock=None
    if _RUN_PAGE_CACHE is not None:
        with _RUN_PAGE_LOCK_GUARD:
            lock=_RUN_PAGE_LOCKS.setdefault(key,threading.Lock())
        with lock:
            cached=_RUN_PAGE_CACHE.get(key)
            if cached is not None: return cached
            result=_fetch_html_uncached(url)
            if result[0]: _RUN_PAGE_CACHE[key]=result
            return result
    return _fetch_html_uncached(url)


def _fetch_html_uncached(url: str) -> tuple[str,str]:
    response=_website_get(url,headers={"User-Agent":USER_AGENT,"Accept":"text/html,application/xhtml+xml"},timeout=(3.5,7),allow_redirects=True)
    response.raise_for_status()
    if "text/html" not in response.headers.get("content-type",""): return "",response.url
    raw=response.content[:2_000_000]
    # Most modern sites are UTF-8: avoid a full statistical encoding scan when
    # strict decoding succeeds without known mojibake. Legacy encodings retain
    # the previous fallback and scoring path.
    try:
        utf8 = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        utf8 = None
    if utf8 is not None and not any(marker in utf8 for marker in ("Ã","Â","Æ","áº","á»","Ä‘","ï¿½","�")):
        return utf8, response.url
    encodings=["utf-8",response.encoding,getattr(response,"apparent_encoding",None)]
    decoded=[]
    for encoding in dict.fromkeys(value for value in encodings if value):
        try: decoded.append(raw.decode(encoding,errors="strict"))
        except (LookupError,UnicodeDecodeError): continue
    if not decoded: decoded=[raw.decode(response.encoding or "utf-8",errors="replace")]
    def decode_penalty(value: str) -> int:
        markers=("Ã","Â","Æ","áº","á»","Ä‘","ï¿½","�")
        return (sum(value.count(marker)*5 for marker in markers)+value.count("?")
                +sum(10 for ch in value if "\x80" <= ch <= "\x9f"))
    return min(decoded,key=decode_penalty),response.url


def parse_html(html: str, url: str) -> dict:
    parser=PageParser(); parser.feed(html); text=" ".join(parser.text)
    decoded_text=decode_obfuscated_emails(text)
    emails=EMAIL_RE.findall(decoded_text)
    links=[]
    for href,anchor in parser.links:
        if href.lower().startswith("mailto:"): emails.append(urllib.parse.unquote(href.split(":",1)[1].split("?",1)[0]))
        absolute=urllib.parse.urljoin(url,href)
        if domain(absolute)==domain(url) and any(h in f"{href} {anchor}".lower() for h in CONTACT_HINTS): links.append(absolute)
    title=" ".join(parser.title).strip()
    jsonld_name=""
    for block in re.findall(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',html,flags=re.I|re.S):
        try: payload=json.loads(html_lib.unescape(block).strip())
        except (json.JSONDecodeError,TypeError): continue
        nodes=payload if isinstance(payload,list) else payload.get("@graph",[payload]) if isinstance(payload,dict) else []
        for node in nodes:
            if not isinstance(node,dict): continue
            types=node.get("@type",[]); types=[types] if isinstance(types,str) else types
            if any(value in {"Organization","Corporation","LocalBusiness","Store"} for value in types) and node.get("name"):
                jsonld_name=str(node.get("legalName") or node["name"]).strip(); break
        if jsonld_name: break
    clean=sorted({normalize_email(e) for e in emails if normalize_email(e)})
    return {"title":title,"site_name":parser.site_name,"jsonld_name":jsonld_name,"text":text[:200_000],"emails":clean,"phones":extract_phone_candidates(text),"links":list(dict.fromkeys(links))}


class SearchPlanLimitError(RuntimeError):
    pass


class TavilyPlanLimitError(SearchPlanLimitError):
    """Backward-compatible name used by older tests and checkpoints."""
    pass


class SearchProviderBase:
    provider_name="search"

    def __init__(self,key):
        self.key=key
        self.response_log=[]
        self.cache_mode="live"
        self.cache_root=Path(os.getenv("KBP_DATA_DIR",".kbp_data"))/"search_cache"
        self.plan_exhausted=False

    def configure(self, mode="live", cache_root=""):
        self.cache_mode=mode
        if cache_root: self.cache_root=Path(cache_root)
        return self

    def cache_path(self,payload):
        envelope={"provider":self.provider_name,"request":payload}
        cache_key=hashlib.sha256(json.dumps(envelope,sort_keys=True,ensure_ascii=False).encode("utf-8")).hexdigest()
        return self.cache_root/f"{cache_key}.json"

    def cached(self,cache_path,query,country):
        if self.cache_mode in {"cache_only","cache_first"} and cache_path.exists():
            try:
                data=json.loads(cache_path.read_text(encoding="utf-8"))
                results=data.get("results",[]) if isinstance(data,dict) else []
                self.response_log.append({"provider":self.provider_name,"query":query,"country":country or "","request_mode":"캐시재사용","http_status":"CACHE","result_count":len(results),"request_id":str(data.get("request_id") or ""),"response_time":0,"credits":0,"error":""})
                return results
            except (OSError,json.JSONDecodeError):
                pass
        if self.cache_mode=="cache_only":
            self.response_log.append({"provider":self.provider_name,"query":query,"country":country or "","request_mode":"캐시없음","http_status":"CACHE_MISS","result_count":0,"request_id":"","response_time":0,"credits":0,"error":"저장된 검색결과 없음"})
            return []
        return None

    def save_cache(self,cache_path,data):
        try:
            cache_path.parent.mkdir(parents=True,exist_ok=True)
            cache_path.write_text(json.dumps(data,ensure_ascii=False),encoding="utf-8")
        except OSError:
            pass


class TavilyProvider(SearchProviderBase):
    provider_name="Tavily"
    def __init__(self,key):
        super().__init__(key)

    def search(self,query,max_results=20,country="",minimal=False):
        payload={
                "query":query,
                "topic":"general",
                "search_depth":"basic",
                "max_results":min(max(int(max_results),1),20),
                "include_answer":False,
                "include_raw_content":False,
                "include_images":False,
                "include_usage":True,
            }
        cache_path=self.cache_path(payload)
        cached=self.cached(cache_path,query,country)
        if cached is not None: return cached
        # 검색은 넓게 수행하고 국가·도메인은 후보 및 공식사이트 검증 단계에서 판정한다.
        headers={"Authorization":f"Bearer {self.key}","Content-Type":"application/json"}
        r=requests.post("https://api.tavily.com/search",headers=headers,json=payload,timeout=30)
        try: data=r.json()
        except Exception: data={}
        request_mode="최소옵션" if minimal else "표준"
        results=data.get("results",[]) if isinstance(data,dict) else []
        usage=data.get("usage",{}) if isinstance(data,dict) else {}
        error=data.get("detail") or data.get("error") or "" if isinstance(data,dict) else ""
        if isinstance(error,dict): error=error.get("error") or str(error)
        self.response_log.append({
            "provider":self.provider_name,
            "query":query,
            "country":country or "",
            "request_mode":request_mode,
            "http_status":r.status_code,
            "result_count":len(results),
            "request_id":str(data.get("request_id") or "") if isinstance(data,dict) else "",
            "response_time":data.get("response_time","") if isinstance(data,dict) else "",
            "credits":usage.get("credits","") if isinstance(usage,dict) else "",
            "error":str(error)[:300],
        })
        if r.status_code==432:
            self.plan_exhausted=True
            raise TavilyPlanLimitError(str(error) or "Tavily 사용 한도 초과")
        r.raise_for_status()
        try:
            self.save_cache(cache_path,data)
        except Exception: pass
        return results


class BraveProvider(SearchProviderBase):
    provider_name="Brave"

    def search(self,query,max_results=20,country="",minimal=False):
        params={"q":query,"count":min(max(int(max_results),1),20),"safesearch":"moderate","text_decorations":"false"}
        cache_path=self.cache_path(params)
        cached=self.cached(cache_path,query,country)
        if cached is not None: return cached
        headers={"Accept":"application/json","Accept-Encoding":"gzip","X-Subscription-Token":self.key}
        started=time.monotonic()
        r=requests.get("https://api.search.brave.com/res/v1/web/search",headers=headers,params=params,timeout=30)
        try: raw=r.json()
        except Exception: raw={}
        web=raw.get("web",{}) if isinstance(raw,dict) else {}
        raw_results=web.get("results",[]) if isinstance(web,dict) else []
        results=[{"title":str(item.get("title") or ""),"url":str(item.get("url") or ""),"content":str(item.get("description") or "")} for item in raw_results if item.get("url")]
        request_id=r.headers.get("x-request-id","")
        error=(raw.get("message") or raw.get("error") or "") if isinstance(raw,dict) else ""
        self.response_log.append({"provider":self.provider_name,"query":query,"country":country or "","request_mode":"최소옵션" if minimal else "표준","http_status":r.status_code,"result_count":len(results),"request_id":request_id,"response_time":round(time.monotonic()-started,3),"credits":0 if not results else 1,"error":str(error)[:300]})
        if r.status_code in {402,429}:
            self.plan_exhausted=True
            raise SearchPlanLimitError(str(error) or f"Brave 사용 한도 초과 (HTTP {r.status_code})")
        r.raise_for_status()
        data={"results":results,"request_id":request_id}
        self.save_cache(cache_path,data)
        return results


class FallbackSearchProvider:
    provider_name="Brave → Tavily"

    def __init__(self,providers):
        self.providers=providers
        self.response_log=[]
        self.plan_exhausted=False

    def configure(self,mode="live",cache_root=""):
        for provider in self.providers: provider.configure(mode,cache_root)
        return self

    def search(self,*args,**kwargs):
        last_error=None
        for provider in self.providers:
            if not provider.key: continue
            try:
                results=provider.search(*args,**kwargs)
                self.response_log.extend(provider.response_log[len(self.response_log):] if len(self.providers)==1 else provider.response_log[-1:])
                if results: return results
            except (SearchPlanLimitError,requests.RequestException) as exc:
                last_error=exc
                if provider.response_log: self.response_log.append(provider.response_log[-1])
                continue
        if last_error: raise SearchPlanLimitError(f"사용 가능한 검색 공급자가 없습니다: {last_error}")
        return []


def make_search_provider(provider_name: str,brave_key: str="",tavily_key: str=""):
    if provider_name.startswith("Brave →"):
        return FallbackSearchProvider([BraveProvider(brave_key),TavilyProvider(tavily_key)])
    if provider_name.startswith("Tavily"):
        return TavilyProvider(tavily_key)
    return BraveProvider(brave_key)


def search_diagnostic(provider,country: str,industry: str,query: str="",max_results: int=5,result_cache: dict|None=None) -> dict:
    industry_hint=next((term for term in INDUSTRY_TERMS.get(INDUSTRY_ALIASES.get(industry,industry),()) if term.isascii()),"products")
    query=query or f"{country} {industry_hint} importer distributor company"
    try:
        results=provider.search(query,max_results=max_results,country="",minimal=True)
        if result_cache is not None:
            result_cache[query]=results
        meta=provider.response_log[-1] if provider.response_log else {}
        provider_name=getattr(provider,"provider_name","검색 API")
        return {"ok":bool(results),"query":query,"result_count":len(results),"message":"정상" if results else f"{provider_name}가 빈 결과를 반환했습니다.",**meta}
    except Exception as exc:
        meta=provider.response_log[-1] if provider.response_log else {}
        return {"ok":False,"query":query,"result_count":0,"message":f"{type(exc).__name__}: {str(exc)[:300]}",**meta}


def tavily_diagnostic(tavily: TavilyProvider,country: str,industry: str) -> dict:
    """Compatibility wrapper for existing callers."""
    return search_diagnostic(tavily,country,industry)


def check_tavily_connection(api_key: str,country: str="Vietnam",industry: str="화장품") -> dict:
    return search_diagnostic(TavilyProvider(api_key),country,industry)


def check_brave_connection(api_key: str,country: str="Vietnam",industry: str="화장품") -> dict:
    return search_diagnostic(BraveProvider(api_key),country,industry)


class HunterProvider:
    def __init__(self,key): self.key=key
    def domain_search(self,host):
        r=requests.get("https://api.hunter.io/v2/domain-search",params={"domain":host,"api_key":self.key,"limit":10},timeout=25)
        r.raise_for_status(); return r.json().get("data",{}).get("emails",[])
    def verify(self,email):
        r=requests.get("https://api.hunter.io/v2/email-verifier",params={"email":email,"api_key":self.key},timeout=25)
        r.raise_for_status(); return r.json().get("data",{})


def discover(cfg: CollectionConfig, tavily, stats: dict|None=None, prefetched_results: dict|None=None) -> list[dict]:
    countries=cfg.countries or [cfg.region]
    final_per_country=max(5,(cfg.candidate_limit+len(countries)-1)//len(countries))
    oversample=DISCOVERY_OVERSAMPLE.get(cfg.search_mode,2.0)
    discovery_total_limit=min(300,max(cfg.candidate_limit,int(cfg.candidate_limit*oversample+0.999)))
    per_country_limit=max(final_per_country,(discovery_total_limit+len(countries)-1)//len(countries))
    excluded=" ".join(f'-"{term}"' if " " in term else f"-{term}" for term in QUERY_EXCLUDE_TERMS)
    profiles=SEARCH_PROFILES.get(cfg.search_mode,SEARCH_PROFILES["균형"])
    keywords=list(dict.fromkeys(cfg.keywords))
    base_count=min(len(keywords),max(1,int(getattr(cfg,"base_keyword_count",5) or 5)))
    adaptive_strategy=getattr(cfg,"search_strategy","적응형 최적화")=="적응형 최적화"
    saving_mode=str(getattr(cfg,"api_usage_mode","")).startswith("절약")
    # 절약 모드는 사전 후보 목표, 전체 검색은 기존 여유 후보 목표까지 탐색한다.
    search_target=final_per_country if saving_mode else per_country_limit
    prefetched=dict(prefetched_results or {})
    metrics=stats if stats is not None else {}
    metrics.update({"queries":0,"fallback_queries":0,"query_errors":0,"query_error_details":[],"raw_results":0,"prefilter_rejected":0,"prefilter_reasons":{},"deduplicated":0,"alternate_urls_stored":0,
                    "source_pages_visited":0,"source_links_found":0,"candidate_shortage":0,
                    "final_candidate_target":cfg.candidate_limit,"discovery_target":discovery_total_limit,
                    "oversample_factor":oversample,"candidate_pool_size":0,
                    "keyword_stats":{},"keyword_stats_by_country":{},"adaptive_expansion_queries":0,
                    "adaptive_expansion_by_country":{},"search_stop_by_country":{}})
    def keyword_stat(keyword: str,country: str) -> dict:
        country_stats=metrics["keyword_stats_by_country"].setdefault(country,{})
        return country_stats.setdefault(keyword,{"calls":0,"raw_results":0,"accepted_results":0,"rejected_results":0})
    selected=[]
    api_stopped=False
    country_queries={country:0 for country in countries}
    per_country_cap=(max(0,int(getattr(cfg,"max_search_queries",0) or 0))+len(countries)-1)//len(countries) if countries else 0
    def query_allowed(country: str):
        cap=max(0,int(getattr(cfg,"max_search_queries",0) or 0))
        return not api_stopped and (not cap or (metrics["queries"]<cap and country_queries[country]<per_country_cap))
    for country in countries:
        pool={}; source_pages=[]
        metrics["adaptive_expansion_by_country"][country]=0
        # 절약모드에서는 호출 예산이 작기 때문에 프로필을 먼저 순회하면
        # 앞쪽 키워드만 반복되고 뒤쪽 키워드가 한 번도 실행되지 않는다.
        # 적응형 순서는 모든 키워드를 먼저 한 번씩 배정한 뒤, 남은 예산에서
        # 프로필을 추가 회전시킨다. 따라서 국가당 5회여도 키워드 5개가 모두 시험된다.
        if getattr(cfg,"search_strategy","적응형 최적화")=="수동 입력 그대로":
            query_tasks=[(profile,keyword) for profile in profiles for keyword in keywords]
        else:
            query_tasks=[]
            if keywords:
                for index,keyword in enumerate(keywords):
                    query_tasks.append((profiles[index % len(profiles)],keyword))
                for profile in profiles:
                    for keyword in keywords:
                        task=(profile,keyword)
                        if task not in query_tasks: query_tasks.append(task)
        for task_index,(profile,keyword) in enumerate(query_tasks):
                if not query_allowed(country): break
                # 기본 5개 축으로 목표 후보를 채우면 확장 축은 호출하지 않는다.
                # 부족할 때만 뒤의 3개를 실행해 수집량을 보충하면서 평균 시간을 줄인다.
                if adaptive_strategy and task_index >= base_count and len(pool) >= search_target:
                    metrics["search_stop_by_country"][country]="사전 후보 목표 충족"
                    break
                if adaptive_strategy and base_count <= task_index < min(base_count+3,len(keywords)):
                    metrics["adaptive_expansion_queries"] += 1
                    metrics["adaptive_expansion_by_country"][country] += 1
                query=build_search_query(country,keyword,profile,excluded)
                metrics["queries"]+=1; country_queries[country]+=1
                stat=keyword_stat(keyword,country); stat["calls"]+=1
                try:
                    results=prefetched.pop(query) if query in prefetched else tavily.search(query,max_results=20,country="",minimal=False)
                except SearchPlanLimitError as exc:
                    metrics["query_errors"]+=1; api_stopped=True
                    metrics["stop_reason"]=f"{tavily.provider_name} 사용 한도 초과"
                    metrics["query_error_details"].append(f"{country} · {profile} · 공급자 한도 · {str(exc)[:180]}")
                    break
                except Exception as exc:
                    metrics["query_errors"]+=1
                    if len(metrics["query_error_details"])<5:
                        metrics["query_error_details"].append(f"{country} · {profile} · {type(exc).__name__}: {str(exc)[:180]}")
                    continue
                metrics["raw_results"]+=len(results)
                stat["raw_results"]+=len(results)
                for item in results:
                    if profile=="전시회·협회" and is_ecosystem_source(item,cfg):
                        source_pages.append({"url":str(item.get("url") or ""),"keyword":keyword,"query":query,
                                             "description":str(item.get("content") or "")})
                        continue
                    accepted,score,reject_reason=candidate_prefilter(item,country,cfg,profile)
                    if not accepted:
                        stat["rejected_results"]+=1
                        metrics["prefilter_rejected"]+=1
                        metrics["prefilter_reasons"][reject_reason]=metrics["prefilter_reasons"].get(reject_reason,0)+1
                        continue
                    stat["accepted_results"]+=1
                    url=str(item.get("url") or ""); base=registrable_domain(url)
                    candidate={"url":url,"root_url":root_url(url),"keyword":keyword,"query":query,
                        "description":str(item.get("content") or ""),"title":str(item.get("title") or ""),
                        "target_country":country,"discovery_source":profile,"discovery_url":url,"candidate_score":score,"alternate_urls":[url]}
                    if base in pool:
                        metrics["deduplicated"]+=1
                        existing=pool[base]
                        alternates=list(dict.fromkeys(existing.get("alternate_urls",[])+[url]))[:6]
                        if len(alternates)>len(existing.get("alternate_urls",[])): metrics["alternate_urls_stored"]+=1
                        sources=list(dict.fromkeys(existing["discovery_source"].split("+")+[profile]))
                        if score>existing["candidate_score"]:
                            candidate["discovery_source"]="+".join(sources); candidate["alternate_urls"]=alternates; pool[base]=candidate
                        else: existing["discovery_source"]="+".join(sources); existing["alternate_urls"]=alternates
                    else: pool[base]=candidate
                time.sleep(cfg.request_delay)
        product_hints=[term.strip() for term in cfg.product.split(",") if term.strip()] or [cfg.industry]
        fallback_queries=[]
        # 적응형 검색이 최종 후보 목표를 채운 경우에는 오버샘플 상한까지
        # 자동보충을 이어서 호출하지 않는다. 부족할 때만 확장 3개·보충축을
        # 사용해 수집량을 늘린다.
        if len(pool)<per_country_limit and (not adaptive_strategy or len(pool)<search_target):
            local_terms=country_meta(country).get("local_buyer",[])
            target_tld=country_meta(country).get("tld","")
            if local_terms:
                for product_hint in product_hints[:3]:
                    fallback_queries.append(f'{country} {product_hint} {" ".join(local_terms[:3])}')
                    if target_tld:
                        fallback_queries.append(f'site:.{target_tld} {product_hint} {" ".join(local_terms[:2])}')
            for product_hint in product_hints[:5]:
                fallback_queries.extend((
                    f'{country} {product_hint} importer distributor wholesaler company',
                    f'{country} {product_hint} retail chain clinic salon supplier',
                ))
            recovery_roles=("importer", "exclusive distributor", "wholesale distributor", "retail chain", "beauty supplier", "aesthetic clinic", "beauty salon")
            recovery_product=product_hints[0]
            for role in recovery_roles:
                fallback_queries.append(f'{country} {recovery_product} {role} official website contact')
            for keyword in cfg.keywords:
                fallback_queries.append(f'{country} {keyword} official website contact')
        fallback_cap={"정확도 우선":12,"균형":18,"최대수집":25}.get(cfg.search_mode,18)
        for fallback_query in list(dict.fromkeys(fallback_queries))[:fallback_cap]:
            if len(pool)>=(search_target if adaptive_strategy else per_country_limit) or not query_allowed(country): break
            metrics["queries"]+=1; metrics["fallback_queries"]+=1; country_queries[country]+=1
            stat=keyword_stat(fallback_query,country); stat["calls"]+=1
            try: fallback_results=tavily.search(fallback_query,max_results=20,country="",minimal=False)
            except SearchPlanLimitError as exc:
                metrics["query_errors"]+=1; api_stopped=True; fallback_results=[]
                metrics["stop_reason"]=f"{tavily.provider_name} 사용 한도 초과"
                metrics["query_error_details"].append(f"{country} · 자동보충 · 공급자 한도 · {str(exc)[:180]}")
            except Exception as exc:
                metrics["query_errors"]+=1; fallback_results=[]
                if len(metrics["query_error_details"])<5:
                    metrics["query_error_details"].append(f"{country} · 자동보충 · {type(exc).__name__}: {str(exc)[:180]}")
            metrics["raw_results"]+=len(fallback_results)
            stat["raw_results"]+=len(fallback_results)
            for item in fallback_results:
                accepted,score,reject_reason=candidate_prefilter(item,country,cfg,"자동보충")
                if not accepted:
                    stat["rejected_results"]+=1
                    metrics["prefilter_rejected"]+=1
                    metrics["prefilter_reasons"][reject_reason]=metrics["prefilter_reasons"].get(reject_reason,0)+1
                    continue
                stat["accepted_results"]+=1
                url=str(item.get("url") or ""); base=registrable_domain(url)
                candidate={"url":url,"root_url":root_url(url),"keyword":"자동보충","query":fallback_query,
                    "description":str(item.get("content") or ""),"title":str(item.get("title") or ""),
                    "target_country":country,"discovery_source":"자동보충","discovery_url":url,"candidate_score":score,"alternate_urls":[url]}
                if base in pool:
                    metrics["deduplicated"]+=1
                    existing=pool[base]
                    alternates=list(dict.fromkeys(existing.get("alternate_urls",[])+[url]))[:6]
                    if len(alternates)>len(existing.get("alternate_urls",[])): metrics["alternate_urls_stored"]+=1
                    sources=list(dict.fromkeys(existing["discovery_source"].split("+")+["자동보충"]))
                    if score>existing["candidate_score"]:
                        candidate["discovery_source"]="+".join(sources); candidate["alternate_urls"]=alternates; pool[base]=candidate
                    else: existing["discovery_source"]="+".join(sources); existing["alternate_urls"]=alternates
                else: pool[base]=candidate
        if "전시회·협회" in profiles:
            seen_sources=set()
            for source in source_pages:
                if adaptive_strategy and len(pool)>=search_target: break
                source_url=source["url"]
                if not source_url or source_url in seen_sources or len(seen_sources)>=3: continue
                seen_sources.add(source_url); metrics["source_pages_visited"]+=1
                try: official_links=external_company_links(source_url,limit=10)
                except Exception:
                    metrics["query_errors"]+=1; continue
                metrics["source_links_found"]+=len(official_links)
                for official in official_links:
                    base=registrable_domain(official)
                    candidate={"url":official,"root_url":official,"keyword":source["keyword"],"query":source["query"],
                        "description":source["description"],"title":"","target_country":country,
                        "discovery_source":"전시회·협회","discovery_url":source_url,"candidate_score":4,"alternate_urls":[official]}
                    if base in pool:
                        metrics["deduplicated"]+=1
                        existing=pool[base]
                        sources=list(dict.fromkeys(existing["discovery_source"].split("+")+["전시회·협회"]))
                        existing["discovery_source"]="+".join(sources)
                    else: pool[base]=candidate
        ranked=sorted(pool.values(),key=lambda row:(row["candidate_score"],"공식기업" in row["discovery_source"]),reverse=True)
        chosen=ranked[:per_country_limit]; selected.extend(chosen)
        metrics["candidate_pool_size"]+=len(pool)
        if len(chosen)<per_country_limit: metrics["candidate_shortage"]+=per_country_limit-len(chosen)
        metrics["search_stop_by_country"].setdefault(country,"검색 한도 또는 검색어 소진" if len(pool)<search_target else "사전 후보 목표 충족")
    metrics["queries_by_country"]=country_queries
    for country_stats in metrics["keyword_stats_by_country"].values():
        for keyword,stat in country_stats.items():
            combined=metrics["keyword_stats"].setdefault(keyword,{key:0 for key in stat})
            for key,value in stat.items(): combined[key]+=value
    return selected[:discovery_total_limit]


def scrape_one(candidate: dict,cfg: CollectionConfig) -> BuyerRecord | None:
    deadline=time.monotonic()+18
    company_root=candidate.get("root_url") or root_url(candidate["url"])
    discovery_url=candidate.get("url") or candidate.get("discovery_url") or ""
    start_urls=[company_root]
    if (discovery_url and registrable_domain(discovery_url)==registrable_domain(company_root)
            and discovery_url.rstrip("/")!=company_root.rstrip("/")):
        start_urls.append(discovery_url)
    start_urls.extend(url for url in candidate.get("alternate_urls",[]) if registrable_domain(url)==registrable_domain(company_root))
    start_urls=list(dict.fromkeys(start_urls))[:4]
    html=""; final=""
    for start_url in start_urls:
        if time.monotonic()>=deadline: break
        if not robots_allowed(start_url): continue
        try:
            html,final=fetch_html(start_url)
            if html: break
        except Exception: continue
    if not html: return None
    first=parse_html(html,final)
    found={e:(final,contact_source_priority(final)) for e in first["emails"]}
    phones=first["phones"]
    evidence_text=[first["text"]]
    identity_text=[first["text"]]
    evidence_pages=[final]
    target_country=candidate.get("target_country") or cfg.region
    root_host=registrable_domain(final)

    def build_record() -> BuyerRecord:
        host=domain(final)
        official=sorted(
            (e for e in found if registrable_domain(e.split("@")[-1])==registrable_domain(host)),
            key=lambda e:email_candidate_sort_key(e,found[e][1]),
        )
        cross_domain=sorted((e for e in found if e not in official),key=lambda e:email_candidate_sort_key(e,found[e][1]))
        chosen=official[0] if official else (cross_domain[0] if cross_domain else "")
        # 공식 홈페이지의 해외파트너·영업 페이지에서 공개한 B2B 주소는 관계사
        # 도메인일 수 있다. 일반 대표주소보다 역할이 명확한 경우에만 우선한다.
        if official and cross_domain:
            related=cross_domain[0]
            related_source_rank=found[related][1]
            if (related_source_rank>=5 and email_purpose(related).startswith("B2B")
                    and not email_purpose(official[0]).startswith("B2B")):
                chosen=related
        company_name=clean_company_name(first["site_name"],first["title"],host,first.get("jsonld_name",""),first.get('text',''))
        brand_name=clean_brand_name(first["site_name"],first["title"],company_name,host)
        phone=next((clean_phone(x,target_country) for x in phones if clean_phone(x,target_country)),"")
        business_description=" ".join(first["text"].split())[:500] or candidate["description"][:500]
        def email_view(email: str) -> dict:
            same_domain=registrable_domain(email.split("@")[-1])==registrable_domain(host)
            source_rank=found[email][1]
            return {"company_email":email,"email_source_url":found[email][0],
                    "email_status":"공식확인","email_domain_status":
                    "동일도메인" if same_domain else "공식페이지·공용메일" if email.split('@')[-1] in {'gmail.com','yahoo.com','hotmail.com','outlook.com'} else "교차도메인·확인필요",
                    "email_grade":"A" if same_domain else "B", "email_purpose":email_purpose(email),
                    "verification_score":None}
        candidates=[email_view(email) for email in sorted(found,key=lambda e:email_candidate_sort_key(e,found[e][1]))]
        record=BuyerRecord(company_id=make_id(registrable_domain(host)),company_name=company_name,brand_name=brand_name,country_region="미확인",
            business_description=business_description,website=root_url(final),company_email=chosen,
            email_candidates=candidates,
            target_country=target_country,
            phone=phone,original_keyword=candidate["keyword"],search_query=candidate["query"],
            discovery_source=candidate.get("discovery_source",""),discovery_url=candidate.get("discovery_url") or candidate.get("url",""),candidate_score=candidate.get("candidate_score",0),
            company_source_url=evidence_pages[0],email_source_url=found.get(chosen,("",0))[0],email_status="공식확인" if chosen else "미확보",
            email_domain_status=("동일도메인" if chosen in official else "공식페이지·관계도메인" if chosen and found.get(chosen,("",0))[1]>=5 else "교차도메인·확인필요" if chosen else "미확보"),
            email_grade=("A" if chosen in official else "B" if chosen else "D"),email_purpose=email_purpose(chosen) if chosen else "",
            evidence_status=("확인됨" if chosen in official else "공식페이지·타도메인" if chosen else "추가확인"))
        apply_quality(record,cfg," ".join(evidence_text),target_country," ".join(identity_text))
        if chosen:
            record.email_domain_status=email_view(chosen)['email_domain_status']
        finalize_email_delivery_grade(record)
        record.discovered_countries=[target_country] if target_country else []
        record.country_assessments=[country_assessment(record)]
        return record

    # 1차 판정은 홈페이지 한 페이지만 사용한다. 명확한 플랫폼·미디어·타국가·
    # 단순 참고기업은 여기서 종료하고, 실제 바이어·검토대상·전략후보만 연락처를 깊게 찾는다.
    provisional=build_record()
    hard_skip_types={
        "플랫폼/디렉터리","도박·스팸","관광·여행","투자·금융사","법률·전문서비스",
        "물류·통관사","산업설비·클린룸","소프트웨어·IT서비스","리서치·미디어",
        "컨설팅·대행사","미용·의료장비사","임상시험·연구대행","업무대행·콜센터",
    }
    deep_eligible=(
        provisional.site_type not in hard_skip_types
        and provisional.quality_decision not in {"타국가후보","참고기업","제외"}
    )
    # 검색결과 점수가 높은 공식기업은 홈페이지에 제품/유통 설명이 부족할 수 있으므로
    # 1차 제외라도 About 페이지 한 번까지는 복구 기회를 준다.
    if (not deep_eligible and provisional.site_type=="기업 공식사이트"
            and provisional.country_score>0 and int(candidate.get("candidate_score",0) or 0)>=10):
        deep_eligible=True
    if not deep_eligible:
        provisional.collection_depth="홈페이지 1차"
        return provisional

    page_candidates=list(first["links"])+explicit_contact_urls(final)
    evidence_url=candidate.get("discovery_url") or candidate.get("url","")
    discovery_path=urllib.parse.urlsplit(evidence_url).path.lower()
    content_path=any(token in discovery_path for token in ("/news","/blog","/article","/academy","/course","/report"))
    if (evidence_url and not content_path and registrable_domain(evidence_url)==registrable_domain(final)
            and evidence_url.rstrip("/")!=final.rstrip("/")):
        page_candidates.insert(0,evidence_url)
    page_candidates=list(dict.fromkeys(page_candidates))
    page_candidates.sort(key=contact_source_priority,reverse=True)
    root_has_official=any(registrable_domain(email.split("@")[-1])==root_host for email in found)
    # A/B 가능성이 높아도 일반 대표주소만 있으면 해외파트너·영업 페이지를
    # 딱 1개 추가 확인한다. 나머지는 기존 조기종료를 유지해 속도 손실을 제한한다.
    generic_official=(root_has_official and provisional.quality_decision=="적합"
                      and provisional.email_purpose=="일반문의")
    page_limit=1 if generic_official else (0 if root_has_official and provisional.quality_decision=="적합" else max(0,cfg.max_pages_per_company-1))
    for url in page_candidates[:page_limit]:
        if time.monotonic()>=deadline: break
        if not robots_allowed(url): continue
        try:
            page_html,resolved=fetch_html(url); page=parse_html(page_html,resolved)
            source_rank=contact_source_priority(resolved)
            for email in page["emails"]:
                previous=found.get(email)
                if previous is None or source_rank>previous[1]: found[email]=(resolved,source_rank)
            evidence_text.append(page["text"])
            if source_rank>=2:
                identity_text.append(page["text"])
            evidence_pages.append(resolved)
            if not phones: phones=page["phones"]
            has_official=any(registrable_domain(email.split("@")[-1])==root_host for email in found)
            if has_official and len(identity_text)>=2: break
            time.sleep(min(cfg.request_delay,0.15))
        except Exception: continue
    record=build_record()
    record.collection_depth="연락처 심층" if page_limit else "홈페이지 완결"
    return record


def make_access_hold(candidate: dict, reason: str) -> dict:
    """접속·파싱 실패 후보를 버리지 않고 검수 대기 행으로 보존한다."""
    url=str(candidate.get("root_url") or candidate.get("url") or "")
    host=registrable_domain(url)
    return {
        "company_id": make_id(host) if host else "",
        "company_name": clean_company_name(candidate.get("title", ""), candidate.get("title", ""), host) if host else (candidate.get("title") or "접속보류 후보"),
        "country_region": "미확인", "target_country": candidate.get("target_country", ""), "verified_country": "",
        "business_description": str(candidate.get("description") or "")[:500], "website": url,
        "company_email": "", "contact_name": "", "contact_title": "", "contact_email": "", "phone": "",
        "original_keyword": candidate.get("keyword", ""), "search_query": candidate.get("query", ""),
        "discovery_source": candidate.get("discovery_source", ""), "discovery_url": candidate.get("discovery_url") or candidate.get("url", ""),
        "candidate_score": candidate.get("candidate_score", 0), "company_source_url": candidate.get("discovery_url") or candidate.get("url", ""),
        "email_source_url": "", "email_status": "미확보", "email_domain_status": "미확보", "email_grade": "보류", "verification_score": None,
        "evidence_status": "접속확인 필요", "country_evidence": "", "country_score": 0, "industry_score": 0,
        "buyer_role_score": 0, "relevance_score": 0, "site_type": "접속·파싱보류", "buyer_type": "미확인",
        "priority": "보류", "decision_evidence": "검색결과는 확보했으나 공식사이트 접속·파싱에 실패",
        "email_purpose": "", "quality_decision": "접속보류", "exclusion_reason": reason or "접속·파싱 실패",
        "collection_depth": "접속 실패·수동확인",
        "collected_at": datetime.now(timezone.utc).isoformat(),
    }


def access_hold_eligible(candidate: dict,cfg: CollectionConfig) -> bool:
    """공식기업일 가능성이 있는 접속 실패만 고객용 보류 목록에 남긴다."""
    url=str(candidate.get("url") or candidate.get("root_url") or "")
    host=registrable_domain(url)
    title=str(candidate.get("title") or "").lower()
    description=str(candidate.get("description") or "").lower()
    path=urllib.parse.urlsplit(url).path.lower()
    if not host or is_blocked_domain(host): return False
    if any(term in title for term in NON_COMPANY_TITLE_TERMS): return False
    if any(term in path for term in NON_COMPANY_PATH_TERMS): return False
    if any(term in description for term in PLATFORM_TERMS) and not any(term in description for term in STRONG_BUYER_TERMS): return False
    industry_hit=any(term_present(description,term) for term in industry_terms(cfg))
    buyer_hit=any(term_present(description,term) for term in BUYER_TERMS+STRONG_BUYER_TERMS)
    country=candidate.get("target_country") or cfg.region
    meta=country_meta(country)
    aliases=meta.get("aliases",[])
    tld=meta.get("tld","")
    country_hit=any(alias and term_present(description,alias) for alias in aliases)
    tld_hit=bool(tld and (host.endswith("."+tld) or host.endswith(".com."+tld)))
    return industry_hit and buyer_hit and (country_hit or tld_hit)


def enrich_hunter(record: BuyerRecord,hunter: HunterProvider,verify: bool):
    if record.company_email: return
    choices=hunter.domain_search(domain(record.website))
    choices=[x for x in choices if x.get("value") and valid_email(x["value"]) and email_is_sendable(x["value"])]
    choices.sort(key=lambda x:(x.get("type")!="generic",-(x.get("confidence") or 0)))
    if not choices: return
    item=choices[0]; email=normalize_email(item["value"]); score=int(item.get("confidence") or 0)
    record.company_email=email; record.contact_name=" ".join(filter(None,[item.get("first_name"),item.get("last_name")]))
    record.contact_title=item.get("position") or ""; record.email_source_url=(item.get("sources") or [{}])[0].get("uri","")
    record.email_purpose=email_purpose(email)
    record.email_status="외부확인"; record.email_domain_status="Hunter 외부확인"; record.email_grade="B"; record.verification_score=score; record.evidence_status="외부검증"
    if verify:
        check=hunter.verify(email); result=check.get("status") or check.get("result")
        record.verification_score=int(check.get("score") or score)
        if result in {"valid","deliverable"}: record.email_status="검증완료"; record.email_grade="B"
        elif result in {"invalid","undeliverable"}:
            record.exclusion_reason="이메일 검증 실패"; record.email_grade="제외"
        elif check.get("accept_all") or result in {"accept_all","risky"}:
            record.email_status="검증필요"; record.email_grade="C"; record.exclusion_reason="Catch-all 또는 수신 불확실"


def collect_buyers(cfg: CollectionConfig,tavily_key: str,hunter_key: str="",progress: Callable|None=None,
                   checkpoint: Callable|None=None,resume_state: dict|None=None,brave_key: str="", shared_cache: bool=False) -> dict:
    global _RUN_PAGE_CACHE, _RUN_PAGE_LOCKS
    # A run-scoped cache reuses successful HTML across countries and search hits.
    # It is discarded before the next run so one campaign cannot leak evidence into another.
    if not shared_cache or _RUN_PAGE_CACHE is None:
        _RUN_PAGE_CACHE={}; _RUN_PAGE_LOCKS={}
    started=time.monotonic(); resume_state=resume_state or {}; errors=list(resume_state.get("errors",[]))
    resumed_from_checkpoint=bool(resume_state)
    records=[BuyerRecord(**row) for row in resume_state.get("records",[])]; tavily=make_search_provider(getattr(cfg,"search_provider","Brave"),brave_key,tavily_key); hunter=HunterProvider(hunter_key) if cfg.use_hunter else None
    mode_label=getattr(cfg,"api_usage_mode","전체 실검색")
    api_mode="cache_only" if mode_label.startswith("개발") else "cache_first"
    if hasattr(tavily,"configure"): tavily.configure(api_mode)
    first_country=(cfg.countries or [cfg.region])[0]
    saved_candidates=resume_state.get("candidates") or []
    prefetched_results={}
    continuing=bool(resume_state.get("discovery_summary") and not saved_candidates)
    if continuing:
        diagnostic=resume_state.get("discovery_summary",{}).get("diagnostic",{"ok":True})
        discovery_stats=dict(resume_state.get("discovery_summary",{})); candidates=[]; search_status="ok"
    elif saved_candidates:
        diagnostic=resume_state.get("discovery_summary",{}).get("diagnostic",{"ok":True,"message":"저장된 후보에서 재개"})
        discovery_stats=dict(resume_state.get("discovery_summary",{})); candidates=saved_candidates; search_status="ok"
    else:
        first_profile=SEARCH_PROFILES.get(cfg.search_mode,SEARCH_PROFILES["균형"])[0]
        first_keyword=(cfg.keywords or [cfg.industry])[0]
        excluded=" ".join(f'-"{term}"' if " " in term else f"-{term}" for term in QUERY_EXCLUDE_TERMS)
        diagnostic_query=build_search_query(first_country,first_keyword,first_profile,excluded)
        # 첫 검색 결과를 메모리에서 재사용한다. 디스크 캐시를 쓸 수 없어도
        # 진단 때문에 동일 검색을 한 번 더 호출하지 않는다.
        diagnostic=search_diagnostic(tavily,first_country,cfg.industry,diagnostic_query,20,result_cache=prefetched_results)
        discovery_stats={"diagnostic":diagnostic}
    if not saved_candidates and not continuing and not diagnostic.get("ok") and not prefetched_results:
        candidates=[]
        discovery_stats.update({"queries":0,"fallback_queries":0,"query_errors":int(bool(diagnostic.get("error"))),"query_error_details":[diagnostic.get("message","")] if diagnostic.get("error") else [],"raw_results":0,"prefilter_rejected":0,"prefilter_reasons":{},"deduplicated":0,"source_pages_visited":0,"source_links_found":0,"candidate_shortage":cfg.candidate_limit})
        discovery_stats["queries"]=1
        discovery_stats["queries_by_country"]={first_country:1}
        search_status="diagnostic_failed"
    elif not saved_candidates and not continuing:
        candidates=discover(cfg,tavily,discovery_stats,prefetched_results=prefetched_results)
        search_status="ok" if discovery_stats.get("raw_results",0)>0 else "empty_after_search"
    previous_api_log=list(discovery_stats.get("api_response_log",[])) if resumed_from_checkpoint else []
    discovery_stats['_prior_api_log']=previous_api_log
    discovery_stats["api_response_log"]=previous_api_log+list(tavily.response_log)
    discovery_stats["api_credits_used"]=sum(int(row.get("credits") or 0) for row in discovery_stats["api_response_log"])
    discovery_stats.setdefault("scrape_skipped",0)
    discovery_stats.setdefault("access_hold_discarded",0)
    total=len(candidates)
    access_holds=list(resume_state.get("access_holds",[]))
    completed_domains=set(resume_state.get("completed_domains") or discovery_stats.get("completed_domain_keys",[]))
    def task_key(candidate: dict) -> str:
        host=registrable_domain(candidate.get("root_url") or candidate.get("url",""))
        return f"{host}|{candidate.get('target_country') or cfg.region}"
    # Old checkpoints contain bare domains; new checkpoints use domain|country so a
    # shared international website can be assessed for each selected country once.
    pending=[candidate for candidate in candidates
             if registrable_domain(candidate.get("root_url") or candidate.get("url","")) not in completed_domains
             and task_key(candidate) not in completed_domains]

    def inspect(candidate):
        _WEBSITE_HTTP.active = True
        try:
            record=scrape_one(candidate,cfg)
            if record and hunter and record.quality_decision=="적합" and not record.company_email: enrich_hunter(record,hunter,cfg.verify_hunter)
            return candidate,record,None
        except Exception as exc:
            return candidate,None,exc
        finally:
            session = getattr(_WEBSITE_HTTP, "session", None)
            if session is not None:
                session.close()
                del _WEBSITE_HTTP.session
            _WEBSITE_HTTP.active = False

    done=len(completed_domains)
    # v2.23.0: paid servers can use higher concurrency, while the UI keeps a
    # conservative default. The cap prevents runaway parallelism on shared hosts.
    workers=max(1,min(int(getattr(cfg,"worker_count",8)),12))
    def analyze(batch):
      nonlocal done
      with ThreadPoolExecutor(max_workers=workers,thread_name_prefix="gloeum-company") as executor:
        futures=[executor.submit(inspect,candidate) for candidate in batch]
        for future in as_completed(futures):
            candidate,record,exc=future.result()
            domain_key=task_key(candidate)
            if domain_key: completed_domains.add(domain_key)
            if record:
                records.append(record)
            else:
                if exc: errors.append(f"{candidate['url']}: {type(exc).__name__}")
                discovery_stats["scrape_skipped"]+=1
                if access_hold_eligible(candidate,cfg):
                    reason=f"공식기업 후보 · 접속·파싱 예외: {type(exc).__name__}" if exc else "공식기업 후보 · 접속·파싱 실패 또는 robots.txt 제한"
                    access_holds.append(make_access_hold(candidate,reason))
                else:
                    discovery_stats["access_hold_discarded"]+=1
            done+=1
            if checkpoint:
                discovery_stats['api_response_log']=previous_api_log+list(tavily.response_log)
                checkpoint({"schema_version":SCHEMA_VERSION,"config":asdict(cfg),"candidates":candidates,
                    "completed_domains":sorted(completed_domains),"records":[asdict(row) for row in records],
                    "access_holds":access_holds,"errors":errors,"discovery_summary":discovery_stats,
                    "progress_done":done,"progress_total":total,"elapsed_seconds":round(time.monotonic()-started,2)})
            if progress: progress(done,total,f"{done}/{total} 기업 병렬 조사 중 · 이메일 {sum(bool(r.company_email) for r in records)}개")
    analyze(pending)
    discovery_stats["completed_domain_keys"]=sorted(completed_domains)
    # Refill is based on completed analyses and unique eligible addresses, not raw hits.
    if cfg.refill_enabled and search_status=="ok":
        from collection_refill import refill_batches
        for batch in refill_batches(cfg,tavily,records,candidates,discovery_stats,progress):
            candidates.extend(batch); total=len(candidates)
            analyze(batch)
            discovery_stats["completed_domain_keys"]=sorted(completed_domains)
            if checkpoint:
                discovery_stats['api_response_log']=previous_api_log+list(tavily.response_log)
                checkpoint({"schema_version":SCHEMA_VERSION,"config":asdict(cfg),"candidates":candidates,
                    "completed_domains":sorted(completed_domains),"records":[asdict(row) for row in records],
                    "access_holds":access_holds,"errors":errors,"discovery_summary":discovery_stats,
                    "progress_done":done,"progress_total":total,"elapsed_seconds":round(time.monotonic()-started,2)})
    discovery_stats["api_response_log"]=previous_api_log+list(tavily.response_log)
    discovery_stats["api_credits_used"]=sum(int(row.get("credits") or 0) for row in discovery_stats["api_response_log"])
    discovery_stats.pop('_prior_api_log',None)
    if not shared_cache:
        _RUN_PAGE_CACHE=None; _RUN_PAGE_LOCKS={}
    return summarize_collection(cfg,records,access_holds,errors,discovery_stats,search_status,tavily.provider_name,started,resumed_from_checkpoint)


def summarize_collection(cfg,records,access_holds,errors,discovery_stats,search_status,provider_name,started,resumed_from_checkpoint=False):
    unique=deduplicate_records(records)
    from delivery_policy import approval_rows
    email_rows=approval_rows(unique,include_external=cfg.include_external_sendable)
    sendable=len(email_rows)
    mailing_company_count=sum(any(row.get("company_id")==r.company_id for row in email_rows) for r in unique)
    blocked_email_purpose=sum(bool(r.company_email) and not email_is_sendable(r.company_email) for r in unique)
    qualified=sum(r.quality_decision=="적합" for r in unique)
    qualified_target=int(getattr(cfg,"qualified_candidate_target",0) or cfg.target_per_country*len(cfg.countries or [cfg.region]))
    qualified_target_met=qualified>=qualified_target
    tier_a=sum(r.priority=="A" for r in unique)
    tier_b=sum(r.priority=="B" for r in unique)
    tier_c=sum(r.priority=="C" for r in unique)
    strategic=sum(r.priority=="전략" for r in unique)
    reference=sum(r.quality_decision=="참고기업" for r in unique)
    other_country=sum(r.quality_decision=="타국가후보" for r in unique)
    excluded=sum(r.quality_decision=="제외" for r in unique)
    quality_reasons={}
    for record in unique:
        if record.quality_decision=="적합": continue
        for reason in (part.strip() for part in record.exclusion_reason.split(";") if part.strip()):
            quality_reasons[reason]=quality_reasons.get(reason,0)+1
    discovery_stats["quality_exclusion_reasons"]=quality_reasons
    country_summary=[]
    for country in (cfg.countries or [cfg.region]):
        subset=[r for r in unique if r.target_country==country]
        country_summary.append({"country":country,"records":len(subset),"qualified":sum(r.quality_decision=="적합" for r in subset),
            "tier_a":sum(r.priority=="A" for r in subset),"tier_b":sum(r.priority=="B" for r in subset),
            "tier_c":sum(r.priority=="C" for r in subset),"strategic":sum(r.priority=="전략" for r in subset),"reference":sum(r.quality_decision=="참고기업" for r in subset),
            "other_country":sum(r.quality_decision=="타국가후보" for r in subset),
            "excluded":sum(r.quality_decision=="제외" for r in subset),
            "emails_found":sum(bool(r.company_email) for r in subset),
            "qualified_emails_found":sum(r.quality_decision=="적합" and bool(r.company_email) for r in subset),
            "mailing_emails_found":sum(row.get('target_country')==country for row in email_rows),
            "sendable":sum(row.get('target_country')==country for row in email_rows),
            "access_holds":sum(row.get("target_country")==country for row in access_holds)})
    qualified_email_count=sum(r.quality_decision=="적합" and bool(r.company_email) for r in unique)
    mailing_email_count=len(email_rows)
    discovery_stats["access_holds"]=len(access_holds)
    # 목표 달성 수량은 실제 공식사이트 분석이 끝난 기업만 계산한다.
    # 접속보류는 별도 참고지표이며 목표 수량을 부풀리지 않는다.
    candidate_results=len(unique)
    target_met=candidate_results>=cfg.candidate_limit
    email_target_met=sendable>=cfg.verified_email_target
    collection_status="목표달성" if target_met and email_target_met and qualified_target_met else "목표미달"
    discovery_stats["resumed_from_checkpoint"] = resumed_from_checkpoint
    discovery_stats["homepage_only"]=sum(r.collection_depth=="홈페이지 1차" for r in unique)
    discovery_stats["homepage_complete"]=sum(r.collection_depth=="홈페이지 완결" for r in unique)
    discovery_stats["deep_contact_review"]=sum(r.collection_depth=="연락처 심층" for r in unique)
    elapsed=round(time.monotonic()-started,2)
    api_calls=max(int(discovery_stats.get("api_credits_used",0) or 0),1)
    efficiency={
        "candidates_per_api_call":round(candidate_results/api_calls,2),
        "sendable_per_api_call":round(sendable/api_calls,2),
        "seconds_per_analyzed_company":round(elapsed/max(candidate_results,1),2),
    }
    return {"schema_version":SCHEMA_VERSION,"mode":"live","search_status":search_status,"collection_status":collection_status,"search_provider":provider_name,"config":asdict(cfg),"generated_at":datetime.now(timezone.utc).isoformat(),
        "summary":{"records":len(unique),"emails_found":sum(bool(r.company_email) for r in unique),"qualified_emails_found":qualified_email_count,"mailing_emails_found":mailing_email_count,"sendable":sendable,"blocked_email_purpose":blocked_email_purpose,
                   "qualified":qualified,"qualified_target":qualified_target,"qualified_target_met":qualified_target_met,"qualified_shortfall":max(qualified_target-qualified,0),"tier_a":tier_a,"tier_b":tier_b,"tier_c":tier_c,"strategic":strategic,"reference":reference,"other_country":other_country,"excluded":excluded,
                   "usable_list":tier_a+tier_b+tier_c+strategic+reference,"customer_list":tier_a+tier_b+tier_c+strategic,"missing_email":sum(not r.company_email for r in unique),"mailing_companies":mailing_company_count,"mailing_unique_emails":mailing_email_count,"access_holds":len(access_holds),"candidate_results":candidate_results,"target_met":target_met,"email_target_met":email_target_met,"candidate_shortfall":max(cfg.candidate_limit-candidate_results,0),"email_shortfall":max(cfg.verified_email_target-sendable,0),"elapsed_seconds":elapsed,"candidates_per_api_call":efficiency["candidates_per_api_call"],"sendable_per_api_call":efficiency["sendable_per_api_call"],"seconds_per_analyzed_company":efficiency["seconds_per_analyzed_company"],"resumed_from_checkpoint":resumed_from_checkpoint,"errors":len(errors)},
        "discovery_summary":discovery_stats,"country_summary":country_summary,"errors":errors,"records":[asdict(r) for r in unique],"access_holds":access_holds}
