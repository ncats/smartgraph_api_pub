#
# The following script was used to sync data between the existing and new SmartGraph database.
# There were some missing properties within the new database that needed to be synced from the old database.
# The old database was a neo4j v3 instance, the new instance was neo4j v5.
# Note that all database connection details have been removed for security reasons.
#
# Author: Nathan Miller (nathan.miller@nih.gov)
# 

from neo4j import GraphDatabase
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

class DatabaseSyncer:
    def __init__(self, uri_old, uri_new, user_old, password_old, user_new, password_new):
        self.driver_old = GraphDatabase.driver(uri_old, auth=(user_old, password_old))
        self.driver_new = GraphDatabase.driver(uri_new, auth=(user_new, password_new))

    def close(self):
        self.driver_old.close()
        self.driver_new.close()

    def sync_nodes(self):
        with self.driver_old.session() as session_old:
            # Fetch 'Target' nodes from the old database
            nodes = session_old.run("MATCH (n:Target) RETURN n.uuid AS uuid, n.activity_cutoff AS activity_cutoff").data()
            with self.driver_new.session() as session_new:
                for node in nodes:
                    # Update node in the new database
                    updated_uuids = session_new.write_transaction(self._update_node_activity_cutoff, node['uuid'], node['activity_cutoff'])
                    if not updated_uuids:
                        logging.info(f"No matching UUID found for node: {node['uuid']}")

    @staticmethod
    def _update_node_activity_cutoff(tx, uuid, activity_cutoff):
        query = (
            "MATCH (n:Target {uuid: $uuid}) "
            "SET n.activity_cutoff = $activity_cutoff "
            "RETURN n.uuid AS updated_uuid"
        )
        result = tx.run(query, uuid=uuid, activity_cutoff=activity_cutoff)
        return [record["updated_uuid"] for record in result]

    def sync_edges(self, edge_type, property_from, property_to):
        with self.driver_old.session() as session_old:
            if edge_type and len(edge_type) > 0:
                query = f"MATCH ()-[r:{edge_type}]->() RETURN r.uuid AS uuid, r.{property_from} AS property"
            else:
                query = f"MATCH ()-[r]->() RETURN r.uuid AS uuid, r.{property_from} AS property"
            # Fetch edges of specified type from the old database
            edges = session_old.run(query).data()
            with self.driver_new.session() as session_new:
                for edge in edges:
                    # Update edge in the new database
                    updated_uuids = session_new.write_transaction(self._update_edge_property, edge['uuid'], edge['property'], property_to)
                    if not updated_uuids:
                        logging.info(f"No matching UUID found for edge: {edge['uuid']}")

    @staticmethod
    def _update_edge_property(tx, uuid, property_value, property_name):
        query = (
            f"MATCH ()-[r]->() WHERE r.uuid = $uuid "
            f"SET r.{property_name} = $property_value "
            "RETURN r.uuid AS updated_uuid"
        )
        result = tx.run(query, uuid=uuid, property_value=property_value)
        return [record["updated_uuid"] for record in result]

    def delete_old_property(self, edge_type, old_property, new_property):
        with self.driver_new.session() as session_new:
            # Delete old property if new property matches the old one in the new database
            session_new.write_transaction(self._delete_property_if_match, edge_type, old_property, new_property)

    @staticmethod
    def _delete_property_if_match(tx, edge_type, old_property, new_property):
        if edge_type and len(edge_type) > 0:
            query = (
                f"MATCH ()-[r:{edge_type}]->() "
                f"WHERE r.{old_property} = r.{new_property} "
                f"REMOVE r.{old_property} "
                "RETURN r.uuid AS updated_uuid"
            )
        else:
            query = (
                f"MATCH ()-[r]->() "
                f"WHERE r.{old_property} = r.{new_property} "
                f"REMOVE r.{old_property} "
                "RETURN r.uuid AS updated_uuid"
            )
        result = tx.run(query)
        return [record["updated_uuid"] for record in result]

if __name__ == "__main__":
    # Initialize with your database connection details
    old_db_uri = "bolt://localhost:1002"
    old_db_username = "username"
    old_db_password = "password"
    new_db_uri = "bolt://localhost:7687"
    new_db_username = "username"
    new_db_password = "password"
    syncer = DatabaseSyncer(old_db_uri, new_db_uri, old_db_username, old_db_password, new_db_username, new_db_password)
    try:
        # Sync 'Target' nodes
        syncer.sync_nodes()
        # Sync 'REGULATES' edges for 'edgeInfo' to 'edge_info'
        syncer.sync_edges("REGULATES", "edgeInfo", "edge_info")
        # Sync all edges for 'edgeType' to 'edge_type', and handle old property deletion
        syncer.sync_edges("", "edgeType", "edge_type")
        syncer.delete_old_property("", "edgeType", "edge_type")
    finally:
        syncer.close()