from __future__ import print_function
from cmath import log
from crypt import methods
from email.message import Message
import email.encoders
from email.mime import base
from email.mime import image
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import mimetypes

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64


from flask import Flask, jsonify, request
import pyqrcode
from pyqrcode import QRCode
import png


app = Flask(__name__)

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

@app.post('/sendUserEmail')
def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    print(request.form)
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)
        # results = service.users().labels().list(userId='me').execute()
        # labels = results.get('labels', [])

        # if not labels:
        #     print('No labels found.')
        #     return
        # print('Labels:')
        # for label in labels:
        #     print(label['name'])
        


        body = ("Hi " + request.form['name'] + ",<br/><br/> Thank you for purchasing a ticket to Diya!<br/>"
        "Please ensure you read everything in this email carefully. In order to enter the event, you will need to present this email and the QR Code attachment.<br/><br/>"
        "<b>ITEMS TO BRING TO DIYA</b><br/>"
        "<ol><li>Husky Card (for UW Students) or US State/Government issued ID (for non-UW Students)</li><li>This confirmation email with the QR Code Attached</li></ol><br/>"
        "<b>ABOUT THE EVENT</b><br/>"
        "<ul><li>WHEN: November 5th, 2022 from 9 PM to 12:30 AM</li><li>WHERE: <a href=\"https://goo.gl/maps/UQxArPCTKEWTHQKh8\">First & Bell</a> (2218 1st Ave, Seattle, WA 98121)</li><li>DRESS: Traditional Indian clothes reccommended</li></ul><br/>"

        "<b>PLEASE BE AWARE, BY ACCEPTING THIS TICKET YOU AGREE TO THE DISCLAIMER ATTACHED IN THE EMAIL</b><br/>"
        "--<br/>"
        "<b>2022-2023 Indian Student Association Executive Officers</b><br/><br/>"
        "<b>President --</b> Aroosh Kumar<br/>"
        "<b>Vice Presidents --</b> Akriti Shrivastava & Krithika Satish<br/>"
        "<b>Secretary --</b> Shrey Kharbanda<br/>"
        "<b>Tresurer --</b> Manasa Lingireddy<br/>"
        "<br/>"
        "<a href=\"https://www.facebook.com/uwindians \">https://www.facebook.com/uwindians</a><br/>"
        "<a href=\"https://www.instagram.com/uwisa/\" >https://www.instagram.com/uwisa/</a><br/>")

        # create the QR code
        url = pyqrcode.create("https://greasy-cable-production.up.railway.app/getUserDetails/" + request.form['uuid'])
        imageName = request.form['uuid'] + ".png"
        url.png(imageName, scale=10)
        message = create_message_with_attachment("kumararoosh@gmail.com", 
        request.form['email'], "Diya Ticket: " + request.form['name'], body, [imageName, "Disclaimer.pdf"])
        send_message(service, "me", message)
        
        os.remove(imageName)

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f'An error occurred: {error}')

    return jsonify({"Choo Choo": "Welcome to your Flask app 🚅"})


def create_message(sender, to, subject, message_text):
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    raw_message = base64.urlsafe_b64encode(message.as_string().encode("utf-8"))
    return {
        'raw': raw_message.decode("utf-8")
    }

def create_message_with_attachment(sender, to, subject, message_text, files):
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    msg = MIMEText(message_text, 'html')
    message.attach(msg)

    for file in files:       
        content_type, encoding = mimetypes.guess_type(file)

        if content_type is None or encoding is not None:
            content_type = 'application/octet-stream'

        main_type, sub_type = content_type.split('/', 1)
        if main_type == 'image':
            fp = open(file, 'rb')
            msg = MIMEImage(fp.read(), _subtype=sub_type)
            fp.close()
        else:
            fp = open(file, 'rb')
            msg = MIMEBase(main_type, sub_type)
            msg.set_payload(fp.read())
            email.encoders.encode_base64(msg)
            fp.close()
        filename = os.path.basename(file)
        msg.add_header('Content-Disposition', 'attachment', filename=filename)
        message.attach(msg)
    raw_message = base64.urlsafe_b64encode(message.as_string().encode("utf-8"))
    return {'raw': raw_message.decode("utf-8")}



def send_message(service, user_id, message):
    try:
        message = service.users().messages().send(userId=user_id, body=message).execute()
        print('Message Id: %s' % message['id'])
        return Message

    except Exception as e:
        print('An error ocurred: %s' % e)
        return None

def create_draft(service, user_id, message_body):
    try:
        message = {'message': message_body}
        draft = service.users().drafts().create(userId=user_id, body=message).execute()
        print("Draft id: %s\nDraft message: %s" % (draft['id'], draft['message']))
        return draft
    except Exception as e:
        print('An error ocurred %s' % e)
        return None

if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))