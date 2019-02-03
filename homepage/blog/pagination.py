#:coding=utf8:

class Page(object):
    def __init__(self, page_number, num_pages):
        try:
            self.number = int(page_number)
            if self.number < 1:
                raise ValueError("Less than 1")
            if self.number > num_pages:
                raise ValueError("Greater than %s", self.num_pages)
        except ValueError:
            self.number = 1

        self.num_pages = num_pages

    def previous_page_number(self):
        return self.number - 1

    def next_page_number(self):
        return self.number + 1

    def has_previous(self):
        return self.number > 1

    def has_next(self):
        return self.number < self.num_pages
