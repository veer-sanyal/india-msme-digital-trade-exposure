"""Build MSME-by-NIC processed slices from Udyam Bulletin VII.

Source: Office of Development Commissioner (MSME), "Analysis of Udyam
Registration Data", Bulletin VII, 13 Oct 2021. Cutoff 30 Sep 2021.
URL: https://dcmsme.gov.in/Buletin-VII-Analysis-of-Udyam-Registration-Data.pdf

Three outputs in data/processed/:
  msme_nic_5digit.csv     Top 50 manufacturing + Top 50 services NIC 5-digit codes
  msme_nic_division.csv   Same data aggregated to NIC 2-digit division and ISIC section
  msme_nic_top5_msm.csv   Section 15 chart: top 5 NIC 2-digit divisions split micro/small/medium

The published bulletin does not give a full NIC 2-digit by enterprise-size
cross-tab. The two top-50 5-digit tables (Annexures 3A and 3B) carry totals
only; the size split exists only for the top 5 divisions in Section 15. This
script captures everything that is published; the dashboard layers on current
totals from the MSME Annual Report 2024-25 for headline figures.

Run from repo root:
    python scripts/build_msme_nic.py
"""

from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)


# Annexure 3A: Top 50 NIC 5-digit codes for Manufacturing Sector.
# Tuples are (rank, nic_5digit, description, msme_count).
MANUFACTURING_TOP_50 = [
    (1, 32909, "Manufacture of other articles n.e.c.", 205103),
    (2, 14101, "Manufacture of all types of textile garments and clothing accessories", 100382),
    (3, 41001, "Construction of buildings carried out on own-account basis or on a fee or contract basis", 80196),
    (4, 13999, "Manufacture of other textiles/textile products n.e.c.", 73707),
    (5, 10799, "Other semi-processed, processed or instant foods n.e.c.", 57894),
    (6, 25999, "Manufacture of other fabricated metal products n.e.c.", 50253),
    (7, 42909, "Other civil engineering projects n.e.c.", 45831),
    (8, 41002, "Activities relating to alteration, addition, repair, maintenance of buildings", 40657),
    (9, 14105, "Custom tailoring", 39066),
    (10, 32111, "Manufacture of jewellery of gold, silver and other precious or base metal", 39042),
    (11, 31001, "Manufacture of furniture made of wood", 36400),
    (12, 13121, "Weaving, manufacture of cotton and cotton mixture fabrics", 34797),
    (13, 22209, "Manufacture of other plastics products n.e.c", 33376),
    (14, 10795, "Grinding and processing of spices", 31512),
    (15, 10611, "Flour milling", 30206),
    (16, 10509, "Manufacture of other dairy products n.e.c.", 26706),
    (17, 42101, "Construction and maintenance of motorways, streets, roads, bridges, tunnels", 25296),
    (18, 24109, "Manufacture of other basic iron and steel n.e.c", 24858),
    (19, 27900, "Manufacture of other electrical equipment", 24602),
    (20, 10712, "Manufacture of biscuits, cakes, pastries, rusks etc.", 23476),
    (21, 14109, "Manufacture of wearing apparel n.e.c.", 22886),
    (22, 10612, "Rice milling", 22527),
    (23, 28299, "Manufacture of other special-purpose machinery n.e.c.", 21776),
    (24, 43900, "Other specialized construction activities", 21330),
    (25, 33140, "Repair of electrical equipment", 21066),
    (26, 13139, "Other activities relating to finishing of textile n.e.c.", 20521),
    (27, 8106, "Crushing and breaking of stone and operation of sand or gravel pits", 19993),
    (28, 10719, "Manufacture of other bakery products n.e.c.", 19291),
    (29, 13122, "Weaving, manufacture of silk and silk mixture fabrics", 18428),
    (30, 31009, "Manufacture of other furniture n.e.c.", 17916),
    (31, 1612, "Operation of agricultural irrigation equipment", 17647),
    (32, 43211, "Installation of electrical wiring and fittings", 17211),
    (33, 10796, "Manufacture of papads, appalam and similar food products", 17169),
    (34, 1620, "Support activities for animal production", 16699),
    (35, 10309, "Preservation of fruit and vegetables n.e.c.", 16613),
    (36, 13991, "Embroidery work and making of laces and fringes", 16473),
    (37, 13131, "Finishing of cotton and blended cotton textiles", 16238),
    (38, 10504, "Manufacture of cream, butter, cheese, curd, ghee, khoya etc.", 15980),
    (39, 16299, "Manufacture of other wood products n.e.c.", 15779),
    (40, 41003, "Assembly and erection of prefabricated constructions on the site", 15591),
    (41, 43303, "Interior and exterior painting, glazing, plastering and decorating of buildings", 15584),
    (42, 10614, "Grain milling other than wheat, rice and dal", 15572),
    (43, 15201, "Manufacture of leather footwear", 15278),
    (44, 22203, "Manufacture of plastic articles for the packing of goods", 15247),
    (45, 10501, "Manufacture of pasteurized milk", 14985),
    (46, 43219, "Other electrical installation n.e.c.", 14377),
    (47, 33200, "Installation of industrial machinery and equipment", 14300),
    (48, 10619, "Other grain milling and processing n.e.c.", 14046),
    (49, 27400, "Manufacture of electric lighting equipment", 14028),
    (50, 36000, "Water collection, treatment and supply", 13918),
]


