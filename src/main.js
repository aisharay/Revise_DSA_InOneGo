const app = document.querySelector("#app");
const appBase = new URL("../", import.meta.url).pathname.replace(/\/$/, "");

const state = {
  data: null,
  categoryId: null,
  query: "",
  searchIndex: [],
  completed: new Set(JSON.parse(localStorage.getItem("dsa-completed") || "[]")),
  starred: new Set(JSON.parse(localStorage.getItem("dsa-starred") || "[]")),
  theme: localStorage.getItem("dsa-theme") || "dark",
  view:
    document.body.dataset.view === "starred" ||
    new URLSearchParams(location.search).has("starred")
      ? "starred"
      : "chapter",
};

const icons = {
  search:
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m21 21-4.35-4.35m2.35-5.65a8 8 0 1 1-16 0 8 8 0 0 1 16 0Z"/></svg>',
  sun: '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M4.93 4.93l1.42 1.42m11.3 11.3 1.42 1.42M2 12h2m16 0h2M4.93 19.07l1.42-1.42m11.3-11.3 1.42-1.42"/></svg>',
  moon: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20.5 14.5A8.5 8.5 0 0 1 9.5 3.5a8.5 8.5 0 1 0 11 11Z"/></svg>',
  menu: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>',
  close: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m6 6 12 12M18 6 6 18"/></svg>',
  copy: '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="8" y="8" width="12" height="12" rx="2"/><path d="M16 8V6a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h2"/></svg>',
  check: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m5 12 4 4L19 6"/></svg>',
  star: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m12 3 2.8 5.7 6.2.9-4.5 4.4 1.1 6.2-5.6-3-5.6 3 1.1-6.2L3 9.6l6.2-.9L12 3Z"/></svg>',
  fullscreen: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 3H3v5m13-5h5v5M8 21H3v-5m18 0v5h-5"/></svg>',
  fullscreenExit: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 8h5V3m13 5h-5V3M3 16h5v5m13-5h-5v5"/></svg>',
  arrow: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m9 18 6-6-6-6"/></svg>',
};

const categoryIcons = [
  "⌕",
  "01",
  "∑",
  "Aa",
  "↗",
  "▤",
  "◆",
  "#",
  "⇆",
  "Σ",
  "↝",
  "♞",
  "♧",
  "⌘",
  "⌗",
  "BIT",
  "∪",
  "◎",
  "ƒ",
  "⌁",
  "G+",
  "S+",
  "ST",
  "⇥",
  "½",
  "…",
];

const chapterGroups = [
  { label: "Foundations", start: 0 },
  { label: "Structures & Patterns", start: 4 },
  { label: "Trees & Range Queries", start: 12 },
  { label: "Graphs & Dynamic Programming", start: 16 },
  { label: "Advanced Topics", start: 19 },
];

function escapeHtml(value = "") {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function inlineFormat(value = "") {
  return escapeHtml(value)
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\b(O\([^)]+\))/g, "<code>$1</code>")
    .replace(/\n/g, "<br>");
}

function cleanTitle(title) {
  return title
    .replace(/^\d+\.\s*/, "")
    .replace(/\s+n\s+/i, " & ")
    .replace(/^tab 26$/i, "Advanced DSA Reference")
    .replace(/\blinkedlist\b/i, "Linked Lists")
    .replace(/\bbit algo\b/i, "Bit Algorithms")
    .replace(/\bstring\b/i, "Strings")
    .replace(/\bgraph\b/i, "Graphs")
    .replace(/\bgreedy\b/i, "Greedy")
    .replace(/\bhashing\b/i, "Hashing")
    .replace(/\bnumber theory\b/i, "Number Theory")
    .replace(/\bbacktracking\b/i, "Backtracking")
    .replace(/\bmeet in the middle\b/i, "Meet in the Middle")
    .replace(/\bsearching and sorting\b/i, "Searching & Sorting")
    .replace(/\bsegment tree\b/i, "Segment Tree")
    .replace(/\bnetwork flow\b/i, "Network Flow")
    .replace(/\btwo pointer\b/i, "Two Pointers")
    .replace(/\bsliding window\b/i, "Sliding Window")
    .replace(/\bprefix sum\b/i, "Prefix Sum")
    .replace(/\bdifference array\b/i, "Difference Array")
    .replace(/\bfenwick tree\b/i, "Fenwick Tree")
    .replace(/\bbinary index tree\b/i, "Binary Indexed Tree")
    .replace(/\bheap\b/i, "Heaps")
    .replace(/\bstack and queue\b/i, "Stacks & Queues")
    .replace(/\btree\b/i, "Trees");
}

