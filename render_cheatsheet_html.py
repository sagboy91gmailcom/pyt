from html import escape
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "simplilearn_ai_ml_cheat_sheet.md"
TARGET = ROOT / "simplilearn_ai_ml_cheat_sheet.html"


def inline_format(text: str) -> str:
    parts = re.split(r"(`[^`]+`)", text)
    out = []
    for part in parts:
        if part.startswith("`") and part.endswith("`") and len(part) >= 2:
            out.append(f"<code>{escape(part[1:-1])}</code>")
        else:
            out.append(escape(part))
    return "".join(out)


def parse_sections(md: str):
    title = "Simplilearn AI and Machine Learning Cheat Sheet"
    sections = []
    current = None

    for raw in md.splitlines():
        line = raw.rstrip()

        h1 = re.match(r"^#\s+(.*)$", line)
        if h1:
            title = h1.group(1).strip()
            continue

        h2 = re.match(r"^##\s+(.*)$", line)
        if h2:
            if current:
                sections.append(current)
            current = {"title": h2.group(1).strip(), "lines": []}
            continue

        if current is not None:
            current["lines"].append(line)

    if current:
        sections.append(current)

    return title, sections


def render_lines(lines):
    html = []
    in_code = False
    code_lines = []
    in_ul = False
    in_ol = False
    paragraph = []

    def flush_paragraph():
        nonlocal paragraph
        if paragraph:
            text = " ".join(x.strip() for x in paragraph).strip()
            if text:
                html.append(f"<p>{inline_format(text)}</p>")
            paragraph = []

    def close_lists():
        nonlocal in_ul, in_ol
        if in_ul:
            html.append("</ul>")
            in_ul = False
        if in_ol:
            html.append("</ol>")
            in_ol = False

    for line in lines:
        stripped = line.rstrip()

        if stripped.startswith("```"):
            flush_paragraph()
            close_lists()
            if in_code:
                code = "\n".join(code_lines)
                html.append(f"<pre><code>{escape(code)}</code></pre>")
                code_lines = []
                in_code = False
            else:
                in_code = True
            continue

        if in_code:
            code_lines.append(line)
            continue

        if not stripped:
            flush_paragraph()
            close_lists()
            continue

        if stripped == "---":
            flush_paragraph()
            close_lists()
            html.append('<hr class="section-rule">')
            continue

        match = re.match(r"^(#{3,6})\s+(.*)$", stripped)
        if match:
            flush_paragraph()
            close_lists()
            level = len(match.group(1))
            text = inline_format(match.group(2).strip())
            html.append(f"<h{level}>{text}</h{level}>")
            continue

        if re.match(r"^- ", stripped):
            flush_paragraph()
            if in_ol:
                html.append("</ol>")
                in_ol = False
            if not in_ul:
                html.append("<ul>")
                in_ul = True
            html.append(f"<li>{inline_format(stripped[2:].strip())}</li>")
            continue

        if re.match(r"^\d+\. ", stripped):
            flush_paragraph()
            if in_ul:
                html.append("</ul>")
                in_ul = False
            if not in_ol:
                html.append("<ol>")
                in_ol = True
            item = re.sub(r"^\d+\. ", "", stripped).strip()
            html.append(f"<li>{inline_format(item)}</li>")
            continue

        paragraph.append(stripped)

    flush_paragraph()
    close_lists()
    return "\n".join(html)


def clean_title(section_title: str) -> str:
    return re.sub(r"^\d+\.\s*", "", section_title).strip()


def build_pages(doc_title: str, sections) -> str:
    pages = []
    for index, section in enumerate(sections, start=1):
        page_title = clean_title(section["title"])
        body = render_lines(section["lines"])
        header_title = "Beginner's AI & ML"
        sub_title = f"Cheat Sheet - {page_title}"

        if index == 1:
            header_title = "Beginner's AI & ML"
            sub_title = "Cheat Sheet"

        pages.append(
            f"""
    <section class="sheet">
      <div class="sheet-header">
        <div class="sheet-brand">{header_title}</div>
        <div class="sheet-title">{sub_title}</div>
      </div>
      <div class="sheet-body">
        <div class="section-intro">
          <h2>{inline_format(page_title)}</h2>
        </div>
        {body}
      </div>
      <div class="sheet-footer">
        <span>{escape(doc_title)}</span>
        <span>{index}</span>
      </div>
    </section>
"""
        )

    return "\n".join(pages)


