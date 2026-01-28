<img src="./readme/card-titles/title1.svg"/>
<br>

## License

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

<br><br>
<!-- project overview -->
<img src="./readme/card-titles/title2.svg"/>

> Aegis-Ignis is an intelligent smart building security system that combines real-time fire detection, face recognition, and occupancy monitoring <br>
>The system provides instant visibility, intelligent alerts, and rapid emergency response through a unified platform that keeps people safe and assets protected.

<br>
<!-- System Design -->
<img src="./readme/card-titles/title3.svg"/>

### System Architecture

<img src="./readme/sql/System.png "/>

<br>

### Microservices Architecture  
<img src="./readme/sql/Microserevces.png "/>

### Entity Relationship Diagram
<img src="./readme/sql/Diagram 3.png"/>

### n8n
<img src="./readme/sql/n8n-workflow.png"/>
<br><br>
<!-- Project Highlights -->
<img src="./readme/card-titles/title4.svg"/>

### Core Features

-ML: YOLOv8-based fire and smoke detection.<br>
-Face Recognition: Fast employee identification using InsightFace embeddings. <br>
-Multi-Channel Alerts: WhatsApp, SMS, and voice notifications via N8N with severity based routing<br>
-Employee Registration Portal: Simple face registration with photo upload and automatic embedding generation<br>
<br>
<img src="./readme/sql/demo.png"/>
<br>
<!-- Demo -->
<img src="./readme/card-titles/title5.svg"/>

### System Screenshots

| Dashboard Overview | Login Overview | Camera Management |
| ------------------ | -------------- | ----------------- |
| <img src="./readme/gif/Dashboard.gif" width="220" alt="Dashboard Overview" /> | <img src="./readme/gif/login.gif" width="220" alt="Login Overview" /> | <img src="./readme/gif/Camera-settings.gif" width="220" alt="Camera Management" /> |

| Fire Alerts | Employee Management | Face Registration |
| ----------- | ------------------- | ----------------- |
| <img src="./readme/gif/alerts.gif" width="220" alt="Fire Alerts" /> | <img src="./readme/sql/Employees.png" width="220" alt="Employee Management" /> | <img src="./readme/gif/face-recognizatipn.gif" width="220" alt="Face Registration" /> |

<br>


| Mobile Overview |
| ---------------------------------------| 
| <img src="./readme/gif/MObile.gif" />  |

<br><br>

<!-- Development & Testing -->
<img src="./readme/card-titles/title6.svg"/>

### Tests

 | Test Coverage |
 | ------------------------------------- |
 | ![CI/CD](./readme/sql/tests.png) |

- **Backend tests**: `cd Server && php artisan test`
- **Python services**: Unit tests for ML models and detection algorithms
- **Frontend tests**: React component testing with Vitest

<br>

### Machine Learning Development
 | Model Performance |
 | ------------------------------------- |
|<img src="./readme/sql/ml-WORKFLOW.png" alt="Machine Learning Development" /> |



| Training Dataset | Model Performance |
| --------------------------------------- | ------------------------------------- |
|  <img src="./readme/sql/ML.png" width="420" alt="Training" /> |<img src="./readme/sql/BoxF1_curve.png" width="420" alt="Model" /> |

<br>

### N8N Workflow Automation

The system uses N8N for intelligent alert routing and multi-channel notifications:

- **Webhook Trigger**: Receives fire alerts from Alert Manager
- **Alert Type Routing**: 
  - `FIRE_EMERGENCY`: Standard fire detection alerts
  - `CRITICAL_EVACUATION`: Alerts when people are present on floor
  - `PRESENCE_UPDATE`: Regular occupancy updates
- **Multi-Channel Delivery**: WhatsApp, SMS, Voice calls based on severity
- **Backend Integration**: Automatic logging and alert history updates

Workflow configuration available in `n8n-workflow-fire-alert.json`
<br><br>
### Additional Tools & Services

| Tool | Purpose |
|------|---------|
| **N8N** | Workflow automation for multi-channel alerts |
| **Twilio** | WhatsApp,  and Voice call integration |
| **MLFlow** | ML model tracking and registry |
| **PostgreSQL** | Primary database for all system data |
| **Docker** | Containerized PostgreSQL deployment |

<br><br>
<!-- Extras -->
<img src="./readme/card-titles/title7.svg"/> 

| Dockers |  Postman |
| ----------- |  ----------------- | 
| <img src="./readme/sql/Dockers.png" width="420" alt="Dockers" /> |  <img src="./readme/sql/postman.png" width="420" alt="Postman" /> | 

<br>

 | CI/CD Pipeline |
 | ----------------- |
 | ![CI/CD](./readme/sql/CiCd.png)

<br><br>
---

**Aegis-Ignis** - Intelligent Smart Building Security System

*Protecting buildings, one detection at a time.*
