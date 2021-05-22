import logging
import azure.functions as func
import psycopg2
import os
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def main(msg: func.ServiceBusMessage):
    print("Starting the ServiceBusMessage function")
    notification_id = int(msg.get_body().decode('utf-8'))
    #notification_id = msg.get_body().decode('utf-8')
    print(notification_id)
    logging.info('Python ServiceBus queue trigger processed message: %s',
                 notification_id)

    # TODO: Get connection to database
    # Update connection string information
    host = os.environ.get('DB_HOST')
    dbname = os.environ.get('DB_NAME')
    user = os.environ.get('DB_USERNAME')
    password = os.environ.get('DB_PASSWORD')

    # Construct connection string
    conn_string = "host={} user={} dbname={} password={}".format(
        host, user, dbname, password)

    conn = psycopg2.connect(conn_string)
    print("Connection established", conn_string)

    cur = conn.cursor()
    try:
        # TODO: Get notification message and subject from database using the
        # notification_id
        # sql1 = "SELECT message, subject FROM notification WHERE id=?"
        cur.execute('SELECT "message", "subject" FROM "notification" WHERE "id"=%s;', (notification_id,))
        message, subject = cur.fetchone()
        logging.error('*** Message: %s -- Subject: %s', message, subject)

        # TODO: Get attendees email and name
        sql2 = "SELECT email, first_name FROM attendee;"
        cur.execute(sql2)
        attendee_details = cur.fetchall()
        print(attendee_details)
        '''
        logging.error(
            '*** email: %s -- first_name: %s',
            attendee_details[0][0],
            attendee_details[0][0])
        '''
        # TODO: Loop through each attendee and send an email with a
        # personalized subject

        for attendee in attendee_details:
            subject = '{}: {}'.format(attendee[1], subject)
            if not os.environ.get('SENDGRID_API_KEY'):
                message = Mail(
                    from_email=os.environ.get('ADMIN_EMAIL_ADDRESS'),
                    to_emails=attendee[0],
                    subject=subject,
                    plain_text_content=message)

                sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
                sg.send(message)
            
        # TODO: Update the notification table by setting the completed date and
        # updating the status with the total number of attendees notified
        date = datetime.utcnow()
        cur.execute('UPDATE "notification" SET "completed_date"=%s WHERE "id"=%s;', (date, notification_id))

        status = 'Notified {} attendees'.format(len(attendee_details))
        print(status, " is the status")
        cur.execute('UPDATE "notification" SET "status"=%s WHERE "id"=%s;', (status, notification_id))
        conn.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)
    finally:
        # TODO: Close connection
        if conn:
            cur.close()
            conn.close()
            print("PostgreSQL connection is closed")
