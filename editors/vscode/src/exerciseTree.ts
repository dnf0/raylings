import * as vscode from 'vscode';
import * as fs from 'fs';
import { ChapterData, ExerciseData, ListResponse } from './types';
import { getEffectiveWorkspaceRoot, resolveExercisePath } from './pathUtils';
import { BUNDLED_CHAPTERS } from './curriculumManifest';
import { cliBridge } from './cliBridge';

export class TreeItemNode extends vscode.TreeItem {
  constructor(
    public readonly label: string,
    public readonly collapsibleState: vscode.TreeItemCollapsibleState,
    public readonly contextValue: string,
    public readonly chapter?: ChapterData,
    public readonly exercise?: ExerciseData
  ) {
    super(label, collapsibleState);
  }
}

export class RaylingsTreeProvider implements vscode.TreeDataProvider<TreeItemNode> {
  private _onDidChangeTreeData: vscode.EventEmitter<TreeItemNode | undefined | null | void> =
    new vscode.EventEmitter<TreeItemNode | undefined | null | void>();
  readonly onDidChangeTreeData: vscode.Event<TreeItemNode | undefined | null | void> =
    this._onDidChangeTreeData.event;

  private chapters: ChapterData[] = [];
  private isRefreshing = false;

  constructor() {
    this.refresh();
  }

  public async refresh(): Promise<void> {
    if (this.isRefreshing) {
      return;
    }
    this.isRefreshing = true;

    try {
      await this.loadExercises();
      this._onDidChangeTreeData.fire();
    } catch (err) {
      console.error('Error refreshing Raylings exercise tree:', err);
    } finally {
      this.isRefreshing = false;
    }
  }

  public async loadExercises(): Promise<void> {
    const workspaceRoot = getEffectiveWorkspaceRoot();

    // 1. Initialize with deep clone of bundled curriculum manifest
    const baseChapters: ChapterData[] = JSON.parse(JSON.stringify(BUNDLED_CHAPTERS));

    // 2. Directly scan local workspace files for completion & existence
    for (const chapter of baseChapters) {
      for (const ex of chapter.exercises) {
        const fullPath = resolveExercisePath(ex.path, workspaceRoot);
        if (fs.existsSync(fullPath) && !fs.statSync(fullPath).isDirectory()) {
          ex.exists = true;
          try {
            const content = fs.readFileSync(fullPath, 'utf8');
            const hasNotDone =
              content.includes('# I AM NOT DONE') ||
              content.includes('// I AM NOT DONE') ||
              content.includes('<!-- I AM NOT DONE -->');
            const hasBlank =
              content.includes('___') ||
              content.includes('/* ??? */') ||
              content.includes('<!-- ANSWER -->');
            const hasMarker = hasNotDone || hasBlank;

            ex.has_marker = hasMarker;
            ex.is_done = !hasMarker;
            ex.completed = !hasMarker;
          } catch {
            ex.has_marker = true;
            ex.is_done = false;
            ex.completed = false;
          }
        } else {
          ex.exists = false;
          ex.has_marker = true;
          ex.is_done = false;
          ex.completed = false;
        }
      }
    }

    this.chapters = baseChapters;

    // 3. Attempt dynamic query via CLI bridge in background to augment with tracker state if available
    try {
      const data: ListResponse = await cliBridge.list(workspaceRoot);
      if (data && Array.isArray(data.chapters) && data.chapters.length > 0) {
        this.chapters = data.chapters;
      }
    } catch {
      // Gracefully continue using filesystem-scanned bundled manifest
    }
  }

  getTreeItem(element: TreeItemNode): vscode.TreeItem {
    return element;
  }

  async getChildren(element?: TreeItemNode): Promise<TreeItemNode[]> {
    if (this.chapters.length === 0 && !this.isRefreshing) {
      await this.loadExercises();
    }

    if (!element) {
      // Root level: Group exercises by Chapter
      return this.chapters.map((ch) => {
        const total = ch.exercises.length;
        const completed = ch.exercises.filter(
          (e) => e.is_done === true || e.completed === true || (!e.has_marker && e.exists)
        ).length;
        const isAllDone = total > 0 && completed === total;
        const label = `Ch ${String(ch.number).padStart(2, '0')}: ${ch.title} (${completed}/${total})`;

        const node = new TreeItemNode(
          label,
          isAllDone ? vscode.TreeItemCollapsibleState.Collapsed : vscode.TreeItemCollapsibleState.Expanded,
          'chapter',
          ch
        );

        node.iconPath = isAllDone
          ? new vscode.ThemeIcon('check-all')
          : new vscode.ThemeIcon('folder');
        node.tooltip = `${ch.title}\n${ch.description}\nProgress: ${completed}/${total} completed`;
        return node;
      });
    }

    if (element.contextValue === 'chapter' && element.chapter) {
      // Child level: Exercises in Chapter
      return element.chapter.exercises.map((ex) => {
        const isCompleted = ex.is_done === true || ex.completed === true || (!ex.has_marker && ex.exists);
        const label = `${ex.name}: ${ex.title}`;
        const node = new TreeItemNode(
          label,
          vscode.TreeItemCollapsibleState.None,
          'exercise',
          element.chapter,
          ex
        );

        node.iconPath = isCompleted
          ? new vscode.ThemeIcon('pass')
          : ex.exists
          ? new vscode.ThemeIcon('circle-large')
          : new vscode.ThemeIcon('circle-outline');

        node.command = {
          command: 'raylings.openExerciseFile',
          title: 'Open Exercise',
          arguments: [ex.path],
        };

        const statusText = isCompleted ? 'Completed ✓' : ex.exists ? 'In Progress ⏳' : 'Not Initialized 📦';
        const tooltip = new vscode.MarkdownString();
        tooltip.isTrusted = true;
        tooltip.appendMarkdown(`### ⚡ ${ex.title}\n\n`);
        tooltip.appendMarkdown(`- **Exercise:** \`${ex.name}\`\n`);
        tooltip.appendMarkdown(`- **Chapter:** \`${ex.chapter_name}\`\n`);
        tooltip.appendMarkdown(`- **Status:** **${statusText}**\n`);
        tooltip.appendMarkdown(`- **Cluster Required:** ${ex.requires_cluster ? 'Yes (multi-node)' : 'No (local)'}\n`);
        tooltip.appendMarkdown(`- **Hints Available:** ${ex.hints.length}\n`);
        tooltip.appendMarkdown(`- **File:** \`${ex.path}\`\n\n`);
        tooltip.appendMarkdown(`*Click to open in editor*`);
        node.tooltip = tooltip;

        return node;
      });
    }

    return [];
  }
}
