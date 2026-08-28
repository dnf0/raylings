import * as vscode from 'vscode';
import { execFile } from 'child_process';
import * as fs from 'fs';
import * as os from 'os';
import * as path from 'path';
import { getEffectiveWorkspaceRoot } from './pathUtils';
import {
  ListResponse,
  ProgressResponse,
  RunResponse,
  HintResponse,
} from './types';

export interface ResolvedCommand {
  command: string;
  argsPrefix: string[];
}

export class RaylingsCliBridge {
  private customExecutablePath?: string;

  constructor(customExecutablePath?: string) {
    this.customExecutablePath = customExecutablePath;
  }

  /**
   * Retrieves the user-configured executable path or custom setting.
   */
  public getConfiguredExecutable(): string {
    if (this.customExecutablePath) {
      return this.customExecutablePath;
    }
    try {
      const config = vscode.workspace.getConfiguration('raylings');
      const execPath = config.get<string>('executablePath');
      if (execPath && execPath.trim().length > 0 && execPath !== 'raylings') {
        return execPath.trim();
      }
    } catch {
      // VS Code not initialized
    }
    return '';
  }

  /**
   * Builds an enhanced PATH environment string that includes standard binary directories.
   */
  public getEnhancedEnv(): NodeJS.ProcessEnv {
    const home = os.homedir();
    const extraPaths = [
      path.join(home, '.local', 'bin'),
      path.join(home, '.cargo', 'bin'),
      '/opt/homebrew/bin',
      '/opt/homebrew/sbin',
      '/usr/local/bin',
      '/usr/bin',
      '/bin',
    ];

    const currentPath = process.env.PATH || '';
    const combinedPath = [...extraPaths, currentPath].filter(Boolean).join(path.delimiter);

    return {
      ...process.env,
      PATH: combinedPath,
      PYTHONUNBUFFERED: '1',
    };
  }

  /**
   * Robustly resolves the best command to invoke raylings.
   */
  public resolveCommand(workspaceRoot?: string): ResolvedCommand {
    const configured = this.getConfiguredExecutable();
    if (configured) {
      if (
        configured.endsWith('python') ||
        configured.endsWith('python.exe') ||
        configured.endsWith('python3') ||
        configured.endsWith('python3.exe')
      ) {
        return { command: configured, argsPrefix: ['-m', 'raylings'] };
      }
      return { command: configured, argsPrefix: [] };
    }

    const root = workspaceRoot || getEffectiveWorkspaceRoot();

    // 1. Check workspace .venv/bin/raylings
    const venvRaylingsPosix = path.join(root, '.venv', 'bin', 'raylings');
    const venvRaylingsWin = path.join(root, '.venv', 'Scripts', 'raylings.exe');
    if (fs.existsSync(venvRaylingsPosix)) {
      return { command: venvRaylingsPosix, argsPrefix: [] };
    }
    if (fs.existsSync(venvRaylingsWin)) {
      return { command: venvRaylingsWin, argsPrefix: [] };
    }

    // 2. Check workspace .venv/bin/python
    const venvPythonPosix = path.join(root, '.venv', 'bin', 'python');
    const venvPythonWin = path.join(root, '.venv', 'Scripts', 'python.exe');
    if (fs.existsSync(venvPythonPosix)) {
      return { command: venvPythonPosix, argsPrefix: ['-m', 'raylings'] };
    }
    if (fs.existsSync(venvPythonWin)) {
      return { command: venvPythonWin, argsPrefix: ['-m', 'raylings'] };
    }

    // 3. Check parent folders up to 5 levels for .venv
    let cur = root;
    for (let i = 0; i < 5; i++) {
      const pRaylings = path.join(cur, '.venv', 'bin', 'raylings');
      if (fs.existsSync(pRaylings)) {
        return { command: pRaylings, argsPrefix: [] };
      }
      const pPython = path.join(cur, '.venv', 'bin', 'python');
      if (fs.existsSync(pPython)) {
        return { command: pPython, argsPrefix: ['-m', 'raylings'] };
      }
      const parent = path.dirname(cur);
      if (parent === cur) break;
      cur = parent;
    }

    // 4. Check known candidate locations (~/repos/raylings, ~/.local/bin/raylings, etc.)
    const home = os.homedir();
    const candidateBinaries = [
      path.join(home, 'repos', 'raylings', '.venv', 'bin', 'raylings'),
      path.join(home, 'raylings', '.venv', 'bin', 'raylings'),
      path.join(home, 'Developer', 'raylings', '.venv', 'bin', 'raylings'),
      path.join(home, '.local', 'bin', 'raylings'),
      path.join(home, '.cargo', 'bin', 'raylings'),
      '/opt/homebrew/bin',
      '/usr/local/bin',
    ];

    for (const bin of candidateBinaries) {
      if (fs.existsSync(bin) && !fs.statSync(bin).isDirectory()) {
        return { command: bin, argsPrefix: [] };
      }
    }

    // 5. Check if uv is available
    const uvCandidates = [
      path.join(home, '.local', 'bin', 'uv'),
      path.join(home, '.cargo', 'bin', 'uv'),
      '/opt/homebrew/bin/uv',
      '/usr/local/bin/uv',
    ];
    for (const uvBin of uvCandidates) {
      if (fs.existsSync(uvBin)) {
        return { command: uvBin, argsPrefix: ['run', 'raylings'] };
      }
    }

    // 6. Default fallback
    return { command: 'raylings', argsPrefix: [] };
  }

