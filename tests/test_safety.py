from app.safety import assess_message


def test_possible_emergency_is_blocked_and_escalated() -> None:
    result = assess_message("I have severe chest pain and trouble breathing")

    assert result.emergency is True
    assert result.blocked is True
    assert "possible_emergency" in result.flags


def test_general_question_is_allowed() -> None:
    result = assess_message("What should I write down before a doctor visit?")

    assert result.emergency is False
    assert result.blocked is False
    assert result.flags == ()


def test_medication_request_is_flagged_without_emergency_block() -> None:
    result = assess_message("What dose of this medication should I take?")

    assert result.emergency is False
    assert result.blocked is False
    assert "medication_guidance" in result.flags