function getCategory() {
  return (
    state.data.categories.find((category) => category.id === state.categoryId) ||
    state.data.categories[0]
  );
}

function categoryUrl(categoryId, sectionId = "", starredOnly = false) {
  const query = starredOnly ? "?starred=1" : "";
  const suffix = sectionId ? `#${encodeURIComponent(sectionId)}` : "";
  return `${appBase}/chapters/${categoryId}.html${query}${suffix}`;
}

function allSections(nodes) {
  return nodes.flatMap((node) => [node, ...allSections(node.children)]);
}

function buildSearchIndex() {
  state.searchIndex = state.data.categories.flatMap((category) =>
    allSections(category.sections).map((section) => ({
      categoryId: category.id,
      category: cleanTitle(category.title),
      id: section.id,
      title: section.title,
      text: section.blocks
        .map((block) =>
          block.type === "table"
            ? block.rows.flat().join(" ")
            : block.text,
        )
        .join(" "),
    })),
  );
}

function progressFor(category) {
  const sections = allSections(category.sections).filter(
    (section) => section.level <= 2,
  );
  const done = sections.filter((section) => state.completed.has(section.id)).length;
  return {
    done,
    total: sections.length,
    percent: sections.length ? Math.round((done / sections.length) * 100) : 0,
  };
}

