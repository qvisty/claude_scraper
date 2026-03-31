"""HTML cleaner using BeautifulSoup to reduce token usage before sending to Claude."""

from bs4 import BeautifulSoup

# Tags that add no value for data extraction
REMOVE_TAGS = {
    "script",
    "style",
    "noscript",
    "iframe",
    "svg",
    "path",
    "meta",
    "link",
    "head",
    "footer",
    "nav",
    "header",
}

# Attributes to strip (keep only structural/semantic ones)
KEEP_ATTRS = {"href", "src", "alt", "title", "class", "id", "data-price", "data-product"}


def clean_html(
    html: str,
    *,
    remove_tags: set[str] | None = None,
    keep_attrs: set[str] | None = None,
    extract_text_only: bool = False,
) -> str:
    """Clean HTML to reduce size and token cost before sending to Claude.

    Args:
        html: Raw HTML string.
        remove_tags: Tags to remove entirely. Defaults to REMOVE_TAGS.
        keep_attrs: Attributes to keep. Defaults to KEEP_ATTRS.
        extract_text_only: If True, return only visible text (no HTML tags).

    Returns:
        Cleaned HTML string or plain text.
    """
    soup = BeautifulSoup(html, "html.parser")

    tags_to_remove = remove_tags if remove_tags is not None else REMOVE_TAGS
    for tag in soup.find_all(tags_to_remove):
        tag.decompose()

    # Remove comments
    from bs4 import Comment

    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()

    if extract_text_only:
        return soup.get_text(separator="\n", strip=True)

    # Strip unnecessary attributes
    attrs_to_keep = keep_attrs if keep_attrs is not None else KEEP_ATTRS
    for tag in soup.find_all(True):
        attrs = dict(tag.attrs)
        for attr in attrs:
            if attr not in attrs_to_keep:
                del tag[attr]

    # Collapse whitespace
    return str(soup).strip()
