#!/usr/bin/env python3
"""
TIL Generator - Converts markdown files to HTML
Usage: python3 til/generate_til.py
"""

import os
import re
from datetime import datetime
from pathlib import Path

TIL_DIR = Path("til")
OUTPUT_FILE = Path("til.html")


def parse_frontmatter(content):
    """Parse YAML frontmatter from markdown content."""
    match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
    if match:
        frontmatter = {}
        for line in match.group(1).split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                frontmatter[key.strip()] = value.strip().strip('"\'')
        return frontmatter, match.group(2)
    return {}, content


def parse_markdown(content):
    """Simple markdown to HTML converter."""
    html = content.strip()

    parts = re.split(r'(```[\w]*\n[\s\S]*?```)', html)
    for i in range(1, len(parts), 2):
        code_block = parts[i]
        match = re.match(r'```(\w*)\n([\s\S]*?)```', code_block)
        if match:
            lang = match.group(1)
            code = match.group(2)
            if code and code.strip():
                highlighted = highlight_snippet(code, lang)
                parts[i] = f'<pre class="til-code">{highlighted}</pre>'
            else:
                parts[i] = ''
    
    html = ''.join(parts)
    html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)
    html = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', html)
    html = re.sub(r'^### (.+)$', r'<h4>\1</h4>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank">\1</a>', html)
    html = re.sub(r'^---.*$', '', html, flags=re.MULTILINE)

    lines = html.split('\n')
    result = []
    in_paragraph = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('<h') or stripped.startswith('<pre'):
            if in_paragraph:
                result.append('</p>')
                in_paragraph = False
            result.append(line)
        elif not stripped:
            if in_paragraph:
                result.append('</p>')
                in_paragraph = False
        else:
            if not in_paragraph:
                result.append('<p>')
                in_paragraph = True
            result.append(line + ' ')
    if in_paragraph:
        result.append('</p>')

    return '\n'.join(result)


def highlight_snippet(code, lang=''):
    """Apply syntax highlighting to code snippet."""
    code = code.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    
    patterns = [
        (r'(^#[^\n]*)', r'<span class="comment">\1</span>'),
        (r'(^//[^\n]*)', r'<span class="comment">\1</span>'),
        (r'(^--[^\n]*)', r'<span class="comment">\1</span>'),
        (r'(\s) (#[^\n]*)', r'\1<span class="comment">\2</span>'),
        (r'(\s)(//[^\n]*)', r'\1<span class="comment">\2</span>'),
        (r'(/\*[\s\S]*?\*/)', r'<span class="comment">\1</span>'),
        (r'(<!--[\s\S]*?-->)', r'<span class="comment">\1</span>'),
    ]
    
    for pattern, replacement in patterns:
        code = re.sub(pattern, replacement, code, flags=re.MULTILINE)
    
    return code


def get_entry_class(tags):
    """Get CSS class based on tags."""
    priority_tags = ['linux', 'docker', 'python', 'devops', 'networking', 'security', 'database', 'vim', 'git', 'bash']
    for tag in priority_tags:
        if tag in tags:
            return tag
    return 'default'


def generate_til_entry(title, date, content, tags):
    """Generate HTML for a single TIL entry."""
    entry_class = get_entry_class(tags)
    tags_html = ''.join(f'<span class="til-tag">{tag}</span>' for tag in tags)

    return f'''
<article class="til-entry {entry_class}">
    <div class="til-header">
        <h3 class="til-title">{title}</h3>
        <div class="til-date">{date}</div>
    </div>
    <div class="til-content">
        {parse_markdown(content)}
    </div>
    <div class="til-tags">
        {tags_html}
    </div>
</article>'''


def get_all_tags(entries):
    """Extract all unique tags from entries."""
    tags = set()
    for entry in entries:
        tags.update(entry['tags'])
    return sorted(tags)


def calculate_stats(entries):
    """Calculate TIL statistics."""
    now = datetime.now()
    this_month = sum(1 for e in entries if e['date'].startswith(now.strftime('%Y-%m')))
    all_tags = get_all_tags(entries)
    unique_months = len(set(e['date'][:7] for e in entries))

    return {
        'total': len(entries),
        'this_month': this_month,
        'categories': len(all_tags),
        'weekly_avg': round(len(entries) / max(unique_months * 4, 1), 1) if entries else 0
    }


