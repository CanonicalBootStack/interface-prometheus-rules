from charms.reactive import hook
from charms.reactive import RelationBase
from charms.reactive import scopes


class ProemetheusRulesProvides(RelationBase):
    scope = scopes.GLOBAL

    @hook('{provides:prometheusrules}-relation-{joined,changed}')
    def changed(self):
        self.set_state('{relation_name}.available')

    @hook('{provides:prometheusrules}-relation-departed')
    def departed(self):
        if len(self.conversation().units) == 1:
            # this is the last departing unit
            self.remove_state('{relation_name}.available')

    def configure(self, hostname, unit_name, rules):
        """
        Exports alerting rules which include specifics for hostname,
        application name, unit name, and some thresholds.

        Required Params:
        hostname: The hostname of the machine
        unit_name: The name of the unit
        rules: The set of rules to pass across the relation
        """
        relation_info = {'groups':
                         [{'name': "{}_{}".format(hostname, unit_name),
                           'rules': rules,
                           },
                          ],
                         }
        self.set_remote(**relation_info)
