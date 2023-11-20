 # Create a Twilio client

import os
from twilio.rest import Client

def send_text(valid):

    from twilio.rest import Client
    #account_sid = 'MGf32c2bf8010ba77d81b738fb76048ddc'
    account_sid = 'AC8010fcf8a7c9217f2e222a62cc0e49cf'
    auth_token = 'c4e6b8b2c222848eb4660cfe1e34f4bf'
    client = Client(account_sid, auth_token)


    if valid:
        message = 'Your image was Sucessfully Authenticated through AWS'
    else:
        message = 'Your image Failed to be Authenticated; The image, metadata, or sender is invalid'


    message = client.messages.create(
    from_='+18573664416',
    body=message,
    to='+17819159187'
    )




send_text(True)