function renderShell() {
  const meta = state.data.meta;
  document.documentElement.dataset.theme = state.theme;
  app.innerHTML = `
    <header class="topbar">
      <button class="icon-button mobile-menu" id="menu-button" aria-label="Open navigation">
        ${icons.menu}
      </button>
      <a class="brand" href="${appBase}/" aria-label="DSA Vault home">
        <span class="brand-mark">&lt;/&gt;</span>
        <span>DSA<span>Vault</span></span>
      </a>
      <button class="search-trigger" id="search-trigger">
        ${icons.search}
        <span>Search concepts, patterns, code…</span>
        <kbd>/</kbd>
      </button>
      <div class="header-meta">
        <span>${meta.sections} topics</span>
        <span class="header-dot"></span>
        <span>${meta.questions} questions</span>
      </div>
      <a class="review-shortcut ${state.view === "starred" ? "active" : ""}" href="${categoryUrl(state.categoryId, "", state.view !== "starred")}">
        ${icons.star}<span>${state.starred.size}</span>
      </a>
      <button class="icon-button" id="fullscreen-toggle" aria-label="Enter fullscreen" title="Enter fullscreen">
        ${icons.fullscreen}
      </button>
      <button class="icon-button" id="theme-toggle" aria-label="Toggle color theme">
        ${state.theme === "dark" ? icons.sun : icons.moon}
      </button>
    </header>
    <div class="layout">
      <aside class="sidebar" id="sidebar">
        <div class="sidebar-head">
          <p>Library</p>
          <button class="icon-button sidebar-close" id="sidebar-close" aria-label="Close navigation">
            ${icons.close}
          </button>
        </div>
        <nav class="category-nav">
          <a class="category-link home-link" href="${appBase}/">
            <span class="category-symbol">⌂</span>
            <span class="category-name">Start here</span>
          </a>
          <a class="category-link starred-link ${state.view === "starred" ? "active" : ""}" href="${categoryUrl(state.categoryId, "", true)}">
            <span class="category-symbol">★</span>
            <span class="category-name">Starred Review</span>
            <span class="starred-count">${state.starred.size}</span>
          </a>
          ${state.data.categories
            .map((category, index) => {
              const progress = progressFor(category);
              const group = chapterGroups.find((item) => item.start === index);
              return `
                ${group ? `<span class="nav-group">${group.label}</span>` : ""}
                <a class="category-link ${category.id === state.categoryId ? "active" : ""}" href="${categoryUrl(category.id, "", state.view === "starred")}">
                  <span class="category-symbol">${categoryIcons[index] || "•"}</span>
                  <span class="chapter-index">${String(index + 1).padStart(2, "0")}</span>
                  <span class="category-name">${escapeHtml(cleanTitle(category.title))}</span>
                  ${progress.done ? `<span class="mini-progress">${progress.percent}%</span>` : ""}
                </a>
              `;
            })
            .join("")}
        </nav>
        <div class="sidebar-card">
          <span class="sidebar-card-icon">⌁</span>
          <strong>Keep building</strong>
          <p>Your completed topics are saved on this device.</p>
          <div class="total-progress">
            <span style="width:${overallProgress()}%"></span>
          </div>
          <small>${overallProgress()}% explored</small>
        </div>
      </aside>
      <main class="main" id="main"></main>
      <aside class="toc" id="toc"></aside>
    </div>
    <div class="search-modal" id="search-modal" aria-hidden="true">
      <div class="search-backdrop" data-close-search></div>
      <section class="search-panel" role="dialog" aria-modal="true" aria-label="Search">
        <div class="search-input-wrap">
          ${icons.search}
          <input id="search-input" type="search" placeholder="Search all ${meta.sections} topics…" autocomplete="off" />
          <button class="esc-button" data-close-search>ESC</button>
        </div>
        <div class="search-results" id="search-results">
          <div class="search-empty">
            <span>⌕</span>
            <p>Search concepts, questions, complexity, or code</p>
          </div>
        </div>
      </section>
    </div>
  `;
  renderCategory();
  bindShellEvents();
}

function overallProgress() {
  const sections = state.data.categories.flatMap((category) =>
    allSections(category.sections).filter((section) => section.level <= 2),
  );
  const done = sections.filter((section) => state.completed.has(section.id)).length;
  return sections.length ? Math.round((done / sections.length) * 100) : 0;
}

function questionStarId(sectionId, blockIndex) {
  return `${sectionId}-question-${blockIndex}`;
}

function sectionHasStars(section) {
  return (
    state.starred.has(section.id) ||
    section.blocks.some(
      (block, index) =>
        block.type === "question" &&
        state.starred.has(questionStarId(section.id, index)),
    ) ||
    section.children.some(sectionHasStars)
  );
}

