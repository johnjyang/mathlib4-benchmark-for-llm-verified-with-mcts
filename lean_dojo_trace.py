from lean_dojo import LeanGitRepo, trace
import tqdm
import jsonlines
import os

os.environ["VERBOSE"] = "1"


def trace_mathlib4_theorems(commit_hash: str) -> None:
    """
    Extract mathlib4 theorems with a tactic proof and save to file.
    """
    mathlib4_repo = LeanGitRepo(
        "https://github.com/leanprover-community/mathlib4",
        commit_hash,
    )
    traced_mathlib4_repo = trace(mathlib4_repo, "traced_mathlib4")

    print("Outputting traced theorems...")
    extracted_theorems = []
    for thm in tqdm.tqdm(traced_mathlib4_repo.get_traced_theorems()):
        if not thm.has_tactic_proof():
            continue
        proof = thm.get_tactic_proof()
        if proof is None:
            continue
        theorem = thm.get_theorem_statement()
        extracted_theorems.append((theorem, proof))

    print(trace_mathlib4_theorems[0])
    print(f"{len(extracted_theorems)=}")

    print("Saving theorems to file...")
    with jsonlines.open("mathlib4_theorems.jsonl", "w") as writer:
        for thm in tqdm.tqdm(extracted_theorems):
            writer.write({"theorem": thm[0], "proof": thm[1]})


if __name__ == "__main__":
    trace_mathlib4_theorems("84c26b211afbd8ae411c6f7cb9458f5a6e44ca0a")
