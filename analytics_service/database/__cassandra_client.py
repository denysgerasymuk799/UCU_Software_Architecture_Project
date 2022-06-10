# Download Amazon TLS certificate to certificates folder:
# curl https://certs.secureserver.net/repository/sf-class2-root.crt -O
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.query import SimpleStatement
from cassandra import ConsistencyLevel
from ssl import SSLContext, PROTOCOL_TLSv1_2, CERT_REQUIRED
from domain_logic.__constants import CERTIFICATE_PATH


class CassandraClient:
    def __init__(self, host, port, keyspace, username, password):
        self.host = host
        self.port = port
        self.keyspace = keyspace
        # Amazon IAM Cassandra privileges credentials.
        self.service_username = username
        self.service_password = password
        # Amazon Keyspaces session.
        self.session = None

    def connect(self):
        # Get the SSL certificate and configure the Python driver to use TLS.
        ssl_context = SSLContext(PROTOCOL_TLSv1_2)
        ssl_context.load_verify_locations(CERTIFICATE_PATH)
        ssl_context.verify_mode = CERT_REQUIRED
        # Provide auth credentials to Amazon Keyspaces user.
        auth_provider = PlainTextAuthProvider(username=self.service_username, password=self.service_password)
        # Create cluster instance and connect to provided keyspace.
        cluster = Cluster([self.host], port=self.port, ssl_context=ssl_context, auth_provider=auth_provider)
        self.session = cluster.connect(self.keyspace)

    def execute_write_query(self, query):
        # Ensure consistency level under write operation is LOCAL_QUORUM.
        query = SimpleStatement(query, consistency_level=ConsistencyLevel.LOCAL_QUORUM)
        return self.session.execute(query)

    def execute_read_query(self, query):
        return self.session.execute(query)

    def close(self):
        self.session.shutdown()
