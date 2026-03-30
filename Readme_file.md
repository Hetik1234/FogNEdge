# Smart Entertainment Arena: Fog-to-Cloud IoT Architecture

A highly scalable, event-driven environmental monitoring system designed for high-occupancy venues. This project implements a true Fog Computing architecture by utilizing a local edge gateway to aggregate sensor telemetry, evaluate safety thresholds, and securely transmit data to an AWS Serverless backend.

## System Architecture

The application is built on a decoupled 3-tier architecture:

1. **The Edge/Fog Layer (Local):** Four independent Python scripts simulate real-time environmental sensors (Occupancy, CO2, Temperature, HVAC). A local Flask-based Fog Node aggregates this data every 10 seconds, calculates the venue's safety status (`NORMAL`, `CAUTION`, `SEVERE`), and securely publishes it to the cloud.
2. **The Serverless Backend (AWS Cloud):** Data is ingested via **AWS IoT Core** using mTLS. It is buffered asynchronously in an **Amazon SQS** queue, processed by an **AWS Lambda** function (`VenueDatabaseWriter`), and persisted in a **DynamoDB** NoSQL table.
3. **The Presentation Layer (Web):** A **Django** web application queries DynamoDB to render a real-time, responsive administrative dashboard using **Bootstrap 5** and **Chart.js**. It is fully deployable to **AWS Elastic Beanstalk**.

## Prerequisites

To run this project, you will need:
* **Python 3.12+** installed on your local machine.
* An **AWS Account** with configured credentials (`~/.aws/credentials`).
* **AWS IoT Core Certificates:** Download the root CA, private key, and device certificate from your AWS IoT Core console.

## 🚀 Setup & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/Hetik1234/FogNEdge
cd FogNEdge