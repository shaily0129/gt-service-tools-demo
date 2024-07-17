# Below is a very basic fitness categorization algorithm.  It is not meant to be a complete solution.  It is just meant to be a starting point for more advanced algorithms.
import unittest

class FitnessEvaluation:
    def __init__(self):
        pass
    

    def _score_body_fat_percentage(gender, body_fat_percentage):
        # Body Fat Percentage scoring
        score = 0
        if gender.lower() == 'male':
            if body_fat_percentage < 14:
                score += 3
            elif 14 <= body_fat_percentage <= 17:
                score += 2
            elif 18 <= body_fat_percentage <= 24:
                score += 1
        elif gender.lower() == 'female':
            if body_fat_percentage < 21:
                score += 3
            elif 21 <= body_fat_percentage <= 24:
                score += 2
            elif 25 <= body_fat_percentage <= 31:
                score += 1
        return score

    def _score_vo2_max(gender, vo2_max):
        # VO2 Max scoring
        score = 0
        if gender.lower() == 'male':
            if vo2_max > 52:
                score += 3
            elif 47 <= vo2_max <= 51:
                score += 2
            elif 40 <= vo2_max <= 46:
                score += 1
        elif gender.lower() == 'female':
            if vo2_max > 42:
                score += 3
            elif 37 <= vo2_max <= 41:
                score += 2
            elif 32 <= vo2_max <= 36:
                score += 1
        return score
    
    def _score_body_mass_index(gender, body_mass_index):
        # Body Mass Index scoring
        score = 0
        if gender.lower() == 'male':
            if body_mass_index < 25:
                score += 3
            elif 25 <= body_mass_index <= 29:
                score += 2
            elif 30 <= body_mass_index <= 35:
                score += 1
        elif gender.lower() == 'female':
            if body_mass_index < 22:
                score += 3
            elif 22 <= body_mass_index <= 24:
                score += 2
            elif 25 <= body_mass_index <= 29:
                score += 1
        return score


    def _calculate_body_mass_index(weight_kg, height_cm):
        if height_cm <=0 or weight_kg <= 0:
            raise ValueError("Height and weight must be greater than 0")
        if height_cm <= 0:
            raise ValueError("Height must be greater than 0")
        if weight_kg <= 0:
            raise ValueError("Weight must be greater than 0")
        
        bmi = weight_kg / (height_cm / 100) * 2.20462262185

        return round(bmi, 1) 


    def calc_fitness_category(self, gender, age, weight, height, body_fat_percentage, body_mass_index, vo2_max):
        # Initialize score
        score = 0
        
        if body_fat_percentage is not None:
            score += self._score_body_fat_percentage(gender, body_fat_percentage)
        
        if body_mass_index is None and weight is not None and height is not None:
            body_mass_index = self._calculate_body_mass_index(weight, height)
        
        if body_mass_index is not None:
            score += self._score_body_mass_index(gender, body_mass_index)
        
        if vo2_max is not None:
            score += self._score_vo2_max(gender, vo2_max)        

        
        # Determine fitness category based on score
        if score >= 7:
            return "Excellent"
        elif 5 <= score <= 6:
            return "Good"
        elif 3 <= score <= 4:
            return "Average"
        else:
            return "Below Average"