function renderCategory() {
  const category = getCategory();
  const categoryIndex = state.data.categories.indexOf(category);
  const progress = progressFor(category);
  const primarySections = category.sections.filter((section) => section.level === 1);
  const visibleSections =
    state.view === "starred"
      ? category.sections.filter(sectionHasStars)
      : category.sections;
  const main = document.querySelector("#main");

  main.innerHTML = `
    <section class="category-hero">
      <div class="hero-grid"></div>
      <div class="hero-copy">
        <div class="eyebrow"><span>${categoryIcons[categoryIndex] || "•"}</span> Chapter ${String(categoryIndex + 1).padStart(2, "0")}</div>
        <h1>${escapeHtml(cleanTitle(category.title))}</h1>
        <p>${categoryIntro(cleanTitle(category.title), primarySections.length)}</p>
        <div class="hero-stats">
          <div><strong>${primarySections.length}</strong><span>Core topics</span></div>
          <div><strong>${allSections(category.sections).length}</strong><span>Total sections</span></div>
          <div><strong>${progress.percent}%</strong><span>Progress</span></div>
        </div>
      </div>
      <div class="hero-orbit" aria-hidden="true">
        <span class="orbit orbit-one"></span>
        <span class="orbit orbit-two"></span>
        <strong>${categoryIcons[categoryIndex] || "DSA"}</strong>
      </div>
    </section>
    ${
      state.view !== "starred" && category.blocks.length
        ? `<section class="category-preface">${renderBlocks(category.blocks)}</section>`
        : ""
    }
    <section class="chapter-heading">
      <div>
        <span class="section-kicker">${state.view === "starred" ? "Quick revision mode" : "Chapter contents"}</span>
        <h2>${state.view === "starred" ? "Starred topics & questions." : "Learn, implement, revisit."}</h2>
      </div>
      ${
        state.view === "starred"
          ? `<a class="show-all-link" href="${categoryUrl(category.id)}">Show all concepts</a>`
          : `<div class="chapter-progress">
              <span>${progress.done} of ${progress.total} complete</span>
              <div><i style="width:${progress.percent}%"></i></div>
            </div>`
      }
    </section>
    <div class="topic-list">
      ${
        visibleSections.length
          ? visibleSections
              .map((section, index) => renderSection(section, index))
              .join("")
          : `<section class="empty-review inline">
              <span>${icons.star}</span>
              <h2>No stars in this chapter</h2>
              <p>Choose “Show all concepts”, then star a topic or an individual question to add it to this view.</p>
              <a href="${categoryUrl(category.id)}">Show all concepts ${icons.arrow}</a>
            </section>`
      }
    </div>
    <footer class="content-footer">
      <span>&lt;/&gt;</span>
      <p>Built as a personal reference for consistent practice.</p>
    </footer>
  `;

  renderToc(category, visibleSections);
  bindContentEvents();

  const target = decodeURIComponent(location.hash.slice(1));
  if (target) {
    requestAnimationFrame(() => document.getElementById(target)?.scrollIntoView());
  } else {
    window.scrollTo({ top: 0 });
  }
}

function categoryIntro(title, count) {
  const intros = {
    "Number Theory":
      "Build the mathematical toolkit behind modular arithmetic, primes, combinatorics, and efficient computation.",
    Strings:
      "Master matching, hashing, tries, palindromes, and the patterns behind efficient text processing.",
    "Searching and sorting":
      "Develop reliable search boundaries, ordering techniques, and divide-and-conquer intuition.",
    "Dynamic Programming":
      "Turn overlapping subproblems into precise states, transitions, and optimized solutions.",
    Graphs:
      "Model relationships and navigate traversal, shortest paths, connectivity, and graph structure.",
  };
  return (
    intros[title] ||
    `A focused collection of ${count} core topics with explanations, complexity analysis, and implementation patterns.`
  );
}

function renderSection(section, index, nested = false) {
  const complete = state.completed.has(section.id);
  const starred = state.starred.has(section.id);
  const hasBody = section.blocks.length || section.children.length;
  const starredOnly = state.view === "starred" && !starred;
  const visibleChildren = starredOnly
    ? section.children.filter(sectionHasStars)
    : section.children;
  return `
    <article class="topic-card ${nested ? "nested-topic" : ""}" id="${section.id}">
      <div class="topic-card-head">
        <div class="topic-number">${String(index + 1).padStart(2, "0")}</div>
        <div class="topic-title">
          <span>${section.level === 1 ? "Core concept" : "Pattern & implementation"}</span>
          <h${Math.min(section.level + 1, 4)}>${escapeHtml(section.title)}</h${Math.min(section.level + 1, 4)}>
        </div>
        <button class="star-button ${starred ? "starred" : ""}" data-star="${section.id}" aria-label="${starred ? "Remove star" : "Star for quick review"}">
          ${icons.star}
        </button>
        <button class="complete-button ${complete ? "complete" : ""}" data-complete="${section.id}" aria-label="${complete ? "Mark incomplete" : "Mark complete"}">
          ${complete ? icons.check : ""}
        </button>
        ${
          hasBody
            ? `<button class="expand-button" data-expand aria-label="Collapse topic">${icons.arrow}</button>`
            : ""
        }
      </div>
      <div class="topic-body">
        ${renderBlocks(section.blocks, section.id, starredOnly)}
        ${
          visibleChildren.length
            ? `<div class="subsections">${visibleChildren
                .map((child, childIndex) =>
                  renderSubsection(child, childIndex, starred),
                )
                .join("")}</div>`
            : ""
        }
      </div>
    </article>
  `;
}

