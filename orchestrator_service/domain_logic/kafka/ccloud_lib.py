def read_ccloud_config(config_file):
    """Read Confluent Cloud configuration for librdkafka clients"""

    conf = {}
    with open(config_file) as fh:
        for line in fh:
            line = line.strip()
            if len(line) != 0 and line[0] != "#":
                parameter, value = line.strip().split('=', 1)
                conf[parameter] = value.strip()

    #conf['ssl.ca.location'] = certifi.where()

    return conf


def pop_schema_registry_params_from_config(conf):
    """Remove potential Schema Registry related configurations from dictionary"""

    conf.pop('schema.registry.url', None)
    conf.pop('basic.auth.user.info', None)
    conf.pop('basic.auth.credentials.source', None)

    return conf
