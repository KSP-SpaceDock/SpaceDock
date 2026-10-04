from KerbalStuff.objects import User


def test_objects_user() -> None:
    # Arrange
    # Create new user
    user = User(username="Test User", email="test_user@example.com")
    password_clear_text = "deRp*qnEX&<6i`=<oFy3j+%ww3<-k*:4"
    user.set_password(password_clear_text)

    # Act
    correct_password_match = user.check_password(password_clear_text)
    incorrect_password_match = user.check_password("password1!")

    # Assert
    assert correct_password_match is True, "user.check_password should return True for matching passwords"
    assert incorrect_password_match is False, "user.check_password should return False for nonmatching passwords"
