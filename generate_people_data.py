from __future__ import annotations

import json
import re
from collections import OrderedDict
from datetime import datetime
from pathlib import Path
import xml.etree.ElementTree as ET


SOURCE_ROOT = Path(
    r"D:\2026 연구정보부\2026 AI 디지털 활용 선도학교\인공지능과 함께 하는 역사야 놀자(동아리 활동)\교육부 국사편찬위원회_한국사데이터베이스 정보_친일파관련문헌 원문_20230518"
)
OUTPUT_PATH = Path(__file__).with_name("people_data.js")
FILES = ["pj_001.xml", "pj_002.xml", "pj_003.xml", "pj_004.xml"]
UNIHAN_READINGS = Path(__file__).with_name("Unihan") / "Unihan_Readings.txt"
HANJA_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]+")
COMMON_REPLACEMENTS = [
    ("조선림전보국단", "조선임전보국단"),
    ("국민총력조선련맹", "국민총력조선연맹"),
    ("림전", "임전"),
    ("련맹", "연맹"),
    ("련합", "연합"),
    ("련구", "연구"),
    ("련설", "연설"),
    ("련락", "연락"),
    ("련표", "연표"),
    ("력사", "역사"),
    ("량심", "양심"),
    ("량식", "양식"),
    ("량민", "양민"),
    ("로동", "노동"),
    ("로선", "노선"),
    ("로인", "노인"),
    ("전률할", "전율할"),
]

# 💡 1. 한자 -> 한글 변환 수동 예외 처리 사전 추가
CUSTOM_NAME_DICT = {
    "崔南善": "최남선",
    "李光洙": "이광수",
    "李鍾滎": "이종형",
    "朴興植": "박흥식",
    "金泰錫": "김태석",
    "盧德述": "노덕술",
    # 필요시 이곳에 변환이 안 되는 인물을 계속 추가하세요.
}

