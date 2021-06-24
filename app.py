import requests
import json
import time
import datetime
import smtplib


def email(str):
    # Configure GMAIL settings
    # From this mail id, the alerts will be sent
    sender_email = "<SENDER EMAIL>"
    sender_pass = "<SENDER EMAIL PASSWORD>"  # Enter the email id's password

    with smtplib.SMTP("smtp.gmail.com") as connection:
        connection.starttls()
        connection.login(sender_email, sender_pass)
        connection.sendmail(
            from_addr=sender_email,

            # For multiple receiver, enter email address with comma seperated
            to_addrs=["<RECEIVER EMAIL1>", "<RECEIVER EMAIL2>"],
            msg=str
        )


if __name__ == '__main__':

    pincodes = ["500018", "500081"]  # Enter pincodes with comma seperated

    # url source is Cowin API - https://apisetu.gov.in/public/api/cowin
    today = time.strftime("%d-%m-%Y")

    while(1):

        available = False  # whether a single vaccine is present or not in that pincode
        t = datetime.datetime.now().strftime("%H:%M:%S")
        # Frame the subject of Email
        message_subject1 = f"Subject: {today}'s Vaccine Alert!! at {t}\n"
        message_subject0 = f"Subject: {today}'s Vaccine NOT Available\n\n"

        full_message = ""
        for pincode in pincodes:

            url_pincode = f"https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin?pincode={pincode}&date={today}"

            # start session for API request
            with requests.session() as session:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}
                response = session.get(url_pincode, headers=headers)
                print(response.status_code)
                # Receive the response
                response = response.json()

                message = ""

                for center in response['centers']:

                    message_string = ""     # Frame info about vaccine
                    message_head = ""       # Frame Hosptial/Center name
                    for session in center['sessions']:
                        # check for available capacity
                        if(session['available_capacity'] > 0 and session['min_age_limit'] == 18):
                        # For both 18+ and 45+ alert uncomment the below line and comment the above line
                        # if(session['available_capacity'] > 0):
                            available = True
                            message_head = f"{center['name']} - {center['pincode']}\n"
                            message_string = message_string + \
                                f"Vaccine : {session['vaccine']}\nFee: {center['fee_type']}\nAge Group: {session['min_age_limit']}\nDose 1: {session['available_capacity_dose1']}\nDose 2: {session['available_capacity_dose2']}\nDate: {session['date']}\n\n"

                    message_string = message_head + message_string
                    message += message_string

                full_message += message
            time.sleep(5)

        # Frame Final message
        final_message = ""
        if available:
            final_message = message_subject1 + full_message
        else:
            final_message = message_subject0

        # print(final_message)
        email(final_message)    # Send message
        # wait for 30 min (Change according to your need)
        time.sleep(1800)
