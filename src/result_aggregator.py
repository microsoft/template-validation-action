from severity import Severity


class ResultAggregator:
    def __init__(self):
        self.categories = {
            "Repository Management": [],
            "Source code structure and conventions": [],
            "Functional Requirements": [],
            "Security Requirements": [],
        }

    def add_result(self, catalog, severity, result, message):
        if "repository_management" in catalog:
            self.categories["Repository Management"].append((severity, result, message))
        elif "source_code_structure" in catalog:
            self.categories["Source code structure and conventions"].append(
                (severity, result, message)
            )
        elif "functional_requirements" in catalog:
            self.categories["Functional Requirements"].append(
                (severity, result, message)
            )
        elif "security_requirements" in catalog:
            self.categories["Security Requirements"].append((severity, result, message))
        else:
            raise ValueError(f"Unknown category for validator: {catalog}")

    def generate_summary(self):
        summary = ["# AI Gallery Standard Validation: "]
        overall_passed = True
        overall_severity = Severity.LOW

        for category, results in self.categories.items():
            if not results:
                continue
            summary.append(f"\n## {category}:")
            for severity, result, message in results:
                overall_passed = overall_passed and result
                overall_severity = (
                    overall_severity if result else max(overall_severity, severity)
                )
                summary.append(message)

        summary[0] += (
            "CONFORMING"
            if overall_passed
            else f"NON-CONFORMING, Severity: {Severity.to_string(overall_severity)}"
        )
        return "\n".join(summary)
