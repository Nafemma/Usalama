import pytest
from unittest.mock import patch, mock_open
from datetime import datetime
from modules.mother import mother_module as mm


# 1. Test calculate_pregnancy_info
@patch("modules.mother.mother_module.datetime")
def test_calculate_pregnancy_info_first_trimester(mock_datetime):
    start_date = "2025-05-01"
    mock_datetime.today.return_value = datetime(2025, 6, 1)
    mock_datetime.strptime = datetime.strptime

    result = mm.calculate_pregnancy_info(start_date)

    assert result["week_number"] == 4
    assert result["trimester"] == "First Trimester"
    assert result["due_date"] == "2026-02-05"

@patch("modules.mother.mother_module.datetime")
def test_calculate_pregnancy_info_second_trimester(mock_datetime):
    start_date = "2025-01-01"
    mock_datetime.today.return_value = datetime(2025, 5, 1)
    mock_datetime.strptime = datetime.strptime

    result = mm.calculate_pregnancy_info(start_date)
    assert 17 <= result["week_number"] <= 18
    assert result["trimester"] == "Second Trimester"


# 2. Test get_health_tip
# @patch("modules.mother.mother_module.TIPS", {
#     4: "Eat healthy",
#     12: "Exercise gently",
#     20: "Stay hydrated"
# })
# def test_get_health_tip():
#     assert mm.get_health_tip(10) == "Eat healthy"
#     assert mm.get_health_tip(12) == "Exercise gently"
#     assert mm.get_health_tip(21) == "Stay hydrated"
#     assert mm.get_health_tip(1) == "Stay positive and follow medical advice."

@patch("modules.mother.mother_module.TIPS", {
    "First Trimester": {
        "tips": [
            "Tip 1: Rest well",
            "Tip 2: Take folic acid"
        ]
    },
    "Second Trimester": {
        "tips": [
            "Tip 3: Do light exercise",
            "Tip 4: Eat iron-rich foods"
        ]
    },
    "Third Trimester": {
        "tips": [
            "Tip 5: Practice breathing",
            "Tip 6: Pack your hospital bag"
        ]
    }
})
@patch("modules.mother.mother_module.random.choice")
def test_get_health_tip_first_trimester(mock_random_choice):
    mock_random_choice.return_value = "Tip 2: Take folic acid"
    result = mm.get_health_tip(week_number=34)
    assert result == "Tip 2: Take folic acid"
    mock_random_choice.assert_called_once()


@patch("modules.mother.mother_module.TIPS", {
    "First Trimester": {"tips": []},
    "Second Trimester": {"tips": []},
    "Third Trimester": {"tips": []}
})
def test_get_health_tip_empty_trimester():
    result = mm.get_health_tip(week_number=30)
    assert result == "Stay positive and follow medical advice."


@patch("modules.mother.mother_module.TIPS", {})
def test_get_health_tip_no_data():
    result = mm.get_health_tip(week_number=10)
    assert result == "Stay positive and follow medical advice."


# 3. Test log_mood
@patch("builtins.open", new_callable=mock_open)
@patch("modules.mother.mother_module.datetime")
def test_log_mood(mock_datetime, mock_file):
    mock_datetime.now.return_value = datetime(2025, 7, 6)
    response = mm.log_mood("user123", "Happy")
    
    mock_file().write.assert_called_once()
    assert "Mood 'Happy' logged." == response


# 4. Test check_danger_signs
@patch("modules.mother.mother_module.DANGER_SIGNS", {
    "bleeding": "Seek medical help immediately",
    "dizziness": "May indicate low blood pressure"
})
def test_check_danger_signs():
    symptoms = ["Bleeding", "nausea"]
    result = mm.check_danger_signs(symptoms)

    assert isinstance(result, dict)
    assert "bleeding" in result
    assert result["bleeding"] == "Seek medical help immediately"

@patch("modules.mother.mother_module.DANGER_SIGNS", {})
def test_check_danger_signs_none_found():
    result = mm.check_danger_signs(["Fatigue"])
    assert result == "No danger signs found."


# 5. Test logout
def test_logout():
    assert mm.logout() == "You have been logged out. Stay healthy!"
