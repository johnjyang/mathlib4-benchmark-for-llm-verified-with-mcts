import jsonlines
from pathlib import Path
import os
from dataclasses import dataclass
from typing import List
import re
from tqdm import tqdm


def read_jsonl_file(file_name: str) -> List:
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
        instances = [
            ModuleInstance(**instance_data)
            for instance_data in data.get("instances", [])
        ]
        declarations = [
            Declaration(**declaration_data)
            for declaration_data in data.get("declarations", [])
        ]
        return cls(
            name=data.get("name"),
            instances=instances,
            imports=data.get("imports", []),
            declarations=declarations,
        )


@dataclass
class ParsedDeclaration:
    modulePath: str
    moduleImports: List[str]
    moduleDocstring: str
    declarationName: str
    declarationKind: str
    declarationDocstring: str
    declarationCode: str
    declarationSourceLink: str
    commitHash: str

    @classmethod
    def from_dict(cls, data):
        return cls(
            modulePath=data.get("modulePath"),
            moduleImports=data.get("moduleImports", []),
            moduleDocstring=data.get("moduleDocstring", ""),
            declarationName=data.get("declarationName"),
            declarationKind=data.get("declarationKind"),
            declarationDocstring=data.get("declarationDocstring", ""),
            declarationCode=data.get("declarationCode"),
            declarationSourceLink=data.get("declarationSourceLink"),
            commitHash=data.get("commitHash"),
        )


def remove_nested_declarations(
    all_pos: List[List[int]], parsed_declarations: List[ParsedDeclaration]
) -> List[ParsedDeclaration]:
    no_nested_declarations = []
    for parsed_declaration in parsed_declarations:
        parsed_pos = [
            int(p)
            for p in parsed_declaration.declarationSourceLink.split("#L")[-1].split(
                "-L"
            )
        ]
        nested = False
        for pos in all_pos:
            if (
                parsed_pos != pos
                and parsed_pos[0] >= pos[0]
                and parsed_pos[1] <= pos[1]
            ):
                nested = True
                break
        if not nested:
            no_nested_declarations.append(parsed_declaration)
    return no_nested_declarations


def parse_module_declarations(
    module: Module, module_path: str, mathlib_source_code: str
) -> List[ParsedDeclaration]:
    parsed_declarations = []
    all_pos = []
    for declaration in module.declarations:
        module_docstring = re.findall(r"/-!(.*?)-/", mathlib_source_code, re.DOTALL)
        if module_docstring:
            module_docstring = module_docstring[0].strip()
        else:
            module_docstring = ""
        if "//" in declaration.sourceLink:
            source_link = declaration.sourceLink.replace("//", "/")
        else:
            source_link = declaration.sourceLink
        pos = [int(p) for p in declaration.sourceLink.split("#L")[-1].split("-L")]
        all_pos.append(pos)
        source_code_lines = mathlib_source_code.split("\n")
        if pos[0] == pos[1]:
            declaration_code = "\n".join(source_code_lines[pos[0] - 1])
        else:
            declaration_code = "\n".join(source_code_lines[pos[0] - 1 : pos[1]])
        commit_hash = declaration.sourceLink.split("blob/")[1].split("/")[0]
        parsed_declaration = ParsedDeclaration.from_dict(
            {
                "modulePath": module_path.strip(),
                "moduleImports": module.imports,
                "moduleDocstring": module_docstring.strip(),
                "declarationName": declaration.name.strip(),
                "declarationKind": declaration.kind.strip(),
                "declarationDocstring": declaration.doc.strip(),
                "declarationCode": declaration_code.strip(),
                "declarationSourceLink": source_link.strip(),
                "commitHash": commit_hash.strip(),
            }
        )
        parsed_declarations.append(parsed_declaration)
    parsed_declarations = remove_nested_declarations(all_pos, parsed_declarations)
    return parsed_declarations


def parse_declarations_from_doc_directory(
    source_code_path: str, doc_directory: str, output_file: str
) -> None:
    print("Parsing source code...")
    if not os.path.exists("data/mathlib4_source_code.jsonl"):
        os.mkdir("data")
        with jsonlines.open("data/mathlib4_source_code.jsonl", mode="w") as writer:
            for root, dirs, files in os.walk(source_code_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    if not file_path.endswith(".lean"):
                        continue
                    try:
                        with open(file_path, "r") as f:
                            source_code = f.read()
                        writer.write({"path": file_path, "source_code": source_code})
                    except Exception as e:
                        print(f"Error reading file {file_path}: {e}")
    mathlib4_code = read_jsonl_file("data/mathlib4_source_code.jsonl")
    print("Parsing declarations...")
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    with jsonlines.open(output_file, mode="w") as writer:
        for root, dirs, files in os.walk(doc_directory):
            for file in tqdm(files):
                file_path = os.path.join(root, file)
                if not file_path.endswith(".jsonl"):
                    continue
                try:
                    module: Module = Module.from_dict(read_jsonl_file(file_path)[0])
                    if not module.declarations:
                        continue
                    module_path = (
                        module.declarations[0].sourceLink.split("//")[-1].split("#")[0]
                    )
                    for source_code_file in mathlib4_code:
                        if source_code_file["path"].endswith(module_path):
                            module_path = source_code_file["path"]
                            source_code = source_code_file["source_code"]
                            break
                    parsed_declarations = parse_module_declarations(
                        module, module_path, source_code
                    )
                    for parsed_declaration in parsed_declarations:
                        writer.write(parsed_declaration.__dict__)
                except Exception as e:
                    print(f"Error processing file {file_path}: {e}")


if __name__ == "__main__":
    parse_declarations_from_doc_directory(
        source_code_path="mathlib4/Mathlib",
        doc_directory="mathlib4/.lake/build/doc/Mathlib",
        output_file="data/Mathlib_declarations.jsonl",
    )
    parsed_declarations = read_jsonl_file("data/Mathlib_declarations.jsonl")
    assert len(parsed_declarations) == 166240
