#!/usr/bin/env python3
import argparse, csv, json, random, re, sys
from pathlib import Path

REQUIRED_COLS = {"user input template"}
SUPPORTED_PLACEHOLDERS = {"company", "ceo", "competitor", "individual"}
PLACEHOLDER_RE = re.compile(r"<([a-zA-Z0-9_]+)>")

def load_config(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    except FileNotFoundError:
        sys.exit(f"Config not found: {path}. Copy config.example.json to config.json and edit it.")
    except json.JSONDecodeError as e:
        sys.exit(f"Invalid JSON in {path}: {e}")

    missing = [k for k in ["company", "ceo", "competitors", "individuals"] if k not in cfg]
    if missing:
        sys.exit(f"Config missing keys: {', '.join(missing)}")

    if not isinstance(cfg["competitors"], list) or len(cfg["competitors"]) == 0:
        sys.exit("Config 'competitors' must be a non-empty list.")
    if not isinstance(cfg["individuals"], list) or len(cfg["individuals"]) == 0:
        sys.exit("Config 'individuals' must be a non-empty list.")

    return cfg

def substitute(template, cfg):
    def pick(lst): return random.choice(lst)

    def repl(m):
        key = m.group(1)
        if key not in SUPPORTED_PLACEHOLDERS:
            raise KeyError(f"Unsupported placeholder <{key}>")
        if key == "company":    return str(cfg["company"])
        if key == "ceo":        return str(cfg["ceo"])
        if key == "competitor": return str(pick(cfg["competitors"]))
        if key == "individual": return str(pick(cfg["individuals"]))
        return m.group(0)

    return PLACEHOLDER_RE.sub(repl, template)

def main():
    ap = argparse.ArgumentParser(description="Populate prompts CSV using config values.")
    ap.add_argument("--templates", default="brand_safety_templates.csv",
                    help="Path to the source templates CSV (default: brand_safety_templates.csv).")
    ap.add_argument("--config", default="config.json", help="Path to the config JSON.")
    ap.add_argument("--out", default="out/populated.csv", help="Output CSV path.")
    ap.add_argument("--seed", type=int, default=None, help="Optional random seed for reproducible picks.")
    args = ap.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    cfg = load_config(args.config)

    in_path = Path(args.templates)
    if not in_path.exists():
        sys.exit(f"Templates CSV not found: {in_path}")

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with open(in_path, "r", encoding="utf-8-sig", newline="") as fin:
        reader = csv.DictReader(fin)
        if not reader.fieldnames:
            sys.exit("CSV header missing.")
        missing_cols = [c for c in REQUIRED_COLS if c not in reader.fieldnames]
        if missing_cols:
            sys.exit(f"CSV missing required columns: {', '.join(missing_cols)}")

        out_fieldnames = list(reader.fieldnames)
        gen_col = "generated user input"
        if gen_col not in out_fieldnames:
            out_fieldnames.insert(out_fieldnames.index("user input template") + 1, gen_col)

        rows_out = []
        for i, row in enumerate(reader, start=1):
            tpl = row.get("user input template", "").strip()
            if not tpl:
                sys.exit(f"Row {i}: 'user input template' is empty.")

            for ph in set(PLACEHOLDER_RE.findall(tpl)):
                if ph not in SUPPORTED_PLACEHOLDERS:
                    sys.exit(f"Row {i}: Unsupported placeholder <{ph}> in template:\n  {tpl}")

            generated = substitute(tpl, cfg)
            row[gen_col] = generated
            rows_out.append(row)

    with open(out_path, "w", encoding="utf-8", newline="") as fout:
        writer = csv.DictWriter(fout, fieldnames=out_fieldnames)
        writer.writeheader()
        writer.writerows(rows_out)

    print(f"Wrote {len(rows_out)} rows → {out_path}")

if __name__ == "__main__":
    main()