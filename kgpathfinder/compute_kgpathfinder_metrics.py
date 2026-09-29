import csv
import re

CSV_PATH = "./data/TRIPLET EXTRACTION PROMPTS - Sheet2.csv"

RESPONSE_COLS = {
    "Prompt A": "Response for A",
    "Prompt B": "Response for B",
    "Prompt C": "Response for C",
}

def parse_response(text):
    """
    Parse a KGPathFinder response block.
    Returns:
      - total_triplets: number of summary triplets found in the block
      - resolved: number of triplets that had at least one path
      - zero_path: number of triplets with no path
      - semantic_confidences: list of confidence scores for semantic_match paths
    """
    if not text or not text.strip():
        return 0, 0, 0, []

    # Split into per-triplet blocks by the "Summary Triplet:" marker
    blocks = re.split(r"Summary Triplet:", text)
    blocks = [b.strip() for b in blocks if b.strip()]

    total_triplets = 0
    resolved = 0
    zero_path = 0
    semantic_confidences = []

    for block in blocks:
        total_triplets += 1

        if "No supporting paths found." in block:
            zero_path += 1
        else:
            resolved += 1

        # Extract all semantic_match confidence values in this block
        for match in re.finditer(
            r"Type:\s*semantic_match,\s*Confidence:\s*([0-9.]+)", block
        ):
            semantic_confidences.append(float(match.group(1)))

    return total_triplets, resolved, zero_path, semantic_confidences


def compute_metrics(responses):
    """
    Given a list of response strings for one prompt,
    compute aggregate metrics.
    """
    total_triplets = 0
    total_resolved = 0
    total_zero = 0
    all_sem_confs = []

    for r in responses:
        t, res, z, confs = parse_response(r)
        total_triplets += t
        total_resolved += res
        total_zero += z
        all_sem_confs.extend(confs)

    if total_triplets == 0:
        return {"path_coverage": 0, "zero_path_rate": 0,
                "mean_sem_conf": 0, "total_triplets": 0,
                "resolved": 0, "zero_path": 0,
                "sem_match_count": 0}

    path_coverage = (total_resolved / total_triplets) * 100
    zero_path_rate = (total_zero / total_triplets) * 100
    mean_sem_conf = (sum(all_sem_confs) / len(all_sem_confs)
                     if all_sem_confs else 0)

    return {
        "path_coverage": round(path_coverage, 1),
        "zero_path_rate": round(zero_path_rate, 1),
        "mean_sem_conf": round(mean_sem_conf, 4),
        "total_triplets": total_triplets,
        "resolved": total_resolved,
        "zero_path": total_zero,
        "sem_match_count": len(all_sem_confs),
    }


# --- Load CSV ---
prompt_responses = {k: [] for k in RESPONSE_COLS}

with open(CSV_PATH, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        for prompt_name, col_name in RESPONSE_COLS.items():
            val = row.get(col_name, "").strip()
            if val:
                prompt_responses[prompt_name].append(val)

# --- Compute and print ---
print("=" * 65)
print(f"{'Metric':<35} {'Prompt A':>8} {'Prompt B':>8} {'Prompt C':>8}")
print("=" * 65)

results = {}
for prompt, col in RESPONSE_COLS.items():
    results[prompt] = compute_metrics(prompt_responses[prompt])

metrics = [
    ("Total summary triplets evaluated", "total_triplets"),
    ("Triplets with paths (resolved)", "resolved"),
    ("Triplets with no path (zero-path)", "zero_path"),
    ("Path Coverage Rate (%)", "path_coverage"),
    ("Zero-Path Rate (%)", "zero_path_rate"),
    ("Semantic match paths found", "sem_match_count"),
    ("Mean Semantic Match Confidence", "mean_sem_conf"),
]

for label, key in metrics:
    a = results["Prompt A"][key]
    b = results["Prompt B"][key]
    c = results["Prompt C"][key]
    print(f"{label:<35} {str(a):>8} {str(b):>8} {str(c):>8}")

print("=" * 65)

# --- Per-example breakdown ---
print("\n--- Per document-pair breakdown ---\n")
with open(CSV_PATH, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader):
        text_snippet = row.get("Text", "")[:60].replace("\n", " ")
        print(f"Doc {i+1}: {text_snippet}...")
        for prompt_name, col_name in RESPONSE_COLS.items():
            val = row.get(col_name, "").strip()
            if not val:
                continue
            t, res, z, confs = parse_response(val)
            cov = round((res / t * 100), 1) if t > 0 else 0
            mean_c = round(sum(confs)/len(confs), 4) if confs else "N/A"
            print(f"  {prompt_name}: {res}/{t} resolved "
                  f"({cov}% coverage) | "
                  f"sem_match confidence mean: {mean_c}")
        print()

        