from web3 import Web3
from web3.beacon import Beacon
from os import getenv
import json
import requests
from requests.exceptions import ConnectionError
import logging


class NodeAPIClient:
    def __init__(
        self, node_name: str = None, beacon_url: str = None, execution_url: str = None
    ):
        if beacon_url:
            self.beacon_url = beacon_url
        else:
            self.beacon_node_url = getenv("BEACON_NODE_URL")
        if execution_url:
            self.execution_node_url = execution_url
        else:
            self.execution_node_url = getenv("EXECUTION_NODE_URL")
        if node_name:
            self.node_name = node_name
        else:
            self.node_name = getenv("NODE_NAME")
        self.logger = logging.getLogger("NodeApiClient")
        self.output_payload = {"name": self.node_name}
        self.beacon_node = Beacon(self.beacon_url)
        self.beacon_is_connected = False
        self.execution_node = Web3(Web3.HTTPProvider(self.execution_node_url))
        self.execution_is_connected = False

    def check_connections(self):
        beacon_output_key = "beacon_is_connected"
        execution_output_key = "execution_is_connected"
        try:
            self.beacon_node.get_spec()
            self.beacon_is_connected = True
            self.output_payload.update({beacon_output_key: True})
        except ConnectionError as ce:
            self.logger.critical(
                f"Failed to Connect to Beacon Node | URL: {self.beacon_node_url} | Error: {str(ce)}"
            )
            self.output_payload.update({beacon_output_key: False})

        if self.execution_node.is_connected():
            self.execution_is_connected = True
            self.output_payload.update({execution_output_key: True})
        else:
            self.logger.critical(
                f"Failed to Connect to Execution Node | URL: {self.execution_node_url}"
            )
            self.output_payload.update({execution_output_key: False})
        return self

    def get_beacon_health(self):
        output_key = "beacon_health_status"
        health_status = self.beacon_node.get_health()
        self.output_payload.update({output_key: health_status})
        self.logger.debug(f"Beacon Health Status: {str(health_status)}")
        return self

    def get_beacon_sync_status(self):
        output_key = "beacon_is_synced"
        sync_status = self.beacon_node.get_syncing().get("data")
        self.logger.debug(f"Beacon Sync Status: {str(sync_status)}")
        if not sync_status.get("is_syncing"):
            self.output_payload.update(
                {output_key: True}
            )  # Need to flip this because we want True if node is in sync
            self.logger.debug("Beacon is Synced: True")
        else:
            self.output_payload.update({output_key: False})
            self.logger.debug("Beacon is Synced: False")
        return self

    def get_beacon_peer_count(self):
        output_key = "beacon_peer_count"
        beacon_peers = self.beacon_node.get_peers()
        peer_count = beacon_peers.get("meta").get(
            "count"
        )  # We're only interested in the total peer count, not each individual peer details
        self.output_payload.update({output_key: peer_count})
        self.logger.debug(f"Beacon Peers: {str(peer_count)}")
        return self

    def get_beacon_version(self):
        output_key = "beacon_version"
        beacon_version = self.beacon_node.get_version().get("data").get("version")
        self.output_payload.update({output_key: beacon_version})
        self.logger.debug(f"Beacon Version Info: {str(beacon_version)}")
        return self

    def get_execution_sync_status(self):
        output_key = "execution_is_synced"
        sync_status = self.execution_node.eth.syncing
        if not sync_status:
            self.output_payload.update({output_key: True})
        else:
            self.output_payload.update({output_key: False})
        self.logger.debug(f"Execution Node is Syncing: {sync_status}")
        return self

    def get_execution_block_height(self):
        output_key = "execution_block_height"
        block_height = self.execution_node.eth.get_block_number()
        self.output_payload.update({output_key: block_height})
        self.logger.debug(f"Execution Block Height: {str(block_height)}")
        return self

    def get_execution_version(self):
        output_key = "execution_version"
        execution_version = self.execution_node.client_version
        self.output_payload.update({output_key: execution_version})
        self.logger.debug(f"Execution Version Info: {str(execution_version)}")
        return self

    def check_beacon_node(self):
        self.get_beacon_sync_status()
        self.get_beacon_health()
        self.get_beacon_peer_count()
        self.get_beacon_version()

    def check_execution_node(self):
        self.get_execution_block_height()
        self.get_execution_sync_status()
        self.get_execution_version()

    def send_output_payload(self):
        self.logger.info(f"Output Payload: {str(self.output_payload)}")
        webhook_url = getenv("BEACONBOT_WEBHOOK_URL")
        response = requests.post(webhook_url, data=json.dumps(self.output_payload))
        if not response.ok:
            self.logger.critical("Failed to Post Event to BeaconBot Webhook")
        else:
            self.logger.info("Successfully Posted Event Payload to BeaconBot")
        return
    
    def run(self):
        self.check_connections()
        if self.beacon_is_connected:
            self.check_beacon_node()
        if self.execution_is_connected:
            self.check_execution_node()
        self.send_output_payload()


def main():
    client = NodeAPIClient()
    client.run()


if __name__ == "__main__":
    main()
