# Visit https://www.gluu.org/docs/gluu-server/user-management/scim-scripting/ to learn more
from org.gluu.oxauth.model.jwt import Jwt, JwtClaimName
from org.gluu.model.custom.script.type.scim import ScimType

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
        
    def allowResourceOperation(self, context, entity, configurationAttributes):
        print "ScimEventHandler (allowResourceOperation): SCIM endpoint invoked is %s (HTTP %s)" \
        % (context.getPath(), context.getMethod())
        
        ptmap = context.getPassthroughMap()
        
        if context.getResourceType() != "User":
            ptmap.put("error", "Not a user operation")
            return False
        
        try:            
            expected_org = self.extractOrganization(context.getQueryParams())
             
            if expected_org == None:
                ptmap.put("error", "No '%s' claim found in token" % self.claim)
                return False                
            
            if expected_org != entity.getAttribute("o"):
                ptmap.put("error", "The user target of this SCIM operation does not match " + \
                    "the expected value %s=%s" % (self.claim, expected_org))
                return False
            
            print "ScimEventHandler (allowResourceOperation): SCIM operation is allowed"
            return True
        except:
            print "ScimEventHandler (init): Error ", sys.exc_info()[1]
            ptmap.put("error", str(sys.exc_info()[1])) 
        
        return False 
    
    def allowSearchOperation(self, context, configurationAttributes):
        print "ScimEventHandler (allowSearchOperation): SCIM endpoint invoked is %s (HTTP %s)" \
        % (context.getPath(), context.getMethod())
        
        ptmap = context.getPassthroughMap()
        
        if context.getResourceType() != "User":
            ptmap.put("error", "Not a user operation")
            return None
        
        try:            
            expected_org = self.extractOrganization(context.getQueryParams())
            
            if expected_org == None:
                ptmap.put("error", "No '%s' claim found in token" % self.claim)
                return None
        
            # build a SCIM equality filter using 'o' attribute part of user extension 
            return "urn:ietf:params:scim:schemas:extension:gluu:2.0:User:o eq \"%s\"" % expected_org         
        except:
            print "ScimEventHandler (init): Error ", sys.exc_info()[1]
            ptmap.put("error", str(sys.exc_info()[1]))
        
        return None
    
    def rejectedResourceOperationResponse(self, context, entity, configurationAttributes):
        return self.buildDenyMessage(context.getPassthroughMap().get("error"))
    
    def rejectedSearchOperationResponse(self, context, configurationAttributes):
        return self.buildDenyMessage(context.getPassthroughMap().get("error"))

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
        
    def buildDenyMessage(self, err):
        if err != None:
            err = ". " + err
        return "Operation not allowed" + err
