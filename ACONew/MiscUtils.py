import sys

def normalize(array):
	sumOfElements = sum(array)
	return [Element/sumOfElements for Element in array] if sumOfElements != 0 else []

def cumulative(maximum, array):
        """
        (int, array) ---> array

        Returns the cumulative array from the given array making sure that the prefix sum never exceeds the maximum

        >>> cumulative (4.0, [0.5, 0.6, 1.0, 1.2])
        [0.0, 0.5, 1.1, 2.1, 3.3]

        >>> cumulative (3.0, [0.5, 0.6, 1.0, 1.2])
        [0.0, 0.5, 1.1, 2.1, 3.0]

        """

        res = [0.0]
        for element in array:
                res.append(min([maximum, res[-1]+element]))
        return res

def scale(array):
        """
        (array) ---> array

        Returns an array where each element gets scaled by the maximum element of the array

        >>> scale ([1.0, 2.0, 3.0, 4.0, 5.0])
        [0.2, 0.4, 0.6, 0.8, 1.0]

        >>> scale ([1, 2, 3, 4, 5])
        [0, 0, 0, 0, 1]
        
        """
        
	maxElement = max(array)
	return [Element/maxElement for Element in array] if maxElement != 0 else []
