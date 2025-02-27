# Hiscox API Integration Module for Odoo  

## Overview  
This Odoo module enables seamless integration with the Hiscox API to manage customer applications. It **collects customer data**, **generates a QR code** for submission, and synchronizes application status via **API requests**. The module includes **robust error handling**, logging, and is **packaged with a Docker environment** for easy deployment.  

## Features  
- **Customer Data Management**: Stores name, email, phone number, and application status.  
- **QR Code Generation**: Encodes customer details and saves them as a Base64 image in Odoo.  
- **API Integration**:  
  - `submit_to_hiscox()`: Sends application data via a **POST request**.  
  - `check_status_from_hiscox()`: Retrieves the latest application status via a **GET request**.  
- **Error Handling & Logging**: Logs API errors and ensures smooth operation.  
- **Docker Deployment**: Pre-configured environment for quick setup.  

## Installation & Setup  
### **1. Clone the Repository into Odoo's `custom_addons` Folder**  
Ensure you clone this repository inside your Odoo installation's **custom_addons** folder:  
```sh
cd ./odoo-x.x/custom_addons/
git clone https://github.com/mahmudaakterdisa/odoo-hiscox-integration.git
cd hiscox_integration
```

### **2. Update Local Paths in `docker-compose.yml`**  
Modify the following paths to match your system:  
```yaml
volumes:
  - "D:/Codes/odoo-18.0/custom_addons:/mnt/extra-addons"  # Update with your local path  
  - "D:/Codes/odoo-18.0/custom_addons/odoo.conf:/etc/odoo/odoo.conf"  
  - "D:/Codes/odoo-18.0/custom_addons/entrypoint-odoo.sh:/entrypoint-odoo.sh"  
```

### **3. Build and Start Containers**  
```sh
docker-compose up --build -d
```

### **4. Access Odoo**  
- Open **[http://localhost:8069](http://localhost:8069)**  
- Log in with default admin credentials  
(email: `admin`, password: `admin`)

### **5. How to use the Module**  
**i.** Navigate to **Hiscox Insurance Integration** App in Odoo & **install** it.  
**ii.** Create a new case clicking **New** button and generate a **QR code**.  
**iii.** Go Back to the **Hiscox Cases** tab and Click **Submit** to send data to the Hiscox API.  
**iv.** Click **Status** to retrieve and check current application status.  

## Troubleshooting  
### **Database Constraint Not Applied**  
Manually apply the unique constraint **only if missing**:  
```sh
docker exec -it hiscox_integration-db-1 psql -U odoo -d odoo -c "ALTER TABLE edited_hiscox_case ADD CONSTRAINT unique_email UNIQUE (email);"
docker restart hiscox_integration-odoo-1
```

### **Viewing Logs**  
can be checked through **Docker Desktop** app
or following command on specific container:
```sh
docker logs -f hiscox_integration-odoo-1
```

