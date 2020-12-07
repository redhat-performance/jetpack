def dict_remove_item( dict, item):
    """Remove an item from a dictionary."""
    del dict[item]
    return dict

class FilterModule(object):
    def filters(self):
      return {
        'dict_remove_item': dict_remove_item,
        }
