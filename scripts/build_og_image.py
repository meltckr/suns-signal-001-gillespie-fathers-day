from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
OUT = ASSETS / "og-collin-gillespie-contract.png"

W, H = 1200, 630


def font(path, size):
    return ImageFont.truetype(str(path), size)


FONT_REG = Path("/System/Library/Fonts/Supplemental/Arial.ttf")
FONT_BOLD = Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf")

regular = font(FONT_REG, 28)
small = font(FONT_REG, 24)
tiny = font(FONT_REG, 18)
bold = font(FONT_BOLD, 30)
display = font(FONT_BOLD, 82)
stat_font = font(FONT_BOLD, 38)


def cover_crop(img, size):
    src_w, src_h = img.size
    dst_w, dst_h = size
    scale = max(dst_w / src_w, dst_h / src_h)
    resized = img.resize((int(src_w * scale), int(src_h * scale)), Image.Resampling.LANCZOS)
    left = (resized.width - dst_w) // 2
    top = (resized.height - dst_h) // 2
    return resized.crop((left, top, left + dst_w, top + dst_h))


def rounded_rect_mask(size, radius):
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, size[0], size[1]), radius=radius, fill=255)
    return mask


def draw_avc_provenance(draw):
    cx, cy = 965, 595
    for radius, width, alpha in [(14, 1, 70), (10, 1, 105), (7, 2, 160)]:
        color = (79, 157, 255, alpha)
        draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), outline=color, width=width)
    draw.line((cx - 6, cy, cx + 7, cy), fill=(95, 177, 255, 190), width=2)
    draw.line((cx + 3, cy - 4, cx + 8, cy, cx + 3, cy + 4), fill=(95, 177, 255, 190), width=2, joint="curve")
    draw.text((986, 585), "Prepared by AVC", font=tiny, fill=(214, 225, 238, 150))


def draw_wrapped(draw, xy, text, font_obj, fill, max_width, line_gap=8):
    x, y = xy
    words = text.split()
    lines = []
    current = ""
    for word in words:
        probe = f"{current} {word}".strip()
        if draw.textbbox((0, 0), probe, font=font_obj)[2] <= max_width:
            current = probe
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    for line in lines:
        draw.text((x, y), line, font=font_obj, fill=fill)
        y += font_obj.size + line_gap
    return y


bg = Image.new("RGB", (W, H), (18, 21, 27))
cover = Image.open(ASSETS / "contract-sentiment-cover.png").convert("RGB")
cover = cover_crop(cover, (W, H)).filter(ImageFilter.GaussianBlur(1.4))
bg = Image.blend(bg, cover, 0.28)

overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
od = ImageDraw.Draw(overlay)
od.rectangle((0, 0, W, H), fill=(12, 15, 20, 142))
od.polygon([(700, 0), (1200, 0), (1200, 630), (830, 630)], fill=(241, 104, 43, 58))
od.line((0, 524, 1200, 470), fill=(241, 152, 67, 120), width=5)
for x in range(780, 1160, 38):
    od.line((x, 515, x, 515 - ((x * 7) % 120)), fill=(39, 200, 194, 95), width=3)
bg = Image.alpha_composite(bg.convert("RGBA"), overlay)
draw = ImageDraw.Draw(bg)

draw.text((70, 54), "SUNS SIGNAL WEEKLY 001", font=bold, fill=(255, 255, 255, 245))
draw.text((72, 90), "FATHER'S DAY EDITION", font=tiny, fill=(214, 225, 238, 210))
draw.text((72, 118), "CURATED FOR MAT ISHBIA", font=tiny, fill=(241, 152, 67, 220))
team_logo = Image.open(ASSETS / "teams" / "suns" / "phoenix-suns-logo.png").convert("RGBA")
team_logo.thumbnail((110, 110), Image.Resampling.LANCZOS)
logo_panel = Image.new("RGBA", (134, 134), (255, 255, 255, 26))
panel_draw = ImageDraw.Draw(logo_panel)
panel_draw.rounded_rectangle((0, 0, 133, 133), radius=10, outline=(255, 255, 255, 58), fill=(255, 255, 255, 22))
logo_panel.alpha_composite(team_logo, ((134 - team_logo.width) // 2, (134 - team_logo.height) // 2))
bg.alpha_composite(logo_panel, (1010, 42))
draw = ImageDraw.Draw(bg)
draw.text((70, 164), "PHOENIX SUNS CONTRACT + SENTIMENT BRIEF", font=tiny, fill=(241, 152, 67, 255))
draw.text((68, 196), "The Earned", font=display, fill=(255, 255, 255, 255))
draw.text((68, 282), "Middle", font=display, fill=(255, 255, 255, 255))
draw_wrapped(
    draw,
    (72, 390),
    "Collin Gillespie's reported four-year, $48M return, decoded through contract context and fan/media reaction.",
    regular,
    (223, 229, 236, 235),
    570,
    6,
)

stats = [("4 yrs", "$48M"), ("AAV", "$12M"), ("Sentiment", "+84")]
x0 = 72
for label, value in stats:
    draw.rounded_rectangle((x0, 522, x0 + 154, 588), radius=8, outline=(255, 255, 255, 55), fill=(255, 255, 255, 20), width=1)
    draw.text((x0 + 14, 530), value, font=stat_font, fill=(18, 21, 27, 255))
    draw.text((x0 + 16, 568), label.upper(), font=tiny, fill=(241, 152, 67, 245))
    x0 += 174

head = Image.open(ASSETS / "collin-gillespie-headshot.png").convert("RGBA")
head.thumbnail((560, 520), Image.Resampling.LANCZOS)
shadow = Image.new("RGBA", head.size, (0, 0, 0, 0))
alpha = head.getchannel("A") if "A" in head.getbands() else Image.new("L", head.size, 255)
shadow.putalpha(alpha.filter(ImageFilter.GaussianBlur(18)))
bg.alpha_composite(shadow, (690, 132))
bg.alpha_composite(head, (642, 100))

draw = ImageDraw.Draw(bg)
draw.rounded_rectangle((748, 454, 1128, 566), radius=8, fill=(247, 243, 236, 232))
draw.text((775, 478), "Collin Gillespie", font=bold, fill=(18, 21, 27, 255))
draw.text((777, 514), "Contract signal + public reaction", font=small, fill=(74, 85, 100, 255))
draw_avc_provenance(draw)

bg.convert("RGB").save(OUT, quality=95)
print(OUT)
