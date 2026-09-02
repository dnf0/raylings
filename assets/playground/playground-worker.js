/**
 * Web Worker for Raylings Pyodide WebAssembly Runtime.
 *
 * Runs Pyodide v0.26+ in a background Web Worker, loads in-memory Ray simulation
 * engine (raylings.wasm_compat), and provides a sandboxed execution environment
 * with captured stdout/stderr, cluster diagnostics, and millisecond-level timing.
 */

/* global loadPyodide, importScripts */
importScripts("https://cdn.jsdelivr.net/pyodide/v0.26.2/full/pyodide.js");

let pyodide = null;
let bundleData = null;

/**
 * Initialize Pyodide WebAssembly runtime and mount Raylings virtual modules.
 * @param {Object} bundle - Playground bundle containing wasm_compat_code.
 */
async function initPyodide(bundle) {
  bundleData = bundle;
  self.postMessage({
    type: "STATUS",
    stage: "loading_pyodide",
    message: "⚡ Initializing Python WebAssembly Runtime..."
  });

  pyodide = await loadPyodide({
    indexURL: "https://cdn.jsdelivr.net/pyodide/v0.26.2/full/"
  });

  self.postMessage({
    type: "STATUS",
    stage: "mounting_bundle",
    message: "🔧 Mounting Raylings WASM Simulation Engine..."
  });

  // Create /lib/raylings virtual package in Pyodide FS
  pyodide.FS.mkdirTree("/lib/raylings");
  pyodide.FS.writeFile("/lib/raylings/__init__.py", "from .wasm_compat import ray, ActorPool\n__version__ = '0.1.0'\n");
  pyodide.FS.writeFile("/lib/raylings/wasm_compat.py", (bundle && bundle.wasm_compat_code) || "");

  // Setup sys.path and in-memory evaluation harness
  await pyodide.runPythonAsync(`
import os
import sys
import io
import time
import types
import traceback

if "/lib" not in sys.path:
    sys.path.insert(0, "/lib")

import raylings.wasm_compat as wasm_compat
from raylings.wasm_compat import ray, ActorPool, WasmObjectRef

# Inject ray and submodules into sys.modules so 'import ray' works seamlessly
sys.modules["ray"] = ray
actor_pool_mod = types.ModuleType("ray.util.actor_pool")
actor_pool_mod.ActorPool = ActorPool
sys.modules["ray.util.actor_pool"] = actor_pool_mod
data_mod = types.ModuleType("ray.data")
data_mod.Dataset = wasm_compat.WasmDataset
data_mod.from_items = wasm_compat.from_items
data_mod.range = wasm_compat.range_dataset
sys.modules["ray.data"] = data_mod

INCOMPLETE_MARKERS = (
    "???",
    "___",
    "/* ??? */",
    "<!-- ANSWER -->",
    "I AM NOT DONE",
)

def run_exercise_eval(exercise_id, code_str, filename="exercise.py"):
    start_time = time.perf_counter()
    stdout_buf = io.StringIO()
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = stdout_buf
    sys.stderr = stdout_buf

    try:
        # 1. Check placeholder markers
        for marker in INCOMPLETE_MARKERS:
            if marker in code_str:
                duration = (time.perf_counter() - start_time) * 1000.0
                return {
                    "passed": False,
                    "error": f"Exercise still contains incomplete placeholder marker '{marker}'. Complete the code to proceed.",
                    "output": stdout_buf.getvalue(),
                    "durationMs": round(duration, 2),
                    "clusterState": ray._get_cluster_stats(),
                }

        # 2. Reset simulated Ray cluster state
        ray.shutdown()
        ray.init(ignore_reinit_error=True)

        # 3. Execute exercise in isolated namespace
        global_env = {
            "__name__": "__main__",
            "__file__": filename,
            "ray": ray,
            "ActorPool": ActorPool,
        }
        exec(code_str, global_env)

        # 4. If verify() is defined, call it
        if "verify" in global_env and callable(global_env["verify"]):
            global_env["verify"]()
        elif "main" in global_env and callable(global_env["main"]):
            global_env["main"]()

        duration = (time.perf_counter() - start_time) * 1000.0
        output_str = stdout_buf.getvalue()
        cluster_stats = ray._get_cluster_stats()

        return {
            "passed": True,
            "error": None,
            "output": output_str if output_str else f"✓ Exercise '{exercise_id}' executed and verified successfully!",
            "durationMs": round(duration, 2),
            "clusterState": cluster_stats,
        }

    except NotImplementedError as exc:
        duration = (time.perf_counter() - start_time) * 1000.0
        return {
            "passed": False,
            "error": f"NotImplementedError: {exc or 'Function not implemented yet.'}",
            "output": stdout_buf.getvalue(),
            "durationMs": round(duration, 2),
            "clusterState": ray._get_cluster_stats(),
        }
    except AssertionError as exc:
        duration = (time.perf_counter() - start_time) * 1000.0
        return {
            "passed": False,
            "error": f"AssertionError: {exc or 'Verification assertion failed'}",
            "output": stdout_buf.getvalue(),
            "durationMs": round(duration, 2),
            "clusterState": ray._get_cluster_stats(),
        }
    except BaseException as exc:
        duration = (time.perf_counter() - start_time) * 1000.0
        tb = traceback.format_exc()
        return {
            "passed": False,
            "error": f"{type(exc).__name__}: {exc}",
            "traceback": tb,
            "output": stdout_buf.getvalue(),
            "durationMs": round(duration, 2),
            "clusterState": ray._get_cluster_stats(),
        }
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr
`);

  self.postMessage({
    type: "STATUS",
    stage: "ready",
    message: "✅ Ready! Python 3.12 Ray WebAssembly loaded."
  });
}

self.onmessage = async function(e) {
  const msg = e.data;
  if (!msg || !msg.type) return;

  if (msg.type === "INIT") {
    try {
      await initPyodide(msg.bundle || {});
    } catch (err) {
      self.postMessage({
        type: "STATUS",
        stage: "error",
        message: "Error initializing Pyodide: " + (err && err.message ? err.message : String(err))
      });
    }
  } else if (msg.type === "RUN_EXERCISE") {
    if (!pyodide) {
      self.postMessage({
        type: "RUN_RESULT",
        exerciseId: msg.exerciseId,
        passed: false,
        error: "Pyodide WebAssembly runtime is still initializing...",
        output: "",
        durationMs: 0
      });
      return;
    }

    let resProxy = null;
    try {
      pyodide.globals.set("temp_exercise_id", msg.exerciseId || "");
      pyodide.globals.set("temp_code_str", msg.code || "");
      pyodide.globals.set("temp_filename", msg.filename || "exercise.py");

      resProxy = await pyodide.runPythonAsync("run_exercise_eval(temp_exercise_id, temp_code_str, temp_filename)");
      const resultObj = resProxy.toJs({ dict_converter: Object.fromEntries });

      self.postMessage({
        type: "RUN_RESULT",
        exerciseId: msg.exerciseId,
        output: "",
        ...resultObj
      });
    } catch (err) {
      self.postMessage({
        type: "RUN_RESULT",
        exerciseId: msg.exerciseId,
        passed: false,
        error: "Execution Error: " + (err && err.message ? err.message : String(err)),
        output: "",
        durationMs: 0
      });
    } finally {
      if (resProxy && typeof resProxy.destroy === "function") {
        resProxy.destroy();
      }
    }
  }
};
