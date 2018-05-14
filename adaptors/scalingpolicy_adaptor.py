"""
MiCADO Submitter Engine ScalingPolicy Adaptor
--------------------------------------

An adaptor for TOSCA to "scaling_policy.yaml" adaptor.
"""

import subprocess
import logging

from toscaparser.tosca_template import ToscaTemplate

import utils
from abstracts import policykeeper as abco
from abstracts.exceptions import AdaptorCritical

logger=logging.getLogger("adaptor."+__name__)

SIMPLE_POL = ("tosca.policies.Scaling.Performance.Consumption.Simple")

class ScalingPolicyAdaptor(abco.PolicyKeeperAdaptor):

    def __init__(self, adaptor_id, template=None):

        super().__init__()
        if template and not isinstance(template, ToscaTemplate):
            raise AdaptorCritical("Template is not a valid TOSCAParser object")

        self.ID = adaptor_id
        self.tpl = template
        try:
            self.sp_data = utils.get_yaml_data(
                            "/var/lib/micado/alert-generator/scaling_policy.yaml")
        except FileNotFoundError:
            self.sp_data = {"services": {"_sample": {"scaledown": 0, "scaleup": 100}}}
        logger.info("ScalingPolicyAdaptor ready!")

    def translate(self):
        """ Translate from TOSCA to scaling_policy.yaml """
        logger.info("Starting ScalingPolicy translation")

        for policy in self.tpl.policies:
            if policy.type in SIMPLE_POL:
                min_cpu = policy.get_property_value("min_cpu_consumption")
                max_cpu = policy.get_property_value("max_cpu_consumption")
                for target in policy.targets:
                    target = f'{self.ID[:8]}_{target}'
                    self.sp_data["services"].update(
                        {target: {"scaledown": min_cpu, "scaleup": max_cpu}})

        utils.dump_order_yaml(
            self.sp_data, f'/var/lib/micado/alert-generator/scaling_policy.yaml')

    def execute(self):
        """ Reset the alertgenerator """
        logger.info("Starting ScalingPolicy execution")
        # Permit dry-runs (no MiCADO in test env)
        try:
            #subprocess.run(["micado", "refresh"], check=True)
            logger.info(f'subprocess.run([\"micado\", \"refresh\"], check=True)')
        except subprocess.CalledProcessError:
            logger.error("Cannot refresh alertgenerator")
            raise AdaptorCritical("Cannot refresh alertgenerator")

    def undeploy(self):
        """ Remove the relevant policy from scaling_policy.yaml """
        logger.info(f'Remove policy in scaling_policy with id {self.ID}')
        try:
            for key in self.sp_data["services"].keys():
                if self.ID[:8] in key:
                    self.sp_data["services"].pop(key)
        # hacky
        except RuntimeError:
            for key in self.sp_data["services"].keys():
                if self.ID[:8] in key:
                    self.sp_data["services"].pop(key)

        utils.dump_order_yaml(
            self.sp_data, f'/var/lib/micado/alert-generator/scaling_policy.yaml')

    def cleanup(self):
        """ Not implemented """
        logger.info("cleaning up pk id {}".format(self.ID))

    def update(self):
        """ Update the scaling_policy file with new data """
        self.undeploy()
        self.translate()
        logger.info("Updating the component config {}".format(self.ID))