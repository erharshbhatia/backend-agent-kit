"""Custom import-linter contract types (configured in `.importlinter`).

- `protected_if_present`: import-linter's `protected` contract, except that a protected module
  (or allowed importer) not yet in the import graph does not abort the run. Vendor packages
  such as `psycopg` enter the graph only once a scanned module imports them directly.
- `forbidden_if_present`: import-linter's `forbidden` contract, except that external forbidden
  packages not yet in the graph (e.g. `httpx` before anything uses it) are skipped.
- `vendor_subpackage`: "`<package>.<subpackage>` may be imported only by these modules".
  Grimp squashes every external package to its top-level name (`google.genai` and
  `google.cloud` are both `google`); this contract reads the import statements to tell them
  apart.
"""

import re
from typing import cast

import grimp
from importlinter import Contract, ContractCheck, fields, output
from importlinter.contracts.forbidden import ForbiddenContract
from importlinter.contracts.protected import ProtectedContract
from importlinter.domain.imports import ModuleExpression


class PresentOnlyProtectedContract(ProtectedContract):
    type_name = "protected_if_present"

    @classmethod
    def _get_field_names(cls) -> list[str]:
        # import-linter discovers fields in the class's own __dict__ only.
        return ProtectedContract._get_field_names()

    def check(self, graph: grimp.ImportGraph, verbose: bool) -> ContractCheck:
        # The graph passed in is a copy (import-linter contract API), so adding absent
        # modules is safe: nothing imports them, so nothing can break because of them.
        # import-linter declares fields as class-level Field objects; instances hold values.
        protected = cast(list[ModuleExpression], self.protected_modules)
        allowed = cast(list[ModuleExpression], self.allowed_importers)
        for expression in protected:
            _ensure_module(graph, expression, is_squashed=True)
        for expression in allowed:
            _ensure_module(graph, expression, is_squashed=False)
        return super().check(graph, verbose)


class PresentOnlyForbiddenContract(ForbiddenContract):
    type_name = "forbidden_if_present"

    @classmethod
    def _get_field_names(cls) -> list[str]:
        return ForbiddenContract._get_field_names()

    def check(self, graph: grimp.ImportGraph, verbose: bool) -> ContractCheck:
        # Absent externals are added as empty squashed modules (the graph is a copy); a
        # misspelt internal module still fails, because its root package is not squashed.
        for expression in cast(set[ModuleExpression], self.forbidden_modules):
            root = expression.expression.split(".")[0]
            if expression.expression not in graph.modules and root not in graph.modules:
                graph.add_module(expression.expression, is_squashed=True)
        return super().check(graph, verbose)


class VendorSubpackageContract(Contract):
    type_name = "vendor_subpackage"

    package = fields.StringField()
    subpackage = fields.StringField()
    allowed_importers = fields.ListField(subfield=fields.StringField())

    def check(self, graph: grimp.ImportGraph, verbose: bool) -> ContractCheck:
        package = cast(str, self.package)
        subpackage = cast(str, self.subpackage)
        allowed = cast(list[str], self.allowed_importers)
        illegal: list[str] = []
        if package in graph.modules:
            pattern = _reference_pattern(package, subpackage)
            for importer in sorted(graph.find_modules_that_directly_import(package)):
                if importer in allowed:
                    continue
                for detail in graph.get_import_details(importer=importer, imported=package):
                    if pattern.search(detail["line_contents"]):
                        illegal.append(
                            f"{importer} -> {package}.{subpackage} (l.{detail['line_number']})"
                        )
        return ContractCheck(kept=not illegal, warnings=[], metadata={"illegal": illegal})

    def render_broken_contract(self, check: ContractCheck) -> None:
        for line in check.metadata["illegal"]:
            output.print_error(f"- {line}", bold=False)
            output.new_line()


def _ensure_module(
    graph: grimp.ImportGraph, expression: ModuleExpression, *, is_squashed: bool
) -> None:
    name = expression.expression
    if not expression.has_wildcard_expression() and name not in graph.modules:
        graph.add_module(name, is_squashed=is_squashed)


def _reference_pattern(package: str, subpackage: str) -> re.Pattern[str]:
    dotted = re.escape(f"{package}.{subpackage}")
    from_import = rf"from\s+{re.escape(package)}\s+import\s+.*\b{re.escape(subpackage)}\b"
    return re.compile(rf"\b{dotted}\b|{from_import}")
