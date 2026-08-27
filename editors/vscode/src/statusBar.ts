import * as vscode from 'vscode';
import { exec } from 'child_process';
import { promisify } from 'util';
import { ProgressResponse } from './types';

const execAsync = promisify(exec);

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
    const executablePath = config.get<string>('executablePath', 'raylings');
    const workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath || process.cwd();

    try {
      const { stdout } = await execAsync(`${executablePath} progress --json`, {
        cwd: workspaceRoot,
        timeout: 10000,
      });
      const data: ProgressResponse = JSON.parse(stdout.trim());

      if (data.is_finished) {
        this.statusBarItem.text = `⚡ Raylings: 🎉 100% Completed! (66/66)`;
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
    } catch {
      this.statusBarItem.text = `⚡ Raylings: Ready`;
      this.statusBarItem.tooltip = 'Raylings extension active. Click to open next exercise.';
      this.statusBarItem.show();
    } finally {
      this.isUpdating = false;
    }
  }

  public dispose(): void {
    this.statusBarItem.dispose();
  }
}
