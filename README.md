# Overview

This interface layer implements the layout for a 'prometheus-rules' interface
protocol. The layer allows passing a list of alerting rules from a charm, e.g.
Telegraf, to Prometheus.

# Usage

## Provides

By providing the `prometheus-rules` interface, your charm is exporting a set
of rules for alerting in Prometheus.  You need to provide the rules as a string,
which is most simply assembled with a template.

```python
@when('prometheus-rules.available')
def render_prometheus_rules(prometheus_rules):
    # Send a list of rules for alerting to Prometheus
    config = hookenv.config()
    hostname = socket.gethostname()
    unit_name = os.environ.get('JUJU_PRINCIPAL_UNIT')
    application_name = unit_name.split('/')[0]
    wait_time = config.get('wait_time')
    lead_time = config.get('lead_time')
    cpu_idle = config.get('cpu_idle')
    prometheus_context = config.get('prometheus_context')
    template = """
      - alert: {{ alert }}
        expr: {{ expr }}
        {% if for %}
        for: {{ for }}
        {% endif %}
        labels:
          severity: page
          application: {{ application_name }}
          unit: {{ unit_name }}
          cloud: {{ prometheus_context }}
        annotations:
          description: "{{ description }}"
          summary: "{{ summary }}"
    """
    rules = [
        {'alert': "{}_CPU_Usage".format(hostname),
         'expr': 'cpu_usage_idle{{host="{}"}} < {}'.format(hostname, cpu_idle),
         'for': "{}m".format(wait_time),
         'summary': ('Instance {{{{ $labels.instance }}}} '
                     'CPU free is less than {}%'.format(cpu_idle)),
         'description': ('{{{{ $labels.instance }}}} has had < {}% idle cpu '
                         'for the last {} minutes'.format(cpu_idle, wait_time)),
         'application_name': application_name,
         'unit_name': unit_name,
         'prometheus_context': prometheus_context,
        },
        ]
    formatted_rules = []
    for rule in rules:
        # render template
        formatted_rules.append(render_template(template, rule))
    prometheus_rules.configure("\n".join(formatted_rules))
```

## Requires

By requiring the `prometheus-rules` interface, your charm is consuming one or
more rules for alerting in Prometheus.

Your charm should respond to the `{relation_name}.available` state, which
indicates that there is at least one rule to import.

The `prometheus_rules()` method returns a list of available rules which
should be included in a .rules file on the Prometheus server.

``` python
@when('prometheus.started')
@when('prometheus-rules.available')
def update_prometheus_rules(prometheus_rules):
    rules = prometheus_rules.prometheus_rules()
    # insert into a template
    template = """
groups:
  - name: JujuRelation
    rules:
{{ rules }}
    """
    with open(PATHS['juju_rules_path'], 'w') as fh:
        fh.write(render_template(template, {'rules': "\n".join(rules)}))
    set_state('prometheus.do-check-reconfig')
    set_state('prometheus.do-restart')
```
