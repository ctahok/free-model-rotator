# Credential Recovery Procedure for Free Model Rotator

When encountering `auth failed (401)` errors for a provider in `hermes auth list`, follow this recovery procedure:

## Step 1: Identify bad credentials
```bash
hermes auth list
# Look for entries marked with: "auth failed (401) (re-auth may be required)"
# Note the credential ID (e.g., id=aac167)
```

## Step 2: Remove bad credential
```bash
hermes auth remove <provider> <credential-id>
# Example: hermes auth remove openrouter aac167
```

## Step 3: Verify remaining credentials
```bash
hermes auth list
# Ensure no "auth failed" markers remain for providers you need
```

## Step 4: Re-add valid credentials if needed
If all credentials for a provider were removed:
```bash
hermes auth add <provider> --api-key "<valid-api-key>"
```

## Step 5: Reset free-model-rotator state
```bash
# Create or reset state.json
cat > $HERMES_HOME/skills/free-model-rotator/state.json << EOF
{
  "current_index": 0,
  "exhausted": [],
  "last_reset": "$(date -u +%Y-%m-%dT%H:%M:%S.%6Z)",
  "session_start": "$(date -u +%Y-%m-%dT%H:%M:%S.%6Z)"
}
EOF
```

## Step 6: Optional - Lock to working provider during recovery
To bypass rotator while verifying fix:
```bash
hermes config set model.provider <working-provider>
hermes config set model.default <working-model>
# Example: hermes config set model.provider nvidia
#          hermes config set model.default nvidia/nemotron-3-super-120b-a12b:free
systemctl --user restart hermes-gateway.service
```

## Step 7: Validate configuration
```bash
hermes config show
# Confirm provider and model are set correctly
```

## Prevention
- Check credential health weekly: `hermes auth list`
- Remove unused credentials to reduce attack surface
- Monitor logs for 401 errors: `journalctl --user -u hermes-gateway.service -g "401\|auth failed"`