function renderSubsection(section, index, parentStarred = false) {
  const complete = state.completed.has(section.id);
  const starred = state.starred.has(section.id);
  const showAll = parentStarred || starred;
  const starredOnly = state.view === "starred" && !showAll;
  const visibleChildren = starredOnly
    ? section.children.filter(sectionHasStars)
    : section.children;
  return `
    <section class="subsection" id="${section.id}">
      <div class="subsection-head">
        <div>
          <span>${String(index + 1).padStart(2, "0")}</span>
          <h${Math.min(section.level + 1, 5)}>${escapeHtml(section.title)}</h${Math.min(section.level + 1, 5)}>
        </div>
        <div class="subsection-actions">
          <button class="star-button small ${starred ? "starred" : ""}" data-star="${section.id}" aria-label="${starred ? "Remove star" : "Star for quick review"}">
            ${icons.star}
          </button>
          <button class="complete-button small ${complete ? "complete" : ""}" data-complete="${section.id}" aria-label="${complete ? "Mark incomplete" : "Mark complete"}">
            ${complete ? icons.check : ""}
          </button>
        </div>
      </div>
      ${renderBlocks(section.blocks, section.id, starredOnly)}
      ${visibleChildren
        .map((child, childIndex) =>
          renderSubsection(child, childIndex, showAll),
        )
        .join("")}
    </section>
  `;
}

function renderBlocks(blocks, sectionId = "", starredOnly = false) {
  return blocks
    .map((block, blockIndex) => {
      const starId =
        block.type === "question" && sectionId
          ? questionStarId(sectionId, blockIndex)
          : "";
      if (starredOnly && (!starId || !state.starred.has(starId))) {
        return "";
      }
      if (block.type === "code") {
        return `
          <div class="code-block">
            <div class="code-topbar">
              <span><i></i><i></i><i></i></span>
              <small>C++</small>
              <button data-copy aria-label="Copy code">${icons.copy}<span>Copy</span></button>
            </div>
            <pre><code>${escapeHtml(block.text)}</code></pre>
          </div>
        `;
      }
      if (block.type === "question") {
        const starred = state.starred.has(starId);
        return `<div class="question-block">
          <span>Q</span>
          <p>${inlineFormat(block.text.replace(/^Question:\s*/i, ""))}</p>
          ${
            starId
              ? `<button class="question-star ${starred ? "starred" : ""}" data-star="${starId}" aria-label="${starred ? "Remove question from starred review" : "Star question for quick review"}">${icons.star}</button>`
              : ""
          }
        </div>`;
      }
      if (block.type === "complexity") {
        return `<div class="complexity-block"><span>⌁ Complexity</span><p>${inlineFormat(block.text)}</p></div>`;
      }
      if (block.type === "callout") {
        return `<div class="callout-block"><span>!</span><p>${inlineFormat(block.text)}</p></div>`;
      }
      if (block.type === "table") {
        if (!block.rows.length) return "";
        const [head, ...rows] = block.rows;
        return `
          <div class="table-wrap">
            <table>
              <thead><tr>${head.map((cell) => `<th>${inlineFormat(cell)}</th>`).join("")}</tr></thead>
              <tbody>${rows
                .map(
                  (row) =>
                    `<tr>${row.map((cell) => `<td>${inlineFormat(cell)}</td>`).join("")}</tr>`,
                )
                .join("")}</tbody>
            </table>
          </div>
        `;
      }
      return `<p class="content-text">${inlineFormat(block.text)}</p>`;
    })
    .join("");
}

