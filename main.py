##!/usr/bin/env python
#
#"""main.py - This file includes generic landing page handler and handlers that are called by taskqueue and/or cronjobs."""

import logging
import webapp2
from google.appengine.api import app_identity
from google.appengine.api import mail
from api import HangmanAPI

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

#class SetAnnouncementHandler(webapp2.RequestHandler):
#    def get(self):
#        """Set Announcement in Memcache."""
#        # TODO 1
#        ConferenceApi._cacheAnnouncement()



class SendConfirmationEmailHandler(webapp2.RequestHandler):
    def post(self):
        """Send email regarding challenge."""

        mail.send_mail(
            'noreply@%s.appspotmail.com' % (
                app_identity.get_application_id()),     # from
            self.request.get('email'),                  # to
            'You have been challenged by {}'.format(self.get.request.get('challenger')),            # subj
            '{}'.format(self.request.get(gameInfo))
        )

class SendConfirmationEmailHandler(webapp2.RequestHandler):
    def post(self):
        """Send email regarding challenge."""

        mail.send_mail(
            'noreply@%s.appspotmail.com' % (
                app_identity.get_application_id()),# from
            self.request.get('email'),# to
            '{} Completed Your Challenge'.format(self.get.request.get('challenged')),            # subj
            '{}'.format(self.request.get(gameInfo))
        )

class SendReminderEmail(webapp2.RequestHandler):
    def get(self):
        """Send a reminder email to each User with an email about games.
        Called every hour using a cron job"""
        app_id = app_identity.get_application_id()
        users = User.query(User.email != None)
        reminder = []
        for user in users:
            if(Game.query(ndb.AND(Game.game_over == False,
                                  ndb.AND(Game.cancel == False,
                                          Game.challenged == user.key))).count() >0):
                reminder.append(user)
        for user in reminder:
            subject = 'This is a reminder!'
            body = 'Hello {}, it is your move!'.format(user.name)
            # This will send test emails, the arguments to send_mail are:
            # from, to, subject, body
            mail.send_mail('noreply@{}.appspotmail.com'.format(app_id),
                           user.email,
                           subject,
                           body)

app = webapp2.WSGIApplication([
    ('/crons/send_reminder', SendReminderEmail),
    ('/tasks/send_confirmation_email', SendConfirmationEmailHandler),
    ('/tasks/send_end_game_email', SendEndGameEmailHandler)
], debug=True)
##from google.appengine.api import mail, app_identity
#from api import HangmanAPI
##from models import User
#
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
