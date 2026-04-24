# Copy to prestonotes_mcp/.env and fill in. Never commit .env.

# Required: absolute path to your Google Drive "MyNotes" root (same as GDRIVE_BASE_PATH in .cursorrules).
GDRIVE_BASE_PATH="/Users/patrick.presto/Google Drive/My Drive/MyNotes"

# Required for discover_doc: Google Drive folder ID of the MyNotes root folder.
MYNOTES_ROOT_FOLDER_ID="1bVAiFR9J1AizNHj43Rs2ZUDqxpvjZkO9"

# Google account for gcloud (Docs/Drive API). Used by check_google_auth and by tools that call gcloud.
# Leave unset to use gcloud's default account; set to pin one account (must match `gcloud auth list`).
GCLOUD_ACCOUNT="patrick.presto@wiz.io"

# Optional: full login command shown when auth fails (overrides the built-in gcloud auth login ...).
# Use if you use a nonstandard login flow. Example:
# GCLOUD_AUTH_LOGIN_COMMAND=gcloud auth login --account='you@company.com' --enable-gdrive-access --force
GCLOUD_AUTH_LOGIN_COMMAND="gcloud auth login --account=patrick.presto@wiz.io --enable-gdrive-access --force"

# For Embedding data into the vectordb
GOOGLE_API_KEY=op://en3gmzphym2lx3tjkuixirhf6m/theprestos-gemini-api-key-prestoNotes/credential

# Wiz Local MCP AuthN
WIZ_CLIENT_ID=op://en3gmzphym2lx3tjkuixirhf6m/csaprod - presto-admin/username
WIZ_CLIENT_SECRET=op://en3gmzphym2lx3tjkuixirhf6m/csaprod - presto-admin/credential
WIZ_ENV=app