# Annexure 3B: Top 50 NIC 5-digit codes for Service Sector.
SERVICES_TOP_50 = [
    (1, 49231, "Motorised road freight transport", 219856),
    (2, 96098, "General household maintenance activities", 193407),
    (3, 56291, "Activities of food service contractors", 188483),
    (4, 74909, "Other professional, scientific and technical activities n.e.c.", 132899),
    (5, 82990, "Other business support service activities n.e.c.", 106541),
    (6, 79110, "Travel agency activities", 73400),
    (7, 62099, "Other information technology and computer service activities n.e.c", 70432),
    (8, 49300, "Transport via pipeline", 63531),
    (9, 96020, "Hairdressing and other beauty treatment", 56153),
    (10, 56292, "Operation of canteens on a concession basis", 53529),
    (11, 71100, "Architectural and engineering activities and related technical consultancy", 44303),
    (12, 68200, "Real estate activities on a fee or contract basis", 43038),
    (13, 56102, "Cafeterias, fast-food restaurants and other food preparation in market stalls", 42908),
    (14, 96091, "Social activities such as escort services, marriage bureaus", 41223),
    (15, 77100, "Renting and leasing of motor vehicles", 39388),
    (16, 64990, "Other financial service activities, except insurance and pension funding", 39086),
    (17, 61900, "Other telecommunications activities", 37713),
    (18, 45200, "Maintenance and repair of motor vehicles", 35525),
    (19, 56101, "Restaurants without bars", 35017),
    (20, 45403, "Maintenance and repair of motor cycles, mopeds, scooters and three wheelers", 34580),
    (21, 95111, "Repair and maintenance of computer and peripheral equipment", 32994),
    (22, 69201, "Accounting, bookkeeping and auditing activities", 32382),
    (23, 63999, "Other information service activities n.e.c.", 31933),
    (24, 70200, "Management consultancy activities", 31912),
    (25, 81300, "Landscape care and maintenance service activities", 31461),
    (26, 79120, "Tour operator activities", 31433),
    (27, 68100, "Real estate activities with own or leased property", 30338),
    (28, 95210, "Repair of consumer electronics", 29249),
    (29, 49224, "Taxi operation", 28769),
    (30, 56210, "Event catering", 28399),
    (31, 69202, "Tax consultancy", 28078),
    (32, 62020, "Computer consultancy and computer facilities management activities", 27650),
    (33, 52219, "Other land transport services n.e.c", 27537),
    (34, 73100, "Advertising", 27386),
    (35, 79900, "Other reservation service and related activities", 27230),
    (36, 52109, "Storage and warehousing n.e.c.", 27184),
    (37, 78300, "Human resources provision and management of human resources functions", 26629),
    (38, 85500, "Educational support services", 26613),
    (39, 52294, "Weighing of goods", 26571),
    (40, 47711, "Retail sale of readymade garments, hosiery goods, clothing accessories", 26274),
    (41, 86909, "Other human health activities n.e.c.", 26188),
    (42, 78100, "Activities of employment placement agencies", 25202),
    (43, 49232, "Non-motorised road freight transport", 24608),
    (44, 96010, "Washing and (dry-) cleaning of textile and fur products", 24292),
    (45, 86100, "Hospital activities", 24159),
    (46, 56302, "Tea/coffee shops", 23466),
    (47, 81100, "Combined facilities support activities", 22443),
    (48, 74101, "Fashion design", 21966),
    (49, 47190, "Other retail sale in non-specialized stores", 20847),
    (50, 78200, "Temporary employment agency activities", 20342),
]