function renderToc(category, sections = category.sections) {
  const toc = document.querySelector("#toc");
  toc.innerHTML = `
    <div class="toc-inner">
      <p>On this page</p>
      <nav>
        ${sections
          .map(
            (section) =>
              `<a href="#${section.id}" data-toc="${section.id}">${escapeHtml(section.title)}</a>`,
          )
          .join("")}
      </nav>
      <div class="toc-tip">
        <span>⌘ K</span>
        <p>Use search to jump to any topic across the handbook.</p>
      </div>
    </div>
  `;
}

function bindShellEvents() {
  document.querySelector("#fullscreen-toggle").addEventListener("click", toggleFullscreen);
  document.onfullscreenchange = updateFullscreenButton;

  document.querySelector("#theme-toggle").addEventListener("click", () => {
    state.theme = state.theme === "dark" ? "light" : "dark";
    localStorage.setItem("dsa-theme", state.theme);
    document.documentElement.dataset.theme = state.theme;
    document.querySelector("#theme-toggle").innerHTML =
      state.theme === "dark" ? icons.sun : icons.moon;
  });

  document.querySelector("#menu-button").addEventListener("click", () => {
    document.querySelector("#sidebar").classList.add("open");
  });
  document.querySelector("#sidebar-close").addEventListener("click", () => {
    document.querySelector("#sidebar").classList.remove("open");
  });
  document.querySelector("#search-trigger").addEventListener("click", openSearch);
  document.querySelectorAll("[data-close-search]").forEach((element) => {
    element.addEventListener("click", closeSearch);
  });
  document.querySelector("#search-input").addEventListener("input", (event) => {
    renderSearch(event.target.value);
  });
  document.onkeydown = handleShortcuts;
}

async function toggleFullscreen() {
  try {
    if (document.fullscreenElement) {
      await document.exitFullscreen();
    } else {
      await document.documentElement.requestFullscreen();
    }
  } catch (error) {
    console.error("Fullscreen mode could not be changed:", error);
  }
}

function updateFullscreenButton() {
  const button = document.querySelector("#fullscreen-toggle");
  if (!button) return;
  const active = Boolean(document.fullscreenElement);
  button.innerHTML = active ? icons.fullscreenExit : icons.fullscreen;
  button.setAttribute("aria-label", active ? "Exit fullscreen" : "Enter fullscreen");
  button.title = active ? "Exit fullscreen" : "Enter fullscreen";
}

function bindContentEvents() {
  document.querySelectorAll("[data-copy]").forEach((button) => {
    button.addEventListener("click", async () => {
      const code = button.closest(".code-block").querySelector("code").textContent;
      await navigator.clipboard.writeText(code);
      button.classList.add("copied");
      button.innerHTML = `${icons.check}<span>Copied</span>`;
      setTimeout(() => {
        button.classList.remove("copied");
        button.innerHTML = `${icons.copy}<span>Copy</span>`;
      }, 1400);
    });
  });

  document.querySelectorAll("[data-complete]").forEach((button) => {
    button.addEventListener("click", () => {
      const id = button.dataset.complete;
      if (state.completed.has(id)) {
        state.completed.delete(id);
      } else {
        state.completed.add(id);
      }
      localStorage.setItem("dsa-completed", JSON.stringify([...state.completed]));
      renderShell();
    });
  });

  document.querySelectorAll("[data-star]").forEach((button) => {
    button.addEventListener("click", () => {
      const id = button.dataset.star;
      if (state.starred.has(id)) {
        state.starred.delete(id);
      } else {
        state.starred.add(id);
      }
      localStorage.setItem("dsa-starred", JSON.stringify([...state.starred]));
      renderShell();
    });
  });

  document.querySelectorAll("[data-expand]").forEach((button) => {
    button.addEventListener("click", () => {
      const card = button.closest(".topic-card");
      card.classList.toggle("collapsed");
      button.setAttribute(
        "aria-label",
        card.classList.contains("collapsed") ? "Expand topic" : "Collapse topic",
      );
    });
  });
}

