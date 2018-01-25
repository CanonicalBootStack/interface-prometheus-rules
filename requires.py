from charms.reactive import hook
from charms.reactive import RelationBase
from charms.reactive import scopes


class PrometheusRulesRequires(RelationBase):
    scope = scopes.UNIT

    @hook('{requires:prometheusrules}-relation-{joined,changed}')
    def changed(self):
        conv = self.conversation()
        if conv.get_remote('groups'):
            # this unit's conversation has rules defined
            conv.set_state('{relation_name}.available')

    @hook('{requires:prometheusrules}-relation-{departed,broken}')
    def broken(self):
        conv = self.conversation()
        conv.remove_state('{relation_name}.available')

    def prometheus_rules(self):
        """
        Returns a dict of available Prometheus rules, to turn into
        a yaml file on the Prometheus host.
        """
        prometheus_rules = []
        for conv in self.conversations():
            groups = conv.get_remote('groups')
            if groups:
                prometheus_rules.append({'groups': groups})
        return [s for s in prometheus_rules if s['groups']]
