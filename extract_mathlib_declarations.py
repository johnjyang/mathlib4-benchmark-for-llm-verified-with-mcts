import jsonlines
import os
from dataclasses import dataclass
from typing import List


def read_jsonl_file(file_name: str):
    with jsonlines.open(file_name) as reader:
        return list(reader)


@dataclass
class Declaration:
    sourceLink: str
    name: str
    kind: str
    doc: str


@dataclass
class ModuleInstance:
    typeNames: List[str]
    name: str
    className: str


@dataclass
class Module:
    name: str
    instances: List[ModuleInstance]
    imports: List[str]
    declarations: List[Declaration]

    @classmethod
    def from_dict(cls, data):
        return cls(**data)


def parse_module_declarations(module: Module):
    declarations = []
    for declaration in module.declarations:
        declarations.append(declaration)
    return declarations


def parse_declarations_from_doc_directory(directory_path: str, output_file: str):
    if not os.path.exists(output_file):
        os.makedirs("/".join(output_file.split("/")[:-1]))
    with jsonlines.open(output_file, mode="w") as writer:
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                if not file_path.endswith(".jsonl"):
                    continue
                try:
                    module: Module = Module.from_dict(read_jsonl_file(file_path)[0])
                    parsed_declarations = parse_module_declarations(module)
                    for parsed_declaration in parsed_declarations:
                        writer.write(parsed_declaration)
                except Exception as e:
                    print(f"Error processing file {file_path}: {e}")


if __name__ == "__main__":
    parse_declarations_from_doc_directory(
        directory_path="mathlib4/.lake/build/doc/Mathlib",
        output_file="data/mathlib_declarations.jsonl",
    )