function handleShortcuts(event) {
  const modalOpen = document.querySelector("#search-modal")?.classList.contains("open");
  if (
    (event.key === "/" && !["INPUT", "TEXTAREA"].includes(document.activeElement.tagName)) ||
    ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k")
  ) {
    event.preventDefault();
    openSearch();
  }
  if (event.key === "Escape" && modalOpen) closeSearch();
}

function openSearch() {
  const modal = document.querySelector("#search-modal");
  modal.classList.add("open");
  modal.setAttribute("aria-hidden", "false");
  setTimeout(() => document.querySelector("#search-input").focus(), 50);
}

function closeSearch() {
  const modal = document.querySelector("#search-modal");
  modal.classList.remove("open");
  modal.setAttribute("aria-hidden", "true");
  document.querySelector("#search-input").value = "";
  renderSearch("");
}

function renderSearch(query) {
  const container = document.querySelector("#search-results");
  const normalized = query.trim().toLowerCase();
  if (!normalized) {
    container.innerHTML = `
      <div class="search-empty">
        <span>⌕</span>
        <p>Search concepts, questions, complexity, or code</p>
      </div>
    `;
    return;
  }
  const terms = normalized.split(/\s+/);
  const results = state.searchIndex
    .map((item) => {
      const haystack = `${item.title} ${item.category} ${item.text}`.toLowerCase();
      const score = terms.reduce(
        (total, term) =>
          total +
          (item.title.toLowerCase().includes(term) ? 5 : 0) +
          (item.category.toLowerCase().includes(term) ? 2 : 0) +
          (haystack.includes(term) ? 1 : -20),
        0,
      );
      return { ...item, score };
    })
    .filter((item) => item.score >= 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, 30);

  if (!results.length) {
    container.innerHTML = `
      <div class="search-empty">
        <span>∅</span>
        <p>No topics found for “${escapeHtml(query)}”</p>
      </div>
    `;
    return;
  }

  container.innerHTML = `
    <div class="result-count">${results.length} best matches</div>
    ${results
      .map(
        (result) => `
          <button class="search-result" data-result-category="${result.categoryId}" data-result-id="${result.id}">
            <span class="result-icon">${icons.arrow}</span>
            <span>
              <strong>${escapeHtml(result.title)}</strong>
              <small>${escapeHtml(result.category)}</small>
            </span>
          </button>
        `,
      )
      .join("")}
  `;

  container.querySelectorAll("[data-result-id]").forEach((button) => {
    button.addEventListener("click", () => {
      location.href = categoryUrl(
        button.dataset.resultCategory,
        button.dataset.resultId,
      );
    });
  });
}

async function init() {
  try {
    const response = await fetch(
      new URL("../public/data/dsa-content.json", import.meta.url),
    );
    if (!response.ok) throw new Error(`Content request failed: ${response.status}`);
    state.data = await response.json();
    const requestedCategory = document.body.dataset.category;
    state.categoryId = state.data.categories.some(
      (category) => category.id === requestedCategory,
    )
      ? requestedCategory
      : state.data.categories[0]?.id;
    buildSearchIndex();
    renderShell();
  } catch (error) {
    app.innerHTML = `
      <main class="error-screen">
        <span>!</span>
        <h1>The vault could not be opened.</h1>
        <p>${escapeHtml(error.message)}</p>
        <code>npm run extract && npm run dev</code>
      </main>
    `;
  }
}

init();
