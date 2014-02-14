#!/usr/bin/env python3.3
#
# yaml-mailer.py
# 2014.01.30
#
# Brandon Amos <http://bamos.io>

import argparse
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os.path import expanduser
import smtplib
import sys
import yaml

def die(msg, code=42): print('Error: ' + msg); sys.exit(code);
def check_key(tag, dict_obj, key):
  if key not in dict_obj:
    die(tag + " does not contain '" + key + "' key.")

parser = argparse.ArgumentParser(description='Mail people with YAML.')
parser.add_argument('messages_yaml', type=str)
parser.add_argument('--config', type=str,
    default=expanduser("~")+"/.yaml-mailer.yaml")
args = parser.parse_args()

with open(args.messages_yaml, 'r') as f: yaml_contents = yaml.load(f)
with open(args.config, 'r') as f: yaml_config = yaml.load(f)

check_key("Yaml config", yaml_config, 'smtp')
smtp = yaml_config['smtp']
for key in ['server', 'port', 'tls', 'user', 'password']:
  check_key("Yaml config - smtp", smtp, key)

server = smtplib.SMTP(smtp['server'], smtp['port'])
server.ehlo_or_helo_if_needed()
if smtp['tls']: server.starttls()
server.login(smtp['user'], smtp['password'])

check_key("Yaml file", yaml_contents, 'messages')
messages = yaml_contents['messages']
for msg in messages:
  for key in ['to', 'subject', 'contents']:
    check_key('Message with contents: ' + str(msg), msg, key)

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
