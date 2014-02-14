#!/usr/bin/env python3.3
#
# yaml-mailer.py
# 2014.01.30
#
# Brandon Amos <http://bamos.io>

import argparse
from email.encoders import encode_base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from os.path import basename,expanduser
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

  # Make non-list fields lists.
  for field in ['to', 'cc', 'bcc', 'attach']:
    if field in msg and not isinstance(msg[field], list):
      msg[field] = [msg[field]]

  multi_msg = MIMEMultipart()
  multi_msg['From'] = smtp['from']
  multi_msg['To'] = ",".join(msg['to'])
  multi_msg['Subject'] = msg['subject']
  if 'cc' in msg: multi_msg['CC'] = ",".join(msg['cc'])
  multi_msg.attach(MIMEText(msg['contents']))

  if 'attach' in msg:
    for f_name in msg['attach']:
      part = MIMEBase('application', "octet-stream")
      with open(f_name, 'rb') as f: part.set_payload(f.read())
      encode_base64(part)
      part.add_header('Content-Disposition',
          'attachment; filename="' + basename(f_name) + '"')
      multi_msg.attach(part)

  print("Sending message.")
  print("  To: " + ",".join(msg['to']))
  if 'cc' in msg: print("  CC: " + ",".join(msg['cc']))
  if 'bcc' in msg: print("  BCC: " + ",".join(msg['bcc']))
  print("  Subject: " + msg['subject'])
  if 'attach' in msg: print("  Attach: " + ",".join(msg['attach']))
  server.sendmail(smtp['from'], msg['to'], multi_msg.as_string())
  if 'bcc' in msg:
    for bcc in msg['bcc']:
      server.sendmail(smtp['from'], bcc, multi_msg.as_string())

print("All messages sent successfully.")
server.close()
