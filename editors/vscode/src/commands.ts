import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';
import { RaylingsTreeProvider } from './exerciseTree';
import { RaylingsStatusBar } from './statusBar';
import { HintResponse, ListResponse, RunResponse } from './types';
import { getEffectiveWorkspaceRoot, resolveExercisePath } from './pathUtils';
import { cliBridge } from './cliBridge';
import { BUNDLED_CHAPTERS } from './curriculumManifest';

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
  // 1. Open Specific Exercise File (with 1-Click Auto-Init UX)
  const openExerciseFileHandler = async (filePath?: string | vscode.Uri) => {
    const workspaceRoot = getEffectiveWorkspaceRoot();

    let rawPath: string;
    if (!filePath) {
      await vscode.commands.executeCommand('raylings.openNextExercise');
      return;
    } else if (typeof filePath === 'string') {
      rawPath = filePath;
    } else {
      rawPath = filePath.fsPath;
    }

    let resolved = resolveExercisePath(rawPath, workspaceRoot);

    if (!fs.existsSync(resolved)) {
      const targetDir =
        vscode.workspace.workspaceFolders?.[0]?.uri.fsPath ||
        path.join(os.homedir(), 'raylings');

      const choice = await vscode.window.showWarningMessage(
        `Raylings exercise file not found at "${resolved}". Would you like to initialize exercises in your workspace ("${targetDir}")?`,
        'Initialize Exercises',
        'Cancel'
      );

      if (choice === 'Initialize Exercises') {
        try {
          if (!fs.existsSync(targetDir)) {
            fs.mkdirSync(targetDir, { recursive: true });
          }
          const out = getOutputChannel();
          out.show(true);
          out.appendLine(`⚡ Initializing Raylings exercises in ${targetDir}...`);
          const res = await cliBridge.init(targetDir);
          out.appendLine(res.message);
          vscode.window.showInformationMessage('✨ Raylings exercises initialized successfully! 🎉');
          await Promise.all([
            treeProvider?.refresh(),
            statusBar?.update(),
          ]);
          resolved = resolveExercisePath(rawPath, targetDir);
        } catch (err: any) {
          vscode.window.showErrorMessage(
            `Failed to initialize exercises: ${err instanceof Error ? err.message : String(err)}`
          );
          return;
        }
      } else {
        return;
      }
    }

    if (fs.existsSync(resolved)) {
      try {
        const doc = await vscode.workspace.openTextDocument(vscode.Uri.file(resolved));
        await vscode.window.showTextDocument(doc);
      } catch (err: any) {
        vscode.window.showErrorMessage(
          `Failed to open exercise file: ${err instanceof Error ? err.message : String(err)}`
        );
      }
    } else {
      vscode.window.showErrorMessage(`Exercise file still not found at: ${resolved}`);
    }
  };

  context.subscriptions.push(
    vscode.commands.registerCommand('raylings.openExerciseFile', openExerciseFileHandler)
  );
  context.subscriptions.push(
    vscode.commands.registerCommand('raylings.openExercise', openExerciseFileHandler)
  );

  // 2. Open Next Incomplete Exercise
  context.subscriptions.push(
    vscode.commands.registerCommand('raylings.openNextExercise', async () => {
      const workspaceRoot = getEffectiveWorkspaceRoot();

      try {
        const data: ListResponse = await cliBridge.list(workspaceRoot);
        const allExercises = (data.chapters || []).flatMap((ch) => ch.exercises);
        const nextExercise = allExercises.find(
          (ex) => !ex.completed && (ex.has_marker || !ex.exists)
        );

        if (nextExercise) {
          await vscode.commands.executeCommand('raylings.openExerciseFile', nextExercise.path);
          return;
        }
      } catch {
        // Fallback to bundled curriculum and local disk check
      }

      for (const chapter of BUNDLED_CHAPTERS) {
        for (const ex of chapter.exercises) {
          const fullPath = resolveExercisePath(ex.path, workspaceRoot);
          let isDone = false;
          if (fs.existsSync(fullPath) && !fs.statSync(fullPath).isDirectory()) {
            try {
              const content = fs.readFileSync(fullPath, 'utf8');
              const hasMarker =
                content.includes('# I AM NOT DONE') ||
                content.includes('// I AM NOT DONE') ||
                content.includes('<!-- I AM NOT DONE -->') ||
                content.includes('___') ||
                content.includes('/* ??? */') ||
                content.includes('<!-- ANSWER -->');
              isDone = !hasMarker;
            } catch {
              isDone = false;
            }
          }
          if (!isDone) {
            await vscode.commands.executeCommand('raylings.openExerciseFile', ex.path);
            return;
          }
        }
      }

      vscode.window.showInformationMessage(
        '🎉 Congratulations! You have completed all Raylings exercises!'
      );
    })
  );

  // 3. Run Current Exercise
  context.subscriptions.push(
    vscode.commands.registerCommand('raylings.runCurrent', async () => {
      const editor = vscode.window.activeTextEditor;
      let targetName = '';

      if (editor && editor.document.fileName.endsWith('.py')) {
        targetName = path.basename(editor.document.fileName, '.py');
      }

      if (!targetName) {
        targetName =
          (await vscode.window.showInputBox({
            prompt: 'Enter exercise name to run (e.g. basics01)',
            placeHolder: 'basics01',
          })) || '';
      }

      if (!targetName) {
        return;
      }

      const out = getOutputChannel();
      out.show(true);
      out.appendLine(`\n⚡ [Raylings] Running exercise: ${targetName}...`);

      const workspaceRoot = getEffectiveWorkspaceRoot();
      try {
        const result: RunResponse = await cliBridge.run(targetName, workspaceRoot);

        if (result.passed) {
          out.appendLine(`✅ Exercise passed cleanly!`);
          vscode.window.showInformationMessage(`✅ ${targetName} passed! Ready for next exercise.`);
        } else {
          out.appendLine(`❌ Exercise failed or contains incomplete placeholders:`);
          if (result.output) {
            out.appendLine(result.output);
          }
          if (result.error) {
            out.appendLine(result.error);
          }
          vscode.window.showWarningMessage(
            `⏳ ${targetName} is not complete yet. Check Raylings output channel.`
          );
        }

        await Promise.all([treeProvider?.refresh(), statusBar?.update()]);
      } catch (err: any) {
        out.appendLine(`❌ Error running exercise:\n${err.message || String(err)}`);
        vscode.window.showErrorMessage(
          `Execution failed for ${targetName}. Check Raylings output.`
        );
        await Promise.all([treeProvider?.refresh(), statusBar?.update()]);
      }
    })
  );

  // 4. Show Exercise Hint
  context.subscriptions.push(
    vscode.commands.registerCommand('raylings.showHint', async () => {
      const editor = vscode.window.activeTextEditor;
      let targetName = '';

      if (editor && editor.document.fileName.endsWith('.py')) {
        targetName = path.basename(editor.document.fileName, '.py');
      }

      const workspaceRoot = getEffectiveWorkspaceRoot();
      let hints: string[] = [];
      let exerciseTitle = targetName;

      try {
        const data: HintResponse = await cliBridge.hint(targetName || 'basics01', undefined, workspaceRoot);
        hints = data.hints || [];
        if (data.name) {
          exerciseTitle = data.name;
        }
      } catch {
        // Fallback to embedded curriculum hints
        for (const chapter of BUNDLED_CHAPTERS) {
          const match = chapter.exercises.find((e) => e.name === targetName);
          if (match) {
            hints = match.hints;
            exerciseTitle = `${match.name}: ${match.title}`;
            break;
          }
        }
      }

      if (!hints || hints.length === 0) {
        vscode.window.showInformationMessage(
          `No hints available for ${exerciseTitle || 'this exercise'}.`
        );
        return;
      }

      const items = hints.map((hint, idx) => ({
        label: `💡 Level ${idx + 1} Hint`,
        description: hint,
      }));

      const selected = await vscode.window.showQuickPick(items, {
        title: `⚡ Progressive Hints for ${exerciseTitle}`,
        placeHolder: 'Select a hint level to reveal details',
      });

      if (selected) {
        vscode.window.showInformationMessage(`💡 [${exerciseTitle}] ${selected.description}`);
      }
    })
  );

  // 5. Start Watcher in Integrated Terminal
  context.subscriptions.push(
    vscode.commands.registerCommand('raylings.startWatcher', () => {
      const workspaceRoot = getEffectiveWorkspaceRoot();
      const resolved = cliBridge.resolveCommand(workspaceRoot);
      const cmdStr = [...resolved.argsPrefix, 'watch'].join(' ');
      const fullCmd = `${resolved.command} ${cmdStr}`.trim();

      let terminal = vscode.window.terminals.find((t) => t.name === 'Raylings Watcher');
      if (!terminal) {
        terminal = vscode.window.createTerminal({
          name: 'Raylings Watcher',
          cwd: workspaceRoot,
          env: cliBridge.getEnhancedEnv(),
        });
      }
      terminal.show();
      terminal.sendText(fullCmd);
    })
  );

  // 6. Initialize Workspace / Exercises
  const initWorkspaceHandler = async () => {
    const targetDir =
      vscode.workspace.workspaceFolders?.[0]?.uri.fsPath ||
      path.join(os.homedir(), 'raylings');

    try {
      if (!fs.existsSync(targetDir)) {
        fs.mkdirSync(targetDir, { recursive: true });
      }
      const out = getOutputChannel();
      out.show(true);
      out.appendLine(`⚡ Initializing Raylings workspace in ${targetDir}...`);
      const res = await cliBridge.init(targetDir);
      out.appendLine(res.message);
      vscode.window.showInformationMessage(
        `✨ Raylings workspace initialized successfully in ${targetDir}! 🎉`
      );
      await Promise.all([treeProvider?.refresh(), statusBar?.update()]);
    } catch (err: any) {
      vscode.window.showErrorMessage(
        `Failed to initialize workspace: ${err instanceof Error ? err.message : String(err)}`
      );
    }
  };

  context.subscriptions.push(
    vscode.commands.registerCommand('raylings.initWorkspace', initWorkspaceHandler)
  );
  context.subscriptions.push(
    vscode.commands.registerCommand('raylings.initExercises', initWorkspaceHandler)
  );

  // 7. View Reference Solution
  context.subscriptions.push(
    vscode.commands.registerCommand('raylings.viewSolution', async () => {
      const editor = vscode.window.activeTextEditor;
      if (!editor || !editor.document.fileName.endsWith('.py')) {
        vscode.window.showWarningMessage(
          'Open an exercise file to view its matching reference solution.'
        );
        return;
      }

      const currentFile = editor.document.fileName;
      // Convert exercises/<chapter>/<name>.py -> solutions/<chapter>/<name>.py
      const relSolutionPath = currentFile
        .replace(/([/\\])exercises([/\\])/, '$1solutions$2');

      const workspaceRoot = getEffectiveWorkspaceRoot();
      const resolved = resolveExercisePath(relSolutionPath, workspaceRoot);

      if (fs.existsSync(resolved)) {
        try {
          const doc = await vscode.workspace.openTextDocument(vscode.Uri.file(resolved));
          await vscode.window.showTextDocument(doc, {
            viewColumn: vscode.ViewColumn.Beside,
            preview: true,
          });
        } catch {
          vscode.window.showErrorMessage(`Solution file not found at: ${resolved}`);
        }
      } else {
        vscode.window.showErrorMessage(`Solution file not found at: ${resolved}`);
      }
    })
  );

  // 8. Sync Progress
  context.subscriptions.push(
    vscode.commands.registerCommand('raylings.syncProgress', async () => {
      await Promise.all([treeProvider?.refresh(), statusBar?.update()]);
      vscode.window.showInformationMessage('🔄 Raylings progress synced!');
    })
  );

  // 9. Start Interactive Onboarding Tour in Integrated Terminal
  context.subscriptions.push(
    vscode.commands.registerCommand('raylings.startTour', () => {
      startTourCommand();
    })
  );

  // 10. Run Preflight Diagnostics (Doctor) in Integrated Terminal
  context.subscriptions.push(
    vscode.commands.registerCommand('raylings.runDoctor', () => {
      runDoctorCommand();
    })
  );
}

