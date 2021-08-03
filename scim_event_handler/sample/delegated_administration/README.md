# Implementing delegated administration in SCIM

Custom scripts can be used to implement advanced use cases that arise in SCIM usage. In this document, a sample script that facilitates the deployment of delegated user administration in the context of SCIM for your organization is presented.

To learn about SCIM custom scripting visit [this](https://www.gluu.org/docs/gluu-server/4.3/user-management/scim-scripting/) page. 

## Requisites and audience

- Gluu Server version 4.3+ with SCIM component installed
- A basic understanding of the SCIM protocol
- Some grasp of Java and Python

## Assumptions

- The communication between the consumer (client) and the service takes place in a controlled environment, like a secured network segment within your corporate LAN
- Administration is delegated to several parties where every party will be able to retrieve/update/search a restricted set of users. Parties don't have shared users.
- A set of users is conformed by those users whose share a common value for a given attribute. In this particular example, we'll use the known `o`/`organizationName` LDAP attribute
- User creation requests must supply a value for `o` which has to match the value the given party is supposed to "manage". Payloads with no `o` will be rejected. 
- Operations targetted at resources other than users, eg. groups, fido devices, etc., will be rejected by default

## Implementation details

To be able to identify which service call corresponds to which party, SCIM requests are expected to contain a query parameter with a JWT-encoded value. A designated claim in the JWT will contain the identifier of the "organization" the request is targeting. These two aspects (the parameter and the JWT claim name) are configurable in the script (ie. not hard-coded).

## Configuration instructions

### Script deployment

1. Log into oxTrust and navigate to `Configuration` > `Other custom Scripts` > `SCIM`
 
1. Expand the only row shown (labeled `scim_event_handler`)

1. Click on add new property. On the left enter `paramName`, on the right `id_token`

1. Again click on add new property. On the left enter `jwtClaimName`, on the right `o`

1. Remove the "test" properties

1. Paste [these contents](https://github.com/GluuFederation/oxExternal/raw/master/scim_event_handler/sample/delegated_administration/scim.py) in the script text area

1. Click on the `Enabled` check box

1. Click on `update` at the bottom of the page

### Add the attribute to the user extension

1. In oxTrust navigate to `Configuration` > `Attributes`

1. In the search box enter `organization` and hit the button

1. In the results, click on the row corresponding to the `o` attribute

1. Ensure that: a) `Multivalued` is not checked, b) `Include in SCIM extension` is checked, and c) `Active` is selected for `Status` 

## Test

Now you should be able to send requests passing an extra param called `id_token` whose contents will help determine if the call is allowed or denied (HTTP status code 403) for the user in question. To learn more about how the rules for execution of SCIM operations work, take a look at this [page](https://www.gluu.org/docs/gluu-server/4.3/user-management/scim-scripting/#defining-rules-for-execution-of-scim-operations).

Note for the case of searches, results will only contain users that match the expected `o` value.

Finally, recall that given that `o` is part of the user extension (ie. not a core attribute per SCIM spec), user payloads would typically look like this:

```
{
  "schemas": [
    "urn:ietf:params:scim:schemas:core:2.0:User",
    "urn:ietf:params:scim:schemas:extension:gluu:2.0:User"
  ],
  ...
  "userName": "...",
  "urn:ietf:params:scim:schemas:extension:gluu:2.0:User": {
    "o": "acme"
  }
}
```
