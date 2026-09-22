from app.matching.status import status_from_event


def test_application_submitted_maps_to_applied():
    assert status_from_event("APPLICATION_SUBMITTED") == "APPLIED"


def test_application_received_maps_to_applied():
    assert status_from_event("APPLICATION_RECEIVED") == "APPLIED"


def test_assessment_maps_to_assessment():
    assert status_from_event("ASSESSMENT_REQUESTED") == "ASSESSMENT"


def test_interview_events_map_to_interview():
    assert status_from_event("INTERVIEW_INVITED") == "INTERVIEW"
    assert status_from_event("INTERVIEW_COMPLETED") == "INTERVIEW"


def test_rejection_maps_to_rejected():
    assert status_from_event("REJECTION") == "REJECTED"


def test_offer_maps_to_offer():
    assert status_from_event("OFFER") == "OFFER"


def test_withdrawn_maps_to_withdrawn():
    assert status_from_event("WITHDRAWN") == "WITHDRAWN"


def test_unknown_event_maps_to_unknown():
    assert status_from_event("OTHER") == "UNKNOWN"
    assert status_from_event(None) == "UNKNOWN"
    assert status_from_event("SOMETHING_UNEXPECTED") == "UNKNOWN"