from org.gluu.model.custom.script.type.scim import ScimType
from org.gluu.util import StringHelper, ArrayHelper
from java.util import Arrays, ArrayList
from org.gluu.oxtrust.service import PersonService
from org.gluu.service.cdi.util import CdiUtil
from org.gluu.oxtrust.model import GluuCustomPerson
#Comment the line below if you are using Gluu CE 3.x
from org.gluu.oxtrust.model.scim import ScimCustomPerson

import java

class ScimEventHandler(ScimType):

    def __init__(self, currentTimeMillis):
        self.currentTimeMillis = currentTimeMillis

    def init(self, configurationAttributes):
        print "ScimEventHandler (init): Initialized successfully"
        return True   

    def destroy(self, configurationAttributes):
        print "ScimEventHandler (destroy): Destroyed successfully"
        return True   

    def getApiVersion(self):
        #return 2 if you want the post* methods executed
        #return 3 if you also want the get* methods executed
        #return 4 if you also want the postSearch* methods executed
        return 4

    # user is an instance of ScimCustomPerson in CE 4.0 for all user-related methods
    def createUser(self, user, configurationAttributes):

        print "ScimEventHandler (createUser): Current id = " + user.getUid()

        testProp1 = configurationAttributes.get("testProp1").getValue2()
        testProp2 = configurationAttributes.get("testProp2").getValue2()

        print "ScimEventHandler (createUser): testProp1 = " + testProp1
        print "ScimEventHandler (createUser): testProp2 = " + testProp2

        return True

    def updateUser(self, user, configurationAttributes):
        personService = CdiUtil.bean(PersonService)
        # oldUser is an instance of GluuCustomPerson
        oldUser = personService.getPersonByUid(user.getUid())
        print "ScimEventHandler (updateUser): Old displayName %s" % oldUser.getDisplayName()
        print "ScimEventHandler (updateUser): New displayName %s" % user.getDisplayName()
        return True

    def deleteUser(self, user, configurationAttributes):
        print "ScimEventHandler (deleteUser): Current id = " + user.getUid()
        return True

    def createGroup(self, group, configurationAttributes):
        print "ScimEventHandler (createGroup): Current displayName = " + group.getDisplayName()
        return True

    def updateGroup(self, group, configurationAttributes):
        print "ScimEventHandler (updateGroup): Current displayName = " + group.getDisplayName()
        return True

    def deleteGroup(self, group, configurationAttributes):
        print "ScimEventHandler (deleteGroup): Current displayName = " + group.getDisplayName()
        return True
        
    def postCreateUser(self, user, configurationAttributes):
    	# user is the instance as modified in createUser method. Modifications applied here will not
    	# take effect in the output of the API and will not be persisted automatically to database either 
        return True

    def postUpdateUser(self, user, configurationAttributes):
    	# user is the instance as modified in updateUser method. Modifications applied here will not
    	# take effect in the output of the API and will not be persisted automatically to database either
        return True

    def postDeleteUser(self, user, configurationAttributes):
        return True

    def postUpdateGroup(self, group, configurationAttributes):
        return True

    def postCreateGroup(self, group, configurationAttributes):
        return True

    def postDeleteGroup(self, group, configurationAttributes):
        return True
    
    #This method is available in CE 4.1 onwards
    def getUser(self, user, configurationAttributes):
        return True
    
    #This method is available in CE 4.1 onwards
    def getGroup(self, group, configurationAttributes):
        return True

	# This method is available in CE 4.2 onwards
	# results is an instance of org.gluu.persist.model.PagedResult<ScimCustomPerson>
    def postSearchUsers(self, results, configurationAttributes):
    	# person = results.getEntries().get(0)
    	# person.setUid("fake_uid")
    	# Modifications on results variable will take effect on the output of the API call
    	return True

	# This method is available in CE 4.2 onwards
	# results is an instance of org.gluu.persist.model.PagedResult<org.gluu.oxtrust.model.GluuGroup>
    def postSearchGroups(self, results, configurationAttributes):
    	# Modifications on results variable will take effect on the output of the API call
    	return True