# 5G Network Traffic Classifier and Projector

This project aims to classify and project 5G network traffic across multiple interfaces, enabling real-time monitoring and analysis of network performance. The system simulates 5G traffic using a client-server model based on HTTP/2, captures network packets using TShark, and stores the data in MongoDB and SQL databases. The classified traffic is visualized using Grafana, providing insights into traffic patterns, latency, and bandwidth utilization.

## Features
- **Packet Capture**: Utilizes TShark for capturing and decoding 5G HTTP/2 traffic.
- **Data Storage**: Stores raw packet data in MongoDB and classified data in an SQL database for efficient querying and retrieval.
- **Traffic Classification**: Implements a custom algorithm to classify traffic based on 5G network interfaces (e.g., RAN, Core Network, User Equipment).
- **Real-Time Visualization**: Uses Grafana to create dynamic dashboards for monitoring traffic patterns, latency, and throughput.

## Technologies Used
- **TShark**: For packet capturing and decoding.
- **MongoDB**: For storing raw packet data.
- **SQL**: For structured storage of classified traffic data.
- **Grafana**: For real-time visualization and analysis.
- **HTTP/2**: For simulating 5G traffic in a client-server model.
- **Node.js**: For server-side implementation.
- **Python**: For packet analysis and classification.

## How It Works
1. **Traffic Simulation**: The client-server model simulates 5G traffic using HTTP/2.
2. **Packet Capture**: TShark captures and decodes HTTP/2 packets, which are stored in MongoDB.
3. **Traffic Classification**: A custom algorithm processes the captured data and classifies it based on 5G network interfaces.
4. **Data Storage**: Classified data is stored in an SQL database for efficient querying.
5. **Visualization**: Grafana connects to the SQL database to create real-time dashboards for traffic analysis.

## Installation and Setup
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/5g-traffic-classifier.git
   cd 5g-traffic-classifier
