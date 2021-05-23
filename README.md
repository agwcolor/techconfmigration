# TechConf Registration Website

## Project Overview
The TechConf website allows attendees to register for an upcoming conference. Administrators can also view the list of attendees and notify all attendees via a personalized email message.

The application is currently working but the following pain points have triggered the need for migration to Azure:
 - The web application is not scalable to handle user load at peak
 - When the admin sends out notifications, it's currently taking a long time because it's looping through all attendees, resulting in some HTTP timeout exceptions
 - The current architecture is not cost-effective 

In this project, you are tasked to do the following:
- Migrate and deploy the pre-existing web app to an Azure App Service
- Migrate a PostgreSQL database backup to an Azure Postgres database instance
- Refactor the notification logic to an Azure Function via a service bus queue message

## Dependencies

You will need to install the following locally:
- [Postgres](https://www.postgresql.org/download/)
- [Visual Studio Code](https://code.visualstudio.com/download)
- [Azure Function tools V3](https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local?tabs=windows%2Ccsharp%2Cbash#install-the-azure-functions-core-tools)
- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest)
- [Azure Tools for Visual Studio Code](https://marketplace.visualstudio.com/items?itemName=ms-vscode.vscode-node-azure-pack)

## Project Instructions

### Part 1: Create Azure Resources and Deploy Web App
1. Create a Resource group
2. Create an Azure Postgres Database single server
   - Add a new database `techconfdb`
   - Allow all IPs to connect to database server
   - Restore the database with the backup located in the data folder
3. Create a Service Bus resource with a `notificationqueue` that will be used to communicate between the web and the function
   - Open the web folder and update the following in the `config.py` file
      - `POSTGRES_URL`
      - `POSTGRES_USER`
      - `POSTGRES_PW`
      - `POSTGRES_DB`
      - `SERVICE_BUS_CONNECTION_STRING`
4. Create App Service plan
5. Create a storage account
6. Deploy the web app

### Part 2: Create and Publish Azure Function
1. Create an Azure Function in the `function` folder that is triggered by the service bus queue created in Part 1.

      **Note**: Skeleton code has been provided in the **README** file located in the `function` folder. You will need to copy/paste this code into the `__init.py__` file in the `function` folder.
      - The Azure Function should do the following:
         - Process the message which is the `notification_id`
         - Query the database using `psycopg2` library for the given notification to retrieve the subject and message
         - Query the database to retrieve a list of attendees (**email** and **first name**)
         - Loop through each attendee and send a personalized subject message
         - After the notification, update the notification status with the total number of attendees notified
2. Publish the Azure Function

### Part 3: Refactor `routes.py`
1. Refactor the post logic in `web/app/routes.py -> notification()` using servicebus `queue_client`:
   - The notification method on POST should save the notification object and queue the notification id for the function to pick it up
2. Re-deploy the web app to publish changes

## Monthly Cost Analysis
Complete a month cost analysis of each Azure resource to give an estimate total cost using the table below:

| Azure Resource | Service Tier | Monthly Cost |
| ------------ | ------------ | ------------ |
| *Azure Postgres Database* | Basic 5Gb 1 or 2 core |     $25.30 or $55.59         |
| *Azure Service Bus Namespace*   | Basic     |     $0.05/million        |
| *App Service*    | Free - F1  |   $0.00      |              |
| *Storage Account* | Standard RA GRS / Cool    |$0.22    ($0.025 (per) GB - First 50 TB), ($0.20 per 10,000 data transfer) |
| *Application Insights* | Basic - B1 | $13.14   |
| *Function App* |  Consumption | $6 (Includes Resource & Executions @1 Million)    |
| TOTAL (Mo)   |    -----    |    $44.71 (1coreDB) / $70.01 (2coreDB)     |

## Architecture Explanation
Reasoning for the architecture selection for the Azure Web App and Azure Function:

**Azure App Service**

I chose the Azure App Service (Managed Service) to create the Web App because it requires fewer administrative tasks and takes care of the server & security maintenance and updates for you. It is also usually less expensive than a lift and shift virtual machine migration.  Since this application needs less than 14 GB/RAM and less than 4 vCPUS, the Azure Web App is a good solution. Since this is a dynamic Python app vs a static one, I chose a Linux environment. Linux also happens to be less expensive than the Windows environment for App Services. I chose the Free plan (Dev/Test) -- F1 -- which provides 60 minutes/day compute & 1GB memory.  For the purpose of this exercise, I chose Shared Compute since I don't need to scale for this exercise.

**Database**

The database used is the managed service Azure Database for PostgreSQL Single server which is a good general purpose Enterprise database.

**AzureFunction & Azure Service Bus**

The original application processed sending a notification email to every person in an attendee database table. The larger the table, the more time-consuming the loop is to execute. One solution is to move this functionality to a background job using an Azure Function so that it does not slow down the main app.  For this application, I created an Azure Service Bus Queue Trigger Function since it is triggered via non-HTTP logic (ie. via a message queue).  One of the jobs of the Azure Service Bus is to help integrate applications. The service bus queue is set up on Azure so that the Service Bus Queue Trigger Function triggers when a message is added to its queue from within the Web App. The Azure Service Bus Queue Trigger Function also communicates with the PosgreSQL database to retrieve and insert the notification details. It also works with the SendGrid API to send all of the messages by looping over them. This all operates in the background so that the main Web App is not affected.  If the queue used for the messages were to grow to larger than 80 GB, however, I would need to move to a Storage Queue.

**Misc**

For this project there were some interesting constraints that I did not anticipate. I was not able to contain all of my resources in the same Resource Group. I was forced to create a 2nd resource group for the Azure Function App. In addition, for the Azure Database for PostreSQL I was occasionally forced to choose 2 cores instead of 1 depending upon the day. (1vCores: $25.30 / mo | 2vCores: $55.59 / mo )
