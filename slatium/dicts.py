class Bidict(dict):
    """
    bidict implementation, allowing for multiple keys and values.
    this is accomplished by maintaining the inverse mapping as a
    dictionary of lists.

    ALL ACCESS returns a list for consistency

    If you try to do anything fancier than what the tests do... then
    I'm certain you'll break something.  Let me know if you expected
    a different result

    Thank you Basj: http://stackoverflow.com/a/21894086/4717806
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.inverse = {}
        # Fill the entries in inverse
        for key, value in self.items():
            self.inverse.setdefault(value, []).append(key)

    def __setitem__(self, key, value):
        # Remove the old reference from the inverse
        self.unlink(key, value)
        # Update new references
        super().__setitem__(key, value)
        self.inverse.setdefault(value, []).append(key)

    def __delitem__(self, key):
        # Switch, depending on whether the user gave us a key for the dict, or the inverse
        if key in self:
            self.unlink(key, super().__getitem__(key))
            super().__delitem__(key)
        elif key in self.inverse:
            for value in self.inverse[key]:
                super().__delitem__(value)
            del self.inverse[key]
        else:
            raise KeyError(key)

    def __getitem__(self, key):
        # Switch, depending on whether the user gave us a key for the dict, or the inverse
        if key in self:
            # This rustles my jimmies, but I can't think of anything better atm
            return [super().__getitem__(key)]
        elif key in self.inverse:
            return self.inverse[key]
        else:
            raise KeyError(key)

    def unlink(self, key, value):
        """
        remove an instance of inverse[value] = [key...]
        (if it exists)
        and delete the entire list if it's the last one
        """
        if value in self.inverse:
            self.inverse[value].remove(key)
            # Check if the list at self.inverse[value] is empty
            if not self.inverse[value]:
                del self.inverse[value]


class SingleModificationError(Exception):
    pass


class Dualdict(dict):
    """
    dualdict implementation, automatically binds two keys to a value if
    the 'add()' method is used

    here for convenience
    """
    def __init__(self, *args, **kwargs):
        # TODO: This constructor can't handle already built dicts from *args
        super().__init__(*args, **kwargs)
        self.bidict = Bidict()

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        super().__setitem__(self.bidict[key][0], value)

    def __delitem__(self, key):
        super().__delitem__(key)
        super().__delitem__(self.bidict[key][0])
        del self.bidict[key]

    def add(self, key1, key2, value):
        if key1 in self:
            raise KeyError(key1)
        if key2 in self:
            raise KeyError(key2)
        super().__setitem__(key1, value)
        super().__setitem__(key2, value)
        self.bidict[key1] = key2

    def update(self, key, update_key):
        if key not in self:
            raise KeyError(key)
        if update_key in self:
            raise KeyError(update_key)

        # delete old 'extra' reference
        super().__delitem__(self.bidict[key][0])

        # update internal bidict reference
        del self.bidict[key]
        self.bidict[key] = update_key

        # add new reference
        super().__setitem__(update_key, self[key])
