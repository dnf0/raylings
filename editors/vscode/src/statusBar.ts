import * as vscode from 'vscode';
import * as fs from 'fs';
import { ProgressResponse } from './types';
import { getEffectiveWorkspaceRoot, resolveExercisePath } from './pathUtils';
import { cliBridge } from './cliBridge';
import { BUNDLED_CHAPTERS } from './curriculumManifest';

export class RaylingsStatusBar implements vscode.Disposable {
  private statusBarItem: vscode.StatusBarItem;
  private isUpdating = false;

  constructor() {
    this.statusBarItem = vscode.window.createStatusBarItem(
      vscode.StatusBarAlignment.Left,
      100
    );
    this.statusBarItem.command = 'raylings.openNextExercise';
    this.statusBarItem.name = 'Raylings Progress';
    this.statusBarItem.show();
  }

  public async update(): Promise<void> {
    if (this.isUpdating) {
      return;
    }

    const config = vscode.workspace.getConfiguration('raylings');
    if (!config.get<boolean>('showStatusBar', true)) {
      this.statusBarItem.hide();
      return;
    }

    this.isUpdating = true;
    const workspaceRoot = getEffectiveWorkspaceRoot();

    try {
      const data: ProgressResponse = await cliBridge.progress(workspaceRoot);
      if (data && typeof data.completed === 'number') {
        if (data.is_finished) {
          this.statusBarItem.text = `⚡ Raylings: 🎉 100% Completed! (${data.total}/${data.total})`;
          this.statusBarItem.tooltip = 'All Raylings exercises completed! Click to view progress summary.';
        } else {
          const nextName = data.current_exercise || 'None';
          this.statusBarItem.text = `⚡ Raylings: ${data.completed}/${data.total} (${data.percentage}%) | Next: ${nextName}`;
          this.statusBarItem.tooltip = new vscode.MarkdownString(
            `**⚡ Raylings Interactive Curriculum**\n\n` +
            `- **Progress:** ${data.completed} / ${data.total} exercises (${data.percentage}%)\n` +
            `- **Current Exercise:** \`${nextName}\`\n\n` +
            `*Click to jump to next incomplete exercise*`
          );
        }
        this.statusBarItem.show();
        return;
      }
    } catch {
      // Fallback to direct disk inspection
    }

    // Direct filesystem calculation fallback
    let total = 0;
    let completed = 0;
    let nextEx: string | null = null;

    for (const chapter of BUNDLED_CHAPTERS) {
      for (const ex of chapter.exercises) {
        total++;
        const fullPath = resolveExercisePath(ex.path, workspaceRoot);
        let done = false;
        if (fs.existsSync(fullPath) && !fs.statSync(fullPath).isDirectory()) {
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
            done = !hasNotDone && !hasBlank;
          } catch {
            done = false;
          }
        }
        if (done) {
          completed++;
        } else if (!nextEx) {
          nextEx = ex.name;
        }
      }
    }

    const pct = total > 0 ? Math.round((completed / total) * 100) : 0;
    if (completed === total && total > 0) {
      this.statusBarItem.text = `⚡ Raylings: 🎉 100% Completed! (${completed}/${total})`;
    } else {
      this.statusBarItem.text = `⚡ Raylings: ${completed}/${total} (${pct}%) | Next: ${nextEx || 'basics01'}`;
    }
    this.statusBarItem.tooltip = `Raylings progress: ${completed}/${total} exercises completed (${pct}%). Click to open next exercise.`;
    this.statusBarItem.show();
    this.isUpdating = false;
  }

  public dispose(): void {
    this.statusBarItem.dispose();
  }
}
