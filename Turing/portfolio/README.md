# 🐍 Python Developer Portfolio & Static Site Generator

A zero-dependency, ultra-fast static portfolio website generator written entirely in pure **Python 3**.

Builds a modern, fully responsive developer portfolio featuring dark/light mode, dynamic typewriter animations, interactive project filtering, experience timeline, and contact form. Ready to deploy directly to **GitHub Pages**, **Vercel**, **Netlify**, or any static hosting service.

---

## ✨ Features

- **⚡ Zero External Pip Dependencies**: Uses only the Python 3 standard library (`json`, `pathlib`, `re`, `http.server`, etc.). No virtual environments or `pip install` required!
- **🎨 Modern Dark & Light Mode**: Glassmorphic UI with CSS custom properties, smooth transitions, and system preference detection.
- **💻 Interactive Python Showcase**: Embedded mock IDE terminal card, dynamic typewriter effect for roles, and interactive category filters.
- **📁 Data-Driven & Modular**: All personal data, projects, skills, and work history live in cleanly organized JSON files in `content/`.
- **🛠️ Built-in Dev Server & Live Watcher**: Preview your changes in real-time with `python3 build.py --serve` or `python3 build.py --watch`.
- **🚀 One-Click GitHub Pages Deployment**: Includes a pre-configured GitHub Actions workflow (`.github/workflows/deploy.yml`).

---

## 🚀 Quick Start

### 1. Build the Website
Generate the static output into the `dist/` directory:
```bash
python3 build.py
```

### 2. Live Local Preview
Start the local preview server at `http://localhost:8000`:
```bash
python3 build.py --serve
```
*(Or specify a custom port: `python3 build.py --serve --port 3000`)*

### 3. Auto-Rebuild on File Changes
Watch for edits in `content/`, `templates/`, or `static/` and auto-rebuild:
```bash
python3 build.py --watch
```

### 4. Clean Output
Remove the generated `dist/` folder:
```bash
python3 build.py --clean
```

---

## 📂 Project Directory Structure

```text
portfolio/
├── build.py                # Main generator script (template engine, watcher, HTTP server)
├── config.json             # Global site settings (site title, SEO, author, social links)
├── content/                # All your editable portfolio data
│   ├── profile.json        # Bio, headline, stats counter, code snippet
│   ├── skills.json         # Technical competencies grouped by category
│   ├── projects.json       # Featured projects, category filters, tags, GitHub/Demo links
│   ├── experience.json     # Work history and education timeline
│   └── testimonials.json   # Peer recommendations and endorsements
├── templates/              # HTML layout templates
│   ├── index.html          # Main portfolio template
│   └── 404.html            # Branded 404 error page
├── static/                 # Static assets (copied directly to dist/static/)
│   ├── css/
│   │   └── style.css       # Design system, themes (dark/light), layout, responsive styling
│   ├── js/
│   │   └── main.js         # Theme toggle, typewriter animation, project filter, contact form
│   └── images/
│       └── avatar.svg      # Avatar and graphics
├── dist/                   # Generated production site (ready to deploy)
├── .github/workflows/
│   └── deploy.yml          # GitHub Actions workflow for automated GitHub Pages deploys
└── README.md
```

---

## 🛠️ How to Customize Your Portfolio

### 1. Update Personal Info & Socials
Edit `config.json` and `content/profile.json`:
- Change your name, job title, email, and location.
- Add your GitHub, LinkedIn, and Twitter/X URLs.
- Customize the dynamic typing phrases under `"typing_phrases"`.
- Update the statistics numbers (Years Experience, Projects Shipped, etc.).

### 2. Add or Edit Projects
Edit `content/projects.json`. Each project card supports:
```json
{
  "id": "project-slug",
  "title": "Your Project Name",
  "category": "Backend & APIs",
  "featured": true,
  "badge": "Featured",
  "short_description": "One sentence summary...",
  "description": "Detailed description of architecture and impact...",
  "tags": ["Python", "FastAPI", "PostgreSQL"],
  "github": "https://github.com/yourusername/repo",
  "demo": "https://your-demo-url.com",
  "highlights": [
    "Key achievement or benchmark 1",
    "Key achievement or benchmark 2"
  ],
  "icon": "fas fa-server"
}
```

### 3. Update Skills & Tech Stack
Edit `content/skills.json` to modify skill categories, proficiency levels, and descriptions.

### 4. Update Career & Education
Edit `content/experience.json` to reflect your roles, dates, achievements, and universities.

---

## 🌐 Deploying to GitHub Pages

1. Initialize a Git repository (if not already done) and push to GitHub:
   ```bash
   git init
   git add .
   git commit -m "Initial portfolio setup"
   git branch -M main
   git remote add origin https://github.com/<your-username>/<your-repo-name>.git
   git push -u origin main
   ```
2. In your GitHub repository:
   - Navigate to **Settings** → **Pages**.
   - Under **Build and deployment** → **Source**, select **GitHub Actions**.
3. Push changes to `main`: GitHub Actions will automatically run `python3 build.py` and publish your site to `https://<your-username>.github.io/<your-repo-name>/`!

---

## 📄 License
MIT License. Free to use, adapt, and customize for your personal developer brand!

