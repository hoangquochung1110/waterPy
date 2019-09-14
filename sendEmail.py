
import smtplib

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587 # typically 25, 465 or 587
SMTP_USER = "arsenalforeversince2007@gmail.com"
SMTP_PASS = "Jackwilshere1"
MAIL_FROM = "Quoc Hung"
MAIL_TO = "arsenalforeversince2007@gmail.com"

def sendMail(subject, body):
    message = "From: "+MAIL_FROM+"\r\nTo: "+MAIL_TO+"\r\n"+\
              "Subject: "+subject+"\r\n\r\n"+body
    mailServer = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    if SMTP_USER != "":
        mailServer.login(SMTP_USER, SMTP_PASS)
    mailServer.sendmail(MAIL_FROM, MAIL_TO, message)
    mailServer.close()

#sendMail("Irrigation System","Your garden has been watered") 
if __name__ == "__main__":
    sendMail("Irrigation System","Your garden has been watered.")
