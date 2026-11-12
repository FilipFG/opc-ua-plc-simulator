# OPC UA PLC Simulator (Welding Station PoC)

Industrial automation repository featuring a Python-based welding station simulation and a Siemens S7-1500 PLC (TIA Portal). Implements secure OPC UA communication with X.509 certificates, polling, and subscriptions.

## Prerequisites

- **Python 3.10+** installed on your machine.
- **TIA Portal (V17/V18/V19)** with an S7-1500 PLC supporting OPC UA Client/Server capabilities.

---

## Environment Setup (Virtual Environment)

Open your terminal in the project directory and follow these steps to set up the virtual environment.

### 1. Create the virtual environment
```bash
python -m venv venv
```
### 2. Activate the virtual environment
```bash
venv\Scripts\activate
```
### 3. Install requirements
```bash
pip install --upgrade pip
pip install -r requirements.txt
```