from item_system.inventory import Inventory

# This class is wrapper for original class Inventory, using for user's interactions with Inventory.


class Interventory(Inventory):
    def __init__(self, items: []):
        super().__init__(items)
        self.stack_size = 10
        self.previous_items = []
        self.next_items = items
        self.stack_store = {}
        self.taken_items = []
        self.put_items_in_stack(True)

    # This method always takes an items(including stackable property) in stack(dictionary),
    # due to show this stack in gui

    def put_items_in_stack(self, is_forward: bool):
        if is_forward:
            items = self.next_items
        else:
            items = self.previous_items

        self.put_items(is_forward)

        counter = 0
        for i in range(len(items)):
            if i in self.taken_items:
                continue
            if not items[i].stackable:
                self.stack_store[counter] = [items[i]]
                self.taken_items.append(i)
                counter += 1
            else:
                item_type = items[i].type
                sliced_items_starts_i = items[i:len(items)]
                range_i_to_end = range(len(sliced_items_starts_i))
                for j in range_i_to_end:
                    if items[j].type == item_type:
                        if counter in self.stack_store.keys():
                            self.stack_store[counter].append(items[j])
                        else:
                            self.stack_store[counter] = [items[j]]
                        self.taken_items.append(j)
                counter += 1

            if counter == self.stack_size:
                break

        self.pool_items(is_forward)

    # This method pooling items from left stack or right stack and put them in middle-stack.
    def pool_items(self, is_forward):
        if len(self.taken_items) != 0:
            for i in reversed(self.taken_items):
                if is_forward:
                    self.next_items.remove(self.next_items[i])
                else:
                    self.previous_items.remove(self.previous_items[i])
            self.taken_items.clear()
        print(self.previous_items)
        print(self.stack_store)
        print(self.next_items)

    # This method provides putting items from middle-stack into others ,
    # it allows searching necessary item object in inventory
    def put_items(self, is_forward):
        if len(self.stack_store) != 0:
            for items in self.stack_store.values():
                if is_forward:
                    self.previous_items.extend(items)
                else:
                    self.next_items.extend(items)
            self.stack_store.clear()
        print(self.previous_items)
        print(self.stack_store)
        print(self.next_items)

    # This method is checker for left border of inventory

    def is_any_items_in_prev_items(self) -> bool:
        if len(self.previous_items) == 0:
            return False
        return True

    # This method is checker for right border of inventory

    def is_any_items_in_next_items(self) -> bool:
        if len(self.next_items) == 0:
            return False
        return True
