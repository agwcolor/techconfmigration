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
    conn = psycopg2.connect(database="", user="", password="")
    cur = connection.cursor()
    try:
        # TODO: Get notification message and subject from database using the notification_id
        notification_query = ""
        cur.execute("SELECT message, subject FROM Notification WHERE id = %s;", (notification_id))
        message, subject = cur.fetchone()
        logging.error('*** Message: %s -- Subject: %s', message, subject)

        # TODO: Get attendees email and name
        cur.execute("SELECT email, name FROM Attendee;")
        attendees = cur.fetchall()
        # TODO: Loop through each attendee and send an email with a personalized subject
        for attendee in attendees:
            subject = '{}: {}'.format(attendee.first_name, notification.subject)
            send_email(attendee.email, subject, notification.message)

        # TODO: Update the notification table by setting the completed date and updating the status with the total number of attendees notified
        notification.completed_date = datetime.utcnow()
        notification.status = 'Notified {} attendees'.format(len(attendees))
        conn.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)
    finally:
        # TODO: Close connection
        if conn:
            cur.close()
            conn.close()
            print("PostgreSQL connection is closed")

def send_email(email, subject, body):
    if not app.config.get('SENDGRID_API_KEY')
        message = Mail(
            from_email=app.config.get('ADMIN_EMAIL_ADDRESS'),
            to_emails=email,
            subject=subject,
            plain_text_content=body)

        sg = SendGridAPIClient(app.config.get('SENDGRID_API_KEY'))
        sg.send(message)