from django import template
from django.forms.utils import flatatt
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from src.utils.cva import cva

BUTTON_CVA = cva(
    base=(
        "group relative inline-flex items-center justify-center cursor-pointer shadow-xs "
        "focus-visible:outline-2 focus-visible:outline-accent-bright "
        "focus-visible:outline-offset-2 "
        "transition-all duration-200"
    ),
    variants={
        "variant": {
            "primary": "text-darker font-bold",
            "secondary": "bg-neutral-800 text-primary hover:bg-neutral-700 font-medium",
            "outline": (
                "border-2 border-accent-bright text-primary bg-transparent "
                "transition-colors duration-200 hover:bg-accent-bright hover:text-black"
            ),
            "muted": (
                "text-neutral-300 hover:text-primary hover:bg-neutral-800 "
                "border border-neutral-700 hover:border-neutral-500 font-medium "
                "transition-colors duration-200"
            ),
            "disabled": (
                "bg-neutral-800 text-secondary border border-neutral-700 "
                "opacity-50 cursor-not-allowed pointer-events-none"
            ),
        },
        "size": {
            "sm": "text-sm px-2 py-1 sm:px-3 sm:py-1.5",
            "md": "text-base px-3 py-1.5 sm:px-4 sm:py-2",
            "lg": "text-lg sm:text-2xl px-3 py-2 sm:px-4 sm:py-2.5",
        },
    },
    default_variants={
        "variant": "primary",
        "size": "md",
    },
)

BUTTON_ICON_CVA = cva(
    base="",
    variants={
        "variant": {
            "primary": "text-darker",
            "secondary": "text-primary",
            "outline": "text-primary group-hover:text-black",
            "muted": "text-neutral-300 group-hover:text-primary",
            "disabled": "text-secondary",
        },
        "size": {
            "sm": "w-4 ht-4",
            "md": "w-5 ht-5",
            "lg": "w-6 ht-6",
        },
    },
    default_variants={
        "variant": "primary",
        "size": "md",
    },
)

BUTTON_TEXT_CVA = cva(
    base="",
    variants={
        "variant": {
            "primary": "",
            "secondary": "font-medium",
            "outline": "font-normal sm:font-semibold",
            "muted": "font-medium",
            "disabled": "text-secondary",
        },
        "size": {
            "sm": "text-sm",
            "md": "text-base",
            "lg": "text-lg",
        },
    },
    default_variants={
        "variant": "primary",
        "size": "md",
    },
)

register = template.Library()


class ButtonNode(template.Node):
    def __init__(self, nodelist, kwargs):
        self.nodelist = nodelist
        self.kwargs = kwargs

    def render(self, context):
        resolved = {key: val.resolve(context) for key, val in self.kwargs.items()}
        content = self.nodelist.render(context).strip() or None

        icon = resolved.get("icon")
        prefix_icon = resolved.get("prefix_icon")
        suffix_icon = resolved.get("suffix_icon")
        href = resolved.get("href")
        variant = resolved.get("variant", "primary")
        size = resolved.get("size", "md")
        as_tag = resolved.get("as")

        is_icon_only = icon and not content and not prefix_icon and not suffix_icon

        user_classes = resolved.pop("class", "")
        user_icon_class = resolved.pop("icon_class", "")
        user_text_class = resolved.pop("text_class", "")

        tag = "a" if href and variant != "disabled" else "button"

        props = {"variant": variant, "size": size}
        wrapper_class = f"{BUTTON_CVA(props)} {user_classes}".strip()
        icon_class = f"{BUTTON_ICON_CVA(props)} {user_icon_class}".strip()
        text_class = f"{BUTTON_TEXT_CVA(props)} {user_text_class}".strip()

        attrs = {}
        attrs["class"] = wrapper_class

        if tag == "a":
            attrs["href"] = href
        else:
            attrs["type"] = "button"
            if variant == "disabled":
                attrs["disabled"] = True

        if is_icon_only and icon:
            attrs["aria-label"] = icon.replace("-", " ").title()

        for key, val in resolved.items():
            attrs[key.replace("_", "-")] = val

        # Clean up
        for key in [
            "icon",
            "prefix_icon",
            "suffix_icon",
            "variant",
            "size",
            "as",
            "class",
            "user_class",
            "icon_class",
            "text_class",
        ]:
            attrs.pop(key, None)

        return render_to_string(
            "includes/button.html",
            {
                "variant": variant,
                "content": content or "",
                "icon": icon,
                "prefix_icon": prefix_icon,
                "suffix_icon": suffix_icon,
                "icon_class": icon_class,
                "text_class": text_class,
                "wrapper_tag": tag,
                "wrapper_class": wrapper_class,
                "wrapper_attrs": mark_safe(flatatt(attrs)),
                "is_input": as_tag == "input",
            },
        )


@register.tag
def button(parser, token):
    """
    Usage:
        {% button href="/signup" variant="primary" icon="plus" %}
            Sign Up
        {% endbutton %}
    """
    nodelist = parser.parse(("endbutton",))
    parser.delete_first_token()

    bits = token.split_contents()[1:]
    kwargs = {}

    for bit in bits:
        if "=" in bit:
            key, value = bit.split("=", 1)
            kwargs[key] = parser.compile_filter(value)

    return ButtonNode(nodelist, kwargs)
