import logging
from io import BytesIO
from urllib.parse import urlparse

import bleach
import markdown
import pymdownx.emoji
import requests
from bs4 import BeautifulSoup, Tag
from PIL import Image

from src.base.blocks.codeblock import highlight_code_with_shiki

logger = logging.getLogger(__name__)


def allow_src(_, name, value):
    if name in ("alt", "height", "width"):
        return True
    if name == "src":
        p = urlparse(value)
        allowed_domains = (".giphy.com", ".tenor.com", ".ibb.co")
        return not p.netloc or any(p.netloc.endswith(domain) for domain in allowed_domains)

    return False


ALLOWED_ATTRS = {"a": ["href"], "img": allow_src, "code": ["class"]}
ALLOWED_TAGS = frozenset(
    {
        "a",
        "del",
        "p",
        "br",
        "strong",
        "em",
        "hr",
        "code",
        "pre",
        "ul",
        "ol",
        "li",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "img",
    }
)


def optimize_img_tag(img: Tag):
    src = img.get("src")
    if not isinstance(src, str):
        return img

    try:
        user_width = int(img.get("width", 0))  # type: ignore
        user_height = int(img.get("height", 0))  # type: ignore

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/115.0.0.0 Safari/537.36 GuestbookBot/1.0"
            ),
            "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "identity",
        }

        response = requests.get(src, headers=headers, timeout=5)
        response.raise_for_status()

        image = Image.open(BytesIO(response.content))
        actual_width, actual_height = image.size
        real_aspect = actual_width / actual_height

        MAX_WIDTH = 600
        MAX_HEIGHT = 600
        MIN_DIM = 16

        if user_width and not user_height:
            width = min(user_width, MAX_WIDTH)
            height = int(width / real_aspect)
        elif user_height and not user_width:
            height = min(user_height, MAX_HEIGHT)
            width = int(height * real_aspect)
        elif user_width and user_height:
            user_aspect = user_width / user_height
            if abs(user_aspect - real_aspect) / real_aspect > 0.2:
                width = min(user_width, MAX_WIDTH)
                height = int(width / real_aspect)
            else:
                width = min(user_width, MAX_WIDTH)
                height = min(user_height, MAX_HEIGHT)
        else:
            width = min(actual_width, MAX_WIDTH)
            height = int(width / real_aspect)

        width = max(width, MIN_DIM)
        height = max(height, MIN_DIM)

        img["width"] = str(width)
        img["height"] = str(height)

        img["style"] = f"aspect-ratio: {actual_width}/{actual_height};"

    except Exception as e:
        logger.exception(f"[IMG ERROR] src={src} — {type(e).__name__}: {e}")

    img["loading"] = "lazy"
    img["decoding"] = "async"
    return img


def highlight_code(pre: Tag):
    code = pre.code
    if not isinstance(code, Tag):
        return

    raw_code = code.get_text()
    lang_class = code.get("class") or []
    language = "plaintext"

    for cls in lang_class:
        if cls.startswith("language-"):
            language = cls.replace("language-", "")
            break

    try:
        highlighted_html = highlight_code_with_shiki(raw_code, language)
        highlighted_fragment = BeautifulSoup(highlighted_html, "html.parser")
        pre.replace_with(highlighted_fragment)
    except Exception as e:
        logger.exception(f"[CODE HIGHLIGHT ERROR] lang={language}: {e}")


def render_guestbook_markdown(value):
    md = markdown.Markdown(
        extensions=[
            "pymdownx.superfences",
            "pymdownx.magiclink",
            "pymdownx.saneheaders",
            "pymdownx.tilde",
            "pymdownx.emoji",
        ],
        extension_configs={"pymdownx.emoji": {"emoji_generator": pymdownx.emoji.to_alt}},
    )
    html_output = md.convert(value)

    sanitized_html = bleach.clean(
        html_output,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRS,
        strip=True,
    )

    soup = BeautifulSoup(sanitized_html, "html.parser")

    return str(soup)
