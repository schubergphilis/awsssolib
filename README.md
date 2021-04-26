# awsssolib
A library to help automate AWS SSO activities as it is still not supported by Boto

DEPRECATION WARNING
===================

This library is now part https://github.com/schubergphilis/awsapilib and thus all development on this repo will stop.



The library supports below AWS SSO actions:

1. Get Groups
1. Get Users
1. Get Accounts
1. Create Permission Sets
1. Assign custom policy to a permission set
1. Update Permission sets
1. Associate user/groups to an Account with a particular permission set
1. Disassociate user/groups from an Account with a particular permission set

#### Below is a snippet on how to get started with the library:

```
import os
from awsssolib.awsssolib import Sso
os.environ['AWS_ACCESS_KEY_ID']=''
os.environ['AWS_SECRET_ACCESS_KEY']=''
os.environ['AWS_DEFAULT_REGION']=''
os.environ['AWS_SESSION_TOKEN']=''
sso_connection = Sso('arn:aws:iam::<<account_id>>:role/<<role_name>>')
for group in sso_connection.groups:
     print(group.name)
```
The role should have access to sso and sso-directory
