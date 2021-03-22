from abc import ABC
import os

from rules import Rule
from rules import (
    STRING_PREDICATES,
    DATE_PREDICATES
)


class Command(ABC):

    def describe(self):
        pass

    def steps(self):
        pass

    def execute(self):
        pass


class AddRule(Command):
    sequence = 1

    def describe(self):
        print("Add a rule")

    def steps(self):
        print("For adding rules, add a field for the rule, a predicate and value ")

    def execute(self):
        field = input("Add the input field out of (from/to/subject/date): ")
        if field not in ["from", "to", "subject", "date"]:
            print("Could not recognize the option. Exiting")
            exit()

#        field_value = input("Value of the field: ")
        used_predicate = None
        if field in ['from', 'to', 'subject']:
            options_string = ""
            used_predicate = STRING_PREDICATES
            for num, option in enumerate(STRING_PREDICATES, 1):
                options_string += "%s. %s " %(num, option)
        elif field in ['date']:
            options_string = ""
            used_predicate = DATE_PREDICATES
            for num, option in enumerate(DATE_PREDICATES, 1):
                options_string += "%s. %s " %(num, option)

        choice = input("Choose the predicate {}: ".format(options_string))
        try:
            choice = int(choice)
        except ValueError:
            print("Need an integer choice")
            exit()

        if (choice > len(used_predicate) or choice < 0):
            print("Choice not found")
            exit()

        predicate = used_predicate[choice - 1]
        comparison_value = input("Value to compare to: ")
        name_rule = input("Name for the rule: ")
        action = input("Choose action (1. Mark as Read/2. Mark as Unread/3. Move): ")
        try:
            action = int(action)
        except ValueError:
            print("Need an integer choice")
            exit()

        if (action <= 0 or action >= 3):
            print("Action not found")
            exit()

        if action == 1:
            action = "mark_as_read"
        elif action == 2:
            action = "mark_as_unread"
        elif action == 3:
            action = "move"
            folder = input("name of folder to move to")

        rule = Rule(name_rule)
        rule.add_field(field)
#        rule.add_field(field, field_value)
        rule.add_predicate(predicate)
        rule.add_value(comparison_value)
        if (action == "mark_as_read" or action == "mark_as_unread"):
            rule.add_action(action)
        if action == "move":
            rule.add_action(action, folder)
        rule.write_to_file()

class ListRules(Command):
    sequence = 2
    def describe(self):
        print("List all saved rules")

    def steps(self):
        pass

    def execute(self):
        all_files = os.listdir()
        rule_files = [file_name for file_name in all_files if ('.json' in file_name and \
                        file_name != 'credentials.json' and file_name != 'tokens.json')]

        for num, rule_file in enumerate(rule_files, 1):
            rule_name = rule_file[:-5]
            print("{}. {}".format(num, rule_name))


class DescribeRule(Command):
    sequence = 3

    def describe(self):
        print("Describes the rule ")

    def steps(self):
        pass

    def execute(self):
        rule = input("Describe the rule: ")
        rule_file = rule + '.json'
        if not os.path.isfile(rule_file):
            print("Could not find the rule")
            exit()
        



class ExecuteRules(Command):
    sequence = 4

    def describe(self):
        print("Apply rule and fetch (Choose applying Any/All rules)")

    def steps(self):
        pass

    def execute(self):
        pass


class ListCommands(Command):
    sequence = 0

    def describe(self):
        print("List Commands")

    def steps(self):
        pass

    def execute(self):
        sorted_classes = sorted(Command.__subclasses__(), key=lambda x: x.sequence)
        for cls in sorted_classes[1:]:
            command = cls()
            print(command.sequence, end=". ")
            command.describe()

        choice = int(input("Choose:"))
        choice = sorted_classes[choice]()
        choice.steps()
        choice.execute()


def find_command_sequence():
    command_cls = [cls for cls in Command.__subclasses__() if cls.sequence == 0]
    if not command_cls:
        raise NotImplementedError
    return command_cls[0]


if __name__ == '__main__':
    first_command = find_command_sequence()
    first_command = first_command()
    first_command.execute()


