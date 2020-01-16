import pytest

# Inter-project
from pca_assessment.tests.conftest import *

class TestParse:
    def test_email_parse(self, target_object, target_json):
        assert target_object.as_dict() == Target.parse(target_json[0]).as_dict()
    
    def test_group_parse(self, group_object, group_json):
        assert group_object.as_dict() == Group.parse(group_json).as_dict()
    
    def test_smtp_parse(self, smtp_object, smtp_json):
        assert smtp_object.as_dict() == SMTP.parse(smtp_json).as_dict()
        
    def test_template_parse(self, template_object, template_json):
        assert template_object.as_dict() == Template.parse(template_json).as_dict()
    
    def test_page_parse(self, page_object, page_json):
        assert page_object.as_dict() == Page.parse(page_json).as_dict()
    
    def test_campaign_parse(self, campaign_object, campaign_json):
        assert campaign_object.as_dict() == Campaign.parse(campaign_json).as_dict()
        
    def test_assessment_parse(self, assessment_object, assessment_json):
        assert assessment_object.as_dict() == Assessment.parse(assessment_json).as_dict()
