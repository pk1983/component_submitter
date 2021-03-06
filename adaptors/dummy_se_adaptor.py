
from abstracts import securityenforcer as abco
import logging
logger=logging.getLogger("adaptor."+__name__)


class DummySeAdaptor(abco.SecurityEnforcerAdaptor):

    def __init__(self, adaptor_id, template = None):
        super().__init__()

        self.ID = adaptor_id
        self.template = template


        logger.info("SeAdaptor initialised")

    def translate(self):

        logger.info("Starting Setranslation")

    def execute(self):

        logger.info("Starting Seexecution {}".format(self.ID))

    def undeploy(self):

        logger.info("Undeploy the Security in Security Enforcer with id {}".format(self.ID))

    def cleanup(self):

        logger.info("cleaning up for Security Enforcer id {}".format(self.ID))

    def update(self):

        logger.info("updating the component config {}".format(self.ID))
