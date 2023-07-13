# from django.test import TestCase
# from my_farm.models import Cattle
# from datetime import date
#
#
# class CattleModelTestCase(TestCase):
#     def test_model_creation(self):
#         # Create an instance of Cattle
#         cattle = Cattle.objects.create(
#             name='Test Cattle',
#             gender='Heifer',
#             breed='Angus',
#             birth_date=date.today(),  # Provide a valid birth date value
#             entry_date=date.today(),
#             comments='Test comments'
#         )
#
#         # Perform assertions to verify the expected behavior
#         self.assertEqual(cattle.name, 'Test Cattle')
#         self.assertEqual(cattle.gender, 'Heifer')
#         self.assertEqual(cattle.breed, 'Angus')
#         self.assertEqual(cattle.birth_date, date.today())  # Assert the birth date value
#         self.assertEqual(cattle.entry_date, date.today())
#         self.assertEqual(cattle.comments, 'Test comments')
#         self.assertFalse(cattle.deleted)
#
#         # Additional assertions for optional fields
#         self.assertIsNone(cattle.acquisition_method)
#         self.assertIsNone(cattle.loss_method)
#         self.assertIsNone(cattle.end_date)
#         self.assertFalse(cattle.picture)
#
#     def test_model_deletion(self):
#         # Create an instance of Cattle
#         cattle = Cattle.objects.create(name='Test Cattle')
#
#         # Delete the cattle
#         cattle.delete()
#
#         # Verify that the deleted flag is set to True
#         self.assertTrue(cattle.deleted)
