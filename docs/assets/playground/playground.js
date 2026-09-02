/**
 * Raylings WebAssembly Playground UI Controller & State Engine
 *
 * Full 81-exercise browser learning environment powered by Pyodide WebAssembly.
 * Features client-side localStorage persistence with legacy migration,
 * interactive split-pane syllabus sidebar, real-time search & filters,
 * progressive hints, side-by-side solution diffs, execution timeout/cancellation,
 * Ray cluster diagnostics inspector, and progress backup / restore.
 */

(function () {
  "use strict";

  const STORAGE_KEY = "raylings_learning_state_v1";
  const LEGACY_STORAGE_KEY = "raylings_playground_v1";
  const EXECUTION_TIMEOUT_MS = 10000;

  /**
   * ==========================================================================
   * RaylingsStorage: Client-Side Progress & Working Code Persistence
   * ==========================================================================
   */
  const RaylingsStorage = {
    state: null,
    saveTimeout: null,

    init(bundle) {
      let saved = null;
      try {
        const raw = localStorage.getItem(STORAGE_KEY);
        if (raw) {
          saved = JSON.parse(raw);
        } else {
          // Check and migrate legacy storage if present
          const legacyRaw = localStorage.getItem(LEGACY_STORAGE_KEY);
          if (legacyRaw) {
            const legacy = JSON.parse(legacyRaw);
            if (legacy && legacy.exercises) {
              saved = {
                version: 1,
                lastActiveExerciseId: legacy.lastActiveExerciseId || "basics01",
                exercises: legacy.exercises,
                stats: { completedCount: 0, totalCount: bundle?.total_exercises || 81, completionPercentage: 0 },
              };
            }
          }
        }
      } catch (e) {
        console.warn("Failed to read Raylings state from localStorage:", e);
      }

      const totalExercises = bundle && bundle.exercises ? Object.keys(bundle.exercises).length : 81;

      if (!saved || saved.version !== 1 || !saved.exercises) {
        saved = {
          version: 1,
          lastActiveExerciseId: "basics01",
          exercises: {},
          stats: {
            completedCount: 0,
            totalCount: totalExercises,
            completionPercentage: 0,
          },
        };
      }

      this.state = saved;
      this.recalculateStats(bundle);
      this.persist();
      return this.state;
    },

    recalculateStats(bundle) {
      if (!this.state || !this.state.exercises) return;
      let completed = 0;
      const total = bundle && bundle.exercises ? Object.keys(bundle.exercises).length : 81;

      for (const exState of Object.values(this.state.exercises)) {
        if (exState && exState.status === "completed") {
          completed++;
        }
      }

      this.state.stats = {
        completedCount: completed,
        totalCount: total || 1,
        completionPercentage: total > 0 ? Math.round((completed / total) * 100) : 0,
      };
    },

    persist() {
      if (!this.state) return;
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(this.state));
      } catch (e) {
        console.warn("Failed to write Raylings state to localStorage:", e);
      }
    },

    getExerciseState(exerciseId, defaultStarterCode = "") {
      if (!this.state) return { status: "not_started", userCode: defaultStarterCode, hintsRevealed: 0 };
      if (!this.state.exercises[exerciseId]) {
        return {
          status: "not_started",
          userCode: defaultStarterCode,
          hintsRevealed: 0,
        };
      }
      const existing = this.state.exercises[exerciseId];
      return {
        status: existing.status || "not_started",
        userCode: existing.userCode !== undefined && existing.userCode !== null ? existing.userCode : defaultStarterCode,
        hintsRevealed: existing.hintsRevealed || 0,
      };
    },

    saveExerciseCode(exerciseId, code, starterCode) {
      if (!this.state) return;
      if (!this.state.exercises[exerciseId]) {
        this.state.exercises[exerciseId] = {
          status: "not_started",
          userCode: null,
          hintsRevealed: 0,
        };
      }

      const exState = this.state.exercises[exerciseId];
      exState.userCode = code;

      // Only mark in_progress if the code differs from starter code and isn't completed
      if (exState.status !== "completed") {
        if (code && code !== starterCode) {
          exState.status = "in_progress";
        }
      }
      exState.lastEvaluatedAt = new Date().toISOString();

      clearTimeout(this.saveTimeout);
      this.saveTimeout = setTimeout(() => {
        this.persist();
      }, 300);
    },

    markCompleted(exerciseId, bundle) {
      if (!this.state) return;
      if (!this.state.exercises[exerciseId]) {
        this.state.exercises[exerciseId] = {
          status: "completed",
          userCode: null,
          hintsRevealed: 0,
        };
      }
      const exState = this.state.exercises[exerciseId];
      exState.status = "completed";
      exState.passedAt = new Date().toISOString();
      this.recalculateStats(bundle);
      this.persist();
    },

    setHintsRevealed(exerciseId, count) {
      if (!this.state) return;
      if (!this.state.exercises[exerciseId]) {
        this.state.exercises[exerciseId] = {
          status: "not_started",
          userCode: null,
          hintsRevealed: 0,
        };
      }
      this.state.exercises[exerciseId].hintsRevealed = count;
      this.persist();
    },

    resetExercise(exerciseId) {
      if (!this.state) return;
      delete this.state.exercises[exerciseId];
      this.persist();
    },

    resetAll(bundle) {
      this.state = {
        version: 1,
        lastActiveExerciseId: "basics01",
        exercises: {},
        stats: {
          completedCount: 0,
          totalCount: bundle && bundle.exercises ? Object.keys(bundle.exercises).length : 81,
          completionPercentage: 0,
        },
      };
      this.persist();
    },

    exportBackupJSON() {
      return JSON.stringify(this.state, null, 2);
    },

    importBackupJSON(jsonStr, bundle) {
      try {
        const parsed = JSON.parse(jsonStr);
        if (parsed && typeof parsed === "object") {
          this.state = {
            version: 1,
            lastActiveExerciseId: parsed.lastActiveExerciseId || "basics01",
            exercises: parsed.exercises || {},
            stats: { completedCount: 0, totalCount: bundle?.total_exercises || 81, completionPercentage: 0 },
          };
          this.recalculateStats(bundle);
          this.persist();
          return true;
        }
      } catch (e) {
        console.error("Invalid JSON backup:", e);
      }
      return false;
    },
  };

  /**
   * ==========================================================================
   * Monaco Editor Loader & Controller
   * ==========================================================================
   */
  let monacoEditor = null;
  let monacoDiffEditor = null;
  let diffOriginalModel = null;
  let diffModifiedModel = null;

  function loadMonaco(callback, onError) {
    if (window.monaco) {
      callback();
      return;
    }

    const loaderScript = document.createElement("script");
    loaderScript.src = "https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.45.0/min/vs/loader.min.js";
    loaderScript.crossOrigin = "anonymous";
    loaderScript.onerror = () => {
      if (onError) onError(new Error("Failed to load Monaco Editor loader script from CDN."));
    };
    loaderScript.onload = () => {
      try {
        window.require.config({
          paths: { vs: "https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.45.0/min/vs" },
        });
        window.require(["vs/editor/editor.main"], () => {
          callback();
        });
      } catch (err) {
        if (onError) onError(err);
      }
    };
    document.head.appendChild(loaderScript);
  }

  /**
   * ==========================================================================
   * Main Playground Application Controller
   * ==========================================================================
   */
  class RaylingsPlaygroundApp {
    constructor(rootEl) {
      this.rootEl = rootEl;
      this.bundle = null;
      this.currentExerciseId = "basics01";
      this.currentFilter = "all"; // 'all', 'pending', 'completed'
      this.searchQuery = "";
      this.worker = null;
      this.isDiffOpen = false;
      this.activeTab = "terminal"; // 'terminal' | 'cluster'
      this.lastClusterState = null;
      this.isLoadingExercise = false;
      this.executionTimer = null;
      this.isEvaluating = false;
      this.expandedChapters = new Set([1]); // Default expand chapter 1

      this.init();
    }

    async init() {
      this.renderLoading();
      try {
        const bundleResp = await fetch("../assets/playground/playground-bundle.json");
        if (!bundleResp.ok) throw new Error(`HTTP error ${bundleResp.status}`);
        this.bundle = await bundleResp.json();
      } catch (err) {
        console.warn("Falling back to root assets bundle path:", err);
        try {
          const fallbackResp = await fetch("docs/assets/playground/playground-bundle.json");
          this.bundle = await fallbackResp.json();
        } catch (e2) {
          this.renderError("Failed to load Raylings playground catalog bundle: " + this.escapeHtml(e2.message));
          return;
        }
      }

      RaylingsStorage.init(this.bundle);

      // Deep link routing via URL query parameters (?exercise=<id> or ?chapter=<n>)
      const urlParams = new URLSearchParams(window.location.search);
      const paramExercise = urlParams.get("exercise");
      const paramChapter = urlParams.get("chapter");

      if (paramExercise && this.bundle.exercises && this.bundle.exercises[paramExercise]) {
        this.currentExerciseId = paramExercise;
        const curEx = this.bundle.exercises[this.currentExerciseId];
        if (curEx && curEx.chapter_number) {
          this.expandedChapters.add(curEx.chapter_number);
        }
      } else if (paramChapter) {
        const chapterNum = parseInt(paramChapter, 10);
        if (!isNaN(chapterNum)) {
          this.expandedChapters.add(chapterNum);
          const firstExInChapter = Object.values(this.bundle.exercises || {}).find(
            (ex) => ex.chapter_number === chapterNum
          );
          if (firstExInChapter) {
            this.currentExerciseId = firstExInChapter.id;
          }
        }
      } else if (
        RaylingsStorage.state.lastActiveExerciseId &&
        this.bundle.exercises &&
        this.bundle.exercises[RaylingsStorage.state.lastActiveExerciseId]
      ) {
        this.currentExerciseId = RaylingsStorage.state.lastActiveExerciseId;
        const curEx = this.bundle.exercises[this.currentExerciseId];
        if (curEx && curEx.chapter_number) {
          this.expandedChapters.add(curEx.chapter_number);
        }
      } else {
        this.currentExerciseId = Object.keys(this.bundle.exercises || {})[0] || "basics01";
      }

      this.initWorker();
      this.renderLayout();
      loadMonaco(
        () => {
          this.initMonaco();
          this.loadExercise(this.currentExerciseId);
        },
        (err) => {
          this.renderError("Monaco Editor failed to load: " + this.escapeHtml(err.message));
        }
      );
      this.bindShortcuts();
    }

    initWorker() {
      if (this.worker) {
        try {
          this.worker.terminate();
        } catch (e) {}
      }

      try {
        this.worker = new Worker("../assets/playground/playground-worker.js");
      } catch (e) {
        console.warn("Fallback worker path:", e);
        this.worker = new Worker("docs/assets/playground/playground-worker.js");
      }

      this.worker.onmessage = (e) => {
        const msg = e.data;
        if (!msg) return;

        if (msg.type === "STATUS") {
          this.updateStatusPill(msg.stage, msg.message);
          if (msg.stage === "ready") {
            const runBtn = this.rootEl.querySelector("#btn-run-exercise");
            if (runBtn) runBtn.disabled = false;
          }
        } else if (msg.type === "RUN_RESULT") {
          this.handleRunResult(msg);
        }
      };

      this.worker.postMessage({
        type: "INIT",
        bundle: this.bundle,
      });
    }

    renderLoading() {
      this.rootEl.innerHTML = `
        <div class="playground-loading-screen" style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; min-height: 400px; gap: 16px;">
          <div style="font-size: 28px;">⚡</div>
          <div style="font-size: 15px; font-weight: 600; color: var(--pg-text);">Loading Raylings WebAssembly Engine...</div>
          <div style="font-size: 12px; color: var(--pg-text-muted);">Initializing Python 3.12, Monaco Editor, and Ray Simulation</div>
        </div>
      `;
    }

    renderError(msg) {
      this.rootEl.innerHTML = `
        <div style="padding: 24px; color: var(--pg-error-text); background: var(--pg-error-bg); border: 1px solid var(--pg-error-border); border-radius: 8px; margin: 20px;">
          <h3 style="margin-top: 0;">Playground Error</h3>
          <p>${this.escapeHtml(msg)}</p>
        </div>
      `;
    }

    renderLayout() {
      const totalCount = this.bundle?.total_exercises || 81;
      this.rootEl.innerHTML = `
        <div class="playground-split-layout">
          <!-- Sidebar: Syllabus & Tree -->
          <aside class="playground-sidebar">
            <div class="sidebar-header">
              <div class="sidebar-title-row">
                <span class="sidebar-title">⚡ Curriculum Syllabus</span>
                <div class="sidebar-actions">
                  <button id="btn-export-backup" class="sidebar-icon-btn" title="Export Progress Backup JSON">📥</button>
                  <button id="btn-import-backup" class="sidebar-icon-btn" title="Import Progress Backup JSON">📤</button>
                  <button id="btn-reset-all" class="sidebar-icon-btn sidebar-icon-danger" title="Reset All Exercises">🗑️</button>
                </div>
              </div>
              <div class="sidebar-progress-container">
                <div class="sidebar-progress-labels">
                  <span>Progress</span>
                  <span id="sidebar-progress-text" class="sidebar-progress-pct">0% (0/${totalCount})</span>
                </div>
                <div class="sidebar-progress-track">
                  <div id="sidebar-progress-fill" class="sidebar-progress-fill" style="width: 0%;"></div>
                </div>
              </div>
              <div class="sidebar-search-row">
                <input type="text" id="sidebar-search" class="sidebar-search-input" placeholder="🔍 Search ${totalCount} exercises or chapters..." />
              </div>
              <div class="sidebar-filter-tabs">
                <button class="filter-tab active" data-filter="all">All</button>
                <button class="filter-tab" data-filter="pending">Pending</button>
                <button class="filter-tab" data-filter="completed">Done</button>
              </div>
            </div>
            <div id="sidebar-syllabus-tree" class="sidebar-syllabus-tree"></div>
          </aside>

          <!-- Main Workspace -->
          <main class="playground-main-workspace">
            <div class="workspace-top-bar">
              <div class="workspace-meta-left">
                <span id="meta-chapter-badge" class="chapter-badge">Chapter 01</span>
                <h2 id="meta-exercise-title" class="exercise-title">basics01.py</h2>
              </div>
              <div class="workspace-meta-right">
                <div class="nav-stepper">
                  <button id="btn-prev-ex" class="nav-btn" title="Previous Exercise (Alt+Left)">◀ Prev</button>
                  <button id="btn-next-ex" class="nav-btn" title="Next Exercise (Alt+Right)">Next ▶</button>
                </div>
                <div id="playground-status-pill" class="playground-status-pill status-loading">
                  <span class="status-dot"></span>
                  <span id="status-pill-text">Starting WASM...</span>
                </div>
              </div>
            </div>

            <!-- Action Toolbar -->
            <div class="playground-toolbar">
              <button id="btn-run-exercise" class="playground-btn playground-btn-primary" disabled>
                <span>▶ Run Exercise</span>
                <span class="playground-btn-kbd">Ctrl+↵</span>
              </button>
              <button id="btn-stop-exercise" class="playground-btn" style="display: none; color: var(--pg-error-text);">
                <span>⏹ Stop</span>
              </button>
              <button id="btn-toggle-hint" class="playground-btn">
                <span>💡 Hints</span>
                <span id="hint-count-badge" class="playground-btn-kbd">0/3</span>
              </button>
              <button id="btn-toggle-diff" class="playground-btn">
                <span>👁️ Solution Diff</span>
              </button>
              <button id="btn-reset-code" class="playground-btn">
                <span>🔄 Reset</span>
              </button>
              <button id="btn-fullscreen" class="playground-btn" title="Fullscreen Mode (F11)">
                <span>⛶ Fullscreen</span>
              </button>
            </div>

            <!-- Hint Drawer -->
            <div id="playground-hints-card" class="playground-hints-card"></div>

            <!-- Workspace: Editor + Terminal Split -->
            <div id="playground-workspace-grid" class="playground-workspace">
              <div class="playground-editor-pane">
                <div id="playground-editor"></div>
                <div id="playground-diff-editor"></div>
              </div>
              <div class="playground-output-pane">
                <div class="playground-output-header">
                  <div class="playground-output-tabs">
                    <button id="tab-btn-terminal" class="playground-output-tab active">📟 Terminal</button>
                    <button id="tab-btn-cluster" class="playground-output-tab">🌐 Cluster Inspector</button>
                  </div>
                  <span id="output-runtime-meta" class="playground-output-meta">Pyodide v0.26 / Python 3.12</span>
                </div>
                <pre id="playground-output"></pre>
                <div id="playground-cluster-view"></div>
              </div>
            </div>
          </main>
        </div>
      `;

      this.bindEvents();
      this.updateProgressUI();
      this.renderSidebarTree();
    }

    initMonaco() {
      const isDark = document.documentElement.getAttribute("data-theme") === "dark" ||
        document.body.getAttribute("data-md-color-scheme") === "slate" ||
        window.matchMedia("(prefers-color-scheme: dark)").matches;
      const theme = isDark ? "vs-dark" : "vs";

      const editorContainer = this.rootEl.querySelector("#playground-editor");
      monacoEditor = window.monaco.editor.create(editorContainer, {
        value: "",
        language: "python",
        theme: theme,
        automaticLayout: true,
        minimap: { enabled: false },
        fontSize: 13,
        lineNumbers: "on",
        scrollBeyondLastLine: false,
        wordWrap: "on",
        tabSize: 4,
        insertSpaces: true,
      });

      monacoEditor.onDidChangeModelContent(() => {
        if (this.isLoadingExercise) return;
        const val = monacoEditor.getValue();
        const ex = this.bundle?.exercises[this.currentExerciseId];
        RaylingsStorage.saveExerciseCode(this.currentExerciseId, val, ex?.starter_code || "");
        this.updateSidebarItemStatus(this.currentExerciseId);
      });

      const diffContainer = this.rootEl.querySelector("#playground-diff-editor");
      monacoDiffEditor = window.monaco.editor.createDiffEditor(diffContainer, {
        theme: theme,
        automaticLayout: true,
        readOnly: true,
        minimap: { enabled: false },
        fontSize: 13,
      });
    }

    loadExercise(exerciseId) {
      if (!this.bundle || !this.bundle.exercises[exerciseId]) return;
      this.currentExerciseId = exerciseId;
      RaylingsStorage.state.lastActiveExerciseId = exerciseId;
      RaylingsStorage.persist();

      const ex = this.bundle.exercises[exerciseId];
      const exState = RaylingsStorage.getExerciseState(exerciseId, ex.starter_code);

      // Expand active chapter
      if (ex.chapter_number) {
        this.expandedChapters.add(ex.chapter_number);
      }

      // Update Topbar Meta
      const metaChapter = this.rootEl.querySelector("#meta-chapter-badge");
      const metaTitle = this.rootEl.querySelector("#meta-exercise-title");
      if (metaChapter) metaChapter.textContent = `Ch ${String(ex.chapter_number).padStart(2, "0")}: ${ex.chapter_title}`;
      if (metaTitle) metaTitle.textContent = `${ex.id}.py — ${ex.title}`;

      // Update Editor Code without triggering in_progress dirty state
      if (monacoEditor) {
        this.isLoadingExercise = true;
        monacoEditor.setValue(exState.userCode || ex.starter_code || "");
        this.isLoadingExercise = false;
      }

      // Close Diff if active
      if (this.isDiffOpen) {
        this.toggleDiff(false);
      }

      // Update Hints UI
      this.renderHints(ex, exState.hintsRevealed || 0);

      // Update Active Navigation Item in Sidebar
      this.updateSidebarActiveItem();
      this.updateNavButtons();

      // Clear terminal output or show welcome
      const term = this.rootEl.querySelector("#playground-output");
      if (term) {
        term.innerHTML = `<span class="term-dim">⚡ Loaded exercise ${this.escapeHtml(ex.id)}.py (${this.escapeHtml(ex.title)}). Press Ctrl+Enter or click 'Run Exercise' to evaluate.</span>\n\n<span class="term-info">Docstring Objective:</span>\n${this.escapeHtml(ex.prompt || "Complete the implementation.")}`;
      }
    }

    bindEvents() {
      // Run Button
      this.rootEl.querySelector("#btn-run-exercise").addEventListener("click", () => this.runExercise());

      // Stop Button
      this.rootEl.querySelector("#btn-stop-exercise").addEventListener("click", () => this.stopExercise());

      // Hints Button
      this.rootEl.querySelector("#btn-toggle-hint").addEventListener("click", () => this.revealNextHint());

      // Diff Button
      this.rootEl.querySelector("#btn-toggle-diff").addEventListener("click", () => this.toggleDiff(!this.isDiffOpen));

      // Reset Button
      this.rootEl.querySelector("#btn-reset-code").addEventListener("click", () => this.resetCurrentCode());

      // Fullscreen Button
      this.rootEl.querySelector("#btn-fullscreen").addEventListener("click", () => this.toggleFullscreen());

      // Step Nav
      this.rootEl.querySelector("#btn-prev-ex").addEventListener("click", () => this.navigateExercise(-1));
      this.rootEl.querySelector("#btn-next-ex").addEventListener("click", () => this.navigateExercise(1));

      // Output Tabs
      const tabTerm = this.rootEl.querySelector("#tab-btn-terminal");
      const tabCluster = this.rootEl.querySelector("#tab-btn-cluster");
      const outputTerm = this.rootEl.querySelector("#playground-output");
      const outputCluster = this.rootEl.querySelector("#playground-cluster-view");

      tabTerm.addEventListener("click", () => {
        this.activeTab = "terminal";
        tabTerm.classList.add("active");
        tabCluster.classList.remove("active");
        outputTerm.style.display = "block";
        outputCluster.style.display = "none";
      });

      tabCluster.addEventListener("click", () => {
        this.activeTab = "cluster";
        tabCluster.classList.add("active");
        tabTerm.classList.remove("active");
        outputTerm.style.display = "none";
        outputCluster.style.display = "block";
        this.renderClusterView();
      });

      // Search & Filters
      const searchInput = this.rootEl.querySelector("#sidebar-search");
      searchInput.addEventListener("input", (e) => {
        this.searchQuery = e.target.value.toLowerCase().trim();
        this.renderSidebarTree();
      });

      const filterTabs = this.rootEl.querySelectorAll(".filter-tab");
      filterTabs.forEach((tab) => {
        tab.addEventListener("click", () => {
          filterTabs.forEach((t) => t.classList.remove("active"));
          tab.classList.add("active");
          this.currentFilter = tab.dataset.filter;
          this.renderSidebarTree();
        });
      });

      // Backup & Reset Buttons
      this.rootEl.querySelector("#btn-export-backup").addEventListener("click", () => this.exportBackup());
      this.rootEl.querySelector("#btn-import-backup").addEventListener("click", () => this.importBackup());
      this.rootEl.querySelector("#btn-reset-all").addEventListener("click", () => this.resetAllExercises());
    }

    bindShortcuts() {
      window.addEventListener("keydown", (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
          e.preventDefault();
          this.runExercise();
        } else if (e.altKey && e.key === "ArrowLeft") {
          e.preventDefault();
          this.navigateExercise(-1);
        } else if (e.altKey && e.key === "ArrowRight") {
          e.preventDefault();
          this.navigateExercise(1);
        } else if (e.key === "F11") {
          e.preventDefault();
          this.toggleFullscreen();
        }
      });
    }

    runExercise() {
      if (!this.worker || !monacoEditor || this.isEvaluating) return;
      const code = monacoEditor.getValue();
      const ex = this.bundle.exercises[this.currentExerciseId];

      this.isEvaluating = true;
      this.updateStatusPill("running", "Evaluating in Pyodide...");

      const runBtn = this.rootEl.querySelector("#btn-run-exercise");
      const stopBtn = this.rootEl.querySelector("#btn-stop-exercise");
      if (runBtn) runBtn.style.display = "none";
      if (stopBtn) stopBtn.style.display = "inline-flex";

      const term = this.rootEl.querySelector("#playground-output");
      term.innerHTML = `<span class="term-info">⚡ Running ${this.escapeHtml(ex.id)}.py via Python 3.12 WebAssembly...</span>\n`;

      // Set execution timeout
      clearTimeout(this.executionTimer);
      this.executionTimer = setTimeout(() => {
        this.stopExercise("Execution timed out (exceeded 10-second limit). Possible infinite loop or blocking ray.get.");
      }, EXECUTION_TIMEOUT_MS);

      this.worker.postMessage({
        type: "RUN_EXERCISE",
        exerciseId: this.currentExerciseId,
        code: code,
        filename: `${ex.id}.py`,
      });
    }

    stopExercise(reason = "Execution cancelled by user.") {
      clearTimeout(this.executionTimer);
      this.isEvaluating = false;

      // Terminate and reboot worker
      this.initWorker();

      const runBtn = this.rootEl.querySelector("#btn-run-exercise");
      const stopBtn = this.rootEl.querySelector("#btn-stop-exercise");
      if (runBtn) runBtn.style.display = "inline-flex";
      if (stopBtn) stopBtn.style.display = "none";

      this.handleRunResult({
        passed: false,
        error: reason,
        durationMs: 0,
        output: "",
      });
    }

    handleRunResult(res) {
      clearTimeout(this.executionTimer);
      this.isEvaluating = false;

      const runBtn = this.rootEl.querySelector("#btn-run-exercise");
      const stopBtn = this.rootEl.querySelector("#btn-stop-exercise");
      if (runBtn) runBtn.style.display = "inline-flex";
      if (stopBtn) stopBtn.style.display = "none";

      this.updateStatusPill("ready", "Ready");
      this.lastClusterState = res.clusterState || null;

      const term = this.rootEl.querySelector("#playground-output");
      let html = "";

      if (res.passed) {
        RaylingsStorage.markCompleted(this.currentExerciseId, this.bundle);
        this.updateProgressUI();
        this.updateSidebarItemStatus(this.currentExerciseId);

        html += `<span class="term-banner-pass">✓ PASS: All assertions and Ray simulations succeeded (${res.durationMs}ms)</span>\n`;
        if (res.output) {
          html += `\n<span class="term-dim">Standard Output:</span>\n${this.escapeHtml(res.output)}\n`;
        }
        html += `\n<button id="btn-next-inline" class="term-inline-btn">Next Exercise ▶</button>`;
      } else {
        html += `<span class="term-banner-fail">❌ FAIL: Execution or Assertion Error (${res.durationMs}ms)</span>\n`;
        if (res.error) {
          html += `<span class="term-fail">${this.escapeHtml(res.error)}</span>\n`;
        }
        if (res.traceback) {
          html += `\n<span class="term-dim">${this.escapeHtml(res.traceback)}</span>\n`;
        }
        if (res.output) {
          html += `\n<span class="term-dim">Standard Output:</span>\n${this.escapeHtml(res.output)}\n`;
        }
      }

      term.innerHTML = html;

      const nextInline = term.querySelector("#btn-next-inline");
      if (nextInline) {
        nextInline.addEventListener("click", () => this.navigateExercise(1));
      }

      if (this.activeTab === "cluster") {
        this.renderClusterView();
      }
    }

    renderClusterView() {
      const view = this.rootEl.querySelector("#playground-cluster-view");
      if (!view) return;

      if (!this.lastClusterState) {
        view.innerHTML = `
          <div style="padding: 20px; color: var(--pg-term-dim); text-align: center;">
            <div style="font-size: 24px; margin-bottom: 8px;">🌐</div>
            <div style="font-weight: 600; color: var(--pg-text); margin-bottom: 4px;">No Cluster Telemetry Recorded Yet</div>
            <div style="font-size: 11px;">Run an exercise to measure active nodes, CPU tasks, Plasma memory, and actor pool statistics.</div>
          </div>
        `;
        return;
      }

      const stats = this.lastClusterState;

      view.innerHTML = `
        <div style="padding: 10px 0;">
          <h4 style="margin: 0 0 12px 0; color: var(--pg-text);">🌐 Simulated Ray Cluster Metrics</h4>
          <div class="cluster-stat-grid">
            <div class="cluster-stat-card">
              <span class="cluster-stat-val">${stats.nodes}</span>
              <span class="cluster-stat-lbl">Active Nodes</span>
            </div>
            <div class="cluster-stat-card">
              <span class="cluster-stat-val">${stats.cpus}</span>
              <span class="cluster-stat-lbl">Worker CPUs</span>
            </div>
            <div class="cluster-stat-card">
              <span class="cluster-stat-val">${stats.objects_count}</span>
              <span class="cluster-stat-lbl">Plasma Objects</span>
            </div>
            <div class="cluster-stat-card">
              <span class="cluster-stat-val">${((stats.objects_bytes || 0) / 1024).toFixed(1)} KB</span>
              <span class="cluster-stat-lbl">Memory Used</span>
            </div>
            <div class="cluster-stat-card">
              <span class="cluster-stat-val">${stats.actors_count || 0}</span>
              <span class="cluster-stat-lbl">Active Actors</span>
            </div>
            <div class="cluster-stat-card">
              <span class="cluster-stat-val">${stats.tasks_count || 0}</span>
              <span class="cluster-stat-lbl">Tasks Dispatched</span>
            </div>
          </div>
          <div style="font-size: 11px; color: var(--pg-term-dim); line-height: 1.4;">
            Simulated in-memory Ray Core runtime running directly in WebAssembly. Actors, tasks, and Plasma ObjectStore execute in the browser without server latency.
          </div>
        </div>
      `;
    }

    revealNextHint() {
      const ex = this.bundle.exercises[this.currentExerciseId];
      if (!ex || !ex.hints || ex.hints.length === 0) return;

      const exState = RaylingsStorage.getExerciseState(this.currentExerciseId);
      const currentRevealed = exState.hintsRevealed || 0;
      const nextRevealed = Math.min(currentRevealed + 1, ex.hints.length);

      RaylingsStorage.setHintsRevealed(this.currentExerciseId, nextRevealed);
      this.renderHints(ex, nextRevealed);
    }

    renderHints(ex, revealedCount) {
      const card = this.rootEl.querySelector("#playground-hints-card");
      const badge = this.rootEl.querySelector("#hint-count-badge");
      const totalHints = ex.hints ? ex.hints.length : 0;

      if (badge) badge.textContent = `${revealedCount}/${totalHints}`;

      if (revealedCount === 0 || totalHints === 0) {
        card.classList.remove("hints-visible");
        card.innerHTML = "";
        return;
      }

      card.classList.add("hints-visible");
      let html = "";
      for (let i = 0; i < revealedCount; i++) {
        html += `
          <div class="playground-hint-item">
            <span class="playground-hint-badge">Hint ${i + 1}</span>
            <span class="playground-hint-text">${this.escapeHtml(ex.hints[i])}</span>
          </div>
        `;
      }
      card.innerHTML = html;
    }

    toggleDiff(open) {
      this.isDiffOpen = open;
      const grid = this.rootEl.querySelector("#playground-workspace-grid");
      const btn = this.rootEl.querySelector("#btn-toggle-diff");
      const ex = this.bundle.exercises[this.currentExerciseId];

      if (open) {
        grid.classList.add("diff-active");
        btn.classList.add("btn-active");

        if (monacoDiffEditor) {
          if (diffOriginalModel) diffOriginalModel.dispose();
          if (diffModifiedModel) diffModifiedModel.dispose();

          diffOriginalModel = window.monaco.editor.createModel(ex.solution_code || "", "python");
          diffModifiedModel = window.monaco.editor.createModel(monacoEditor ? monacoEditor.getValue() : "", "python");
          monacoDiffEditor.setModel({
            original: diffOriginalModel,
            modified: diffModifiedModel,
          });
        }
      } else {
        grid.classList.remove("diff-active");
        btn.classList.remove("btn-active");
      }
    }

    resetCurrentCode() {
      const ex = this.bundle.exercises[this.currentExerciseId];
      if (!ex) return;
      if (confirm(`Reset ${ex.id}.py back to the starter code template?`)) {
        RaylingsStorage.resetExercise(this.currentExerciseId);
        if (monacoEditor) {
          this.isLoadingExercise = true;
          monacoEditor.setValue(ex.starter_code || "");
          this.isLoadingExercise = false;
        }
        this.renderHints(ex, 0);
        this.updateSidebarItemStatus(this.currentExerciseId);
      }
    }

    toggleFullscreen() {
      if (!document.fullscreenElement) {
        this.rootEl.requestFullscreen().catch(() => {
          this.rootEl.classList.toggle("is-fullscreen");
        });
      } else {
        document.exitFullscreen();
      }
    }

    navigateExercise(direction) {
      const ids = Object.keys(this.bundle.exercises);
      const curIdx = ids.indexOf(this.currentExerciseId);
      if (curIdx === -1) return;

      const nextIdx = curIdx + direction;
      if (nextIdx >= 0 && nextIdx < ids.length) {
        this.loadExercise(ids[nextIdx]);
      }
    }

    updateNavButtons() {
      const ids = Object.keys(this.bundle.exercises);
      const curIdx = ids.indexOf(this.currentExerciseId);
      const prevBtn = this.rootEl.querySelector("#btn-prev-ex");
      const nextBtn = this.rootEl.querySelector("#btn-next-ex");

      if (prevBtn) prevBtn.disabled = curIdx <= 0;
      if (nextBtn) nextBtn.disabled = curIdx >= ids.length - 1;
    }

    updateStatusPill(stage, message) {
      const pill = this.rootEl.querySelector("#playground-status-pill");
      const text = this.rootEl.querySelector("#status-pill-text");
      if (!pill || !text) return;

      pill.className = `playground-status-pill status-${stage}`;
      text.textContent = message;
    }

    updateProgressUI() {
      const stats = RaylingsStorage.state.stats;
      const text = this.rootEl.querySelector("#sidebar-progress-text");
      const fill = this.rootEl.querySelector("#sidebar-progress-fill");

      if (text) text.textContent = `${stats.completionPercentage}% (${stats.completedCount}/${stats.totalCount})`;
      if (fill) fill.style.width = `${stats.completionPercentage}%`;
    }

    renderSidebarTree() {
      const container = this.rootEl.querySelector("#sidebar-syllabus-tree");
      if (!container || !this.bundle) return;

      let html = "";
      for (const chapter of this.bundle.chapters) {
        let matchingExercises = [];
        for (const exId of chapter.exercise_ids) {
          const ex = this.bundle.exercises[exId];
          if (!ex) continue;

          const exState = RaylingsStorage.getExerciseState(exId);
          if (this.currentFilter === "pending" && exState.status === "completed") continue;
          if (this.currentFilter === "completed" && exState.status !== "completed") continue;

          if (this.searchQuery) {
            const matchesSearch =
              ex.id.toLowerCase().includes(this.searchQuery) ||
              ex.title.toLowerCase().includes(this.searchQuery) ||
              chapter.title.toLowerCase().includes(this.searchQuery);
            if (!matchesSearch) continue;
          }
          matchingExercises.push(ex);
        }

        if (matchingExercises.length === 0 && (this.searchQuery || this.currentFilter !== "all")) {
          continue;
        }

        const isExpanded = this.expandedChapters.has(chapter.number) || Boolean(this.searchQuery);
        const expandedClass = isExpanded ? "expanded" : "";

        let completedInCh = 0;
        for (const exId of chapter.exercise_ids) {
          const s = RaylingsStorage.getExerciseState(exId);
          if (s.status === "completed") completedInCh++;
        }
        const isChComplete = completedInCh === chapter.exercise_ids.length && chapter.exercise_ids.length > 0;
        const countBadgeClass = isChComplete ? "chapter-badge-count complete" : "chapter-badge-count";

        html += `
          <div class="chapter-group ${expandedClass}" data-chapter-num="${chapter.number}">
            <div class="chapter-header">
              <div class="chapter-header-title">
                <span class="chapter-chevron">▶</span>
                <span class="chapter-num">${String(chapter.number).padStart(2, "0")}.</span>
                <span class="chapter-name" title="${this.escapeHtml(chapter.title)}">${this.escapeHtml(chapter.title)}</span>
              </div>
              <span class="${countBadgeClass}">${completedInCh}/${chapter.exercise_ids.length}</span>
            </div>
            <div class="chapter-exercise-list">
        `;

        for (const ex of matchingExercises) {
          const exState = RaylingsStorage.getExerciseState(ex.id);
          const activeClass = ex.id === this.currentExerciseId ? "active" : "";
          let statusClass = "status-unstarted";
          let statusIcon = "○";

          if (exState.status === "completed") {
            statusClass = "status-done";
            statusIcon = "✓";
          } else if (exState.status === "in_progress") {
            statusClass = "status-progress";
            statusIcon = "⏳";
          }

          html += `
            <div class="exercise-item ${activeClass} ${statusClass}" data-exercise-id="${this.escapeHtml(ex.id)}">
              <span class="exercise-status-icon">${statusIcon}</span>
              <div class="exercise-item-content">
                <div class="exercise-item-title">${this.escapeHtml(ex.id)}.py — ${this.escapeHtml(ex.title)}</div>
              </div>
            </div>
          `;
        }

        html += `
            </div>
          </div>
        `;
      }

      container.innerHTML = html || '<div class="sidebar-empty">No exercises found matching search.</div>';

      // Bind Chapter Accordions and Exercise Click
      container.querySelectorAll(".chapter-header").forEach((hdr) => {
        hdr.addEventListener("click", () => {
          const grp = hdr.parentElement;
          const chNum = parseInt(grp.dataset.chapterNum, 10);
          if (grp.classList.contains("expanded")) {
            grp.classList.remove("expanded");
            this.expandedChapters.delete(chNum);
          } else {
            grp.classList.add("expanded");
            this.expandedChapters.add(chNum);
          }
        });
      });

      container.querySelectorAll(".exercise-item").forEach((item) => {
        item.addEventListener("click", () => {
          this.loadExercise(item.dataset.exerciseId);
        });
      });
    }

    updateSidebarActiveItem() {
      const items = this.rootEl.querySelectorAll(".exercise-item");
      items.forEach((item) => {
        if (item.dataset.exerciseId === this.currentExerciseId) {
          item.classList.add("active");
          const parentGroup = item.closest(".chapter-group");
          if (parentGroup) {
            parentGroup.classList.add("expanded");
            const chNum = parseInt(parentGroup.dataset.chapterNum, 10);
            if (!isNaN(chNum)) this.expandedChapters.add(chNum);
          }
        } else {
          item.classList.remove("active");
        }
      });
    }

    updateSidebarItemStatus(exerciseId) {
      const item = this.rootEl.querySelector(`.exercise-item[data-exercise-id="${exerciseId}"]`);
      if (!item) return;

      const exState = RaylingsStorage.getExerciseState(exerciseId);
      item.classList.remove("status-unstarted", "status-progress", "status-done");
      const icon = item.querySelector(".exercise-status-icon");

      if (exState.status === "completed") {
        item.classList.add("status-done");
        if (icon) icon.textContent = "✓";
      } else if (exState.status === "in_progress") {
        item.classList.add("status-progress");
        if (icon) icon.textContent = "⏳";
      } else {
        item.classList.add("status-unstarted");
        if (icon) icon.textContent = "○";
      }
    }

    exportBackup() {
      const jsonStr = RaylingsStorage.exportBackupJSON();
      const dateStr = new Date().toISOString().slice(0, 10);
      const blob = new Blob([jsonStr], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `raylings-progress-${dateStr}.json`;
      a.click();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    }

    importBackup() {
      const input = document.createElement("input");
      input.type = "file";
      input.accept = "application/json";
      input.onchange = (e) => {
        const file = e.target.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = (re) => {
          if (RaylingsStorage.importBackupJSON(re.target.result, this.bundle)) {
            alert("✓ Progress backup successfully restored!");
            this.updateProgressUI();
            this.renderSidebarTree();
            this.loadExercise(this.currentExerciseId);
          } else {
            alert("❌ Failed to parse valid Raylings progress backup JSON.");
          }
        };
        reader.readAsText(file);
      };
      input.click();
    }

    resetAllExercises() {
      const totalCount = this.bundle?.total_exercises || 81;
      if (confirm(`Are you sure you want to reset ALL ${totalCount} exercises and clear all stored progress? This cannot be undone.`)) {
        RaylingsStorage.resetAll(this.bundle);
        this.updateProgressUI();
        this.renderSidebarTree();
        this.loadExercise(this.currentExerciseId);
      }
    }

    escapeHtml(str) {
      if (!str) return "";
      return String(str).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
    }
  }

  // Auto mount when DOM is ready
  document.addEventListener("DOMContentLoaded", () => {
    const root = document.getElementById("raylings-playground") || document.getElementById("kubelings-playground");
    if (root) {
      window.raylingsPlayground = new RaylingsPlaygroundApp(root);
    }
  });
})();