CSS = """
:root {
    --bg: #0f0f0f;
    --text: #e5e5e5;
    --accent: #00ff9f;
    --muted: #888;
    --border: #333;
    --bg-subtle: #1a1a1a;
    --warning: #ff9500;
    --info: #0099ff;
    --error: #ff4444;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'SF Mono', 'Monaco', 'Cascadia Code', 'Roboto Mono', monospace;
    background: var(--bg);
    color: var(--text);
    line-height: 1.6;
    font-size: 14px;
}

.container {
    max-width: 800px;
    margin: 0 auto;
    padding: 2rem 1rem;
}

.header {
    margin-bottom: 3rem;
}

.prompt {
    color: var(--accent);
    font-weight: 600;
}

.title {
    font-size: 1.5rem;
    font-weight: 700;
    margin: 0.5rem 0 1rem 0;
}

.back-link {
    color: var(--muted);
    text-decoration: none;
    font-size: 0.9rem;
    margin-bottom: 2rem;
    display: inline-block;
}

.back-link:hover {
    color: var(--accent);
}

.search-box {
    width: 100%;
    background: var(--bg-subtle);
    border: 1px solid var(--border);
    color: var(--text);
    padding: 0.75rem 1rem;
    font-family: inherit;
    font-size: 0.9rem;
    margin-bottom: 2rem;
    transition: all 0.2s ease;
}

.search-box:focus {
    outline: none;
    border-color: var(--accent);
    box-shadow: 0 0 15px rgba(0, 255, 159, 0.15);
}

.search-box::placeholder {
    color: var(--muted);
}

.filter-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-bottom: 2rem;
}

.filter-tag {
    background: var(--bg-subtle);
    color: var(--muted);
    padding: 0.5rem 1rem;
    font-size: 0.75rem;
    border: 1px solid var(--border);
    cursor: pointer;
    transition: all 0.2s ease;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.filter-tag:hover,
.filter-tag.active {
    background: var(--accent);
    color: var(--bg);
    border-color: var(--accent);
    box-shadow: 0 0 15px rgba(0, 255, 159, 0.3);
}

.til-entry {
    background: var(--bg-subtle);
    border: 1px solid var(--border);
    border-left: 4px solid var(--accent);
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    transition: all 0.2s ease;
}

.til-entry:hover {
    border-left-color: var(--warning);
    background: rgba(0, 255, 159, 0.02);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.til-entry.linux { border-left-color: var(--info); }
.til-entry.docker { border-left-color: #2496ed; }
.til-entry.python { border-left-color: #3776ab; }
.til-entry.devops { border-left-color: var(--warning); }
.til-entry.networking { border-left-color: #ff6b6b; }
.til-entry.security { border-left-color: var(--error); }
.til-entry.database { border-left-color: #9b59b6; }
.til-entry.vim { border-left-color: var(--accent); }
.til-entry.git { border-left-color: #f05032; }
.til-entry.bash { border-left-color: #4eaa25; }

.til-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 1rem;
}

.til-title {
    font-weight: 600;
    color: var(--text);
    flex: 1;
    margin-right: 1rem;
}

.til-date {
    color: var(--muted);
    font-size: 0.8rem;
    white-space: nowrap;
}

.til-content {
    color: var(--text);
    margin-bottom: 1rem;
    line-height: 1.5;
}

.til-content code {
    background: var(--bg);
    padding: 0.15rem 0.4rem;
    color: var(--accent);
    font-size: 0.9em;
    border: 1px solid var(--border);
}

.til-content strong {
    color: var(--text);
}

.til-content em {
    color: var(--muted);
    font-style: italic;
}

.til-code {
    background: var(--bg);
    border: 1px solid var(--border);
    padding: 1rem;
    font-family: inherit;
    font-size: 0.85rem;
    overflow-x: auto;
    margin: 0.75rem 0;
    color: var(--accent);
    line-height: 1.6;
    white-space: pre;
    tab-size: 2;
}

.til-code .comment,
.til-code .cmt {
    color: #6a737d;
    font-style: italic;
}

.til-code .keyword,
.til-code .kw {
    color: #ff79c6;
}

.til-code .string,
.til-code .str {
    color: #f1fa8c;
}

.til-code .function,
.til-code .fn {
    color: #50fa7b;
}

.til-code .number,
.til-code .num {
    color: #bd93f9;
}

.til-code .operator,
.til-code .op {
    color: #ff79c6;
}

.til-code .punctuation,
.til-code .punct {
    color: #8be9fd;
}

.til-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
}

.til-tag {
    background: var(--bg);
    color: var(--accent);
    padding: 0.25rem 0.5rem;
    font-size: 0.75rem;
    border: 1px solid var(--border);
}

.stats {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin-bottom: 2rem;
    padding: 1rem;
    background: var(--bg-subtle);
    border: 1px solid var(--border);
}

.stat {
    text-align: center;
}

.stat-value {
    font-size: 1.2rem;
    font-weight: 700;
    color: var(--accent);
    display: block;
}

.stat-label {
    font-size: 0.8rem;
    color: var(--muted);
    margin-top: 0.25rem;
}

.footer {
    margin-top: 4rem;
    padding-top: 2rem;
    border-top: 1px solid var(--border);
    text-align: center;
    color: var(--muted);
    font-size: 0.8rem;
}

@media (max-width: 600px) {
    .til-header {
        flex-direction: column;
        gap: 0.5rem;
    }

    .til-title {
        margin-right: 0;
    }
}
"""

