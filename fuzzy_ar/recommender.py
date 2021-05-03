import pandas as pd


class Recommender():
    def __init__(self, rules: pd.DataFrame, fuzzy_sets: dict):
        self._rules = rules
        self._fuzzy_sets = fuzzy_sets

    def trigger_rules(self, data, memberships):
        candidate_rules = []
        for _, rule in self._rules.iterrows():
            memberships_rule = []
            for index, item in enumerate(rule['antecedents']):
                if item in self.fuzzy_sets_transpose:
                    fuzzy_set_idx = self._fuzzy_sets[
                        self.fuzzy_sets_transpose[item]
                        ].index(item)
                    memberships_rule.append(memberships[
                        self.fuzzy_sets_transpose[item]
                        ][fuzzy_set_idx])
            if min(memberships_rule) > 0:
                rule['memberships'] = memberships_rule
                rule['mu_rule'] = min(memberships_rule)
                features = ['antecedents', 'consequents', 'confidence',
                            'weigth', 'memberships', 'mu_rule']
                candidate_rules.append(rule[features])
        self.candidate_rules = pd.DataFrame(candidate_rules)
        return self.candidate_rules

    def new_rules(self, rule: set, index: int, fuzzy_sets: list):
        new_rules_list = []
        for fuzzy_set in fuzzy_sets:
            if fuzzy_set != fuzzy_sets[index]:
                new_rule = rule.copy()
                new_rule.remove(fuzzy_sets[index])
                new_rule.add(fuzzy_set)
                new_rules_list.append(new_rule)

        return new_rules_list

    def get_new_rules(self):
        new_rules = []
        for _, rule in self.candidate_rules.iterrows():
            for index, item in enumerate(rule['antecedents']):
                if item in self.fuzzy_sets_transpose:
                    new_rules.append(self.new_rules(
                        (rule['antecedents']),
                        self._fuzzy_sets[
                            self.fuzzy_sets_transpose[item]
                            ].index(item),
                        self._fuzzy_sets[self.fuzzy_sets_transpose[item]]))

        rules_wildcards = pd.DataFrame()
        for rule in new_rules:
            for x in rule:
                out = self.candidate_rules[
                        self.candidate_rules['antecedents'] == x]
                if len(out) > 0:
                    rules_wildcards = pd.concat([rules_wildcards, out])
        return rules_wildcards.sort_values(by=['weigth'], ascending=False)

    @property
    def fuzzy_sets_transpose(self):
        fuzzy_sets_dict = {}
        for key, value in self._fuzzy_sets.items():
            for val in value:
                fuzzy_sets_dict[val] = key
        return fuzzy_sets_dict