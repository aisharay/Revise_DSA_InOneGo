# DSA Vault

A searchable personal DSA handbook generated from `1. DSA (2).docx`. The site
contains all document categories, sections, questions, code examples,
complexity notes, and comparison tables.

## Run locally

```powershell
npm install
npm run dev
```

If Node.js is not installed, the site can also be opened with Python:

```powershell
python -m http.server 4173
```

Then visit `http://localhost:4173`.

## Rebuild the content

The generated website content is stored in
`public\data\dsa-content.json`, so the DOCX is not needed when deploying the
site. The importer also generates one standalone page for every chapter in
`chapters`.

```powershell
npm run extract
```

To import another document:

```powershell
python scripts\extract_docx.py "C:\path\to\document.docx"
```

## Production build

```powershell
npm run build
```

The deployable static site is generated in `dist`.

## Progress and starred review

Completion progress and starred concepts are saved automatically in the
browser. Select the star beside any concept or question, then open **Starred
Review** from the menu. The normal chapter UI remains in place and filters each
chapter down to only its starred material.