# Section 15: Top 5 NIC 2-digit divisions split by enterprise size.
# Bar values read from Figure 28. Order in the chart: 10, 49, 56, 96, 32.
TOP_5_DIVISION_BY_SIZE = [
    (10, "Manufacture of food products", 491674, 33467, 5780),
    (49, "Land transport and transport via pipelines", 418228, 17946, 1541),
    (56, "Food and beverage service activities", 410507, 12649, 967),
    (96, "Other personal service activities", 363218, 4437, 228),
    (32, "Other manufacturing", 280821, 26324, 3746),
]


# NIC 2-digit to ISIC Rev 4 section mapping. NIC 2008 follows ISIC Rev 4
# structure so divisions map directly to one-letter sections. Only the
# divisions that appear in the top 50 lists above need names here; the
# rest are filled programmatically as "".
NIC_2DIGIT_NAMES = {
    1: "Crop and animal production, hunting and related service activities",
    8: "Other mining and quarrying",
    10: "Manufacture of food products",
    13: "Manufacture of textiles",
    14: "Manufacture of wearing apparel",
    15: "Manufacture of leather and related products",
    16: "Manufacture of wood and of products of wood and cork",
    22: "Manufacture of rubber and plastic products",
    24: "Manufacture of basic metals",
    25: "Manufacture of fabricated metal products",
    27: "Manufacture of electrical equipment",
    28: "Manufacture of machinery and equipment n.e.c.",
    31: "Manufacture of furniture",
    32: "Other manufacturing",
    33: "Repair and installation of machinery and equipment",
    36: "Water collection, treatment and supply",
    41: "Construction of buildings",
    42: "Civil engineering",
    43: "Specialized construction activities",
    45: "Wholesale and retail trade and repair of motor vehicles and motorcycles",
    47: "Retail trade, except of motor vehicles and motorcycles",
    49: "Land transport and transport via pipelines",
    52: "Warehousing and support activities for transportation",
    56: "Food and beverage service activities",
    61: "Telecommunications",
    62: "Computer programming, consultancy and related activities",
    63: "Information service activities",
    64: "Financial service activities, except insurance and pension funding",
    68: "Real estate activities",
    69: "Legal and accounting activities",
    70: "Activities of head offices; management consultancy activities",
    71: "Architectural and engineering activities; technical testing",
    73: "Advertising and market research",
    74: "Other professional, scientific and technical activities",
    77: "Rental and leasing activities",
    78: "Employment activities",
    79: "Travel agency, tour operator and other reservation service activities",
    81: "Services to buildings and landscape activities",
    82: "Office administrative, office support and other business support activities",
    85: "Education",
    86: "Human health activities",
    95: "Repair of computers and personal and household goods",
    96: "Other personal service activities",
}


