from abc import ABC
import json
import os

from pony.orm import select
from pony.orm import db_session

from cron import (
    authenticate,
    mark_as_read,
    mark_as_unread,
    move_message
)
from db import (
    db,
    Message
)

STRING_FIELDTYPES = ['subject', 'from_email', 'to_email']
STRING_PREDICATES = ['contains', 'does not contain', 'equals', 'does not equal']
DATE_FIELDTYPES = ['date']
DATE_PREDICATES = ["less than", "greater than"]


class Field(ABC):

    def field_name(self):
        pass

    def render(self):
        pass

    def field(self):
        pass

class Predicate(ABC):

    def query(self):
        pass

class Contains(ABC):
    name = "contains"

    def query(self, column, value):
        with db_session:

            query = select(m for m in Message if value in getattr(m, column))
            results = query.fetch()
            return results


class DoesNotContain(ABC):

    def query(self, column, value):
        with db_session:
            query = select(m for m in Message if value not in getattr(m, column))
            results = query.fetch()
            return results


class Equal(ABC):

    def query(self, column, value):
        with db_session:
            query = select(m for m in Message if value == getattr(m, column))
            results = query.fetch()
            return results


class NotEqual(ABC):

    def query(self, column, value):
        with db_session:
            query = select(m for m in Message if value != getattr(m, column))
            results = query.fetch()
            return results

class LessThan(ABC):
    def query(self, column, value):
        with db_session:
            query = select(m for m in Message if value > getattr(m, column))
            results = query.fetch()
            return results

class GreaterThan(ABC):
    def query(self, column, value):
        with db_session:
            query = select(m for m in Message if value < getattr(m, column))
            results = query.fetch()
            return results


class FromEmail(Field):
    field_name = "from_email"

#    def __init__(self, value):
#        if not self.verify(value):
#            raise ValueError("Wrong Value type for field FromEmail")
#        self.value = value

#    def verify(self, value):
#        if not isinstance(value, str):
#            return False
#        return True


class ToEmail(Field):
    field_name = "to_email"

    def apply_rule(self, predicate, compare_values):
        pass

class Date(Field):
    field_name = "date"

    def apply_rule(self, predicate, compare_values):
        pass


class Subject(Field):
    field_name = "subject"

#    def __init__(self, value):
#        if not self.verify(value):
#            raise ValueError("Wrong Value type for field Subject")
#        self.value = value

#    def verify(self, value):
#        if not isinstance(value, str):
#            return False
#        return True


class ActionType(ABC):
    def apply(self):
        pass


class Move(ActionType):
    action_name = "move"

    def __init__(self):
        pass

    def apply(self, message_ids, move_folder=None):
        service = authenticate()
        for message_id in message_ids:
            move_message(service, message_id, move_folder)


class MarkRead(ActionType):
    action_name = "mark_as_read"

    def __init__(self):
        pass

    def apply(self, message_ids, move_folder=None):
        service = authenticate()
        for message_id in message_ids:
            mark_as_read(service, message_id)



class MarkUnread(ActionType):
    action_name = "mark_as_unread"

    def __init__(self):
        pass

    def apply(self, message_ids, move_folder=None):
        service = authenticate()
        for message_id in message_ids:
            mark_as_unread(service, message_id)



class Rule(object):
    def __init__(self, rule_name):
        self.rule_name = rule_name
        self.field = None
        self.predicate = None
        self.compare_value = None
        self.action = None

    def find_field(self, field_name):
        field_cls = [cls for cls in Field.__subclasses__() if cls.field_name == field_name]
        if not field_cls:
            raise NotImplementedError
        return field_cls[0]

    def find_action(self, action_name):
        field_cls = [cls for cls in ActionType.__subclasses__() if cls.action_name == action_name]
        if not field_cls:
            raise NotImplementedError
        return field_cls[0]

    def add_field(self, field_name, value=None):
        self.field = self.find_field(field_name)

    def add_predicate(self, predicate):
        self.verify_predicate(predicate)
        self.predicate = predicate

    def add_value(self, value):
        self.compare_value = value

    def add_action(self, action, new_folder=None):
        action = self.find_action(action)
        self.action = action
        self.action.new_folder = new_folder

    def verify_predicate(self, predicate):
        if self.field.field_name in STRING_FIELDTYPES and predicate in STRING_FIELDTYPES:
            return True

        if self.field.field_name in DATE_FIELDTYPES and predicate in DATE_FIELDTYPES:
            return True

        return False

    def verify_value(self, value):
        pass

    def render(self):
        return """
        Field Name: %s \n
        Predicate: %s  \n
        Value: %s   \n      
        """ %(self.field.field_name, self.predicate, self.compare_value)


    @property
    def rule_file(self):
        filename = self.rule_name + '.json'
        return filename

    def from_json(self, rule_file):
        with open(rule_file, 'r') as fp:
            rule_json = json.load(fp)

        self.field = self.find_field(rule_json['field_name'])
        self.predicate = rule_json['predicate']
        self.compare_value = rule_json['compare_value']
#        self.action = self.find_action(rule_json['action'])
#        self.new_folder = rule_json['new_folder']
        return self


    def remove(self):
        os.remove(self.rule_file)

    def write_to_file(self):
        with open(self.rule_file, 'w') as fp:
            json.dump({
                "field_name": self.field.field_name,
#                "field_value": self.field.value,
                "predicate": self.predicate,
                "compare_value": self.compare_value,
 #               "action": self.action.action_name,
 #               "new_folder": None or self.action.new_folder
            }, fp)

    def fetch_for_rule(self):
        if self.predicate == "contains":
            results = Contains().query(self.field.field_name, self.compare_value)

        if self.predicate == "does not contain":
            results = DoesNotContain().query(self.field.field_name, self.compare_value)

        if self.predicate == "equals":
            results = Equal().query(self.field.field_name, self.compare_value)

        if self.predicate == "does not equal":
            results = NotEqual().query(self.field.field_name, self.compare_value)

        if self.predicate == "less than":
            results = LessThan().query(self.field.field_name, self.compare_value)

        if self.predicate == "greater than":
            results = GreaterThan().query(self.field.field_name, self.compare_value)

        return results