/**
 * Launch the interactive onboarding tour in a dedicated terminal.
 */
export function startTourCommand(): void {
  const workspaceRoot = getEffectiveWorkspaceRoot();
  const resolved = cliBridge.resolveCommand(workspaceRoot);
  const cmdStr = [...resolved.argsPrefix, 'tour'].join(' ');
  const fullCmd = `${resolved.command} ${cmdStr}`.trim();

  let terminal = vscode.window.terminals.find((t) => t.name === 'Raylings Tour');
  if (!terminal) {
    terminal = vscode.window.createTerminal({
      name: 'Raylings Tour',
      cwd: workspaceRoot,
      env: cliBridge.getEnhancedEnv(),
    });
  }
  terminal.show();
  terminal.sendText(fullCmd);
}

/**
 * Launch the preflight doctor diagnostics in a dedicated terminal.
 */
export function runDoctorCommand(): void {
  const workspaceRoot = getEffectiveWorkspaceRoot();
  const resolved = cliBridge.resolveCommand(workspaceRoot);
  const cmdStr = [...resolved.argsPrefix, 'doctor'].join(' ');
  const fullCmd = `${resolved.command} ${cmdStr}`.trim();

  let terminal = vscode.window.terminals.find((t) => t.name === 'Raylings Doctor');
  if (!terminal) {
    terminal = vscode.window.createTerminal({
      name: 'Raylings Doctor',
      cwd: workspaceRoot,
      env: cliBridge.getEnhancedEnv(),
    });
  }
  terminal.show();
  terminal.sendText(fullCmd);
}

/**
 * Open a specified exercise file or uri in the active text editor.
 */
export async function openExerciseCommand(filePath?: string | vscode.Uri): Promise<void> {
  await vscode.commands.executeCommand('raylings.openExerciseFile', filePath);
}
