import logging
import azure.functions as func
#import psycopg2
import psycopg2-binary
import os
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def main(msg: func.ServiceBusMessage):

    notification_id = int(msg.get_body().decode('utf-8'))
    logging.info('Python ServiceBus queue trigger processed message: %s',notification_id)

    # TODO: Get connection to database
    # Update connection string information
    host = "<server-name>"
    dbname = "<database-name>"
    user = "<admin-username>"
    password = "<admin-password>"
    sslmode = "require"

    # Construct connection string
    conn_string = "host={0} user={1} dbname={2} password={3} sslmode={4}".format(host, user, dbname, password, sslmode)

    conn = psycopg2.connect(conn_string)
    print("Connection established")

    cur = conn.cursor()
    try:
        # TODO: Get notification message and subject from database using the notification_id
        sql1 = "SELECT message, subject FROM Notification WHERE id = %s;"
        cur.execute(sql1, (notification_id))
        message, subject = cur.fetchone()
        logging.error('*** Message: %s -- Subject: %s', message, subject)

        # TODO: Get attendees email and name
        sql2 = "SELECT email, name FROM Attendee;"
        cur.execute(sql2)
        attendee_details = cur.fetchall()

        # TODO: Loop through each attendee and send an email with a personalized subject

        for attendee in attendee_details:
            message = Mail(
                from_email=app.config.get('ADMIN_EMAIL_ADDRESS'),
                to_emails=email,
                subject=subject,
                plain_text_content=body)

            try:
                sg = SendGridAPIClient(app.config.get('SENDGRID_API_KEY'))
                sg.send(message)

        # TODO: Update the notification table by setting the completed date and updating the status with the total number of attendees notified
        sql3 = "UPDATE Notification SET completed_date = %s;"
        date = datetime.utc.now()
        cur.execute(sql3, (date))

        sql4 = "UPDATE Notification SET status = %s;"
        status = 'Notified {} attendees'.format(len(attendee_details))
        cur.execute(sql4, (status))

        #notification.completed_date = datetime.utcnow()
        #notification.status = 'Notified {} attendees'.format(len(attendee_details))

        conn.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)
    finally:
        # TODO: Close connection
        if conn:
            cur.close()
            conn.close()
            print("PostgreSQL connection is closed")