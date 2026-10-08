# SIFA - Smart IoT Farm Agriculture

SIFA is a local IoT smart agriculture system designed to monitor greenhouse water diagnostics. The entire system operates over a secure private network with zero cloud dependencies.


### Core Component Breakdown

* **IoT Edge Devices:** Physical hardware that collects live environmental readings from soil moisture probes and water flow meters. This data is transmitted as structured JSON payloads across the local Wi-Fi or LAN network.
* **FastAPI Backend:** A Python server running on a local PC or dedicated on-site machine. It intercepts incoming IoT data streams, keeps track of active hardware statuses (last_seen timestamps), and handles administrative logs.
* **PostgreSQL Database:** A relational database instance deployed locally on the network. It persists all user credentials, hardware device configurations, and historical water metrics.



## Running the System via Docker

### 1. Prerequisites
Ensure you have Docker and Docker Compose installed on your local server machine.

### 2. Launch the Ecosystem

```bash
docker compose up --build
```

### 3. Local Access
* **FastAPI Gateway:** http://localhost:8000
* **Interactive Documentation (Swagger):** http://localhost:8000/docs
# sifa
