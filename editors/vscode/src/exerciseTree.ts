import * as vscode from 'vscode';
import { exec } from 'child_process';
import { promisify } from 'util';
import * as path from 'path';
import { ChapterData, ExerciseData, ListResponse } from './types';

const execAsync = promisify(exec);

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
    const config = vscode.workspace.getConfiguration('raylings');
    const executablePath = config.get<string>('executablePath', 'raylings');
    const workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath || process.cwd();

    try {
      const { stdout } = await execAsync(`${executablePath} list --json`, {
        cwd: workspaceRoot,
        timeout: 15000,
      });
      const data: ListResponse = JSON.parse(stdout.trim());
      this.chapters = data.chapters || [];
    } catch (err) {
      console.error('Error loading exercises via raylings list --json:', err);
    }
  }

  getTreeItem(element: TreeItemNode): vscode.TreeItem {
    return element;
  }

  async getChildren(element?: TreeItemNode): Promise<TreeItemNode[]> {
    if (this.chapters.length === 0 && !this.isRefreshing) {
      await this.loadExercises();
    }

    const workspaceRoot =
      vscode.workspace.workspaceFolders?.[0]?.uri.fsPath || process.cwd();

    if (!element) {
      // Root level: Group exercises by Chapter
      return this.chapters.map((ch) => {
        const total = ch.exercises.length;
        const completed = ch.exercises.filter((e) => e.completed).length;
        const isAllDone = total > 0 && completed === total;
        const label = `Ch ${String(ch.number).padStart(2, '0')}: ${ch.title} (${completed}/${total})`;

        const node = new TreeItemNode(
          label,
          vscode.TreeItemCollapsibleState.Collapsed,
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
        const isCompleted = ex.completed;
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
          : new vscode.ThemeIcon('circle-outline');

        const absPath = path.isAbsolute(ex.path)
          ? ex.path
          : path.resolve(workspaceRoot, ex.path);
        const fileUri = vscode.Uri.file(absPath);

        node.command = {
          command: 'vscode.open',
          title: 'Open Exercise',
          arguments: [fileUri],
        };

        const statusText = isCompleted ? 'Completed ✓' : 'Incomplete ⏳';
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
