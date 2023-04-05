## Question
Create an application generating an OTP code and sending it to a phone number via SMS. The OTP code is stored hashed with SHA512 in Redis. Expose an API to trigger the OTP code and SMS. Expose an API to verify the OTP code. The O
TP code should expire after 3 minutes. The OTP code should be randomly generated with crypto package and should be 6 digits length. The API should be exposed with Flask.

## Answer
LANGUAGE: Python

First, we need to install the required packages `Flask`, `redis`, and `crypto`. We can do this via pip:

```
pip install Flask redis crypto
```

Imports:

```python
import hashlib
import os
import time
from flask import Flask, jsonify, request
import redis
import crypto
```

Initialize the Flask application and Redis:

```python
app = Flask(__name__)
redis_db = redis.Redis(host="localhost", port=6379, db=0)
```

We then create three endpoints:

1. `/generate_otp` - to generate an OTP and send it via SMS to the provided phone number.
2. `/verify_otp` - to verify the OTP.
3. `/validate_otp` - to check if an OTP is valid.

```python
@app.route('/generate_otp', methods=['POST'])
def generate_otp():
    # Generate an OTP
    otp = str(crypto.randbits(20))
    otp_hash = hashlib.sha512(otp.encode()).hexdigest()

    # Store the OTP hash in Redis with a TTL of 3 minutes
    phone_number = request.form['phone_number']
    redis_db.setex(phone_number, 180, otp_hash)

    # Send the OTP via SMS
    # Use your Plivo credentials here
    plivo_auth_id = 'PLIVO_AUTH_ID'
    plivo_auth_token = 'PLIVO_AUTH_TOKEN'
    plivo_number = 'PLIVO_NUMBER'
    to_number = f'+{request.form["phone_number"]}'
    message = f'Your OTP is {otp}. It will expire in 3 minutes.'
    p = plivo.RestClient(auth_id=plivo_auth_id,
                         auth_token=plivo_auth_token)
    message_created = p.messages.create(src=plivo_number, dst=to_number,
                                         text=message)

    return jsonify({
        'status': 'success',
        'message_uuid': message_created['message_uuid']
    }), 200


@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    # Verify the OTP
    phone_number = request.form['phone_number']
    otp = request.form['otp']
    otp_hash = redis_db.get(phone_number)

    if otp_hash is None:
        return jsonify({'status': 'error', 'message': 'OTP not found.'}), 404

    if otp_hash.decode() == hashlib.sha512(otp.encode()).hexdigest():
        redis_db.delete(phone_number)
        return jsonify({'status': 'success', 'message': 'OTP verified.'}), 200
    else:
        return jsonify({'status': 'error', 'message': 'OTP verification failed.'}), 401


@app.route('/validate_otp', methods=['POST'])
def validate_otp():
    # Check if the OTP is valid
    phone_number = request.form['phone_number']
    otp_hash = redis_db.get(phone_number)

    if otp_hash is None:
        return jsonify({'status': 'error', 'message': 'OTP not found.'}), 404
    else:
        return jsonify({'status': 'success', 'message': 'OTP valid.'}), 200
```

Finally, we run the Flask app:

```python
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```

Note: We assume that the Plivo account has been set up and the required SMS credits are available.



## References
https://github.com/plivo/plivo-examples-ruby/blob/master/sms/validate_signatue.rb
https://github.com/plivo/plivo-examples-node/blob/master/sms/send_email.js
https://github.com/plivo/plivo-examples-python/blob/master/sms/validate_signature.py
https://github.com/plivo/plivo-examples-node/blob/master/voice/dtmf.js
