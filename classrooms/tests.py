from django.test import TestCase

import time
import datetime










# def countdown(stop):
#     while True:
#         difference = stop - datetime.datetime.now()
#         if difference.days < 0:
#             print("Already Expired")
#             break
#
#         count_hours, rem = divmod(difference.seconds, 3600)
#         count_minutes, count_seconds = divmod(rem, 60)
#         if difference.days == 0 and count_hours == 0 and count_minutes == 0 and count_seconds == 0:
#             print("Good bye!")
#             break
#         print('The count is: '
#               + str(difference.days) + " day(s) "
#               + str(count_hours) + " hour(s) "
#               + str(count_minutes) + " minute(s) "
#               + str(count_seconds) + " second(s) "
#               )
#         time.sleep(1)
#
#
# end_time = datetime.datetime(2023, 4, 16, 20, 12, 0)
# countdown(end_time)




# def bubble_sort(array):
#     n = len(array)  # [10, 30, 20]
#
#     for i in range(n):  # 3
#         # Create a flag that will allow the function to
#         # terminate early if there's nothing left to sort
#         already_sorted = True
#
#         # Start looking at each item of the list one by one,
#         # comparing it with its adjacent value. With each
#         # iteration, the portion of the array that you look at
#         # shrinks because the remaining items have already been
#         # sorted.
#         for j in range(n - i - 1):  # 2
#             if array[j] > array[j + 1]:
#                 # If the item you're looking at is greater than its
#                 # adjacent value, then swap them
#                 array[j], array[j + 1] = array[j + 1], array[j]
#
#                 # Since you had to swap two elements,
#                 # set the `already_sorted` flag to `False` so the
#                 # algorithm doesn't finish prematurely
#                 already_sorted = False
#
#         # If there were no swaps during the last iteration,
#         # the array is already sorted, and you can terminate
#         if already_sorted:
#             break
#     return array

#
# arr = [10, 100, 800, 1, 20, 40, 4, 5, 30, 40, 50]
# print(bubble_sort(arr))

