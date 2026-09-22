"""Phrase evidence and curated Vietnamese aliases, without network translation.

An alias proves a product mention, never purchase intent. Unknown products retain
their English phrase. Accent folding handles Vietnamese pages without diacritics.
"""
import re
import unicodedata
from functools import lru_cache

VI = {
    "facial serum": ("serum dưỡng da", "tinh chất dưỡng da"),
    "moisturizing cream": ("kem dưỡng ẩm",), "sunscreen": ("kem chống nắng",),
    "facial cleanser": ("sữa rửa mặt",), "sheet masks": ("mặt nạ giấy",),
    "lipstick": ("son môi",), "foundation makeup": ("kem nền",),
    "eye shadow": ("phấn mắt",), "mascara": ("mascara",), "blush makeup": ("phấn má",),
    "shampoo": ("dầu gội",), "hair conditioner": ("dầu xả",),
    "body wash": ("sữa tắm",), "body lotion": ("sữa dưỡng thể",), "hand cream": ("kem dưỡng tay",),
    "vitamin supplements": ("thực phẩm bổ sung vitamin", "viên uống vitamin"),
    "probiotic supplements": ("men vi sinh",), "omega 3 supplements": ("viên uống omega 3",),
    "red ginseng supplements": ("hồng sâm",), "collagen supplements": ("collagen dạng uống", "viên uống collagen"),
    "meal replacement shakes": ("sữa lắc thay thế bữa ăn",),
    "weight management supplements": ("thực phẩm hỗ trợ giảm cân",),
    "low calorie snacks": ("đồ ăn nhẹ ít calo",),
    "high protein meal replacements": ("bữa ăn thay thế giàu protein",),
    "dietary fiber supplements": ("thực phẩm bổ sung chất xơ",),
    "protein powder": ("bột protein", "bột đạm"), "protein bars": ("thanh protein",),
    "t shirts": ("áo thun", "áo phông"), "summer dresses": ("váy mùa hè",),
    "knitwear": ("đồ dệt kim",), "winter coats": ("áo khoác mùa đông",), "jackets": ("áo khoác",),
    "sports leggings": ("quần legging thể thao",), "tracksuits": ("bộ đồ thể thao",),
    "yoga apparel": ("đồ tập yoga",), "golf apparel": ("quần áo golf",),
    "handbags": ("túi xách",), "backpacks": ("ba lô",), "sneakers": ("giày thể thao",),
    "fashion jewelry": ("trang sức thời trang",), "hair accessories": ("phụ kiện tóc",),
    "filling machines": ("máy chiết rót",), "labeling machines": ("máy dán nhãn",),
    "sealing machines": ("máy hàn miệng túi", "máy dán miệng"),
    "wrapping machines": ("máy bọc màng", "máy quấn màng"), "cartoning machines": ("máy đóng hộp",),
    "cnc lathes": ("máy tiện cnc",), "machining centers": ("trung tâm gia công",),
    "milling machines": ("máy phay",), "grinding machines": ("máy mài",),
    "cutting tools": ("dụng cụ cắt gọt",), "centrifugal pumps": ("máy bơm ly tâm",),
    "diaphragm pumps": ("bơm màng",), "gear pumps": ("bơm bánh răng",),
    "control valves": ("van điều khiển",), "ball valves": ("van bi",),
    "servo motors": ("động cơ servo",), "industrial sensors": ("cảm biến công nghiệp",),
    "industrial bearings": ("vòng bi công nghiệp",), "industrial robots": ("robot công nghiệp",),
    "instant noodles": ("mì ăn liền", "mì gói"), "ready to eat rice": ("cơm ăn liền", "cơm đóng hộp"),
    "seaweed snacks": ("snack rong biển", "rong biển ăn liền"), "rice crackers": ("bánh gạo",),
    "frozen dumplings": ("há cảo đông lạnh", "bánh xếp đông lạnh", "sủi cảo đông lạnh"),
    "soy sauce": ("nước tương",), "barbecue sauce": ("sốt nướng",), "food seasonings": ("gia vị thực phẩm",),
    "fruit juice": ("nước ép trái cây",), "soft drinks": ("nước giải khát",),
    "blood pressure monitors": ("máy đo huyết áp",), "blood glucose meters": ("máy đo đường huyết",),
    "medical gloves": ("găng tay y tế",), "medical syringes": ("bơm kim tiêm",),
    "hospital beds": ("giường bệnh",), "wheelchairs": ("xe lăn",),
    "laundry detergent": ("bột giặt", "nước giặt"), "dishwashing detergent": ("nước rửa chén",),
    "wet wipes": ("khăn ướt",), "kitchen utensils": ("dụng cụ nhà bếp",),
    "professional hair dryers": ("máy sấy tóc chuyên nghiệp",), "hair straighteners": ("máy duỗi tóc",),
    "salon chairs": ("ghế salon tóc",), "hair clippers": ("tông đơ cắt tóc",),
    "air purifiers": ("máy lọc không khí",), "wireless earbuds": ("tai nghe không dây",),
    "smart watches": ("đồng hồ thông minh",), "semiconductors": ("chất bán dẫn",),
    "packaging films": ("màng bao bì",), "corrugated boxes": ("thùng carton",),
    "packaging pouches": ("túi bao bì",), "industrial adhesives": ("keo công nghiệp",),
    "nonwoven fabrics": ("vải không dệt",),
}


def normalize(text):
    text=unicodedata.normalize("NFKD", str(text).casefold().replace("đ", "d"))
    return " ".join(re.sub(r"[^\w]+", " ", "".join(c for c in text if not unicodedata.combining(c))).split())


@lru_cache(maxsize=1024)
def aliases(product, country=""):
    variants=[product]
    # Only safe plural endings; never reduce a product phrase to broad tokens.
    if product.casefold().endswith(("machines", "masks", "supplements", "pumps", "valves", "crackers", "dumplings")):
        variants.append(product[:-1])
    if country=="Vietnam": variants.extend(VI.get(product.casefold(), ()))
    return tuple(dict.fromkeys(variants))


def phrase_present(text, phrase):
    return f" {normalize(phrase)} " in f" {normalize(text)} " if normalize(phrase) else False


def product_evidence(text, products, country=""):
    normalized=f" {normalize(text)} "
    return {p:[a for a in aliases(p,country) if f" {normalize(a)} " in normalized] for p in products
            if any(f" {normalize(a)} " in normalized for a in aliases(p,country))}


def subcategory_products(major, subcategories, products):
    from industry_catalog import CATALOG
    catalog=CATALOG.get(major,(None,{}))[1]
    return {s:[p for p in products if normalize(p) in {normalize(v) for v in catalog.get(s,{}).values()}]
            for s in subcategories}
