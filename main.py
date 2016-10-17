##!/usr/bin/env python
#
#"""main.py - This file includes generic landing page handler and handlers that are called by taskqueue and/or cronjobs."""

import logging

from flask import Flask

app = Flask(__name__)

@app.route('/')
def welcome():
    return 'App is serving'

@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500

##from google.appengine.api import mail, app_identity
#from api import HangmanAPI
##from models import User
#
#
##class SendReminderEmail(webapp2.RequestHandler):
##    def get(self):
##        """Send a reminder email to each User with an email about games.
##        Called every hour using a cron job"""
##        app_id = app_identity.get_application_id()
##        users = User.query(User.email != None)
##        for user in users:
##            subject = 'This is a reminder!'
##            body = 'Hello {}, try out Guess A Number!'.format(user.name)
##            # This will send test emails, the arguments to send_mail are:
##            # from, to, subject, body
##            mail.send_mail('noreply@{}.appspotmail.com'.format(app_id),
##                           user.email,
##                           subject,
##                           body)
#
##
##class UpdateAverageMovesRemaining(webapp2.RequestHandler):
##    def post(self):
##        """Update game listing announcement in memcache."""
##        GuessANumberApi._cache_average_attempts()
##        self.response.set_status(204)
##
#
#app = webapp2.WSGIApplication([], debug=True)
