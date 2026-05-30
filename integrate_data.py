#!/usr/bin/env python3
"""Integrate the 78-card RWS tarot JSON data into the index.html"""
import json

# Read the JSON reference data
with open('/root/.openclaw/media/inbound/tarot-images_1---01d2ac05-36fd-444f-b33d-3de767943bec.json') as f:
    ref_data = json.load(f)

# Map card name to data for easy lookup
ref = {}
for c in ref_data['cards']:
    ref[c['name'].lower()] = c

# Build a mapping from our card numbers to the reference data
# Major Arcana: num 0-21
# Minor: num 100-114 (Wands), 200-214 (Cups), 300-314 (Swords), 400-414 (Pentacles)

name_to_num = {
    # Major
    'the fool': 0, 'the magician': 1, 'the high priestess': 2, 'the empress': 3,
    'the emperor': 4, 'the hierophant': 5, 'the lovers': 6, 'the chariot': 7,
    'strength': 8, 'the hermit': 9, 'wheel of fortune': 10, 'justice': 11,
    'the hanged man': 12, 'death': 13, 'temperance': 14, 'the devil': 15,
    'the tower': 16, 'the star': 17, 'the moon': 18, 'the sun': 19,
    'judgement': 20, 'the world': 21,
}

# Minor suits mapping
suit_prefix = {'wands': 100, 'cups': 200, 'swords': 300, 'pentacles': 400}
rank_suffix = {'ace': 0, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6,
               'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
               'page': 11, 'knight': 12, 'queen': 13, 'king': 14}

# Build card num -> ref data mapping
card_ref = {}

# Major Arcana
for c in ref_data['cards']:
    name = c['name'].lower()
    if name in name_to_num:
        card_num = name_to_num[name]
        card_ref[card_num] = c

# Minor Arcana
for c in ref_data['cards']:
    if c['arcana'] == 'Major Arcana':
        continue
    name = c['name'].lower()
    # Parse "X of Y" format
    parts = name.split(' of ')
    if len(parts) == 2:
        rank, suit = parts[0], parts[1]
        if suit in suit_prefix and rank in rank_suffix:
            card_num = suit_prefix[suit] + rank_suffix[rank]
            card_ref[card_num] = c

print(f"Matched {len(card_ref)} cards to reference data")
for num, c in sorted(card_ref.items()):
    print(f"  {num}: {c['name']}")

# Generate JS code for enriched card data
lines = []
lines.append("// ===== 卡牌深度数据（来自 RWS 参考）=====")
lines.append("const CARD_DEEP_DATA = {")

for num in sorted(card_ref.keys()):
    c = card_ref[num]
    name = c['name']
    fortune = json.dumps(c.get('fortune_telling', []), ensure_ascii=False)
    keywords = json.dumps(c.get('keywords', []), ensure_ascii=False)
    light = json.dumps(c.get('meanings', {}).get('light', []), ensure_ascii=False)
    shadow = json.dumps(c.get('meanings', {}).get('shadow', []), ensure_ascii=False)
    archetype = json.dumps(c.get('Archetype', ''), ensure_ascii=False)
    hebrew = json.dumps(c.get('Hebrew Alphabet', ''), ensure_ascii=False)
    numer = json.dumps(c.get('Numerology', ''), ensure_ascii=False)
    elem = json.dumps(c.get('Elemental', ''), ensure_ascii=False)
    mythic = json.dumps(c.get('Mythical/Spiritual', ''), ensure_ascii=False)
    questions = json.dumps(c.get('Questions to Ask', []), ensure_ascii=False)

    lines.append(f"  {num}: {{")
    lines.append(f"    fortune: {fortune},")
    lines.append(f"    keywords: {keywords},")
    lines.append(f"    light: {light},")
    lines.append(f"    shadow: {shadow},")
    lines.append(f"    archetype: {archetype},")
    lines.append(f"    hebrew: {hebrew},")
    lines.append(f"    numerology: {numer},")
    lines.append(f"    element: {elem},")
    lines.append(f"    mythic: {mythic},")
    lines.append(f"    questions: {questions},")
    lines.append(f"  }},")

lines.append("};")
lines.append("")

js_block = '\n'.join(lines)

# Read index.html and inject the data block
with open('/root/.openclaw/workspace/tarot/index.html', 'r') as f:
    html = f.read()

# Inject after the CARD_VISUALS section (before generateCardSVG)
marker = "// ===== 卡牌视觉数据（韦特系意象） ====="
if marker in html:
    # Insert before the marker
    html = html.replace(marker, js_block + "\n\n" + marker)
    print("Injected CARD_DEEP_DATA before CARD_VISUALS")
else:
    print(f"Marker not found, trying alternative...")
    marker2 = "// ===== 罗马数字辅助 ====="
    if marker2 in html:
        html = html.replace(marker2, js_block + "\n\n" + marker2)
        print("Injected CARD_DEEP_DATA before Roman numeral helper")

# Write back
with open('/root/.openclaw/workspace/tarot/index.html', 'w') as f:
    f.write(html)

print("Done! File updated.")
