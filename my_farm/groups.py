from dateutil.relativedelta import relativedelta
from .models import Cattle
from .constants import FEMALE_BIRTH_WEIGHT, MALE_BIRTH_WEIGHT, FEMALE_MAX_WEIGHT, MALE_MAX_WEIGHT, DAILY_WEIGHT_GAIN


class GroupNumbers:
    """
    Represents a group of numbers with various calculations and data.
    """

    def __init__(self, group_name, group_data):
        """
        Initializes a GroupNumbers instance with the provided group name and group data.

        :param group_name: The name of the group.
        :param group_data: The data associated with the group.
        """
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
        """
        Returns a string representation of the GroupNumbers instance.

        :return: The string representation of the instance.
        """
        return self.group_name

    def quantity(self, start_date_groups, end_date_groups, start_date, end_date):
        """
        Calculates the quantity and weight of cattle for the group based on the provided start and end date groups.

        :param start_date: The start date for the period of calculation.
        :param end_date: The end date for the period of calculation.
        :param start_date_groups: A dictionary containing the group data organized by group name for the start date.
        :param end_date_groups: A dictionary containing the group data organized by group name for the end date.
        """
        start_date_list = start_date_groups.get(self.group_name, [])
        end_date_list = end_date_groups.get(self.group_name, [])

        start_date_filtered = [cattle for cattle in start_date_list if (cattle['cattle']['end_date'] is None or
                                                                        cattle['cattle']['end_date'] >= start_date)]

        end_date_filtered = [cattle for cattle in end_date_list if (cattle['cattle']['end_date'] is None or
                                                                    cattle['cattle']['end_date'] >= end_date)]

        self.start_date_count = len(start_date_filtered)
        self.end_date_count = len(end_date_filtered)

        self.count_difference = self.end_date_count - self.start_date_count

        self.start_date_group_weight = round(sum(cattle_dict['weight'] for cattle_dict in start_date_filtered))
        self.end_date_group_weight = round(sum(cattle_dict['weight'] for cattle_dict in end_date_filtered))

        self.weight_difference = round((self.end_date_group_weight - self.start_date_group_weight))

    def acquisition_loss(self, start_date, end_date):
        """
        Calculates the acquisition and loss statistics of the group based on the provided start and end dates.

        The weight in the acquisition or loss column will be estimated based on the acquisition date for the acquisition
        methods and the end date for the loss methods.

        :param start_date: The start date for the acquisition/loss calculation.
        :param end_date: The end date for the acquisition/loss calculation.
        """
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

            entry_weight = round(GroupsManagement().estimate_cattle_weight(cattle['id'], cattle['entry_date']))
            end_weight = round(GroupsManagement().estimate_cattle_weight(cattle['id'], cattle['end_date'])) if \
                cattle['end_date'] is not None else 0

            if 'acquisition_method' in cattle:
                if cattle['acquisition_method'] == 'Birth':
                    self.birth_count += 1
                    self.birth_weight += entry_weight
                elif cattle['acquisition_method'] == 'Purchase':
                    self.purchase_count += 1
                    self.purchase_weight += entry_weight
                elif cattle['acquisition_method'] == 'Gift':
                    self.gift_count += 1
                    self.gift_weight += entry_weight

            if 'loss_method' in cattle:
                if cattle['loss_method'] == 'Death':
                    self.death_count += 1
                    self.death_weight += end_weight
                elif cattle['loss_method'] == 'Sold':
                    self.sold_count += 1
                    self.sold_weight += end_weight
                elif cattle['loss_method'] == 'Consumed':
                    self.consumed_count += 1
                    self.consumed_weight += end_weight
                elif cattle['loss_method'] == 'Gifted':
                    self.gifted_count += 1
                    self.gifted_weight += end_weight

    def check_movement(self, start_date_groups, end_date_groups):
        """
        Checks the movement of the group by comparing the start and end date groups.

        :param start_date_groups: The dictionary of start date groups.
        :param end_date_groups: The dictionary of end date groups.
        """
        start_date_list = start_date_groups.get(self.group_name, [])
        end_date_list = end_date_groups.get(self.group_name, [])

        moved_out = [item for item in start_date_list if
                     item['cattle']['id'] not in [cattle['cattle']['id'] for cattle in end_date_list] and
                     item not in self.filter_acquisition_loss_dates]

        moved_in = [item for item in end_date_list if
                    item['cattle']['id'] not in [cattle['cattle']['id'] for cattle in start_date_list] and
                    item not in self.filter_acquisition_loss_dates]
        print(self.filter_acquisition_loss_dates)
        self.moved_in = len(moved_in)
        self.moved_out = len(moved_out)

        self.weight_moved_in = round(sum(item.get('weight', 0) for item in moved_in))
        self.weight_moved_out = round(sum(item.get('weight', 0) for item in moved_out))

    def to_dict(self, start_date=None, end_date=None):
        """
        Converts the GroupNumbers instance to a dictionary representation.

        :param start_date: The optional start date for inclusion in the dictionary.
        :param end_date: The optional end date for inclusion in the dictionary.
        :return: The dictionary representation of the GroupNumbers instance.
        """
        data = {
            'group_name': self.group_name,
            'group_data': self.group_data,
            'start_date_count': str(self.start_date_count),
            'end_date_count': str(self.end_date_count),
            'count_difference': str(self.count_difference),
            'start_date_group_weight': str(self.start_date_group_weight),
            'end_date_group_weight': str(self.end_date_group_weight),
            'weight_difference': str(self.weight_difference),
            'birth_count': str(self.birth_count),
            'birth_weight': str(self.birth_weight),
            'purchase_count': str(self.purchase_count),
            'purchase_weight': str(self.purchase_weight),
            'gift_count': str(self.gift_count),
            'gift_weight': str(self.gift_weight),
            'death_count': str(self.death_count),
            'death_weight': str(self.death_weight),
            'sold_count': str(self.sold_count),
            'sold_weight': str(self.sold_weight),
            'consumed_count': str(self.consumed_count),
            'consumed_weight': str(self.consumed_weight),
            'gifted_count': str(self.gifted_count),
            'gifted_weight': str(self.gifted_weight),
            'moved_in': self.moved_in,
            'moved_out': self.moved_out,
            'weight_moved_in': self.weight_moved_in,
            'weight_moved_out': self.weight_moved_out,
        }

        if start_date:
            data['start_date'] = start_date.isoformat()
        if end_date:
            data['end_date'] = end_date.isoformat()

        return data


