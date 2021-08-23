# Visit https://www.gluu.org/docs/gluu-server/user-management/scim-scripting/ to learn more
from org.gluu.model.custom.script.type.scim import ScimType
from org.gluu.oxauth.model.jwt import Jwt, JwtClaimName
from org.gluu.oxtrust.ws.rs.scim2 import BaseScimWebService

import java
import sys
import datetime

class ScimEventHandler(ScimType):

    def __init__(self, currentTimeMillis):
        self.currentTimeMillis = currentTimeMillis

    def init(self, configurationAttributes):
        try:
            self.req_param = configurationAttributes.get("paramName").getValue2()
            self.claim = configurationAttributes.get("jwtClaimName").getValue2()    

            if self.req_param != None and self.claim != None:
                print "ScimEventHandler (init): Initialized successfully"
                return True
            else:
                print "ScimEventHandler (init): One or more config properties are missing"
        except:
            print "ScimEventHandler (init)", sys.exc_info()[1]
            
        print "ScimEventHandler (init): There were problems during initialization. SCIM script won't get executed"
        return False   

    def destroy(self, configurationAttributes):
        print "ScimEventHandler (destroy): Destroyed successfully"
        return True   

    def getApiVersion(self):
        return 5

    def createUser(self, user, configurationAttributes):
        return True

    def updateUser(self, user, configurationAttributes):
        return True

    def deleteUser(self, user, configurationAttributes):
        return True

    def createGroup(self, group, configurationAttributes):
        return True

    def updateGroup(self, group, configurationAttributes):
        return True

    def deleteGroup(self, group, configurationAttributes):
        return True
        
    def postCreateUser(self, user, configurationAttributes):
        return True

    def postUpdateUser(self, user, configurationAttributes):
        return True

    def postDeleteUser(self, user, configurationAttributes):
        return True

    def postUpdateGroup(self, group, configurationAttributes):
        return True

    def postCreateGroup(self, group, configurationAttributes):
        return True

    def postDeleteGroup(self, group, configurationAttributes):
        return True
    
    def getUser(self, user, configurationAttributes):
        return True
    
    def getGroup(self, group, configurationAttributes):
        return True
        
    def postSearchUsers(self, results, configurationAttributes):
        return True

    def postSearchGroups(self, results, configurationAttributes):
        return True
        
    def manageResourceOperation(self, context, entity, payload, configurationAttributes):
        print "ScimEventHandler (manageResourceOperation): SCIM endpoint invoked is %s (HTTP %s)" \
        % (context.getPath(), context.getMethod())
        
        if context.getResourceType() != "User":
            return self.errorResponse(403, "Not a user operation")
        
        try:            
            expected_org = self.extractOrganization(context.getQueryParams())
             
            if expected_org == None:
                return self.errorResponse(400, "No '%s' claim found in token" % self.claim)
            
            if expected_org != entity.getAttribute("o"):
                return self.errorResponse(403, "The user target of this SCIM operation does not match " + \
                    "the expected value %s=%s" % (self.claim, expected_org))
            
            print "ScimEventHandler (manageResourceOperation): SCIM operation is allowed"
            return None
        except:
            print "ScimEventHandler (manageResourceOperation): Error ", sys.exc_info()[1]
            return self.errorResponse(500, str(sys.exc_info()[1]))
    
    def manageSearchOperation(self, context, searchRequest, configurationAttributes):
        print "ScimEventHandler (manageSearchOperation): SCIM endpoint invoked is %s (HTTP %s)" \
        % (context.getPath(), context.getMethod())
        
        if context.getResourceType() != "User":
            return self.errorResponse(403, "Not a user operation")
        
        try:            
            expected_org = self.extractOrganization(context.getQueryParams())
            
            if expected_org == None:
                return self.errorResponse(400, "No '%s' claim found in token" % self.claim)
        
            # build a SCIM equality filter using 'o' attribute part of user extension 
            context.setFilterPrepend("urn:ietf:params:scim:schemas:extension:gluu:2.0:User:o eq \"%s\"" % expected_org)
            return None       
        except:
            print "ScimEventHandler (manageSearchOperation): Error ", sys.exc_info()[1]
            return self.errorResponse(500, str(sys.exc_info()[1]))

# Misc functions

    # queryParams is an instance of javax.ws.rs.core.MultivaluedMap<String,String> 
    def extractOrganization(self, queryParams):

        # retrieve jwt value
        value = queryParams.getFirst(self.req_param)        
        if value == None:
            raise Exception("Missing query parameter %s" % self.req_param)
            
        jwt = Jwt.parse(value)            
        
        jwt_claims = jwt.getClaims()
        
        exp = jwt_claims.getClaimAsString(JwtClaimName.EXPIRATION_TIME)
        if exp != None:
            exp_date_timestamp = float(exp)
            exp_date = datetime.datetime.fromtimestamp(exp_date_timestamp)
            if exp_date < datetime.datetime.now():
                raise Exception("Presented token is expired")            
        
        return jwt_claims.getClaimAsString(self.claim)


    def errorResponse(self, code, err):
        return BaseScimWebService.getErrorResponse(code, None, err)
