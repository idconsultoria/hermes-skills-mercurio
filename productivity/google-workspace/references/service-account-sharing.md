# Service Account Sharing — Cross-Account Drive Access

## Problem

Service accounts (`*.iam.gserviceaccount.com`) and user OAuth accounts have **separate Drive scopes**. A folder created by one is invisible (`404 Not Found`) to the other until explicitly shared.

### Direction 1: Service account can't access user-owned resources
```
HttpError 404: File not found: <user_folder_id>
```
**Fix:** Share via user OAuth: `$GAPI drive share <FILE_ID> --email "sa@project.iam.gserviceaccount.com" --role writer`

### Direction 2: User OAuth can't access service-account-owned resources
Same 404 but the folder was created by the SA. The SA already has access — no sharing needed for the SA. To give user access, share FROM the service account side.

## Detection
When a Drive API call returns 404 for a known-valid file ID, check ownership:
```bash
$GAPI drive get <FILE_ID>
```
If the owner email has a different domain (`@gmail.com` vs `@project.iam.gserviceaccount.com`), cross-account sharing is needed.

## Best practice
For project folders that both accounts need:
1. Create with either account
2. Immediately share with the other
3. Both can now operate on the folder
