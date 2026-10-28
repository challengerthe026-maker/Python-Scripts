#!/usr/bin/env python3
"""
Python Static Site Generator for Developer Portfolio
---------------------------------------------------
A zero-dependency, lightweight static site generator written in pure Python 3.
Reads structured content from JSON files and templates, generating a modern,
responsive, static portfolio website in the `dist/` directory.

Usage:
    python3 build.py          # Build the static site into dist/
    python3 build.py --serve  # Build and start a local live preview server
    python3 build.py --watch  # Build, watch for file changes, and serve
    python3 build.py --clean  # Clean the dist/ output directory
"""

import os
import sys
import json
import shutil
import time
import re
import http.server
import socketserver
import threading
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent
CONTENT_DIR = BASE_DIR / "content"
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
DIST_DIR = BASE_DIR / "dist"


class MiniTemplateEngine:
    """
    A robust, token-based template engine implemented using Python's standard library.
    Supports:
      - Variable interpolation: {{ variable }} or {{ nested.key }}
      - Arbitrarily nested loops: {% for item in items %} ... {% endfor %}
      - Arbitrarily nested conditionals: {% if condition %} ... {% else %} ... {% endif %}
      - Partials/Includes: {% include "partial.html" %}
    """

    def __init__(self, templates_dir: Path):
        self.templates_dir = templates_dir

    def resolve(self, expr: str, ctx: dict):
        """Resolves dotted variable paths like 'author.name' or list indexing."""
        expr = expr.strip()
        parts = expr.split(".")
        current = ctx

        for part in parts:
            if isinstance(current, dict):
                current = current.get(part, "")
            elif isinstance(current, (list, tuple)) and part.isdigit():
                idx = int(part)
                current = current[idx] if 0 <= idx < len(current) else ""
            else:
                return ""
            if current is None:
                return ""
        return current

    def eval_condition(self, expr: str, ctx: dict) -> bool:
        """Evaluates boolean conditions, supporting 'not' negation."""
        expr = expr.strip()
        if expr.startswith("not ") or expr.startswith("!"):
            var_name = re.sub(r"^(not\s+|!\s*)", "", expr).strip()
            return not bool(self.resolve(var_name, ctx))
        return bool(self.resolve(expr, ctx))

    def render_includes(self, template_str: str) -> str:
        """Recursively processes {% include "filename" %} directives."""
        include_pattern = re.compile(r'\{%\s*include\s+["\']([^"\']+)["\']\s*%\}')

        def replacer(match):
            filename = match.group(1)
            include_path = self.templates_dir / filename
            if include_path.is_file():
                return self.render_includes(include_path.read_text(encoding="utf-8"))
            return f"<!-- Missing include: {filename} -->"

        # Expand includes iteratively up to depth 10
        prev = ""
        curr = template_str
        depth = 0
        while prev != curr and depth < 10:
            prev = curr
            curr = include_pattern.sub(replacer, curr)
            depth += 1
        return curr

    def tokenize(self, template_str: str):
        tag_pattern = re.compile(r"(\{%.*?%\}|\{\{.*?\}\})", re.DOTALL)
        tokens = tag_pattern.split(template_str)
        return [t for t in tokens if t]

    def render_tokens(self, tokens, pos, ctx):
        output = []
        while pos < len(tokens):
            token = tokens[pos]
            pos += 1

            if token.startswith("{%") and token.endswith("%}"):
                content = token[2:-2].strip()
                words = content.split()
                if not words:
                    continue
                tag_name = words[0]

                if tag_name == "for":
                    # Syntax: {% for item in collection %}
                    if len(words) >= 4 and words[2] == "in":
                        item_var = words[1]
                        coll_expr = words[3]
                    else:
                        continue

                    # Collect tokens until corresponding endfor
                    loop_body_tokens = []
                    nested_count = 1
                    while pos < len(tokens):
                        t = tokens[pos]
                        pos += 1
                        if t.startswith("{%") and t.endswith("%}"):
                            inner_content = t[2:-2].strip()
                            inner_words = inner_content.split()
                            if inner_words and inner_words[0] == "for":
                                nested_count += 1
                            elif inner_words and inner_words[0] == "endfor":
                                nested_count -= 1
                                if nested_count == 0:
                                    break
                        loop_body_tokens.append(t)

                    collection = self.resolve(coll_expr, ctx)
                    if isinstance(collection, (list, tuple)):
                        for i, item in enumerate(collection):
                            sub_ctx = ctx.copy()
                            sub_ctx[item_var] = item
                            sub_ctx[f"{item_var}_index"] = i + 1
                            sub_ctx[f"{item_var}_is_first"] = (i == 0)
                            sub_ctx[f"{item_var}_is_last"] = (i == len(collection) - 1)
                            res, _ = self.render_tokens(loop_body_tokens, 0, sub_ctx)
                            output.append(res)

                elif tag_name == "if":
                    cond_expr = content[len("if"):].strip()
                    true_tokens = []
                    false_tokens = []
                    target = true_tokens
                    nested_count = 1
                    while pos < len(tokens):
                        t = tokens[pos]
                        pos += 1
                        if t.startswith("{%") and t.endswith("%}"):
                            inner_content = t[2:-2].strip()
                            inner_words = inner_content.split()
                            if inner_words and inner_words[0] == "if":
                                nested_count += 1
                            elif inner_words and inner_words[0] == "endif":
                                nested_count -= 1
                                if nested_count == 0:
                                    break
                            elif inner_words and inner_words[0] == "else" and nested_count == 1:
                                target = false_tokens
                                continue
                        target.append(t)

                    cond_met = self.eval_condition(cond_expr, ctx)
                    branch_tokens = true_tokens if cond_met else false_tokens
                    res, _ = self.render_tokens(branch_tokens, 0, ctx)
                    output.append(res)

            elif token.startswith("{{") and token.endswith("}}"):
                expr = token[2:-2].strip()
                val = self.resolve(expr, ctx)
                output.append(str(val) if val is not None else "")
            else:
                output.append(token)

        return "".join(output), pos

    def render(self, template_name: str, context: dict) -> str:
        """Loads and renders a top-level template file."""
        template_file = self.templates_dir / template_name
        if not template_file.is_file():
            raise FileNotFoundError(f"Template not found: {template_file}")

        raw_template = template_file.read_text(encoding="utf-8")
        with_includes = self.render_includes(raw_template)
        tokens = self.tokenize(with_includes)
        rendered, _ = self.render_tokens(tokens, 0, context)
        return rendered