class CattleGroupData:
    """
    Represents a group of cattle data with various properties and calculations.
    """

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
        """
        Extracts the cattle data from the group data and assigns it to the instance properties.
        """
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
        """
        Counts the number of active cattle in the group.

        The active cattle are those whose 'end_date' is None in the group data.
        """
        self.active_cattle = sum(
            1 for cattle_data in self.group_data if cattle_data['cattle']['end_date'] is None)


class GroupsManagement:
    """
    Manages groups of cattle and performs calculations on the groups.
    """

    def __init__(self):
        """
        Initializes a GroupsManagement instance with an empty list of groups.
        """
        self.groups: list[GroupNumbers] = []

    def calculate_groups(self, estimation_date):
        """
        Calculates the groups of cattle based on the provided estimation date.

        :param estimation_date: The estimation date for the calculation.
        :return: A dictionary containing the calculated groups of cattle.
        """
        cattle_list = list(Cattle.objects.filter(deleted=False).values())
        groups = {
            'Cows': [{'cattle': cattle, 'weight': round(self.estimate_cattle_weight(cattle['id'], estimation_date), 2)}
                     for cattle in cattle_list if cattle['gender'] == 'Cow'
                     and cattle['entry_date'] <= estimation_date],

            'Calves': [{'cattle': cattle, 'weight': round(self.estimate_cattle_weight(cattle['id'],
                                                                                      estimation_date), 2)} for cattle
                       in cattle_list if cattle['gender'] in ['Heifer', 'Bull']
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
        """
        Adds a group with the provided group name to the groups list based on the estimation date.

        :param group_name: The name of the group to add.
        :param estimation_date: The estimation date for the group calculation.
        """
        groups = self.calculate_groups(estimation_date)
        group_data = groups.get(group_name, {})
        self.groups[group_name] = group_data

    def calculate_age(self, birth_date, estimation_date):
        """
        Calculates the age in months based on the birthdate and estimation date.

        :param birth_date: The birthdate of the cattle.
        :param estimation_date: The estimation date for the calculation.
        :return: The age in months.
        """
        if estimation_date < birth_date:
            return -1
        else:
            age = relativedelta(estimation_date, birth_date)
            age_in_months = age.years * 12 + age.months
            return age_in_months

    def estimate_cattle_weight(self, cattle_id, estimation_date):
        """
        Estimates the weight of cattle based on its ID and the estimation date.

        :param cattle_id: The ID of the cattle.
        :param estimation_date: The estimation date for the weight calculation.
        :return: The estimated weight of the cattle.
        """
        cattle = Cattle.objects.get(id=cattle_id)
        birth_date = cattle.birth_date

        days_passed = (estimation_date - birth_date).days if estimation_date > birth_date else 0

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