MANUAL_OVERRIDES = {
    "朴興植": {
        "summary": "화신백화점과 조선비행기회사 운영을 바탕으로 일본의 전시 동원 체제에 적극 협력한 대표적 친일 실업가로 여러 문헌에서 반복적으로 언급됩니다.",
        "actions": [
            "화신백화점과 화신별관을 기반으로 성장했고, 총독부와 군부의 유력 인물들과 긴밀한 관계를 맺으며 친일 실업계의 핵심 인물로 떠올랐습니다.",
            "임전보국단, 국민총력조선연맹, 대화동맹 등 전시 동원 단체의 간부로 참여해 일본의 전쟁 수행을 위한 동원 체제에 협력한 것으로 정리됩니다.",
            "학병 동원과 전쟁 협력 사업에 필요한 자금과 조직을 지원한 인물로 묘사되며, 조선비행기회사 사장까지 맡아 군수 협력의 상징처럼 다뤄집니다.",
            "1949년 반민특위 수사와 공판 과정에서 대표적인 재계 친일 인물로 체포·조사되었습니다.",
        ],
        "charges": "전시 동원 협력, 학병·징용 선동, 군부 결탁, 친일 경제 활동",
        "category": "경제",
        "role": "경제·실업 인물",
    },
    "金泰錫": {
        "summary": "일제 고등경찰 출신으로 항일 인사 체포와 사상 사건 탄압에 관여한 인물로, 반민특위 공판에서 대표적인 경찰계 피고로 다뤄집니다.",
        "actions": [
            "경찰 통역생으로 시작해 고등경찰 계통에서 활동하며 항일 세력과 사상 사건을 다루었습니다.",
            "강우규 의사 체포와 관련된 인물로 지목되며, 항일 인사 색출과 탄압의 상징처럼 기사에 등장합니다.",
            "반민특위 공판에서는 자신의 행위를 축소하거나 부인하려는 태도가 보이지만, 전체 기록은 그를 식민지 경찰 체제의 핵심 실행자로 봅니다.",
        ],
        "charges": "항일 인사 체포, 고등경찰 활동, 사상 사건 탄압",
        "category": "경찰",
        "role": "경찰·치안 인물",
    },
    "李鍾滎": {
        "summary": "만주와 국내에서 일제 측에 협력하며 혁명투사와 교회를 탄압했고, 해방 후에는 반민법 철폐를 외친 인물로 정리됩니다.",
        "actions": [
            "만주 지역에서 토공군 사령부의 고문·재판관으로 활동하며 혁명투사 체포와 투옥에 깊이 관여한 것으로 기록됩니다.",
            "귀국 후에도 경찰·헌병 계통과 연결되어 국내 항일 세력과 교회를 탄압한 인물로 묘사됩니다.",
            "해방 뒤에는 신문사 사장과 정치 활동을 하며 반민법 철폐와 국회 공격을 선동한 사례로 소개됩니다.",
        ],
        "charges": "혁명투사 체포·투옥, 교회 탄압, 반민법 철폐 선동",
        "category": "정치·치안",
        "role": "정치·치안 인물",
    },
    "崔南善": {
        "summary": "초기에는 민족운동의 상징적 인물이었으나 이후 중추원참의와 조선사편수 관련 활동 등으로 친일 협력에 가담한 사례로 제시됩니다.",
        "actions": [
            "독립선언문 작성과 3·1운동으로 이름을 알렸지만, 이후 친일 체제에 협력하며 큰 비판을 받았습니다.",
            "중추원참의, 조선사편수 관련 직책, 만주 건국대학 교수 등을 맡으며 식민지 지배 논리를 뒷받침한 인물로 정리됩니다.",
            "전쟁 말기에는 이광수와 함께 유학생과 학도에게 학병 참여를 독려한 사례가 핵심 문제로 제시됩니다.",
        ],
        "charges": "중추원참의 활동, 식민사관 협력, 학병 동원 선전",
        "category": "학술",
        "role": "역사·학술 인물",
    },
    "李光洙": {
        "summary": "문학적 명성과 별개로 황도정신과 전쟁 협력을 선전한 대표적 친일 문인으로 여러 자료에서 반복적으로 다뤄집니다.",
        "actions": [
            "일본식 이름을 사용하며 황도정신, 황도문화, 내선일체 같은 논리를 퍼뜨린 대표적 친일 문인으로 기록됩니다.",
            "글과 강연을 통해 일본 제국의 전쟁 수행을 정당화하고 청년·학생 동원을 독려한 인물로 소개됩니다.",
            "반민특위 시기에는 변절의 상징적 사례로 호출되며 문화계 친일의 대표 사례처럼 다뤄집니다.",
        ],
        "charges": "친일 문필 활동, 황도정신 선전, 학병 동원 선동",
        "category": "문학·언론",
        "role": "문학·언론 인물",
    },
    "盧德述": {
        "summary": "일제 경찰로 오래 복무하며 고문과 항일단체 탄압에 관여했고, 해방 후에도 경찰권을 유지하다가 반민특위에 체포된 인물입니다.",
        "actions": [
            "사법주임, 고등계 주임, 보안과장 등 식민지 경찰의 핵심 보안 직위를 거치며 활동했습니다.",
            "혁조회, 신간회 관련 사건, 학생 사건 등에서 고문과 강압 수사를 벌인 인물로 기록됩니다.",
            "해방 후에도 수도청 핵심 경찰로 남아 있었으나 은신 끝에 체포되었고, 반민특위의 현실적 난관을 보여주는 사례로 자주 언급됩니다.",
        ],
        "charges": "고문치사, 항일단체 탄압, 경찰 권력을 이용한 전쟁 협력",
        "category": "경찰",
        "role": "경찰·치안 인물",
    },
}


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def normalize_key(text: str) -> str:
    return re.sub(r"[\s'\"“”‘’·,./()\[\]-]+", "", text or "").strip()


def add_unique(items: list[str], value: str, limit: int) -> None:
    if not value or value in items or len(items) >= limit:
        return
    items.append(value)


def infer_category(context: str) -> str:
    if re.search(r"경찰|경부|경시|헌병|보안과|고등경찰|특고", context):
        return "경찰"
    if re.search(r"총독부|도지사|군수|참의|관료|행정|국장|학무", context):
        return "행정"
    if re.search(r"백화점|회사|사장|실업|경제|상공|재계", context):
        return "경제"
    if re.search(r"문인|문학|시인|역사가|기자|신문|잡지|편집", context):
        return "문학·언론"
    if re.search(r"목사|교회|천도교|종교|불교", context):
        return "종교·사회"
    if re.search(r"학병|학생|교수|학교|학도", context):
        return "교육"
    if re.search(r"왕족|귀족|자작|백작|후작|종친", context):
        return "귀족·정치"
    if re.search(r"암살|공판|특위|사건", context):
        return "사건 관련"
    return "기타"


def infer_role(category: str, context: str) -> str:
    if category == "경찰":
        return "경찰·치안 인물"
    if category == "행정":
        return "행정·관변 인물"
    if category == "경제":
        return "경제·실업 인물"
    if category == "문학·언론":
        return "문학·언론 인물"
    if category == "종교·사회":
        return "종교·사회 인물"
    if category == "교육":
        return "교육 관련 인물"
    if category == "귀족·정치":
        return "귀족·정치 인물"
    if category == "사건 관련":
        return "사건 연루 인물"
    if re.search(r"의사|독립", context):
        return "독립운동 관련 인물"
    return "원문 등장 인물"


