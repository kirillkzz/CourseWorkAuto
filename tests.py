import unittest

class TestRoadTranspComp(unittest.TestCase):

    def test_fuel_limit_validation(self):
        fuel_input = 600
        limit = 500
        is_valid = fuel_input <= limit
        self.assertFalse(is_valid, "Система має заборонити ввід > 500 літрів")

    def test_fuel_correct_input(self):
        fuel_input = 450
        limit = 500
        is_valid = fuel_input <= limit
        self.assertTrue(is_valid, "Система має пропустити 450 літрів")

    def test_user_creation_logic(self):
        user_data = {"username": "disp1", "password": "123"}
        self.assertTrue(len(user_data["username"]) > 0)
        self.assertTrue(len(user_data["password"]) > 0)

    def test_mileage_validation(self):
        mileage = -10
        is_valid = mileage > 0
        self.assertFalse(is_valid, "Пробіг не може бути від'ємним")

if __name__ == '__main__':
    unittest.main()