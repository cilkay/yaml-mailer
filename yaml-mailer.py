#!/usr/bin/env python3.3
#
# yaml-mailer.py
# 2014.01.30
#
# Brandon Amos <http://bamos.io>

import argparse
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import sys
import yaml

parser = argparse.ArgumentParser(description='Mail people with YAML.')
parser.add_argument('yaml_file', type=str)
args = parser.parse_args()

f = open(args.yaml_file, 'r')
yaml_contents = yaml.load(f)
f.close()

smtp = yaml_contents['smtp']
messages = yaml_contents['messages']

server = smtplib.SMTP(smtp['server'], smtp['port'])
server.ehlo_or_helo_if_needed()
if smtp['tls']: server.starttls()
server.login(smtp['user'], smtp['password'])

for msg in messages:
  # TODO: Check that every expected field is in the message.

  if 'attach' in msg:
    print("Error: Attachments not supported. Not sending.")
    sys.exit(42)

  for field in ['to', 'cc', 'bcc']:
    if field in msg and not isinstance(msg[field], list):
      msg[field] = [msg[field]]

  multi_msg = MIMEMultipart()
  multi_msg['From'] = smtp['from']
  multi_msg['To'] = ",".join(msg['to'])
  multi_msg['Subject'] = msg['subject']
  if 'cc' in msg: multi_msg['CC'] = ",".join(msg['cc'])
  text = MIMEText(msg['contents'])
  #text.add_header("Content-Disposition", "inline")
  multi_msg.attach(text)

  print("Sending message.")
  print("  To: " + ",".join(msg['to']))
  if 'cc' in msg: print("  CC: " + ",".join(msg['cc']))
  if 'bcc' in msg: print("  BCC: " + ",".join(msg['bcc']))
  print("  Subject: " + msg['subject'])
  server.sendmail(smtp['from'], msg['to'], multi_msg.as_string())
  if 'bcc' in msg:
    for bcc in msg['bcc']:
      server.sendmail(smtp['from'], bcc, multi_msg.as_string())

print("All messages sent successfully.")
server.close()
