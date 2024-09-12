class ResultAggregator:
    def __init__(self):
        self.categories = {
            "Repository Management": [],
            "Source code structure and conventions": [],
            "Functional Requirements": [],
            "Security Requirements": [],
        }

    def add_result(self, catalog, result, message):
        if "repository_management" in catalog:
            self.categories["Repository Management"].append((result, message))
        elif "source_code_structure" in catalog:
            self.categories["Source code structure and conventions"].append(
                (result, message)
            )
        elif "functional_requirements" in catalog:
            self.categories["Functional Requirements"].append((result, message))
        elif "security_requirements" in catalog:
            self.categories["Security Requirements"].append((result, message))
        else:
            raise ValueError(f"Unknown category for validator: {catalog}")

    def generate_summary(self):
        summary = ["# AI Gallery Standard Validation: "]
        overall_passed = True

        for category, results in self.categories.items():
            if not results:
                continue
            summary.append(f"\n## {category}:")
            for result, message in results:
                overall_passed = overall_passed and result
                summary.append(message)

        summary[0] += "PASSED" if overall_passed else "FAILED"
        return "\n".join(summary)
