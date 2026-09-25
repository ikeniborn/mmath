# Operator-assisted account recovery

Initial email addresses are login identifiers, not verified mailbox ownership. The operator must establish the requester's identity outside this application before recovery. No HTTP reset endpoint or outgoing email exists.

Run the command in the API container. It requires the exact account email, asks for explicit confirmation, prompts for the new password twice without echoing it, updates the Argon2id hash and revokes all active sessions in one database transaction. Do not pass a password on the command line or paste it into a log.

```bash
docker compose --env-file .env -f compose.yaml -f deploy/compose.public.yaml exec api /app/backend/.venv/bin/python -m mental_math.accounts.cli parent@example.com
```

The account must sign in again with the new password. Record the recovery ticket and operator identity outside the application; never record the password.
