# YAML mailer.

YAML mailer, written in Python 3.3, parses a YAML file and
uses SMTP to email many people _different_ messages.
YAML mailer is different than typical mass mailers because it is
not meant for emailing many people identical messages.

This is useful to help organize email composition if you want
to email a lot of people similar messages and add
notes of individualization to each message.

# Configuration.
By default, configuration is expected to be in `~/.mailer.yaml`,
but can be changed with the `--config` flag.
See the [example configuration][example-conf].

# Example.
See [example-messages.yaml][example-messages] for an example to
get started with!

```
$ ./yaml-mailer.py example-messages.yaml

Sending message.
  To: bdamos@vt.edu
  Subject: yaml-mailer: Hi Brandon.
  Attach: yaml-mailer.py
Sending message.
  To: bdamos@vt.edu,bdamos+other-to@vt.edu
  CC: bdamos+cc@vt.edu
  BCC: bdamos+bcc@vt.edu
  Subject: yaml-mailer: Testing CC/BCC.
All messages sent successfully.
```

[example-messages]: https://github.com/cilkay/yaml-mailer/blob/master/example-messages.yaml
[example-conf]: https://github.com/cilkay/yaml-mailer/blob/master/example-conf.yaml
