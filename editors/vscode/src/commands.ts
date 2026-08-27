import * as vscode from 'vscode';
import { exec } from 'child_process';
import { promisify } from 'util';
import * as path from 'path';
import { RaylingsTreeProvider } from './exerciseTree';
import { RaylingsStatusBar } from './statusBar';
import { HintResponse, ProgressResponse, RunResponse } from './types';

const execAsync = promisify(exec);

let outputChannel: vscode.OutputChannel | undefined;

function getOutputChannel(): vscode.OutputChannel {
  if (!outputChannel) {
    outputChannel = vscode.window.createOutputChannel('Raylings');
  }
  return outputChannel;
}

export function registerCommands(
  context: vscode.ExtensionContext,
  treeProvider?: RaylingsTreeProvider,
  statusBar?: RaylingsStatusBar
): void {
  const getExecutable = (): string => {
    const config = vscode.workspace.getConfiguration('raylings');
    return config.get<string>('executablePath', 'raylings');
  };

  const getWorkspaceRoot = (): string => {
    return vscode.workspace.workspaceFolders?.[0]?.uri.fsPath || process.cwd();
  };

  // 1. Open Next Incomplete Exercise
  context.subscriptions.push(
    vscode.commands.registerCommand('raylings.openNextExercise', async () => {
      try {
        const { stdout } = await execAsync(`${getExecutable()} progress --json`, {
          cwd: getWorkspaceRoot(),
        });
        const data: ProgressResponse = JSON.parse(stdout.trim());

        if (data.is_finished || !data.current_path) {
          vscode.window.showInformationMessage('🎉 Congratulations! You have completed all Raylings exercises!');
          return;
        }

        const absPath = path.isAbsolute(data.current_path)
          ? data.current_path
          : path.resolve(getWorkspaceRoot(), data.current_path);

        const doc = await vscode.workspace.openTextDocument(vscode.Uri.file(absPath));
        await vscode.window.showTextDocument(doc);
      } catch (err: any) {
        vscode.window.showErrorMessage(`Failed to determine next exercise: ${err.message}`);
      }
    })
  );

  // 2. Run Current Exercise
  context.subscriptions.push(
    vscode.commands.registerCommand('raylings.runCurrent', async () => {
      const editor = vscode.window.activeTextEditor;
      let targetName = '';

      if (editor && editor.document.fileName.endsWith('.py')) {
        targetName = path.basename(editor.document.fileName, '.py');
      }

      if (!targetName) {
        targetName = await vscode.window.showInputBox({
          prompt: 'Enter exercise name to run (e.g. basics01)',
          placeHolder: 'basics01',
        }) || '';
      }

      if (!targetName) {
        return;
      }

      const out = getOutputChannel();
      out.show(true);
      out.appendLine(`\n⚡ [Raylings] Running exercise: ${targetName}...`);

      try {
        const { stdout } = await execAsync(`${getExecutable()} run ${targetName} --json`, {
          cwd: getWorkspaceRoot(),
        });
        const result: RunResponse = JSON.parse(stdout.trim());

        if (result.passed) {
          out.appendLine(`✅ Exercise passed cleanly!`);
          vscode.window.showInformationMessage(`✅ ${targetName} passed! Ready for next exercise.`);
        } else {
          out.appendLine(`❌ Exercise failed or contains '# I AM NOT DONE':`);
          if (result.output) {
            out.appendLine(result.output);
          }
          if (result.error) {
            out.appendLine(result.error);
          }
          vscode.window.showWarningMessage(`⏳ ${targetName} is not complete yet. Check Raylings output channel.`);
        }

        await Promise.all([treeProvider?.refresh(), statusBar?.update()]);
      } catch (err: any) {
        out.appendLine(`❌ Error running exercise:\n${err.stdout || err.message}`);
        vscode.window.showErrorMessage(`Execution failed for ${targetName}. Check Raylings output.`);
        await Promise.all([treeProvider?.refresh(), statusBar?.update()]);
      }
    })
  );

  // 3. Show Exercise Hint
  context.subscriptions.push(
    vscode.commands.registerCommand('raylings.showHint', async () => {
      const editor = vscode.window.activeTextEditor;
      let targetName = '';

      if (editor && editor.document.fileName.endsWith('.py')) {
        targetName = path.basename(editor.document.fileName, '.py');
      }

      try {
        const cmd = targetName
          ? `${getExecutable()} hint ${targetName} --json`
          : `${getExecutable()} hint --json`;
        const { stdout } = await execAsync(cmd, { cwd: getWorkspaceRoot() });
        const data: HintResponse = JSON.parse(stdout.trim());

        if (!data.hints || data.hints.length === 0) {
          vscode.window.showInformationMessage(`No hints available for ${data.name || 'this exercise'}.`);
          return;
        }

        const items = data.hints.map((hint, idx) => ({
          label: `💡 Level ${idx + 1} Hint`,
          description: hint,
        }));

        const selected = await vscode.window.showQuickPick(items, {
          title: `⚡ Progressive Hints for ${data.name}`,
          placeHolder: 'Select a hint level to reveal details',
        });

        if (selected) {
          vscode.window.showInformationMessage(`💡 [${data.name}] ${selected.description}`);
        }
      } catch (err: any) {
        vscode.window.showErrorMessage(`Failed to fetch hint: ${err.message}`);
      }
    })
  );

  // 4. Start Watcher in Integrated Terminal
  context.subscriptions.push(
    vscode.commands.registerCommand('raylings.startWatcher', () => {
      const terminal = vscode.window.createTerminal('Raylings Watcher');
      terminal.show();
      terminal.sendText(`${getExecutable()} watch`);
    })
  );

  // 5. Initialize Workspace
  context.subscriptions.push(
    vscode.commands.registerCommand('raylings.initWorkspace', async () => {
      try {
        const out = getOutputChannel();
        out.show(true);
        out.appendLine(`⚡ Initializing Raylings workspace in ${getWorkspaceRoot()}...`);
        const { stdout } = await execAsync(`${getExecutable()} init`, {
          cwd: getWorkspaceRoot(),
        });
        out.appendLine(stdout);
        vscode.window.showInformationMessage('✨ Raylings workspace initialized successfully!');
        await Promise.all([treeProvider?.refresh(), statusBar?.update()]);
      } catch (err: any) {
        vscode.window.showErrorMessage(`Failed to initialize workspace: ${err.message}`);
      }
    })
  );

  // 6. View Reference Solution
  context.subscriptions.push(
    vscode.commands.registerCommand('raylings.viewSolution', async () => {
      const editor = vscode.window.activeTextEditor;
      if (!editor || !editor.document.fileName.endsWith('.py')) {
        vscode.window.showWarningMessage('Open an exercise file to view its matching reference solution.');
        return;
      }

      const currentFile = editor.document.fileName;
      // Convert exercises/<chapter>/<name>.py -> solutions/<chapter>/<name>.py
      const solutionFile = currentFile.replace(/([/\\])exercises([/\\])/, '$1solutions$2');

      try {
        const doc = await vscode.workspace.openTextDocument(vscode.Uri.file(solutionFile));
        await vscode.window.showTextDocument(doc, {
          viewColumn: vscode.ViewColumn.Beside,
          preview: true,
        });
      } catch {
        vscode.window.showErrorMessage(`Solution file not found at: ${solutionFile}`);
      }
    })
  );

  // 7. Sync Progress
  context.subscriptions.push(
    vscode.commands.registerCommand('raylings.syncProgress', async () => {
      await Promise.all([treeProvider?.refresh(), statusBar?.update()]);
      vscode.window.showInformationMessage('🔄 Raylings progress synced!');
    })
  );
}
