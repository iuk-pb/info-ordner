import logging
import copy

logger = logging.getLogger(__name__)


class ReplaceItem:
    def __init__(self, name, value):
        self.name = name
        self.value = value


class Contact:
    def __init__(self, vcard):
        self.id = vcard.nickname.value
        self.vcard = vcard
        self.replace_items = []
        #vcard.prettyPrint()

        if hasattr(self.vcard, 'title'):
            self.create("TITLE", self.vcard.title.value)

        if hasattr(self.vcard, 'role'):
            self.create("RUFNAME", self.vcard.role.value)

        if hasattr(self.vcard, 'fn'):
            self.create("NAME", self.vcard.fn.value)

        if hasattr(self.vcard, 'label'):
            self.create("ADRESSE", self.vcard.label.value)

        if hasattr(self.vcard, 'tel_list'):
            self.create_list("TEL", self.vcard.tel_list, True)

        if hasattr(self.vcard, 'email_list'):
            self.create_list("EMAIL", self.vcard.email_list, False)

        self.categories = []
        if hasattr(self.vcard, 'categories'):
            self.categories = self.vcard.categories.value

        if hasattr(self.vcard, 'x_sip_list'):
            self.create_list("SIP", self.vcard.x_sip_list, False)

        for item in self.replace_items:
            logger.warning("Replace variables " + item.name + ": " + item.value)

    def format_telephone(self, value):
        tel = value

        if tel.startswith("+49"):
            tel = "0" + tel[3:]
        split = 5
        if tel.startswith("01"):
            split = 4
        elif tel.startswith("032"):
            split = 3
        elif tel.startswith("0700"):
            split = 4
        elif tel.startswith("0800"):
            split = 4
        elif tel.startswith("0900"):
            split = 4

        tel = tel[:split] + " / " + tel[split:]
        split += 3

        split += 3
        while split < (len(tel) - 1):
            tel = tel[:split] + " " + tel[split:]
            split += 4

        return tel

    def create_list(self, nameprefix, list, format_tel):
        for e in list:
            value = e.value
            paramlist = ""
            for param in e.type_paramlist:
                paramlist = paramlist + "_" + param
            if len(list) > 1:
                name = nameprefix + paramlist
            else:
                name = nameprefix + paramlist
            if format_tel:
                value = self.format_telephone(value)
            self.create(name, value)

    def item_exists(self, name):
        for item in self.replace_items:
            if item.name == name:
                return True
        return False

    def create(self, name, content):
        id = self.id + "_" + name
        tmpid = id
        counter = 2
        while self.item_exists(tmpid):
            tmpid = id + str(counter)
            counter += 1
        self.replace_items.append(ReplaceItem(tmpid, str(content)))

    def replace_data(self, data, prefix, postfix):
        tmpdata = data

        for item in self.replace_items:
            name = prefix + item.name + postfix
            tmpdata = tmpdata.replace(name, item.value)

        return tmpdata

    def is_for_sets(self, name, sets):
        for curr_set in self.categories:
            if curr_set in sets:
                return True
        return False

    def serialize(self, sets):
        tmp = copy.deepcopy(self.vcard)
        new_cats = []
        for cat in self.categories:
            if cat in sets:
                new_cats.append(cat)
        tmp.categories.value = new_cats
        return tmp.serialize()
