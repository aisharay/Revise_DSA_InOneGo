# Interview Vault

A searchable personal interview handbook generated from `1. DSA (2).docx` and
`LLD.docx`. DSA and LLD are separate top-level libraries with their own
chapters, sections, questions, code examples, and progress.

**Live site:** https://aisharay.github.io/Revise_DSA_InOneGo/

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
python -m pip install -r requirements.txt
npm run extract
```

To import documents from other locations:

```powershell
python scripts\extract_docx.py "C:\path\to\dsa.docx" "C:\path\to\lld.docx"
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