JS = """
(function() {
    const searchBox = document.getElementById('searchBox');
    const filterTags = document.querySelectorAll('.filter-tag');
    const entries = document.querySelectorAll('.til-entry');
    const countDisplay = document.getElementById('entryCount');

    let activeTag = 'all';

    filterTags.forEach(tag => {
        tag.addEventListener('click', () => {
            filterTags.forEach(t => t.classList.remove('active'));
            tag.classList.add('active');
            activeTag = tag.dataset.tag;
            filterEntries();
        });
    });

    searchBox.addEventListener('input', filterEntries);

    function filterEntries() {
        const term = searchBox.value.toLowerCase().trim();
        let visibleCount = 0;

        entries.forEach(entry => {
            const title = entry.querySelector('.til-title').textContent.toLowerCase();
            const content = entry.querySelector('.til-content').textContent.toLowerCase();
            const tags = Array.from(entry.querySelectorAll('.til-tag'))
                .map(t => t.textContent.toLowerCase());

            const matchSearch = !term || title.includes(term) || content.includes(term);
            const matchTag = activeTag === 'all' ||
                entry.classList.contains(activeTag) ||
                tags.includes(activeTag);

            entry.style.display = matchSearch && matchTag ? 'block' : 'none';
            if (matchSearch && matchTag) visibleCount++;
        });

        countDisplay.textContent = visibleCount;

        const noResults = document.querySelector('.no-results');
        if (noResults) {
            noResults.style.display = visibleCount === 0 ? 'block' : 'none';
        }
    }
})();
"""


def generate_html(entries, tags):
    """Generate the complete TIL HTML page."""
    stats = calculate_stats(entries)

    entries_html = '\n'.join(
        generate_til_entry(e['title'], e['date'], e['content'], e['tags'])
        for e in entries
    )

    filter_tags_html = '\n'.join(
        f'<span class="filter-tag" data-tag="{tag}">{tag}</span>'
        for tag in ['all'] + tags
    )

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <link rel="icon" type="image/x-icon" href="/static/favicon.ico">
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TIL • sumit.engineer</title>
    <meta name="description" content="Quick insights, discoveries, and learnings from daily development work.">
    <style>
{CSS}
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <a href="/" class="back-link">← sumit.engineer</a>
            <div class="prompt">sumit@engineer:~/til$</div>
            <h1 class="title">Today I Learned</h1>
        </header>

        <input type="text" class="search-box" id="searchBox" placeholder="$ grep -i 'search term' *.til">
        
        <div class="filter-tags">
            {filter_tags_html}
        </div>

        <div class="stats">
            <div class="stat">
                <span class="stat-value">{stats['total']}</span>
                <div class="stat-label">Total TILs</div>
            </div>
            <div class="stat">
                <span class="stat-value">{stats['this_month']}</span>
                <div class="stat-label">This month</div>
            </div>
            <div class="stat">
                <span class="stat-value">{stats['categories']}</span>
                <div class="stat-label">Categories</div>
            </div>
            <div class="stat">
                <span class="stat-value">{stats['weekly_avg']}</span>
                <div class="stat-label">Per week avg</div>
            </div>
        </div>

        <div class="til-entries">
            {entries_html}
            <div class="til-entry no-results" style="display: none;">
                <div class="til-content">No entries match your search criteria</div>
            </div>
        </div>

        <footer class="footer">
            <p>TIL entries are brief discoveries and insights from daily work • Searchable and filterable</p>
        </footer>
    </div>
    <script>
{JS}
    </script>
</body>
</html>'''


def main():
    entries = []

    if not TIL_DIR.exists():
        print(f"[!] TIL directory '{TIL_DIR}' not found")
        TIL_DIR.mkdir()
        print(f"[+] Created {TIL_DIR}/ directory")
        print("[+] Add markdown files with frontmatter:")
        print("""
---
title: Your discovery title
date: 2025-01-29
tags: [linux, bash]
---

Your content here with **markdown** support.
""")
        return

    for md_file in sorted(TIL_DIR.glob('*.md')):
        if md_file.name == 'generate_til.py':
            continue

        try:
            content = md_file.read_text(encoding='utf-8')
            frontmatter, body = parse_frontmatter(content)

            title = frontmatter.get('title', md_file.stem.replace('-', ' ').title())
            date = frontmatter.get('date', datetime.fromtimestamp(md_file.stat().st_mtime).strftime('%Y-%m-%d'))

            tags_str = frontmatter.get('tags', 'general')
            tags = [t.strip().lower() for t in tags_str.strip('[]').split(',')]

            entries.append({
                'title': title,
                'date': date,
                'content': body,
                'tags': tags,
                'filename': md_file.name
            })

            print(f"[+] {md_file.name}: {title}")

        except Exception as e:
            print(f"[!] Error processing {md_file.name}: {e}")

    entries.sort(key=lambda x: x['date'], reverse=True)
    tags = get_all_tags(entries)

    html = generate_html(entries, tags)
    OUTPUT_FILE.write_text(html, encoding='utf-8')

    print(f"\n[+] Generated {OUTPUT_FILE} with {len(entries)} entries")


if __name__ == '__main__':
    main()
