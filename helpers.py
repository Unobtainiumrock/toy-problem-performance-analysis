import numpy as np


def convert_to_native(value):
    if isinstance(value, (np.integer, np.int64)):
        return int(value)
    elif isinstance(value, (np.floating, np.float64)):
        return float(value)
    elif isinstance(value, np.ndarray):
        return value.tolist()  # Convert arrays to lists if needed
    else:
        return value


# Function to group consecutive numbers into ranges
# The function assumes that any nums array given may not already be sorted
# incase its reused elsewhere.
def group_consecutive_numbers(nums):
  nums = np.sort(nums)
  ranges = []
  start = prev = nums[0]
  
  for num in nums[1:]:
      if num == prev + 1:
          prev = num
      else:
          ranges.append((start, prev))
          start = prev = num
          
  ranges.append((start, prev))
  
  return ranges
