class VitalsCalculations:

    class MeanArterialPressure:
        @staticmethod
        def calculate_map(sys_bp, dia_bp):

            # Check for missing values
            if sys_bp is None:
                raise ValueError ("Missing systolic blood pressure")

            if dia_bp is None:
                raise ValueError ("Missing diastolic blood pressure")
            
            # Convert to string numbers tofloat if necessary
            sys_bp = float(sys_bp)
            dia_bp = float(dia_bp)
            
            # Check if systolic and diastolic are valid numbers
            if not isinstance(sys_bp, (int, float)) or not isinstance(dia_bp, (int, float)):
                raise ValueError ("Systolic and diastolic blood pressure must be numbers")

            # Check if systolic less than diastolic
            if sys_bp <= dia_bp:
                raise ValueError ("Systolic blood pressure must be greater than diastolic blood pressure")

            map = (1/3 * sys_bp) + (2/3 * dia_bp)
            return round(map,2)

