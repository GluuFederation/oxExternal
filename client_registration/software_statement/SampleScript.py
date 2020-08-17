from org.gluu.oxauth.model.jwt import Jwt, JwtClaimName
from org.gluu.oxauth.service import ScopeService
from org.gluu.model.custom.script.type.client import ClientRegistrationType
from org.gluu.service.cdi.util import CdiUtil
from org.gluu.util import StringHelper, ArrayHelper

from java.lang import Boolean
from java.util import Arrays, ArrayList, HashSet
from java.util.stream import Collectors, Stream

import datetime
import java
import sys

class ClientRegistration(ClientRegistrationType):
    def __init__(self, currentTimeMillis):
        self.currentTimeMillis = currentTimeMillis

    def init(self, configurationAttributes):
        print "Client registration. Initialization"
        
        prop = "client_redirect_uris"
        if not configurationAttributes.containsKey(prop):
            print "Client registration. Initialization. Property '%s' is mandatory" % prop
            return False
        else:
            self.clientRedirectUrisSet = self.prepareClientRedirectUris(configurationAttributes.get(prop).getValue2())
            
        prop = "JWKS"
        if not configurationAttributes.containsKey(prop):
            print "Client registration. Initialization. Property '%s' is mandatory" % prop
            return False
        else:
            # JSON string expected: { "keys": [ ... ] }
            self.jwks = configurationAttributes.get(prop).getValue2()
        
        # Used if signature algorithm belongs to HMAC family
        prop = "shared_secret"
        self.shared_secret = configurationAttributes.get(prop).getValue2() if configurationAttributes.containsKey(prop) else None
        
        prop = "software_authorized_client"
        if not configurationAttributes.containsKey(prop):
            print "Client registration. Initialization. Assuming '%s' = False" % prop
            self.software_authorized_client = False
        else:
            self.software_authorized_client = Boolean.valueOf(configurationAttributes.get(prop).getValue2())

        print "Client registration. Initialized successfully"
        return True   

    def destroy(self, configurationAttributes):
        print "Client registration. Destroy"
        print "Client registration. Destroyed successfully"
        return True   

    def createClient(self, registerRequest, client, configurationAttributes):
        print "Client registration. CreateClient"

        redirectUris = client.getRedirectUris()
        print "Client registration. Client's redirect URIs are: %s" % redirectUris
        
        match = False
        for redirectUri in redirectUris:
            if self.clientRedirectUrisSet.contains(redirectUri):
                print "Client registration. Match found for client %s based on redirect_uri %s" % (client.getClientId(), redirectUri)
                match = True
                break
        
        if not match:
            print "Client registration. No match was found for client %s based on redirect_uri" % client.getClientId()
            return True
            
        statement = client.getSoftwareStatement()
        try:
            if StringHelper.isEmpty(statement): 
                print "Client registration. No software statement found for client"
            else:
                print "Client registration. Parsing statement as JWT"
                jwt = Jwt.parse(statement)
                
                allowed_scopes = jwt.getClaims().getClaimAsString("software_scopes")
                print "Client registration. Software scopes are: %s" % allowed_scopes                
                allowed_scopes = StringHelper.split(allowed_scopes, " ")
                
                self.setClientScopes(client, allowed_scopes)
                client.setTrustedClient(self.software_authorized_client)
        except:
            print "Exception: ", sys.exc_info()[1]
            
        return True
            

    # Update client entry before persistent it
    #   registerRequest is org.gluu.oxauth.client.RegisterRequest
    #   client is org.gluu.oxauth.model.registration.Client
    #   configurationAttributes is java.util.Map<String, SimpleCustomProperty>
    def updateClient(self, registerRequest, client, configurationAttributes):
        print "Client registration. UpdateClient method"
        return True

    # This method is invoked if softwareStatementValidationType = script in your oxAuth JSON configuration
    # and your JWT software statement is signed with an algorithm belonging to the HMAC family  
    # context is an instance of org.gluu.oxauth.service.external.context.DynamicClientRegistrationContext
    def getSoftwareStatementHmacSecret(self, context):
        return self.shared_secret

    # This method is invoked if softwareStatementValidationType = script in your oxAuth JSON configuration
    # context is an instance of org.gluu.oxauth.service.external.context.DynamicClientRegistrationContext
    def getSoftwareStatementJwks(self, context):
        # Returns a JWKS as a JSON string 
        print "Client registration. JWKS called"
        return self.jwks
        
    def getApiVersion(self):
        return 2

    def prepareClientRedirectUris(self, redirectUris):
        clientRedirectUrisSet = HashSet()

        if StringHelper.isEmpty(redirectUris):
            print "Client registration. Empty redirect URIs list"
            return clientRedirectUrisSet    

        clientRedirectUrisArray = StringHelper.split(redirectUris, ",")
        if ArrayHelper.isEmpty(clientRedirectUrisArray):
            print "Client registration. Empty redirect URIs list"
        
        return Stream.of(clientRedirectUrisArray).collect(Collectors.toSet())


    def isExpired(self, jwt):
        print "Client registration. Checking JWT expiration"
        try:
            exp_date = jwt.getClaims().getClaimAsDate(JwtClaimName.EXPIRATION_TIME)
            print "Client registration. JWT exp is %s" % exp_date    
            expired = exp_date < datetime.datetime.now()
        except:
            print "Exception: ", sys.exc_info()[1]
        print "Client registration. JWT has %s expired" % ("" if expired else "not yet")
        return expired


    def setClientScopes(self, client, requiredScopes):
        
        if requiredScopes == None or len(requiredScopes) == 0:
            print "Client registration. Allowed scopes list is empty"
            return

        newScopes = client.getScopes()
        scopeService = CdiUtil.bean(ScopeService)

        for scopeName in requiredScopes:
            scope = scopeService.getScopeById(scopeName)
            if not scope.isDefaultScope():
                newScopes = ArrayHelper.addItemToStringArray(newScopes, scope.getDn())

        print "Client registration. Resulting scopes will be: %s" % newScopes
        client.setScopes(newScopes)
