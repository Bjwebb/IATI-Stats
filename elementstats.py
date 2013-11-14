from stats import returns_intdict, element_to_count_dict

class PublisherStats(object):
    pass

class ActivityFileStats(object):
    pass

class ActivityStats(object):
    blank = False

    @returns_intdict
    def elements(self):
        return element_to_count_dict(self.element, 'iati-activity', {})

class OrganisationFileStats(object):
    pass

class OrganisationStats(object):
    blank = False

    @returns_intdict
    def elements(self):
        return element_to_count_dict(self.element, 'iati-organisation', {})
