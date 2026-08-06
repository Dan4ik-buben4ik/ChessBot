class ErroneousDataException(BaseException):
    def __init__(self, passed_data, expected_data):
        super(ErroneousDataException, self).__init__(f"Erroneous data passed int the function\nPassed data: {passed_data}\nExpected data: {expected_data}")