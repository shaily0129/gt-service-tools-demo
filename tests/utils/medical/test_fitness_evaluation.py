# import unittest
# from gt_service_tools.utils.medical.fitness_evaluation import FitnessEvaluation

# class TestFitnessEvaluation(unittest.TestCase):
#     def setUp(self):
#         self.fitness_evaluator = FitnessEvaluation()

#     def test_calc_fitness_category_excellent(self):
#         # Test for Excellent fitness category
#         gender = 'male'
#         age = 30
#         weight = 80
#         height = 180
#         body_fat_percentage = 10
#         body_mass_index = 22
#         vo2_max = 55

#         result = self.fitness_evaluator.calc_fitness_category(gender, age, weight, height, body_fat_percentage, body_mass_index, vo2_max)
#         self.assertEqual(result, 'Excellent')

#     def test_calc_fitness_category_good(self):
#         # Test for Good fitness category
#         gender = 'female'
#         age = 25
#         weight = 65
#         height = 160
#         body_fat_percentage = 23
#         body_mass_index = 23.4
#         vo2_max = 40

#         result = self.fitness_evaluator.calc_fitness_category(gender, age, weight, height, body_fat_percentage, body_mass_index, vo2_max)
#         self.assertEqual(result, 'Good')

#     def test_calc_fitness_category_average(self):
#         # Test for Average fitness category
#         gender = 'male'
#         age = 40
#         weight = 90
#         height = 175
#         body_fat_percentage = 20
#         body_mass_index = 28
#         vo2_max = 45

#         result = self.fitness_evaluator.calc_fitness_category(gender, age, weight, height, body_fat_percentage, body_mass_index, vo2_max)
#         self.assertEqual(result, 'Average')

#     def test_calc_fitness_category_below_average(self):
#         # Test for Below Average fitness category
#         gender = 'female'
#         age = 35
#         weight = 70
#         height = 165
#         body_fat_percentage = 28
#         body_mass_index = 26.8
#         vo2_max = 35

#         result = self.fitness_evaluator.calc_fitness_category(gender, age, weight, height, body_fat_percentage, body_mass_index, vo2_max)
#         self.assertEqual(result, 'Below Average')

# if __name__ == '__main__':
#     unittest.main()