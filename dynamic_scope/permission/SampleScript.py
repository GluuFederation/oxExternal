# oxAuth is available under the MIT License (2008). See http://opensource.org/licenses/MIT for full text.
# Copyright (c) 2016, Gluu
#
# Author: Yuriy Movchan
#

from org.xdi.model.custom.script.type.scope import DynamicScopeType
from org.xdi.oxauth.service import UserService
from org.xdi.util import StringHelper, ArrayHelper
from java.util import Arrays, ArrayList

import java

class DynamicScope(DynamicScopeType):
    def __init__(self, currentTimeMillis):
        self.currentTimeMillis = currentTimeMillis

    def init(self, configurationAttributes):
        print "Permission dynamic scope. Initialization"

        print "Permission dynamic scope. Initialized successfully"

        return True   

    def destroy(self, configurationAttributes):
        print "Permission dynamic scope. Destroy"
        print "Permission dynamic scope. Destroyed successfully"
        return True   

    # Update Json Web token before signing/encrypring it
    #   dynamicScopeContext is org.xdi.oxauth.service.external.context.DynamicScopeExternalContext
    #   configurationAttributes is java.util.Map<String, SimpleCustomProperty>
    def update(self, dynamicScopeContext, configurationAttributes):
        print "Permission dynamic scope scope. Update method"

        dynamicScopes = dynamicScopeContext.getDynamicScopes()
        authorizationGrant = dynamicScopeContext.getAuthorizationGrant()
        user = dynamicScopeContext.getUser()
        jsonWebResponse = dynamicScopeContext.getJsonWebResponse()
        claims = jsonWebResponse.getClaims()

        # Iterate through list of dynamic scopes in order to add custom scopes if needed
        print "Permission dynamic scope. Dynamic scopes:", dynamicScopes
        for dynamicScope in dynamicScopes:

            # Add role  if there is scope = permission
            if (StringHelper.equalsIgnoreCase(dynamicScope, "permission")):
                roles = userService.getCustomAttribute(user, "role");
                if roles != None:
                    claims.setClaim("role", role.getValues())
                continue

        return True

    def logout(self, configurationAttributes, requestParameters):
        return True

    def getApiVersion(self):
        return 1
