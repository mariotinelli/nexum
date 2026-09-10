import copy
import unittest
from pathlib import Path

from render_publication import build_payload, check_projection, sections, split_managed


class RenderPublicationTest(unittest.TestCase):
    def document(self, kind="Feature"):
        template = Path(__file__).parent.parent / "templates" / f"{kind.lower()}.md"
        return "# Exemplo\n\nIssue: #42. Proposta.\n\n" + "\n\n".join(
            f"## {name}\n\n" + ("R1. Conta ativa.\n\nR2. Somente dados próprios." if name == "Regras de negócio" else
            "CA1 — Com conta ativa, ao abrir, mostrar dados. [R1]\n\nCA2 — Ao abrir dados alheios, recusar. [R2]" if name == "Critérios de aceite" else
            "Conteúdo aprovado com ação, condição e resultado.")
            for name, _ in sections(template.read_text(encoding="utf-8")))

    def setUp(self):
        self.before = {"id": 42, "subject": "Exemplo", "description": "Nota humana\r\n<!-- project-flow:start -->antigo<!-- project-flow:end -->\r\nOutra nota", "status": "New"}
        self.path = "docs/harness/features/42-exemplo/feature.md"

    def rendered(self, document=None, kind="Feature"):
        document = document or self.document(kind)
        payload = build_payload(document, kind, self.path, "Revisor", self.before)
        current = copy.deepcopy(self.before)
        current.update(payload["changes"])
        return document, payload, current

    def test_preserves_rules_criteria_and_unmanaged_bytes_without_status_changes(self):
        document, payload, current = self.rendered()
        check_projection(document, "Feature", self.path, "Revisor", self.before, current)
        self.assertEqual(set(payload["changes"]), {"description"})
        self.assertTrue(current["description"].startswith("Nota humana\r\n"))
        self.assertTrue(current["description"].endswith("\r\nOutra nota"))
        self.assertIn("CA2 — Ao abrir dados alheios, recusar. [R2]", current["description"])
        self.assertNotIn("Issue: #42", current["description"])
        self.assertNotIn("Designs e evidências", current["description"])

    def test_rejects_omitted_merged_renumbered_or_changed_acceptance(self):
        document, _, current = self.rendered()
        for replacement in ("", "Critérios resumidos.", "CA3 — Ao abrir dados alheios, recusar. [R2]", "CA2 — Ao abrir dados alheios, permitir. [R2]"):
            with self.subTest(replacement=replacement):
                altered = copy.deepcopy(current)
                altered["description"] = altered["description"].replace("CA2 — Ao abrir dados alheios, recusar. [R2]", replacement)
                with self.assertRaises(ValueError):
                    check_projection(document, "Feature", self.path, "Revisor", self.before, altered)

    def test_rejects_changed_unmanaged_content(self):
        document, _, current = self.rendered()
        current["description"] = current["description"].replace("Nota humana", "Alterada")
        with self.assertRaises(ValueError):
            check_projection(document, "Feature", self.path, "Revisor", self.before, current)

    def test_rejects_unaccounted_text_before_sections_or_in_footer(self):
        document, _, current = self.rendered()
        for description in (current["description"].replace("<!-- project-flow:start -->", "<!-- project-flow:start -->Regra escondida.\n"), current["description"].replace("<!-- project-flow:end -->", "Regra escondida.\n<!-- project-flow:end -->")):
            with self.subTest(description=description), self.assertRaises(ValueError):
                check_projection(document, "Feature", self.path, "Revisor", self.before, {**current, "description": description})
        with self.assertRaises(ValueError):
            self.rendered(document.replace("Issue: #42. Proposta.", "Comportamento que seria perdido."))

    def test_bug_retains_evidence_and_correction_criteria(self):
        document, _, current = self.rendered(kind="Bug")
        check_projection(document, "Bug", self.path, "Revisor", self.before, current)
        self.assertIn("## Evidências", current["description"])
        self.assertIn("## Critérios de correção", current["description"])
        self.assertNotIn("## Histórias de usuário", current["description"])

    def test_rejects_missing_empty_and_duplicate_canonical_sections(self):
        document = self.document()
        for altered in (document.replace("## Objetivo", "## Outro"), document + "\n## Objetivo\nDuplicado", document.replace("## Objetivo\n\nConteúdo aprovado com ação, condição e resultado.", "## Objetivo\n")):
            with self.subTest(document=altered):
                with self.assertRaises(ValueError):
                    self.rendered(altered)

    def test_fenced_headings_remain_part_of_the_approved_body(self):
        document = self.document().replace("R1. Conta ativa.", "R1. Conta ativa.\n\n```text\n## Exemplo interno\n```\n")
        _, _, current = self.rendered(document)
        check_projection(document, "Feature", self.path, "Revisor", self.before, current)
        self.assertIn("## Exemplo interno", current["description"])

    def test_crlf_managed_body_and_existing_footer_wording_are_accepted(self):
        document, _, current = self.rendered()
        prefix, managed, suffix = split_managed(current["description"])
        managed = managed.replace(f"Documento aprovado por Revisor: {self.path}", f"Documento aprovado: {self.path}\n\nRequisito aprovado por Revisor.").replace("\n", "\r\n")
        current["description"] = prefix + "<!-- project-flow:start -->" + managed + "<!-- project-flow:end -->" + suffix
        check_projection(document, "Feature", self.path, "Revisor", self.before, current)

    def test_rejects_ambiguous_delimiters_and_wrong_title(self):
        for description in ("sem marcadores", "<!-- project-flow:end --><!-- project-flow:start -->", "<!-- project-flow:start --><!-- project-flow:start --><!-- project-flow:end -->"):
            with self.subTest(description=description), self.assertRaises(ValueError):
                split_managed(description)
        self.before["subject"] = "Outra issue"
        with self.assertRaises(ValueError):
            self.rendered()


if __name__ == "__main__":
    unittest.main()
