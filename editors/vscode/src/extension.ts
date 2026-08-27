import * as vscode from 'vscode';
import { RaylingsStatusBar } from './statusBar';
import { RaylingsTreeProvider } from './exerciseTree';
import { registerCommands } from './commands';

let statusBar: RaylingsStatusBar | undefined;
let treeProvider: RaylingsTreeProvider | undefined;

export async function activate(context: vscode.ExtensionContext): Promise<void> {
  statusBar = new RaylingsStatusBar();
  treeProvider = new RaylingsTreeProvider();

  context.subscriptions.push(statusBar);

  // Register TreeDataProvider for the Activity Bar exercise explorer
  context.subscriptions.push(
    vscode.window.registerTreeDataProvider('raylings.exerciseTree', treeProvider)
  );

  // Register all extension command handlers
  registerCommands(context, treeProvider, statusBar);

  // Initial update for status bar and exercise tree
  await statusBar.update();

  // Auto-run on save if enabled in settings
  context.subscriptions.push(
    vscode.workspace.onDidSaveTextDocument(async (doc) => {
      if (doc.languageId === 'python' || doc.fileName.endsWith('.py')) {
        const config = vscode.workspace.getConfiguration('raylings');
        const autoRun = config.get<boolean>('autoRunOnSave', true);

        if (autoRun && /[/\\]exercises[/\\]/.test(doc.fileName)) {
          vscode.commands.executeCommand('raylings.runCurrent');
        } else {
          await Promise.all([
            statusBar?.update(),
            treeProvider?.refresh(),
          ]);
        }
      }
    })
  );

  // Handle configuration changes
  context.subscriptions.push(
    vscode.workspace.onDidChangeConfiguration(async (e) => {
      if (e.affectsConfiguration('raylings')) {
        await Promise.all([
          statusBar?.update(),
          treeProvider?.refresh(),
        ]);
      }
    })
  );
}

export function deactivate(): void {
  if (statusBar) {
    statusBar.dispose();
  }
}