def build_page(doc_title: str, pages: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{escape(doc_title)}</title>
  <style>
    :root {{
      --paper: #ffffff;
      --ink: #111111;
      --muted: #4d4d4d;
      --accent: #1b7f89;
      --accent-soft: #dff1f4;
      --rule: #d7d7d7;
      --code-bg: #f5f5f5;
      --shadow: rgba(0, 0, 0, 0.08);
    }}

    * {{
      box-sizing: border-box;
    }}

    body {{
      margin: 0;
      font-family: Arial, Helvetica, sans-serif;
      color: var(--ink);
      background: #ececec;
      line-height: 1.28;
      font-size: 12px;
    }}

    .stack {{
      width: max-content;
      margin: 18px auto 28px;
      padding: 6px 0 24px;
    }}

    .sheet {{
      width: 11in;
      min-height: 8.5in;
      margin: 0 auto 20px;
      padding: 0.42in 0.5in 0.34in;
      background: var(--paper);
      box-shadow: 0 10px 28px var(--shadow);
      position: relative;
      page-break-after: always;
    }}

    .sheet-header {{
      margin-bottom: 0.18in;
    }}

    .sheet-brand {{
      font-size: 28px;
      font-weight: 700;
      line-height: 1;
      color: var(--ink);
    }}

    .sheet-title {{
      margin-top: 2px;
      font-size: 28px;
      font-weight: 700;
      line-height: 1;
      color: var(--accent);
    }}

    .sheet-body {{
      column-count: 2;
      column-gap: 0.42in;
      column-fill: auto;
    }}

    .sheet-body > * {{
      break-inside: avoid;
    }}

    .section-intro {{
      margin-bottom: 8px;
    }}

    h2 {{
      margin: 0 0 10px;
      font-size: 17px;
      font-weight: 700;
      color: var(--accent);
      border-bottom: 1px solid var(--rule);
      padding-bottom: 4px;
    }}

    h3 {{
      margin: 8px 0 4px;
      font-size: 13px;
      font-weight: 700;
      color: var(--ink);
    }}

    h4, h5, h6 {{
      margin: 6px 0 3px;
      font-size: 12px;
      font-weight: 700;
      color: var(--ink);
    }}

    p {{
      margin: 0 0 7px;
      orphans: 3;
      widows: 3;
    }}

    ul, ol {{
      margin: 0 0 8px 17px;
      padding: 0;
    }}

    li {{
      margin: 0 0 3px;
    }}

    code {{
      font-family: Consolas, "Courier New", monospace;
      font-size: 11px;
      background: var(--code-bg);
      padding: 1px 4px;
      border-radius: 3px;
    }}

    pre {{
      margin: 0 0 9px;
      padding: 8px 10px;
      background: var(--code-bg);
      border: 1px solid #e2e2e2;
      border-radius: 4px;
      overflow: hidden;
      white-space: pre-wrap;
      word-break: break-word;
    }}

    pre code {{
      padding: 0;
      background: transparent;
      border-radius: 0;
      font-size: 10.5px;
      line-height: 1.25;
    }}

    .section-rule {{
      border: 0;
      border-top: 1px solid var(--rule);
      margin: 9px 0;
    }}

    .sheet-footer {{
      position: absolute;
      left: 0.5in;
      right: 0.5in;
      bottom: 0.16in;
      display: flex;
      justify-content: space-between;
      font-size: 10px;
      color: #666;
    }}

    @media (max-width: 1200px) {{
      .stack {{
        width: auto;
        margin: 8px;
      }}

      .sheet {{
        width: auto;
        min-height: 0;
        padding: 18px 18px 30px;
      }}

      .sheet-body {{
        column-count: 1;
      }}
    }}

    @media print {{
      @page {{
        size: letter landscape;
        margin: 0;
      }}

      body {{
        background: #fff;
      }}

      .stack {{
        margin: 0;
        padding: 0;
      }}

      .sheet {{
        width: 11in;
        min-height: 8.5in;
        margin: 0;
        box-shadow: none;
      }}
    }}
  </style>
</head>
<body>
  <div class="stack">
    {pages}
  </div>
</body>
</html>
"""


def main() -> None:
    markdown = SOURCE.read_text(encoding="utf-8")
    doc_title, sections = parse_sections(markdown)
    pages = build_pages(doc_title, sections)
    html = build_page(doc_title, pages)
    TARGET.write_text(html, encoding="utf-8")
    print(f"Generated {TARGET.name}")


if __name__ == "__main__":
    main()
