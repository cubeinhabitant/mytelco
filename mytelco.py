import logging
import re

from google.appengine.api import mail

from twilio import twiml

import webapp2

# Update these values as appropriate

# These are the different number that the caller can choose from.
# The array corresponds to the number that the caller enters on
# there keypad. If there is only one number in the list the
# OPTION_MESSAGE is not played and the caller is directly connected
# to the only outgoing number.
OUTGOING_NUMBERS = ["sip:*46217771234567@sipbroker.com", "+18005558355"]

# This is the message that a caller will here. 
OPTION_MESSAGE = "To use SIP, press 0. To use D.I.D., press 1. Or, please hold a moment."

# Notification email is sent to the configured email address(es). If
# want to send to more than one email address, separate the address
# with a comma and space, like this: "user@email.com, another@email.com"
VOICEMAIL_EMAIL_NOTIFICATION = "user@email.com"

# Source email address for the voicemail notification email.
VOICEMAIL_EMAIL_NOTIFICATION_SENDER = "sender@email.com"

# constants

SIP_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")

class Utility():
    @staticmethod
    def is_sip(phone):
        """Determine if the phone number is a SIP number.
        
        Args:
            phone: The phone number to check.
        
        Returns:
            True if the phone number is a SIP number, false otherwise.
        """
        return SIP_REGEX.match(phone)

class IncomingCall(webapp2.RequestHandler):
    def post(self):
        r = twiml.Response()
        
        logging.debug('IncomingCall, CallSid[{}],AccountSid[{}],From[{}],To[{}],CallStatus[{}],ApiVersion[{}],Direction[{}],ForwardedFrom[{}],FromCity[{}],FromState[{}],FromZip[{}],FromCountry[{}],ToCity[{}],ToState[{}],ToZip[{}],ToCountry[{}]'.format(
                      self.request.get('CallSid'),
                      self.request.get('AccountSid'),
                      self.request.get('From'),
                      self.request.get('To'),
                      self.request.get('CallStatus'),
                      self.request.get('ApiVersion'),
                      self.request.get('Direction'),
                      self.request.get('ForwardedFrom'),
                      self.request.get('FromCity'),
                      self.request.get('FromState'),
                      self.request.get('FromZip'),
                      self.request.get('FromCountry'),
                      self.request.get('ToCity'),
                      self.request.get('ToState'),
                      self.request.get('ToZip'),
                      self.request.get('ToCountry')))
        
        to = self.request.get('To')
        logging.debug('IncomingCall, to: %s', to)

        if to:
            
            if OUTGOING_NUMBERS is None:
                r.say('There is no configured treatment for the called number: {number}.'.format(number=to))
            else:
                # determine if there are enough numbers to provide option treatment
                if (len(OUTGOING_NUMBERS) > 1):
                    # option treatment is the only current treatment
                    with r.gather(action=webapp2.uri_for('choice-selection'), timeout=30, numDigits=1) as g:
                        g.say(OPTION_MESSAGE)
                    
                dial = r.dial(action=webapp2.uri_for('call-end'), timeout=30)
                if (Utility.is_sip(OUTGOING_NUMBERS[0])):
                    dial.sip(OUTGOING_NUMBERS[0])
                else:
                    dial.number(OUTGOING_NUMBERS[0])
                    
        else:
            r.say('There was no indicated called number.')
        
        self.response.headers['Content-Type'] = 'text/xml'
        self.response.write(str(r))

class ChoiceSelection(webapp2.RequestHandler):
    def post(self):
        r = twiml.Response()
        
        logging.debug('IncomingCall, CallSid[{}],AccountSid[{}],From[{}],To[{}],CallStatus[{}],ApiVersion[{}],Direction[{}],ForwardedFrom[{}],FromCity[{}],FromState[{}],FromZip[{}],FromCountry[{}],ToCity[{}],ToState[{}],ToZip[{}],ToCountry[{}],Digits[{}]'.format(
                      self.request.get('CallSid'),
                      self.request.get('AccountSid'),
                      self.request.get('From'),
                      self.request.get('To'),
                      self.request.get('CallStatus'),
                      self.request.get('ApiVersion'),
                      self.request.get('Direction'),
                      self.request.get('ForwardedFrom'),
                      self.request.get('FromCity'),
                      self.request.get('FromState'),
                      self.request.get('FromZip'),
                      self.request.get('FromCountry'),
                      self.request.get('ToCity'),
                      self.request.get('ToState'),
                      self.request.get('ToZip'),
                      self.request.get('ToCountry'),
                      self.request.get('Digits')))
        
        digits = int(self.request.get('Digits'))
        logging.debug('ChoiceSelection, digits: %s', digits)

        dial = r.dial(action=webapp2.uri_for('call-end'), timeout=30)

        if OUTGOING_NUMBERS[digits]:
            if (Utility.is_sip(OUTGOING_NUMBERS[digits])):
                dial.sip(OUTGOING_NUMBERS[digits])
            else:
                dial.number(OUTGOING_NUMBERS[digits])
        else:
            # no phone number for that choice, send to default
            if (Utility.is_sip(OUTGOING_NUMBERS[0])):
                dial.sip(OUTGOING_NUMBERS[0])
            else:
                dial.number(OUTGOING_NUMBERS[0])
        
        self.response.headers['Content-Type'] = 'text/xml'
        self.response.write(str(r))

