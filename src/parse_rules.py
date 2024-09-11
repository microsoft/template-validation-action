import json
import os
from validator.file_validator import FileValidator
from validator.azd_validator import AzdValidator
# from validator.msdo_validator import MsdoValidator
from validator.topic_validator import TopicValidator

class RuleParse:
    def __init__(self, rules_file_path, args):
        self.rules_file_path = rules_file_path
        self.args = args

    def parse(self):
        with open(self.rules_file_path, 'r') as file:
            rules = json.load(file)

        validators = []

        for rule_name, rule_details in rules.items():
            validator_type = rule_details.get('validator')
            catalog = rule_details.get('catalog', "")
            error_as_warning = rule_details.get('error_as_warning', False)

            if validator_type == 'FileValidator':
                ext = rule_details.get('ext', [])
                candidate_path = rule_details.get('candidate_path', [""])
                case_sensitive = rule_details.get('case_sensitive', False)
                h2_tags = rule_details.get('assert_in', None)
                accept_folder = rule_details.get('accept_folder', False)
                validator = FileValidator(catalog, rule_name, ext, ".", candidate_path, h2_tags, case_sensitive, error_as_warning, accept_folder)
            
            elif validator_type == 'AzdValidator':
                if rule_name == 'azd up' and not self.args.azdup:
                    continue
                if rule_name == 'azd down' and not self.args.azddown:
                    continue
                validator = AzdValidator(catalog, ".", rule_name, error_as_warning)

            # TODO 
            # elif validator_type == 'MsdoValidator':
                # validator = MsdoValidator(catalog, ".", rule_name, error_as_warning)
            
            elif validator_type == 'TopicValidator':
                topics = rule_details.get('topics', [])
                validator = TopicValidator(catalog, rule_name, topics, self.args.topics, error_as_warning)
            
            else:
                continue

            validators.append(validator)

        return validators

# Example usage
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Parse rules and generate validators.")
    parser.add_argument('--azdup', action='store_true', help="Check infra code with azd up.")
    parser.add_argument('--azddown', action='store_true', help="Check infra code with azd down.")
    args = parser.parse_args()

    rules_file_path = os.path.join(os.path.dirname(__file__), 'rules.json')
    parser = RuleParse(rules_file_path, args)
    validators = parser.parse()
    for validator in validators:
        print(f"Validator: {validator.__class__.__name__}, Rule: {validator.validatorCatalog}")