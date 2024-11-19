# from neo4j import GraphDatabase

# class Neo4jConnection:
#     def __init__(self, uri, user, password):
#         """
#         Initialize the connection to the Neo4j database.
#         """
#         self._driver = GraphDatabase.driver(uri, auth=(user, password))
#         print("Neo4j connection established.")

#     def close(self):
#         """
#         Close the database connection.
#         """
#         if self._driver:
#             self._driver.close()
#             print("Neo4j connection closed.")

#     def execute_query(self, query, parameters=None):
#         """
#         Execute a query in the Neo4j database.
#         :param query: The Cypher query to execute.
#         :param parameters: Optional parameters for the query.
#         :return: Query results.
#         """
#         with self._driver.session() as session:
#             result = session.run(query, parameters or {})
#             return [record.data() for record in result]

#     def create_address_node(self, address):
#         """
#         Create a node for an address in the database.
#         :param address: The blockchain address.
#         """
#         query = """
#         MERGE (a:Address {address: $address})
#         RETURN a
#         """
#         self.execute_query(query, {"address": address})
#         print(f"Address node created or matched: {address}")

#     def create_transaction_node(self, transaction_id, amount, timestamp):
#         """
#         Create a node for a transaction in the database.
#         :param transaction_id: The unique transaction hash.
#         :param amount: The transaction amount.
#         :param timestamp: The timestamp of the transaction.
#         """
#         query = """
#         MERGE (t:Transaction {id: $transaction_id})
#         SET t.amount = $amount, t.timestamp = $timestamp
#         RETURN t
#         """
#         self.execute_query(query, {
#             "transaction_id": transaction_id,
#             "amount": amount,
#             "timestamp": timestamp
#         })
#         print(f"Transaction node created or updated: {transaction_id}")

#     def create_relationship(self, from_address, to_address, transaction_id, amount):
#         """
#         Create a relationship between two addresses for a transaction.
#         :param from_address: Sender address.
#         :param to_address: Receiver address.
#         :param transaction_id: Transaction hash.
#         :param amount: Transaction amount.
#         """
#         query = """
#         MATCH (from:Address {address: $from_address})
#         MATCH (to:Address {address: $to_address})
#         MERGE (from)-[r:SENT_TO {transaction_id: $transaction_id}]->(to)
#         SET r.amount = $amount
#         RETURN r
#         """
#         self.execute_query(query, {
#             "from_address": from_address,
#             "to_address": to_address,
#             "transaction_id": transaction_id,
#             "amount": amount
#         })
#         print(f"Relationship created: {from_address} -> {to_address} for transaction {transaction_id}")

# def connect_to_neo4j(uri, user, password):
#     """
#     Helper function to instantiate a Neo4jConnection.
#     :param uri: The URI of the Neo4j database.
#     :param user: The username for Neo4j authentication.
#     :param password: The password for Neo4j authentication.
#     :return: An instance of Neo4jConnection.
#     """
#     return Neo4jConnection(uri, user, password)
from neo4j import GraphDatabase

class Neo4jConnection:
    def __init__(self, uri, user, pwd):
        self.__uri = uri
        self.__user = user
        self.__pwd = pwd
        self.__driver = None
        try:
            self.__driver = GraphDatabase.driver(self.__uri, auth=(self.__user, self.__pwd))
            print("Connection successful")
        except Exception as e:
            print("Failed to create the driver:", e)

    def close(self):
        if self.__driver is not None:
            self.__driver.close()

    def get_neo4j_session(self):
        return self.__driver.session() if self.__driver else None

    def execute_query(self, query):
        with self.__driver.session() as session:
            result = session.run(query)
            return [record for record in result]

    def save_transaction(self, tx):
        query_create_sender = f"MERGE (s:Address {{address: '{tx['from']}'}})"
        query_create_recipient = f"MERGE (r:Address {{address: '{tx['to']}'}})"
        query_create_transaction = f"""
        CREATE (t:Transaction {{
            id: '{tx['hash']}',
            amount: {tx['value']},
            timestamp: {tx['timeStamp']}
        }})
        """
        query_create_relationship = f"""
        MATCH (s:Address {{address: '{tx['from']}'}}), (r:Address {{address: '{tx['to']}'}}), (t:Transaction {{id: '{tx['hash']}'}})
        MERGE (s)-[:SENT_TO {{amount: {tx['value']}, timestamp: {tx['timeStamp']}}}]->(t)
        MERGE (t)-[:RECEIVED_FROM {{amount: {tx['value']}, timestamp: {tx['timeStamp']}}}]->(r)
        """

        self.execute_query(query_create_sender)
        self.execute_query(query_create_recipient)
        self.execute_query(query_create_transaction)
        self.execute_query(query_create_relationship)
