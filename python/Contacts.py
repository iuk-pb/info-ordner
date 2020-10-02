import vobject
import Contact

class Contacts:
    def __init__(self):
        self.items = []

    def read_file(self, path):
        with open(path) as file:
            for vcard in vobject.readComponents(file):
                self.items.append(Contact.Contact(vcard))

    def replace_data(self, data, prefix, postfix):
        tmpdata = data
        for item in self.items:
            tmpdata = item.replace_data(tmpdata, prefix, postfix)
        return tmpdata

    def write_file(self, path, sets):
        with open(path, 'w') as file:
            for contact in self.items:
                file.write(contact.serialize(sets))
                file.write('\n')