def load_json_file(file_path: Path, default=None):
    """Safely loads a JSON file."""
    if not file_path.is_file():
        return default if default is not None else {}
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ Error loading {file_path.name}: {e}")
        return default if default is not None else {}


def build_portfolio():
    """Generates the static portfolio in DIST_DIR."""
    start_time = time.time()
    print("🚀 Building portfolio website...")

    # Ensure output directory exists
    DIST_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Load Data
    config = load_json_file(BASE_DIR / "config.json", {})
    profile = load_json_file(CONTENT_DIR / "profile.json", {})
    skills = load_json_file(CONTENT_DIR / "skills.json", {"categories": []})
    projects = load_json_file(CONTENT_DIR / "projects.json", {"projects": []})
    experience = load_json_file(CONTENT_DIR / "experience.json", {"work": [], "education": []})
    testimonials = load_json_file(CONTENT_DIR / "testimonials.json", {"testimonials": []})

    # Prepare Context
    context = {
        "site": config,
        "profile": profile,
        "skills": skills,
        "skills_categories": skills.get("categories", []),
        "projects": projects.get("projects", []),
        "project_filters": projects.get("filters", ["All"]),
        "experience": experience.get("work", []),
        "education": experience.get("education", []),
        "testimonials": testimonials.get("testimonials", []),
        "current_year": time.strftime("%Y"),
        "build_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    # 2. Render Template
    engine = MiniTemplateEngine(TEMPLATES_DIR)
    try:
        rendered_html = engine.render("index.html", context)
        output_file = DIST_DIR / "index.html"
        output_file.write_text(rendered_html, encoding="utf-8")
        print(f"  ✓ Rendered HTML -> {output_file.relative_to(BASE_DIR)}")
    except Exception as e:
        print(f"❌ Error rendering template: {e}")
        raise

    # 3. Copy Static Assets
    if STATIC_DIR.is_dir():
        dist_static = DIST_DIR / "static"
        if dist_static.exists():
            shutil.rmtree(dist_static)
        shutil.copytree(STATIC_DIR, dist_static)
        print(f"  ✓ Copied static assets -> {dist_static.relative_to(BASE_DIR)}")

    # 4. Copy 404 or other auxiliary pages if present
    if (TEMPLATES_DIR / "404.html").is_file():
        rendered_404 = engine.render("404.html", context)
        (DIST_DIR / "404.html").write_text(rendered_404, encoding="utf-8")
        print("  ✓ Rendered 404 page -> dist/404.html")

    elapsed = (time.time() - start_time) * 1000
    print(f"✨ Portfolio successfully built in {elapsed:.1f}ms! Ready in {DIST_DIR}/")


def clean_dist():
    """Removes the generated dist/ folder."""
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
        print("🧹 Cleaned dist/ directory.")
    else:
        print("dist/ directory already clean.")


def serve_dist(port: int = 8000):
    """Starts a local HTTP server to preview dist/."""
    build_portfolio()

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(DIST_DIR), **kwargs)

        def log_message(self, format, *args):
            sys.stdout.write(f"[{time.strftime('%H:%M:%S')}] {args[0]} - {args[1]}\n")

    print(f"\n🌐 Live preview server running at: http://localhost:{port}")
    print("Press Ctrl+C to stop the server.\n")

    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", port), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped.")


def watch_and_serve(port: int = 8000):
    """Watches source directories for changes and auto-rebuilds."""
    build_portfolio()

    watched_dirs = [CONTENT_DIR, TEMPLATES_DIR, STATIC_DIR, BASE_DIR / "config.json"]

    def get_mtimes():
        mtimes = {}
        for item in watched_dirs:
            if item.is_file():
                mtimes[item] = item.stat().st_mtime
            elif item.is_dir():
                for p in item.rglob("*"):
                    if p.is_file():
                        mtimes[p] = p.stat().st_mtime
        return mtimes

    def watcher():
        last_mtimes = get_mtimes()
        while True:
            time.sleep(1.0)
            current_mtimes = get_mtimes()
            if current_mtimes != last_mtimes:
                print("\n🔄 Detected file change. Rebuilding portfolio...")
                try:
                    build_portfolio()
                    last_mtimes = current_mtimes
                except Exception as err:
                    print(f"⚠️ Rebuild error: {err}")

    t = threading.Thread(target=watcher, daemon=True)
    t.start()

    serve_dist(port=port)


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--clean" in args:
        clean_dist()
    elif "--serve" in args:
        port = 8000
        for i, arg in enumerate(args):
            if arg == "--port" and i + 1 < len(args):
                port = int(args[i + 1])
        serve_dist(port)
    elif "--watch" in args:
        port = 8000
        for i, arg in enumerate(args):
            if arg == "--port" and i + 1 < len(args):
                port = int(args[i + 1])
        watch_and_serve(port)
    else:
        build_portfolio()
