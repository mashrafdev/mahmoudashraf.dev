from django import template
from django.forms.utils import flatatt
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from src.utils.cva import cva

LINK_CVA = cva(
    base=(
        "inline-flex items-center gap-3 group focus-visible:outline-none focus-visible:ring "
        "focus-visible:ring-primary underline-offset-4 hover:underline"
    ),
    variants={
        "variant": {
            "default": "text-primary hover:text-accent",
            "icon": "text-primary hover:text-accent",
            "nav": "text-white hover:text-accent",
            "nav_active": "text-accent",
            "breadcrumb": "h-breadcrumb text-secondary hover:text-accent hover:underline",
            "tag": (
                "p-category inline-block rounded-full border border-primary/30 "
                "bg-primary/5 px-2.5 py-0.5 text-xs font-medium text-primary "
                "transition-colors duration-200 hover:bg-accent hover:text-black"
            ),
            "auth": (
                "inline-flex items-center justify-center gap-2 rounded-full "
                "border border-primary/20 "
                "bg-transparent px-4 py-1.5 text-sm font-medium text-primary "
                "hover:bg-accent hover:text-black transition-colors duration-200 "
                "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent "
                "focus-visible:ring-offset-2 focus-visible:ring-offset-darker"
            ),
        },
        "size": {
            "sm": "text-sm",
            "md": "text-base",
            "lg": "text-lg",
        },
    },
    default_variants={
        "variant": "default",
        "size": "md",
    },
)

LINK_ICON_CVA = cva(
    base="transition-colors",
    variants={
        "variant": {
            "default": "text-primary group-hover:text-accent",
            "icon": "text-primary group-hover:text-accent",
            "nav": "text-white group-hover:text-accent",
            "nav_active": "text-accent",
        },
        "size": {
            "sm": "w-4 ht-4",
            "md": "w-6 ht-6",
            "lg": "w-8 ht-8",
        },
    },
    default_variants={
        "variant": "default",
        "size": "md",
    },
)

register = template.Library()


class LinkNode(template.Node):
    def __init__(self, nodelist, kwargs):
        self.nodelist = nodelist
        self.kwargs = kwargs

    def render(self, context):
        resolved = {key: val.resolve(context) for key, val in self.kwargs.items()}
        content = self.nodelist.render(context).strip() or None

        icon = resolved.get("icon")
        prefix_icon = resolved.get("prefix_icon")
        suffix_icon = resolved.get("suffix_icon")
        href = resolved.get("href", "#")
        variant = resolved.get("variant", "default")
        size = resolved.get("size", "md")
        user_classes = resolved.get("class", "")
        user_icon_class = resolved.pop("icon_class", "")

        is_icon_only = icon and not content and not prefix_icon and not suffix_icon

        if is_icon_only:
            variant = "icon"

        props = {"variant": variant, "size": size}
        cva_class = LINK_CVA(props)
        icon_class = f"{LINK_ICON_CVA(props)} {user_icon_class}".strip()

        attrs = {}

        attrs["class"] = f"{cva_class} {user_classes}".strip()
        attrs["href"] = href

        if variant == "nav_active":
            attrs["aria-current"] = "page"

        if is_icon_only and icon:
            attrs["aria-label"] = icon.replace("-", " ").title()

        # These keys configure the template tag; they are not valid anchor attributes.
        for key, val in resolved.items():
            if key in {"icon", "prefix_icon", "suffix_icon", "variant", "size", "class"}:
                continue

            attrs[key.replace("_", "-")] = val

        return render_to_string(
            "includes/link.html",
            {
                "content": content,
                "icon": icon,
                "prefix_icon": prefix_icon,
                "suffix_icon": suffix_icon,
                "icon_class": icon_class,
                "wrapper_attrs": mark_safe(flatatt(attrs)),
            },
        )


@register.tag
def link(parser, token):
    """
    Usage:
        {% link href="/about" icon="github" class="ml-2" target="_blank" %}
          About Us
        {% endlink %}
    """
    nodelist = parser.parse(("endlink",))
    parser.delete_first_token()

    bits = token.split_contents()[1:]
    kwargs = {}

    for bit in bits:
        if "=" in bit:
            key, value = bit.split("=", 1)
            kwargs[key] = parser.compile_filter(value)

    return LinkNode(nodelist, kwargs)
