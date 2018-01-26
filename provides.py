from charms.reactive import hook
from charms.reactive import RelationBase
from charms.reactive import scopes


class ProemetheusRulesProvides(RelationBase):
    scope = scopes.GLOBAL

    @hook('{provides:prometheus-rules}-relation-{joined,changed}')
    def changed(self):
        self.set_state('{relation_name}.available')

    @hook('{provides:prometheus-rules}-relation-departed')
    def departed(self):
        if len(self.conversation().units) == 1:
            # this is the last departing unit
            self.remove_state('{relation_name}.available')

    def configure(self, rules):
        """
        Exports alerting rules which include specifics for hostname,
        application name, unit name, and some thresholds.

        Required Params:
        rules: The set of rules to pass across the relation, yaml format string
        """
        relation_info = {'groups': rules}
        self.set_remote(**relation_info)
