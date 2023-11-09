# NodeWatch Monitoring Service

## To be used in conjunction with BeaconBot

## Overview
 - This script is designed to be deployed on servers running execution & consensus nodes to access locally available API's

 - Events are pushed to BeaconBot monitoring service's NodeTrigger and stored in a SQL database

 - BeaconBot will audit events using configurable policies and create incidents in PagerDuty on any violations

 ## Environment Variables
  - `BEACON_NODE_URL`
    - Must point to Beacon node's HTTP API (typically port 5052)
  - `EXECUTION_NODE_URL`
    - Must point to Execution Node's JSONRPC API (typically port 8545)
  - `NODE_NAME`
    - A friendly name for this node cluster that will be reported to PagerDuty
  - `BEACONBOT_WEBHOOK_URL`
    - URL for BeaconBot monitoring service that receives events