# (low, high, section_code, section_name) ranges, half-open via inclusive ends.
ISIC_SECTION_RANGES = [
    (1, 3, "A", "Agriculture, forestry and fishing"),
    (5, 9, "B", "Mining and quarrying"),
    (10, 33, "C", "Manufacturing"),
    (35, 35, "D", "Electricity, gas, steam and air conditioning supply"),
    (36, 39, "E", "Water supply; sewerage, waste management"),
    (41, 43, "F", "Construction"),
    (45, 47, "G", "Wholesale and retail trade; repair of motor vehicles and motorcycles"),
    (49, 53, "H", "Transportation and storage"),
    (55, 56, "I", "Accommodation and food service activities"),
    (58, 63, "J", "Information and communication"),
    (64, 66, "K", "Financial and insurance activities"),
    (68, 68, "L", "Real estate activities"),
    (69, 75, "M", "Professional, scientific and technical activities"),
    (77, 82, "N", "Administrative and support service activities"),
    (84, 84, "O", "Public administration and defence; compulsory social security"),
    (85, 85, "P", "Education"),
    (86, 88, "Q", "Human health and social work activities"),
    (90, 93, "R", "Arts, entertainment and recreation"),
    (94, 96, "S", "Other service activities"),
    (97, 98, "T", "Activities of households as employers"),
    (99, 99, "U", "Activities of extraterritorial organizations and bodies"),
]


def isic_section_for(division: int) -> tuple[str, str]:
    for low, high, code, name in ISIC_SECTION_RANGES:
        if low <= division <= high:
            return code, name
    return "", ""


def build_5digit_table() -> pd.DataFrame:
    rows = []
    for sector_type, series in (("manufacturing", MANUFACTURING_TOP_50), ("services", SERVICES_TOP_50)):
        for rank, code, desc, count in series:
            division = code // 1000
            section_code, section_name = isic_section_for(division)
            rows.append(
                {
                    "sector_type": sector_type,
                    "rank_within_sector": rank,
                    "nic_5digit": code,
                    "description": desc,
                    "msme_count": count,
                    "nic_2digit": division,
                    "nic_2digit_name": NIC_2DIGIT_NAMES.get(division, ""),
                    "isic_section": section_code,
                    "isic_section_name": section_name,
                }
            )
    return pd.DataFrame(rows)


def build_division_table(five_digit: pd.DataFrame) -> pd.DataFrame:
    grouped = (
        five_digit.groupby(
            ["sector_type", "nic_2digit", "nic_2digit_name", "isic_section", "isic_section_name"],
            as_index=False,
        )
        .agg(msme_count=("msme_count", "sum"), num_codes_in_top50=("nic_5digit", "count"))
        .sort_values(["sector_type", "msme_count"], ascending=[True, False])
        .reset_index(drop=True)
    )
    return grouped


def build_top5_msm_table() -> pd.DataFrame:
    rows = []
    for division, name, micro, small, medium in TOP_5_DIVISION_BY_SIZE:
        section_code, section_name = isic_section_for(division)
        rows.append(
            {
                "nic_2digit": division,
                "nic_2digit_name": name,
                "micro": micro,
                "small": small,
                "medium": medium,
                "total": micro + small + medium,
                "isic_section": section_code,
                "isic_section_name": section_name,
            }
        )
    return pd.DataFrame(rows).sort_values("total", ascending=False).reset_index(drop=True)


def main() -> None:
    five = build_5digit_table()
    five.to_csv(OUT / "msme_nic_5digit.csv", index=False)

    division = build_division_table(five)
    division.to_csv(OUT / "msme_nic_division.csv", index=False)

    top5 = build_top5_msm_table()
    top5.to_csv(OUT / "msme_nic_top5_msm.csv", index=False)

    print(f"msme_nic_5digit.csv      {len(five):>4} rows")
    print(f"msme_nic_division.csv    {len(division):>4} rows")
    print(f"msme_nic_top5_msm.csv    {len(top5):>4} rows")


if __name__ == "__main__":
    main()