  /**
   * Executes a command with JSON output and parses the returned JSON payload.
   */
  public async executeJson<T>(args: string[], cwd?: string): Promise<T> {
    const effectiveCwd = cwd || getEffectiveWorkspaceRoot();
    const resolved = this.resolveCommand(effectiveCwd);
    const fullArgs = args.includes('--json')
      ? [...resolved.argsPrefix, ...args]
      : [...resolved.argsPrefix, ...args, '--json'];

    const env = this.getEnhancedEnv();

    return new Promise<T>((resolve, reject) => {
      execFile(
        resolved.command,
        fullArgs,
        {
          cwd: effectiveCwd,
          maxBuffer: 10 * 1024 * 1024,
          timeout: 45000,
          env,
        },
        (error, stdout, stderr) => {
          const rawOutput = (stdout || '').trim();
          if (rawOutput) {
            try {
              const jsonStart = rawOutput.indexOf('{');
              const jsonEnd = rawOutput.lastIndexOf('}');
              if (jsonStart !== -1 && jsonEnd !== -1 && jsonEnd >= jsonStart) {
                const jsonStr = rawOutput.substring(jsonStart, jsonEnd + 1);
                return resolve(JSON.parse(jsonStr) as T);
              }
              return resolve(JSON.parse(rawOutput) as T);
            } catch (parseError) {
              if (error) {
                return reject(
                  new Error(
                    `Command '${resolved.command} ${fullArgs.join(' ')}' failed: ${stderr || error.message}`
                  )
                );
              }
              return reject(
                new Error(
                  `Failed to parse JSON from '${resolved.command} ${fullArgs.join(' ')}': ${parseError instanceof Error ? parseError.message : String(parseError)}`
                )
              );
            }
          }

          if (error) {
            return reject(
              new Error(
                `Command '${resolved.command} ${fullArgs.join(' ')}' failed: ${stderr || error.message}`
              )
            );
          }

          reject(new Error(`Command '${resolved.command} ${fullArgs.join(' ')}' returned empty output`));
        }
      );
    });
  }

  /**
   * Retrieves the full curriculum list.
   */
  public async list(cwd?: string): Promise<ListResponse> {
    return this.executeJson<ListResponse>(['list'], cwd);
  }

  /**
   * Retrieves overall progress metrics.
   */
  public async progress(cwd?: string): Promise<ProgressResponse> {
    return this.executeJson<ProgressResponse>(['progress'], cwd);
  }

  /**
   * Runs an exercise.
   */
  public async run(exerciseName: string, cwd?: string): Promise<RunResponse> {
    return this.executeJson<RunResponse>(['run', exerciseName], cwd);
  }

  /**
   * Retrieves a hint for an exercise.
   */
  public async hint(exerciseName: string, level?: number, cwd?: string): Promise<HintResponse> {
    const args = ['hint', exerciseName];
    if (level !== undefined) {
      args.push('--level', String(level));
    }
    return this.executeJson<HintResponse>(args, cwd);
  }

  /**
   * Initializes exercises into the target workspace.
   */
  public async init(targetDir?: string, force: boolean = false): Promise<{ success: boolean; message: string }> {
    const finalDir = targetDir || getEffectiveWorkspaceRoot();
    if (finalDir && !fs.existsSync(finalDir)) {
      try {
        fs.mkdirSync(finalDir, { recursive: true });
      } catch {
        // ignore
      }
    }
    const executionCwd =
      finalDir && fs.existsSync(finalDir) && finalDir !== '/' && finalDir !== '\\'
        ? finalDir
        : os.homedir();

    const resolved = this.resolveCommand(executionCwd);
    const args = finalDir
      ? [...resolved.argsPrefix, 'init', '--dir', finalDir]
      : [...resolved.argsPrefix, 'init'];

    if (force) {
      args.push('--force');
    }

    return new Promise<{ success: boolean; message: string }>((resolve, reject) => {
      execFile(
        resolved.command,
        args,
        {
          cwd: executionCwd,
          maxBuffer: 5 * 1024 * 1024,
          timeout: 30000,
          env: this.getEnhancedEnv(),
        },
        (error, stdout, stderr) => {
          if (error && error.code !== 0) {
            return reject(
              new Error(
                stderr?.trim() ||
                  stdout?.trim() ||
                  `Command failed with code ${error.code}`
              )
            );
          }
          resolve({
            success: true,
            message: stdout?.trim() || 'Initialized exercises successfully.',
          });
        }
      );
    });
  }
}

export const cliBridge = new RaylingsCliBridge();
