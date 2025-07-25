class UserStatus:
    COUPLED = "coupled"
    IDLE = "idle"
    IN_SEARCH = "in_search"
    PARTNER_LEFT = "partner_left"

    possible_states = [COUPLED, IDLE, IN_SEARCH, PARTNER_LEFT]

import os
from flask import Flask

app = Flask(__name__)

@app.route("/")
def healthz():
    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
