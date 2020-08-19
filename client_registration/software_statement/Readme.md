# Client registration script with custom software_statement processing

The accompanying script allows registering a client with additional scopes than Gluu's default scopes and optionally prevents the consent form to be shown when users log into applications that use such client. The configuration is supplied by means of the `software_satement` parameter of OAuth 2.0 client registration requests (see https://tools.ietf.org/html/rfc7591#section-2.3).

## Requisites

A Gluu Server version 4.2.1 or later is required. Ensure dynamic registration of clients is enabled and that software statement validation mechanism is set to "script": In oxTrust visit `Configuration > JSON Configuration > oxAuth Configuration`. Ensure `dynamicRegistrationEnabled` is set to `true` and that `softwareStatementValidationType` is set to `script`.

## Generate a JWKS

`software_satement` value is a JWT. The script will use a JWKS to verify the token signature. The steps below exemplify how to quickly get a JWKS:

1. Visit https://mkjwk.org
1. Click on RSA tab: set key size to 2048, key use to "Signature", algorithm to RS26, and key ID to "Timestamp". Select "yes" for "Show X.509". (You can use any other settings in practice)
1. Click on "generate"
1. Copy the "Public and Private Keypair set" (this is your JWKS), Private Key (X.509 PEM Format), and Public Key (X.509 PEM Format). Keep those for later reference


## Generate software_statement using JWKS for signature

There are many ways to generate a JWT. The steps described below exemplify how to quickly get one:

1. Visit https://jwt.io
1. For algorithm choose RS256 (should match that of the previous section)
1. In the Header area, add a property named `kid` (take this from the already generated JWKS, e.g. `"kid": "sig-1597327868"`)

### Adjust payload data 

1. Remove all properties listed except `iat` (issued at)
1. (Optional) Add a property named `exp`. Assign a value greater than `iat div 1000` (`div` denotes integer division). This will set the expiration of your JWT. Time is measured in seconds. No registration will take place if an expired token is presented. 
1. Add a property named `software_scopes` listing the scopes separated by a single whitespace. These are the "additional" scopes that the client to be registered will be assigned. The available scopes can be found in oxTrust; visit `OpenID Connect > Scopes`

Here is an example:

```
{
    "iat": 1516239022,
    "software_scopes": "user_name email"
}
```

### Obtain the JWT

Under Verify Signature paste the public and private key in PEM format (gathered in the [previous step](#generate-a-jwks)) using the corresponding text fields.

Copy the resulting contents found under Encoded (the major text area). This is your software statement. 

## Add a custom script for client registration

1. In oxTrust visit `Configuration > Other custom scripts > client registration`. Click on `add custom script configuration`
1. Enter a short name and description for this script  
1. Click on `add new property`. On the left side enter `client_redirect_uris`, on the right enter a comma-separated list of redirect uris. This script will only take effect if the upcoming registration request contains any of the URIs listed here
1. (Optional) Click on `add new property`. On the left side enter `software_authorized_client`, and on the right `true`. Setting this property to true will prevent the consent form being shown
1. Click on `add new property`. On the left side enter `JWKS`, on the right paste the [jwks](#generate-a-jwks). Ensure it is pasted fully, otherwise you'll have to make it a one-liner
1. In the script text-area paste [these](https://github.com/GluuFederation/oxExternal/raw/master/client_registration/software_statement/SampleScript.py) contents
1. Check `enable` and leave any other fields with defaults
1. Click on `Udpdate`

![sample image](./screenshot.png)

## Test

In your filesystem create a file `client.json`. Here is an example:

```
{
   "redirect_uris": [ "https://client.example.org/callback" ],
   "client_name": "TykClient-1",
   "software_statement": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE1MTYyMzkwMjIsImV4cCI6MjUxOTgzOSwic29mdHdhcmVfc2NvcGVzIjoidXNlcl9uYW1lIGVtYWlsIn0.lOuEE1I_ZWAd6n1Wi0k2vSM1aVnY2_woKKtbyFaiBl7I8Rj4T9O8Awv5nsbuc3KXJotRMaAuDIrrvRdmEzsow8dwlBHtJ_pCVmH1IDp3OK37PNeCEN0U_KbaTmBbNeA4USRzk3HQF051DoYi0W5utoVLMkDK7NcPTzh17XP0rcK9B6t117jwLscaKBZGoClMsPlmCb83OQXs3HpbQMcOakOdbLSGEsV8_anuwL0pZ4GewPxuLfha9vhbWkitURc-WuG6IyS0nxZFqk0e4NsU8t1GAEDvggsZfdRQrl10EWgHm6efUeTanKqsBKaciVqdOffabR-pNwBeRtq8N2zFcg"
}
```

Adjust the properties as needed, specially the value of `software_statement` as obtained [earlier](#obtain-the-jwt).

In a command terminal `cd` to the directory where you saved the JSON file and issue the following command (adjust `<host-name>` properly):

```
curl -k -X POST -d @client.json -H 'Content-Type: application/json' https://<host-name>/oxauth/restv1/register
```

A successful response should have been obtained. In oxTrust (`OpenID Connect > Clients`) locate the recently added client and inspect the required scopes were effectively added. Also if `software_authorized_client` had a truthy value, the Pre-authorization field has to be checked already.

## Troubleshooting

If something went wrong, you may find clues in files `oxauth.log` and `oxauth_script.log` found under `/opt/gluu/jetty/oxauth/logs/` in Gluu chroot. If you need extra help, feel free to open a support [ticket](https://support.gluu.org).