def convert_hanja_only(text: str, hangul_map: dict[str, list[str]]) -> str:
    # 💡 2. 본문 변환 시에도 수동 사전에 있는 단어를 우선 변경
    for hanja, hangul in CUSTOM_NAME_DICT.items():
        text = text.replace(hanja, hangul)

    def repl(match: re.Match[str]) -> str:
        return reading_for_hanja(match.group(0), hangul_map)

    return HANJA_RE.sub(repl, text)


def load_hangul_map() -> dict[str, list[str]]:
    readings: dict[str, list[str]] = {}
    if not UNIHAN_READINGS.exists():
        return readings

    for line in UNIHAN_READINGS.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) < 3 or parts[1] != "kHangul":
            continue

        char = chr(int(parts[0][2:], 16))
        values: list[str] = []
        for token in parts[2].split():
            value = re.sub(r":[0-9A-Z]+$", "", token)
            value = normalize_text(value)
            if value and value not in values:
                values.append(value)
        if values:
            readings[char] = values

    return readings


def dueum_transform(syllable: str) -> str:
    dueum_map = {
        "라": "나", "래": "내", "랴": "야", "량": "양", "려": "여",
        "례": "예", "로": "노", "뢰": "뇌", "료": "요", "루": "누",
        "류": "유", "륙": "육", "륜": "윤", "률": "율", "륭": "융",
        "륵": "늑", "름": "늠", "릉": "능", "리": "이", "린": "인",
        "림": "임", "립": "입", "녕": "영", "녀": "여", "뇨": "요",
        "뉴": "유", "니": "이",
    }
    return dueum_map.get(syllable, syllable)


def choose_reading(char: str, position: int, hangul_map: dict[str, list[str]]) -> str:
    options = hangul_map.get(char, [])
    # 💡 3. 사전에 한자 독음이 없을 경우 콘솔에 경고 메시지 출력
    if not options:
        print(f"⚠️ [변환 실패] '{char}' 한자의 독음을 Unihan 사전에서 찾을 수 없습니다.")
        return char
    
    if position == 0:
        transformed = dueum_transform(options[0])
        if transformed in options:
            return transformed
        return transformed
    return options[0]


def reading_for_hanja(text: str, hangul_map: dict[str, list[str]]) -> str:
    result: list[str] = []
    hanja_index = 0
    for ch in text:
        if HANJA_RE.fullmatch(ch):
            result.append(choose_reading(ch, hanja_index, hangul_map))
            hanja_index += 1
        else:
            result.append(ch)
    return "".join(result)


def format_display_name(raw_name: str, hangul_map: dict[str, list[str]]) -> tuple[str, str]:
    name = normalize_text(raw_name)
    if not HANJA_RE.search(name):
        return name, ""

    match = re.fullmatch(r"([가-힣A-Za-z·\s]+)\(([\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]+)\)", name)
    if match:
        hangul_name = normalize_text(match.group(1))
        hanja_name = match.group(2)
        return f"{hanja_name}({hangul_name})", hanja_name

    if re.fullmatch(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]+", name):
        # 💡 4. 이름 변환 시 수동 사전을 최우선으로 확인
        if name in CUSTOM_NAME_DICT:
            return f"{name}({CUSTOM_NAME_DICT[name]})", name
            
        return f"{name}({reading_for_hanja(name, hangul_map)})", name

    return name, ""


def normalize_korean_text(text: str, hangul_map: dict[str, list[str]]) -> str:
    converted = convert_hanja_only(normalize_text(text), hangul_map)
    converted = re.sub(r"\s*/\s*", ", ", converted)
    converted = re.sub(r"[;]+", ".", converted)
    converted = re.sub(r"\s+", " ", converted).strip(" ,")
    for old, new in COMMON_REPLACEMENTS:
        converted = converted.replace(old, new)
    return converted


def make_short_sentence(text: str, limit: int = 180) -> str:
    text = normalize_text(text)
    if len(text) <= limit:
        return text
    cut = text[:limit]
    last_space = cut.rfind(" ")
    if last_space > limit * 0.6:
        cut = cut[:last_space]
    return cut.rstrip(",. ") + "..."


def looks_like_name_list(text: str) -> bool:
    if len(text) < 20:
        return False
    comma_like = text.count(",") + text.count("·") + text.count(" / ") + text.count(" 등")
    return comma_like >= 3 or bool(re.search(r"(명단|목차|대표자|명록|일행들)", text))


