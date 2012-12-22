from flaskext.mail import Message
from offenesparlament.core import mail

def send_message(to, subject, body):
    msg = Message(subject, 
            sender=('OffenesParlament.de', 'info@offenesparlament.de'),
            recipients=[to])
    msg.body = body
    mail.send(msg)

