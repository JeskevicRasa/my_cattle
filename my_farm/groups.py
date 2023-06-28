from dateutil.relativedelta import relativedelta
from .models import Cattle


class GroupNumbers:

    def __init__(self, group_name, group_data):
        self.group_name = group_name
        self.group_data = group_data
        self.start_date_count = 0
        self.end_date_count = 0
        self.count_difference = 0
        self.birth_count = 0
        self.purchase_count = 0
        self.gift_count = 0
        self.death_count = 0
        self.sold_count = 0
        self.consumed_count = 0
        self.gifted_count = 0

    def __repr__(self):
        return self.group_name

    def quantity(self, start_date_groups, end_date_groups):

        self.start_date_count = len(start_date_groups[self.group_name])
        self.end_date_count = len(end_date_groups[self.group_name])
        self.count_difference = self.end_date_count - self.start_date_count

    def acquisition_loss(self, start_date, end_date):

        # print(self.group_name)
        # print(self.group_data)

        filter_acquisition_loss_dates = [
            cattle for cattle in self.group_data
            if (
                    ('entry_date' in cattle and cattle['entry_date'] is not None and start_date <= cattle[
                        'entry_date'] <= end_date)
                    or ('end_date' in cattle and cattle['end_date'] is not None and start_date <= cattle[
                'end_date'] <= end_date)
            )
        ]

        for item in filter_acquisition_loss_dates:
            if 'acquisition_method' in item:
                if item['acquisition_method'] == 'Birth':
                    self.birth_count += 1
                elif item['acquisition_method'] == 'Purchase':
                    self.purchase_count += 1
                elif item['acquisition_method'] == 'Gift':
                    self.gift_count += 1
            if 'loss_method' in item:
                if item['loss_method'] == 'Death':
                    self.death_count += 1
                elif item['loss_method'] == 'Sold':
                    self.sold_count += 1
                elif item['loss_method'] == 'Consumed':
                    self.consumed_count += 1
                elif item['loss_method'] == 'Gifted':
                    self.gifted_count += 1

class GroupsManagement:
    def __init__(self):
        self.groups: list[GroupNumbers] = []

    def calculate_groups(self, estimation_date):
        cattle_list = list(Cattle.objects.values())

        groups = {
            'Cows': [cattle for cattle in cattle_list if cattle['gender'] == 'Cow'],

            'Calves': [
                cattle for cattle in cattle_list if cattle['gender'] in ['Heifer', 'Bull']
                and 0 <= self.calculate_age(cattle['birth_date'], estimation_date) < 12],

            'Young Heifer': [
                cattle for cattle in cattle_list if cattle['gender'] == 'Heifer'
                and 12 <= self.calculate_age(cattle['birth_date'],
                estimation_date) < 24],

            'Adult Heifer': [
                cattle for cattle in cattle_list if cattle['gender'] == 'Heifer'
                and self.calculate_age(cattle['birth_date'], estimation_date) >= 24],

            'Young Bull': [
                cattle for cattle in cattle_list if cattle['gender'] == 'Bull'
                and 12 <= self.calculate_age(cattle['birth_date'], estimation_date) < 24],

            'Adult Bull': [
                cattle for cattle in cattle_list if cattle['gender'] == 'Bull'
                and self.calculate_age(cattle['birth_date'], estimation_date) >= 24],
        }


        return groups

    def add_group(self, group_name, estimation_date):
        groups = self.calculate_groups(estimation_date)
        group_data = groups.get(group_name, {})
        self.groups[group_name] = group_data



#         '''

#Explanation:
#
# The add_group method takes two parameters: group_name and estimation_date.
#
# These parameters are used to calculate the groups using the calculate_groups method.
#
# groups variable is assigned the dictionary of groups returned by the calculate_groups method.
#
# group_data is initialized as an empty list using the get method on the groups dictionary. If the group_name exists in the dictionary,
# it will return the corresponding list of cattle; otherwise, it will return an empty list.
#
# Finally, the group_data list is appended to the self.groups list, which keeps track of all the groups created.
# Note: Make sure that the GroupNumbers class is defined and imported correctly to use it as the type hint for the self.groups attribute.
#
#
#         '''

    # def add_group2(self, group_name, estimation_date):
    #     groups = self.calculate_groups(estimation_date)
    #     group_data = groups.get(group_name, [])
    #     self.groups.append(group_data)


    def calculate_age(self, birth_date, estimation_date):
        if estimation_date < birth_date:
            return -1
        else:
            age = relativedelta(estimation_date, birth_date)
            age_in_months = age.years * 12 + age.months
            return age_in_months


#
# a = Groups_management()
# a.calculate_groups(estimation_date=date.today())
#
# # Access the groups and their numbers
# for group in a.groups:
#     print(f"Group: {group.group_name}")
#     print("Data from the database:")
#     for cattle in group.group_data:
#         print(cattle)  # You can access all the information of each cattle in the group
#     print(f"Numbers: {group.numbers}")
#     print()