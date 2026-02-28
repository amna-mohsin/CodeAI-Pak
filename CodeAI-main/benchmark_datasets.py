#benchmark_datasets.py

import argparse
import json
import os
import pathlib
import statistics
import tempfile
import time
from typing import Any, Dict, List, Optional

import requests

try:
    from datasets import load_dataset  # type: ignore
except Exception as e:  # pragma: no cover
    raise SystemExit("datasets package is required. Run: pip install datasets") from e


def write_file(path: pathlib.Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def post_file(server: str, file_path: pathlib.Path) -> Dict[str, Any]:
    with file_path.open("rb") as fh:
        resp = requests.post(
            f"{server}/analyze",
            files={"file": (file_path.name, fh, "text/plain")},
            timeout=120,
            headers={"Accept": "application/json"},
        )
    resp.raise_for_status()
    return resp.json()


def collect_metric(report: Dict[str, Any], key: str, default: float = 0.0) -> float:
    try:
        return float(report.get("report", {}).get("scores", {}).get(key, default))
    except Exception:
        return default


def run_python_samples(limit: int, uploads_dir: pathlib.Path, source: str = "humaneval", max_chars: Optional[int] = 1200) -> List[pathlib.Path]:
    paths: List[pathlib.Path] = []
    if limit <= 0:
        return paths
    if source == "humaneval":
        ds = load_dataset("openai_humaneval", split="test")
        prefix = "humaneval"
        candidates = ["canonical_solution", "completion", "prompt"]
    else:
        ds = load_dataset("mbpp", split="test")
        prefix = "mbpp"
        candidates = ["code", "code_solution", "text"]

    written = 0
    idx = 0
    for row in ds:
        code = ""
        for k in candidates:
            v = row.get(k)
            if isinstance(v, str) and v.strip():
                code = v
                break
        if not code.strip():
            continue
        if isinstance(max_chars, int) and max_chars > 0:
            code = code[:max_chars]
        p = uploads_dir / f"{prefix}_{idx}.py"
        write_file(p, code)
        paths.append(p)
        written += 1
        idx += 1
        if written >= limit:
            break
    return paths


def run_java_samples(
    limit: int,
    uploads_dir: pathlib.Path,
    max_chars: Optional[int] = 1200,
    clean_only: bool = False,
    wrap: bool = False,
) -> List[pathlib.Path]:
    paths: List[pathlib.Path] = []
    if limit <= 0:
        return paths
    # CodeXGLUE defect detection (Java) uses the default config
    ds = load_dataset("code_x_glue_cc_defect_detection", split="test")
    written = 0
    i = 0
    for row in ds:
        # Filter to clean (non-buggy) samples when requested
        if clean_only:
            # In CodeXGLUE defect detection, target==0 is clean, 1 is buggy
            if row.get("target") not in (0, "0"):
                continue
        code = row.get("func") or "public class Main { public static void main(String[] args){} }"
        if isinstance(max_chars, int) and max_chars > 0:
            code = code[:max_chars]
        if wrap and ("class " not in code and "interface " not in code):
            code = (
                "public class Main {\n"
                + code.rstrip()
                + "\n}"
            )
        p = uploads_dir / f"defect_{i}.java"
        write_file(p, str(code))
        paths.append(p)
        written += 1
        i += 1
        if written >= limit:
            break
    return paths


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark /analyze with HF datasets")
    parser.add_argument("--server", default="http://127.0.0.1:5000", help="Server base URL")
    parser.add_argument("--python-samples", type=int, default=1)
    parser.add_argument("--java-samples", type=int, default=1)
    parser.add_argument("--python-source", choices=["humaneval", "mbpp"], default="humaneval")
    parser.add_argument("--max-chars", type=int, default=1200)
    parser.add_argument("--java-clean-only", action="store_true", help="Use only clean (non-buggy) Java samples")
    parser.add_argument("--java-wrap", action="store_true", help="Wrap Java snippets without classes into a Main class")
    parser.add_argument("--out", default=str(pathlib.Path("uploads/benchmark_summary.json")))
    parser.add_argument("--skip-post", action="store_true", help="Only write local files, do not call the server")
    args = parser.parse_args()

    uploads_dir = pathlib.Path("uploads")
    uploads_dir.mkdir(exist_ok=True)

    files: List[pathlib.Path] = []
    files.extend(run_python_samples(args.python_samples, uploads_dir, source=args.python_source))
    files.extend(
        run_java_samples(
            args.java_samples,
            uploads_dir,
            max_chars=args.max_chars,
            clean_only=args.java_clean_only,
            wrap=args.java_wrap,
        )
    )

    results: List[Dict[str, Any]] = []
    if not args.skip_post:
        for fp in files:
            t0 = time.time()
            try:
                data = post_file(args.server, fp)
                elapsed = time.time() - t0
                report = data.get("report", {})
                scores = report.get("scores", {})
                results.append({
                    "file": fp.name,
                    "language": report.get("language"),
                    "overall": scores.get("overall"),
                    "review_score": scores.get("review_score"),
                    "test_score": scores.get("test_score"),
                    "doc_score": scores.get("doc_score"),
                    "ux_score": scores.get("ux_score"),
                    "bug_efficiency": scores.get("bug_analysis", {}).get("detection_efficiency"),
                    "quality_level": scores.get("quality_level") or report.get("quality_level"),
                    "elapsed_sec": round(elapsed, 2),
                })
            except Exception as e:  # pragma: no cover
                results.append({
                    "file": fp.name,
                    "error": str(e),
                })

    # Aggregate
    def safe_vals(k: str) -> List[float]:
        vals = []
        for r in results:
            v = r.get(k)
            if isinstance(v, (int, float)):
                vals.append(float(v))
        return vals

    summary = {
        "count": len(results),
        "avg_overall": round(statistics.fmean(safe_vals("overall")), 2) if safe_vals("overall") else 0,
        "avg_test_score": round(statistics.fmean(safe_vals("test_score")), 2) if safe_vals("test_score") else 0,
        "avg_doc_score": round(statistics.fmean(safe_vals("doc_score")), 2) if safe_vals("doc_score") else 0,
        "avg_review_score": round(statistics.fmean(safe_vals("review_score")), 2) if safe_vals("review_score") else 0,
        "avg_elapsed_sec": round(statistics.fmean(safe_vals("elapsed_sec")), 2) if safe_vals("elapsed_sec") else 0,
        "results": results,
    }

    out_path = pathlib.Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":  # pragma: no cover
    main()


