from lean_dojo import LeanGitRepo, trace
from tqdm import tqdm
import jsonlines


def extract_mathlib4_theorems(commit_hash: str) -> None:
    """
    Extract mathlib4 theorems with a tactic proof and save to file.
    """
    mathlib4_repo = LeanGitRepo(
        "https://github.com/leanprover-community/mathlib4",
        commit_hash,
    )
    traced_mathlib4_repo = trace(mathlib4_repo)

    print("Extracting theorems...")
    extracted_theorems = []
    for thm in tqdm.tqdm(traced_mathlib4_repo.get_traced_theorems()):
        if not thm.has_tactic_proof():
            continue
        proof = thm.get_tactic_proof()
        if proof is None:
            continue
        theorem = thm.get_theorem_statement()
        extracted_theorems.append((theorem, proof))

    print(extract_mathlib4_theorems[0])
    print(f"{len(extracted_theorems)=}")

    print("Saving theorems to file...")
    with jsonlines.open("mathlib4_theorems.jsonl", "w") as writer:
        for thm in tqdm.tqdm(extracted_theorems):
            writer.write({"theorem": thm[0], "proof": thm[1]})


if __name__ == "__main__":
    extract_mathlib4_theorems("19210bcc58535416f6009c53089eeab4ef608b4d")
