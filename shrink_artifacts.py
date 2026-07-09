"""
shrink_artifacts.py
-------------------
One-time helper: shrinks the two big model files so the backend fits in a
512 MB free-tier server (e.g. Render Free).

The two big matrices hold cosine-similarity values (always between -1 and 1),
so storing them in float16 instead of float64 keeps ~3 decimal digits of
precision -- more than enough for ranking -- while cutting memory roughly 4x.

Reads from   artifacts/
Writes to    artifacts_slim/   (originals are left untouched)

Run it once:
    python shrink_artifacts.py
Then, when you're happy with it, replace the big files:
    (Windows PowerShell)
    Copy-Item artifacts_slim\* artifacts\ -Force
"""
import os
import pickle
import shutil
import numpy as np

SRC = "artifacts"
DST = "artifacts_slim"
os.makedirs(DST, exist_ok=True)


def mb(path):
    return f"{os.path.getsize(path) / 1e6:.1f} MB"


# --- 1. Content similarity: dense float64 matrix -> float16 ------------------
with open(os.path.join(SRC, "similarity.pkl"), "rb") as f:
    sim = pickle.load(f)
sim = np.asarray(sim).astype(np.float16)
with open(os.path.join(DST, "similarity.pkl"), "wb") as f:
    pickle.dump(sim, f, protocol=4)
print("similarity.pkl   :", mb(os.path.join(SRC, "similarity.pkl")),
      "->", mb(os.path.join(DST, "similarity.pkl")))

# --- 2. Collaborative similarity: sparse CSR float64 -> float16 --------------
loaded = np.load(os.path.join(SRC, "movie_similarity.npy"), allow_pickle=True)
csr = loaded.item() if loaded.ndim == 0 else loaded
# scipy sparse can't hold float16, so float32 is the smallest safe choice here.
csr = csr.astype(np.float32)          # only the .data array shrinks; indices stay int32
# save back in the exact same 0-d object-array wrapper main.py expects
wrapper = np.empty((), dtype=object)
wrapper[()] = csr
np.save(os.path.join(DST, "movie_similarity.npy"), wrapper, allow_pickle=True)
print("movie_similarity :", mb(os.path.join(SRC, "movie_similarity.npy")),
      "->", mb(os.path.join(DST, "movie_similarity.npy")))

# --- 3. Small files: copy across unchanged ----------------------------------
for name in ("movies_df.pkl", "tmdb_to_ml.pkl", "movie_id_search.pkl", "trending.pkl"):
    src = os.path.join(SRC, name)
    if os.path.exists(src):
        shutil.copy2(src, os.path.join(DST, name))
        print(f"copied {name}")

print("\nDone. Slim artifacts are in ./artifacts_slim/")
