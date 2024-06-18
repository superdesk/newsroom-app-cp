from urllib.parse import quote


def set_photo_coverage_href(coverage, planning_item, deliveries=[]) -> str:
    slugline = coverage.get("slugline")
    if not slugline:
        return ""
    return f"https://www.cpimages.com/CS.aspx?VP3=DirectSearch&FT={quote(slugline)}"


def init_app(app):
    app.set_photo_coverage_href = set_photo_coverage_href
