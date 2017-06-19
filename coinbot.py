#!/usr/bin/env python

"""
Author: John D. Anderson
Email: jander43@vols.utk.edu
Description: BTC bot for GDAX
Usage:
    coinbot.py slackchat
    coinbot.py report [--period|slack|terminal]
    coinbot.py price
"""

# libs
import os
import sys
import time
import multiprocessing
import GDAX
import slackclient
import apitoken
import procmanager

# constants
TOKENLS = ('SLACK_API_TOKEN', 'SLACK_BOT_ID')
CHANNEL = 'gdax'
COINBOTMSG = '{1}: BTC-USD/${0}'
COINBOTCMDS = '''
Commands:
    report (stop|<seconds>)
    price
'''


# funcs
def warn(msg, exit=1):
    # check for exit
    if exit:
        sys.exit(msg)
    else:
        print msg


# classes
class CoinBot(object):
    def __init__(self):
        # create command dictionary
        self._commands = {
                         'price': self._format_msg,
                         'report': self._report_process
                         }

        # generate msg format
        self._msg = COINBOTMSG

        # get public endpoint
        self._pubapi = GDAX.PublicClient(product_id='BTC-USD')

        # get tokens
        self._tokens = apitoken.get_toke(token_names=TOKENLS)

        # storage for slack instance
        self._slackapi = None

        # storage for report process id
        self._report_pid = procmanager.ProcManager()

    def _terminal_out(self, msg):
        print msg

    def _slack_out(self, msg, chan=CHANNEL):
        # send message
        self._slackapi.api_call('chat.postMessage', as_user='true',
                                channel=chan,
                                text=msg)

    def _format_msg(self, data=None):
        # get current BTC data
        return self._msg.format(self._pubapi.getProductTicker()['price'],
                                time.asctime()
                                )

    def _get_slack_instance(self):
        # get slack token
        slk_token = self._tokens['SLACK_API_TOKEN']

        # update storage
        self._slackapi = slackclient.SlackClient(slk_token)

    def _parse_chat_msg(self, bot_id, data):
        # storage for response
        response = None

        # get msg from data
        msg = data['text']

        # first split on bot_id
        words = ''.join(msg.split('<@{0}>'.format(bot_id)))

        # now get command + args
        cmd = words.split()

        # check first word
        if cmd[0] in self._commands:
            response = self._commands[cmd[0]](cmd)

        else:
            # send usage statement
            response = COINBOTCMDS

        # post to slack
        self._slack_out(response, data['channel'])

    def _report_process(self, arguments):
        # check for stop
        if len(arguments) < 2:
            # no args
            response = 'What frequency? i.e. report "seconds"'

        elif 'stop' in arguments[1]:
            # terminate
            self._report_pid.terminate()

            # respond
            response = 'Stopping reporting cycle ...'

        else:
            try:
                # check period
                period = int(arguments[1])

                # create outlet
                outlet = [self._slack_out]

                # check existing process
                self._report_pid.terminate()

                # then launch a new one
                process = multiprocessing.Process(target=self._post_outlets,
                                                  args=(outlet, period)
                                                  )

                # start
                process.start()

                # store
                self._report_pid.ppid = process

                # get response
                response = 'Reporting every {0}s'.format(period)

            except (ValueError, IndexError) as error:
                # can't read arg
                response = 'Check argument \'{0}\''.format(arguments[1])

        # respond
        return response

    def _post_outlets(self, outlets, period):
        # report cycle
        while 1:
            try:
                # get msg / post msg / sleep
                msg = self._format_msg()
                for out in outlets:
                    out(msg)
                time.sleep(period)
            except KeyboardInterrupt:
                warn('\nShutting report cycle down ...')

    def price(self, data=None):
        print self._format_msg()

    def slackchat(self):
        # get slack instance
        self._get_slack_instance()

        # get bot id
        bot_id = self._tokens['SLACK_BOT_ID']

        if self._slackapi.rtm_connect():
            while True:
                try:
                    # get conversations
                    messages = self._slackapi.rtm_read()
                    for data in messages:
                        if 'text' in data and bot_id in data['text']:
                            # parse text for commands
                            self._parse_chat_msg(bot_id, data)
                    time.sleep(1)

                except KeyboardInterrupt:
                    warn('\nShutting @coinbot down ...')

    def report(self, period=5, slack=None, terminal=None):
        # storage for outlets
        outlets = list()

        # check period
        if type(period) is not int:
            warn('--period argument must be an integer')

        # check outlet
        if slack:
            # get slack instance
            self._get_slack_instance()

            # turn on slack
            outlets.append(self._slack_out)

        if terminal:
            # turn on terminal outlet
            outlets.append(self._terminal_out)

        if not any(outlets):
            # turn on terminal outlet
            outlets.append(self._terminal_out)
            warn('No outlet specified, defaulting to terminal', exit=0)

        # enter report cycle
        self._post_outlets(outlets, period)


# executable
if __name__ == '__main__':

    # get fire
    import fire

    # launch
    fire.Fire(CoinBot)