def summarize_action(text: str, hangul_map: dict[str, list[str]]) -> str:
    converted = normalize_korean_text(text, hangul_map)
    if not converted:
        return ""

    if looks_like_name_list(converted):
        return "명단·목록 또는 단체 구성 문맥에서 함께 언급됩니다."

    if re.search(r"(체포|구속|공판|심리|재판)", converted):
        return make_short_sentence(converted, 150)

    if re.search(r"(사장|간부|참의|도지사|군수|경찰|총독부)", converted):
        return make_short_sentence(converted, 150)

    return make_short_sentence(converted, 140)


def iter_level2(root: ET.Element):
    for level2 in root.findall(".//level2"):
        title = normalize_text("".join(level2.findtext("./front/biblioData/title/mainTitle", default="")))
        if not title:
            title = "제목 없음"
        yield level2, title


def main() -> None:
    hangul_map = load_hangul_map()
    people: OrderedDict[str, dict] = OrderedDict()
    file_summaries: list[dict] = []

    for file_name in FILES:
        path = SOURCE_ROOT / file_name
        root = ET.parse(path).getroot()
        file_names: set[str] = set()

        for level2, title in iter_level2(root):
            for paragraph in level2.findall(".//paragraph"):
                paragraph_text = normalize_text("".join(paragraph.itertext()))
                if not paragraph_text:
                    continue

                for index in paragraph.findall('.//index[@type="이름"]'):
                    name = normalize_text("".join(index.itertext()))
                    if not name:
                        continue

                    file_names.add(name)

                    if name not in people:
                        people[name] = {
                            "id": "",
                            "name": name,
                            "hanja": "",
                            "alias": "",
                            "category": "",
                            "role": "",
                            "period": "",
                            "summary": "",
                            "actions": [],
                            "charges": "",
                            "sources": [],
                            "files": [],
                            "titles": [],
                            "occurrences": 0,
                            "key": normalize_key(name),
                        }

                    entry = people[name]
                    entry["occurrences"] += 1
                    add_unique(entry["files"], file_name, 8)
                    add_unique(entry["titles"], title, 8)
                    add_unique(entry["actions"], paragraph_text, 4)
                    add_unique(entry["sources"], f"{file_name} - {title}", 10)

        file_summaries.append({"file": file_name, "uniqueNames": len(file_names)})

    sorted_people = sorted(
        people.values(),
        key=lambda item: (-item["occurrences"], item["name"]),
    )

    output_people: list[dict] = []
    for idx, entry in enumerate(sorted_people, start=1):
      context = " ".join(entry["titles"] + entry["actions"])
      converted_context = normalize_korean_text(context, hangul_map)
      category = infer_category(context)
      if category == "기타":
          category = infer_category(converted_context)
      role = infer_role(category, converted_context)
      lead_title = entry["titles"][0] if entry["titles"] else "원문"
      display_name, hanja_name = format_display_name(entry["name"], hangul_map)
      normalized_sources = [
          f"{source.split(' - ')[0]} - {normalize_korean_text(source.split(' - ', 1)[1], hangul_map)}"
          if " - " in source else normalize_korean_text(source, hangul_map)
          for source in entry["sources"]
      ]
      normalized_alias = " / ".join(
          normalize_korean_text(title, hangul_map) for title in entry["titles"][:2]
      ) if entry["titles"] else "원문 등장 인물"
      normalized_actions = []
      for action in entry["actions"]:
          summary_action = summarize_action(action, hangul_map)
          if summary_action and summary_action not in normalized_actions:
              normalized_actions.append(summary_action)
      output_people.append(
          {
              "id": f"person-{idx:04d}",
              "name": display_name,
              "hanja": hanja_name,
              "alias": normalized_alias,
              "category": category,
              "role": role,
              "period": ", ".join(entry["files"]),
              "summary": f'{len(entry["files"])}개 XML에서 {entry["occurrences"]}회 언급되며, 대표적으로 {normalize_korean_text(lead_title, hangul_map)} 항목에서 확인됩니다.',
              "actions": normalized_actions,
              "charges": "원문 문맥상 친일·동원·공판 관련 서술 확인 필요" if entry["actions"] else "원문 추가 확인 필요",
              "sources": normalized_sources,
              "key": entry["key"],
              "occurrences": entry["occurrences"],
          }
      )

    for person in output_people:
        hanja_key = person["hanja"]
        if hanja_key and hanja_key in MANUAL_OVERRIDES:
            override = MANUAL_OVERRIDES[hanja_key]
            for key, value in override.items():
                person[key] = value

    payload = {
        "generatedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "totalPeople": len(output_people),
        "files": file_summaries,
        "people": output_people,
    }

    OUTPUT_PATH.write_text(
        "window.AUTO_PEOPLE_PAYLOAD = " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";",
        encoding="utf-8",
    )

    print(f"Generated {len(output_people)} people -> {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
