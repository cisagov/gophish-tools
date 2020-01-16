import pytest

# Inter-project
from pca_assessment.util.validate import *
from pca_assessment.util.validate import FormatError

@pytest.mark.parametrize('email', ["name.last@domain.test", "name.last+phish@domain.test"])
def test_validate_email_valid(email):
    assert validate_email(email)

@pytest.mark.parametrize('email', ["@domain.test", "phish@test"])
def test_validate_email_invalid(email):
    with pytest.raises(FormatError):
        validate_email(email)

@pytest.mark.parametrize('email', ["name.last@domain.test"])
@pytest.mark.parametrize('domain', ["domain.test"])
def test_validate_domain_valid(email, domain):
    assert validate_domain(email, domain)

@pytest.mark.parametrize('email', ["name.last@domain.test"])
@pytest.mark.parametrize('domain', ["test.test"])
def test_validate_domain_invalid(email, domain):
    assert not validate_domain(email, domain)