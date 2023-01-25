from item_system.inventory import Inventory


# This subclass to store and transmit user's interactions over inventory.


class InteractionHistory:
    def __init__(self):
        self.chosen_item = None
        self.__current_page__ = 1
# This class is wrapper for original class Inventory, using for user's interactions with Inventory.


class Interventory(Inventory):
    def __init__(self, items: [], inter_history: InteractionHistory = None):
        super().__init__(items)
        self.stack_size = 10
        self.trade_limit = 10
        self.previous_items = []
        self.next_items = items
        self.stack_store = {}
        self.taken_items = []

        self.trade_items = {}
        if inter_history is not None:
            self.inter_history: InteractionHistory = inter_history
            for page in range(0, self.inter_history.__current_page__):
                self.put_items_in_stack(True)
        else:
            self.inter_history: InteractionHistory = InteractionHistory()
            self.put_items_in_stack(True)

    # This method triggers when user push the buttons `left` or `right`.
    def on_switch_page(self, is_forward: bool):
        if is_forward:
            if len(self.next_items) == 0:
                return
            self.inter_history.__current_page__ += 1
        else:
            if len(self.previous_items) == 0:
                return
            self.inter_history.__current_page__ -= 1
        self.put_items_in_stack(is_forward)

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
                self.stack_store[counter] = [items[i]]
                self.taken_items.append(i)
                item_type = items[i].type
                sliced_items_starts_i = items[i:len(items)]
                range_i_to_end = range(len(sliced_items_starts_i))
                for j in range_i_to_end:
                    if sliced_items_starts_i[j].type == item_type and j + i not in self.taken_items:
                        if counter in self.stack_store.keys():
                            self.stack_store[counter].append(sliced_items_starts_i[j])
                        self.taken_items.append(j + i)
                counter += 1

            if counter == self.stack_size:
                break

        self.pool_items(is_forward)

    # This method pooling items from left stack or right stack and put them in middle-stack.
    def pool_items(self, is_forward):
        if len(self.taken_items) != 0:
            self.taken_items.sort()
            for i in reversed(self.taken_items):
                if is_forward:
                    self.next_items.remove(self.next_items[i])
                else:
                    self.previous_items.remove(self.previous_items[i])
            self.taken_items.clear()

    # This method provides putting items from middle-stack into others ,
    # it allows searching necessary item object in inventory
    def put_items(self, is_forward):
        if len(self.stack_store) != 0:
            for items in reversed(self.stack_store.values()):
                for item in reversed(items):
                    if is_forward:
                        self.previous_items.insert(0, item)
                    else:
                        self.next_items.insert(0, item)
            self.stack_store.clear()

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

    # Adding items from inventory in trade list.
    def add_items_in_trade(self, items: []):
        for item in items:
            is_added = False
            if len(self.trade_items) > 0:
                for slot in self.trade_items.values():
                    is_stackable = slot[0].type == item.type and item.stackable
                    if is_stackable:
                        print(f"{slot[0].type} ?= {item.type} :{is_stackable}")
                        slot.append(item)
                        is_added = True
                if not is_added:
                    if len(self.trade_items) <= self.trade_limit:
                        self.trade_items[len(self.trade_items)] = [item]
                    else:
                        raise TradeLimitExceeded()
            else:
                self.trade_items[0] = [item]

        self.withdraw_items_from_stack_store(items)

    # Withdraws added items from stack.
    def withdraw_items_from_stack_store(self, items: []):
        list_item_ids = [item.id for item in items]
        for i in range(len(list_item_ids)):
            for j in range(len(self.stack_store.values())-1, -1, -1):
                stack = self.stack_store
                for item in stack[j]:
                    if item.id == list_item_ids[i]:
                        stack[j].remove(item)
        self.delete_empty_keys_in_store()

    # Deletes empty keys from stack store.
    def delete_empty_keys_in_store(self):
        keys_to_delete = []
        for key, slot in self.stack_store.items():
            if len(slot) == 0:
                keys_to_delete.append(key)
        for key in keys_to_delete:
            if key in self.stack_store.keys():
                del self.stack_store[key]
        self.reset_keys()

    # Update stack store's keys.
    def reset_keys(self):
        new_reset_store = {}
        count = 0
        for slot in self.stack_store.values():
            new_reset_store[count] = slot
            count += 1
        self.stack_store = new_reset_store


class TradeLimitExceeded(Exception):
    def __init__(self):
        self.txt = f"Limit of items in trade exceeded."

