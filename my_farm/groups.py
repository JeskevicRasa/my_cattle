from dateutil.relativedelta import relativedelta
from .models import Cattle
from .constants import FEMALE_BIRTH_WEIGHT, MALE_BIRTH_WEIGHT, FEMALE_MAX_WEIGHT, MALE_MAX_WEIGHT, DAILY_WEIGHT_GAIN


class GroupNumbers:

    def __init__(self, group_name, group_data):
        self.filter_acquisition_loss_dates = None
        self.group_name = group_name
        self.group_data = group_data
        self.start_date_count = 0
        self.end_date_count = 0
        self.count_difference = 0
        self.start_date_group_weight = 0
        self.end_date_group_weight = 0
        self.weight_difference = 0
        self.birth_count = 0
        self.birth_weight = 0
        self.purchase_count = 0
        self.purchase_weight = 0
        self.gift_count = 0
        self.gift_weight = 0
        self.death_count = 0
        self.death_weight = 0
        self.sold_count = 0
        self.sold_weight = 0
        self.consumed_count = 0
        self.consumed_weight = 0
        self.gifted_count = 0
        self.gifted_weight = 0
        self.moved_in = 0
        self.moved_out = 0
        self.weight_moved_in = 0
        self.weight_moved_out = 0

    def __repr__(self):
        return self.group_name

    def quantity(self, start_date_groups, end_date_groups):

        self.start_date_count = len(start_date_groups[self.group_name])
        self.end_date_count = len(end_date_groups[self.group_name])
        self.count_difference = self.end_date_count - self.start_date_count

    def weight_in_groups_by_date(self, start_date_groups, end_date_groups):
        start_date_group_data = start_date_groups.get(self.group_name, [])
        self.start_date_group_weight = round(sum(cattle_dict['weight'] for cattle_dict in start_date_group_data), 2)

        end_date_group_data = end_date_groups.get(self.group_name, [])
        self.end_date_group_weight = round(sum(cattle_dict['weight'] for cattle_dict in end_date_group_data), 2)

        self.weight_difference = round((self.end_date_group_weight - self.start_date_group_weight), 2)

    def acquisition_loss(self, start_date, end_date):

        self.filter_acquisition_loss_dates = [
            cattle for cattle in self.group_data
            if (
                    ('entry_date' in cattle['cattle'] and cattle['cattle']['entry_date'] is not None and start_date <=
                     cattle['cattle']['entry_date'] <= end_date)
                    or ('end_date' in cattle['cattle'] and cattle['cattle']['end_date'] is not None and start_date <=
                        cattle['cattle']['end_date'] <= end_date)
            )
        ]

        for item in self.filter_acquisition_loss_dates:
            cattle = item['cattle']
            weight = item['weight']

            if 'acquisition_method' in cattle:
                if cattle['acquisition_method'] == 'Birth':
                    self.birth_count += 1
                    self.birth_weight += weight
                elif cattle['acquisition_method'] == 'Purchase':
                    self.purchase_count += 1
                    self.purchase_weight += weight
                elif cattle['acquisition_method'] == 'Gift':
                    self.gift_count += 1
                    self.gift_weight += weight

            if 'loss_method' in cattle:
                if cattle['loss_method'] == 'Death':
                    self.death_count += 1
                    self.death_weight += weight
                elif cattle['loss_method'] == 'Sold':
                    self.sold_count += 1
                    self.sold_weight += weight
                elif cattle['loss_method'] == 'Consumed':
                    self.consumed_count += 1
                    self.consumed_weight += weight
                elif cattle['loss_method'] == 'Gifted':
                    self.gifted_count += 1
                    self.gifted_weight += weight

    def check_movement(self, start_date_groups, end_date_groups):
        start_date_list = start_date_groups.get(self.group_name, [])
        end_date_list = end_date_groups.get(self.group_name, [])

        moved_out = [item for item in start_date_list if
                     item['cattle']['id'] not in [cattle['cattle']['id'] for cattle in end_date_list] and
                     item not in self.filter_acquisition_loss_dates]

        moved_in = [item for item in end_date_list if
                    item['cattle']['id'] not in [cattle['cattle']['id'] for cattle in start_date_list] and
                    item not in self.filter_acquisition_loss_dates]

        self.moved_in = len(moved_in)
        self.moved_out = len(moved_out)

        self.weight_moved_in = round(sum(item.get('weight', 0) for item in moved_in), 2)
        self.weight_moved_out = round(sum(item.get('weight', 0) for item in moved_out), 2)


