# oxAuth is available under the MIT License (2008). See http://opensource.org/licenses/MIT for full text.
# Copyright (c) 2016, Gluu
#


from org.xdi.service.cdi.util import CdiUtil
from org.xdi.model.custom.script.type.user import UserRegistrationType
from org.xdi.service import MailService
from org.gluu.oxtrust.ldap.service import IPersonService
from org.xdi.ldap.model import GluuStatus
from org.xdi.util import StringHelper, ArrayHelper
from java.util import Arrays, ArrayList
from org.xdi.config.oxtrust import AppConfiguration
from org.gluu.oxtrust.util import ServiceUtil

import java

class UserRegistration(UserRegistrationType):
    def __init__(self, currentTimeMillis):
        self.currentTimeMillis = currentTimeMillis

    def init(self, configurationAttributes):
        print "User registration. Initialization"

        self.enable_user = StringHelper.toBoolean(configurationAttributes.get("enable_user").getValue2(), False)

        print "User registration. Initialized successfully"

        return True   

    def destroy(self, configurationAttributes):
        print "User registration. Destroy"
        print "User registration. Destroyed successfully"
        return True   

    # User registration init method
    #   user is org.gluu.oxtrust.model.GluuCustomPerson
    #   requestParameters is java.util.Map<String, String[]>
    #   configurationAttributes is java.util.Map<String, SimpleCustomProperty>
    def initRegistration(self, user, requestParameters, configurationAttributes):
        print "User registration. Init method"

        return True

    # User registration pre method
    #   user is org.gluu.oxtrust.model.GluuCustomPerson
    #   requestParameters is java.util.Map<String, String[]>
    #   configurationAttributes is java.util.Map<String, SimpleCustomProperty>
    def preRegistration(self, user, requestParameters, configurationAttributes):
        print "User registration. Pre method"

	userStatus = GluuStatus.INACTIVE


        # Disable/Enable registered user
        user.setStatus(userStatus)
        self.guid=StringHelper.getRandomString(16)
        user.setGuid(self.guid)
        return user

    # User registration post method
    #   user is org.gluu.oxtrust.model.GluuCustomPerson
    #   requestParameters is java.util.Map<String, String[]>
    #   configurationAttributes is java.util.Map<String, SimpleCustomProperty>
    def postRegistration(self, user, requestParameters, configurationAttributes):
        print "User registration. Post method"
	appConfiguration= CdiUtil.bean(AppConfiguration)
        servername = appConfiguration.getApplianceUrl()
        mailService = CdiUtil.bean(MailService)
        subject = "Confirmation mail for user registration"
        body = "User Registered for %s. Please Confirm User Registration by clicking url: %s/confirm/registration?code=%s" % (user.getMail(),servername,self.guid)
        print body
        mailService.sendMail(user.getMail(), subject, body)
        return True

    def confirmRegistration(self, user, requestParameters, configurationAttributes):
	print "User registration. Confirm method"
	confirmation_code = ServiceUtil.getFirstValue(requestParameters, "code")
        personService = CdiUtil.bean(IPersonService)
        if not confirmation_code:
	    	print "User registration. Confirm method. Confirmation code not existin tin request"
	if confirmation_code == user.getGuid():
		user.setStatus(GluuStatus.ACTIVE)
                user.setGuid("")
                personService.updatePerson(user)
		self.enable_user = True
	return True

    def getApiVersion(self):
        return 1