class CallEnd(webapp2.RequestHandler):
    def post(self):
        r = twiml.Response()
        
        logging.debug('CallEnd, CallSid[{}],AccountSid[{}],From[{}],To[{}],CallStatus[{}],ApiVersion[{}],Direction[{}],ForwardedFrom[{}],FromCity[{}],FromState[{}],FromZip[{}],FromCountry[{}],ToCity[{}],ToState[{}],ToZip[{}],ToCountry[{}],DialCallStatus[{}],DialCallSid[{}],DialCallDuration[{}]'.format(
                      self.request.get('CallSid'),
                      self.request.get('AccountSid'),
                      self.request.get('From'),
                      self.request.get('To'),
                      self.request.get('CallStatus'),
                      self.request.get('ApiVersion'),
                      self.request.get('Direction'),
                      self.request.get('ForwardedFrom'),
                      self.request.get('FromCity'),
                      self.request.get('FromState'),
                      self.request.get('FromZip'),
                      self.request.get('FromCountry'),
                      self.request.get('ToCity'),
                      self.request.get('ToState'),
                      self.request.get('ToZip'),
                      self.request.get('ToCountry'),
                      self.request.get('DialCallStatus'),
                      self.request.get('DialCallSid'),
                      self.request.get('DialCallDuration')))
        
        dial_call_status = self.request.get('DialCallStatus')

        if dial_call_status != 'completed':
            r.say('You have reached my telco. Please leave a message after the tone.')
            r.record(action=webapp2.uri_for('voicemail'), )
            r.say('I did not receive a recording')
        else:
            # TODO: put call record
            pass
        
        self.response.headers['Content-Type'] = 'text/xml'
        self.response.write(str(r))

class Voicemail(webapp2.RequestHandler):
    def post(self):
        r = twiml.Response()
        
        logging.debug('IncomingCall, CallSid[{}],AccountSid[{}],From[{}],To[{}],CallStatus[{}],ApiVersion[{}],Direction[{}],ForwardedFrom[{}],FromCity[{}],FromState[{}],FromZip[{}],FromCountry[{}],ToCity[{}],ToState[{}],ToZip[{}],ToCountry[{}],RecordingUrl[{}],RecordingDuration[{}],Digits[{}]'.format(
                      self.request.get('CallSid'),
                      self.request.get('AccountSid'),
                      self.request.get('From'),
                      self.request.get('To'),
                      self.request.get('CallStatus'),
                      self.request.get('ApiVersion'),
                      self.request.get('Direction'),
                      self.request.get('ForwardedFrom'),
                      self.request.get('FromCity'),
                      self.request.get('FromState'),
                      self.request.get('FromZip'),
                      self.request.get('FromCountry'),
                      self.request.get('ToCity'),
                      self.request.get('ToState'),
                      self.request.get('ToZip'),
                      self.request.get('ToCountry'),
                      self.request.get('RecordingUrl'),
                      self.request.get('RecordingDuration'),
                      self.request.get('Digits')))
        
        # send notification
        if ((VOICEMAIL_EMAIL_NOTIFICATION is not None) and (VOICEMAIL_EMAIL_NOTIFICATION)):
            mail.send_mail(sender="myTelco <{}>".format(VOICEMAIL_EMAIL_NOTIFICATION_SENDER),
                           to=VOICEMAIL_EMAIL_NOTIFICATION,
                           subject="myTelco New Voicemail",
                           body="""
You have a new voicemail message from {}:

{}.mp3
""".format(self.request.get('From'),
           self.request.get('RecordingUrl')))
            
        self.response.headers['Content-Type'] = 'text/xml'
        self.response.write(str(r))
        
application = webapp2.WSGIApplication([
    webapp2.Route('/twiml/incomingCall', handler=IncomingCall, name='incoming-call'),
    webapp2.Route('/twiml/choiceSelection', handler=ChoiceSelection, name='choice-selection'),
    webapp2.Route('/twiml/callEnd', handler=CallEnd, name='call-end'),
    webapp2.Route('/twiml/voicemail', handler=Voicemail, name='voicemail'),
], debug=True)