class CattleGroupData:
    def __init__(self, group_name, group_data):
        self.group_name = group_name
        self.group_data = group_data
        self.id = None
        self.type = None
        self.number = None
        self.name = None
        self.gender = None
        self.breed = None
        self.birth_date = None
        self.acquisition_method = None
        self.entry_date = None
        self.comments = None
        self.active_cattle = 0

    def cattle_data(self):
        for cattle_data in self.group_data:
            if cattle_data['cattle']['end_date'] is not None:
                self.id = cattle_data['cattle']['id']
                self.type = cattle_data['cattle']['type']
                self.number = cattle_data['cattle']['number']
                self.name = cattle_data['cattle']['name']
                self.gender = cattle_data['cattle']['gender']
                self.breed = cattle_data['cattle']['breed']
                self.birth_date = cattle_data['cattle']['birth_date']
                self.acquisition_method = cattle_data['cattle']['acquisition_method']
                self.entry_date = cattle_data['cattle']['entry_date']
                self.comments = cattle_data['cattle']['comments']

    def count_active_cattle(self):
        print(self.group_data)
        self.active_cattle = sum(
            1 for cattle_data in self.group_data if cattle_data['cattle']['end_date'] is None)


class GroupsManagement:
    def __init__(self):
        self.groups: list[GroupNumbers] = []

    def calculate_groups(self, estimation_date):
        cattle_list = list(Cattle.objects.filter(deleted=False).values())
        groups = {
            'Cows': [{'cattle': cattle, 'weight': round(self.estimate_cattle_weight(cattle['id'], estimation_date), 2)}
                     for cattle in cattle_list if cattle['gender'] == 'Cow'
                     and cattle['entry_date'] <= estimation_date],

            'Calves': [
                {'cattle': cattle, 'weight': round(self.estimate_cattle_weight(cattle['id'], estimation_date), 2)}
                for cattle in cattle_list if cattle['gender'] in ['Heifer', 'Bull']
                and 0 <= self.calculate_age(cattle['birth_date'], estimation_date) < 12
                and cattle['entry_date'] <= estimation_date],

            'Young_Heifer': [
                {'cattle': cattle, 'weight': round(self.estimate_cattle_weight(cattle['id'], estimation_date), 2)}
                for cattle in cattle_list if cattle['gender'] == 'Heifer'
                and 12 <= self.calculate_age(cattle['birth_date'], estimation_date) < 24
                and cattle['entry_date'] <= estimation_date],

            'Adult_Heifer': [
                {'cattle': cattle, 'weight': round(self.estimate_cattle_weight(cattle['id'], estimation_date), 2)}
                for cattle in cattle_list if cattle['gender'] == 'Heifer'
                and self.calculate_age(cattle['birth_date'], estimation_date) >= 24
                and cattle['entry_date'] <= estimation_date],

            'Young_Bull': [
                {'cattle': cattle, 'weight': round(self.estimate_cattle_weight(cattle['id'], estimation_date), 2)}
                for cattle in cattle_list if cattle['gender'] == 'Bull'
                and 12 <= self.calculate_age(cattle['birth_date'], estimation_date) < 24
                and cattle['entry_date'] <= estimation_date],

            'Adult_Bull': [
                {'cattle': cattle, 'weight': round(self.estimate_cattle_weight(cattle['id'], estimation_date), 2)}
                for cattle in cattle_list if cattle['gender'] == 'Bull'
                and self.calculate_age(cattle['birth_date'], estimation_date) >= 24
                and cattle['entry_date'] <= estimation_date],
        }

        return groups

    def add_group(self, group_name, estimation_date):
        groups = self.calculate_groups(estimation_date)
        group_data = groups.get(group_name, {})
        self.groups[group_name] = group_data

    # Explanation:
    #
    # The add_group method takes two parameters: group_name and estimation_date.
    #
    # These parameters are used to calculate the groups using the calculate_groups method.
    #
    # groups variable is assigned the dictionary of groups returned by the calculate_groups method.
    #
    # group_data is initialized as an empty list using the get method on the 'groups' dictionary. If the group_name
    # exists in the dictionary, it will return the corresponding list of cattle; otherwise, it will return an empty
    # list.
    #
    # Finally, the group_data list is appended to the self.groups list, which keeps track of all the groups created.
    # Note: Make sure that the GroupNumbers class is defined and imported correctly to use it as the type hint for
    # the self.groups attribute.

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

    def estimate_cattle_weight(self, cattle_id, estimation_date):
        cattle = Cattle.objects.get(id=cattle_id)
        birth_date = cattle.birth_date

        days_passed = (estimation_date - birth_date).days

        gender = cattle.gender

        if gender in ['Heifer', 'Cow']:
            weight = FEMALE_BIRTH_WEIGHT + (days_passed * DAILY_WEIGHT_GAIN)
            weight = min(weight, FEMALE_MAX_WEIGHT)
        elif gender == 'Bull':
            weight = MALE_BIRTH_WEIGHT + (days_passed * DAILY_WEIGHT_GAIN)
            weight = min(weight, MALE_MAX_WEIGHT)
        else:
            raise ValueError("Invalid gender. Must be 'Heifer', 'Cow', or 'Bull'.")

        return weight
