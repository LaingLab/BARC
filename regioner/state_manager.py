import copy

class StateManager:
    def __init__(self):
        self.undo_stack = []

    def save_state(self, viewer):
        state = {
            "current_page": viewer.current_page,
            "img_x": viewer.img_x,
            "img_y": viewer.img_y,
            "zoom": viewer.zoom,
            "zone_counters": copy.deepcopy(viewer.zone_counters),
            "zone_names": copy.deepcopy(viewer.zone_names),
        }
        self.undo_stack.append(state)

    def undo(self, viewer):
        if not self.undo_stack:
            return
        state = self.undo_stack.pop()
        viewer.current_page = state["current_page"]
        viewer.img_x = state["img_x"]
        viewer.img_y = state["img_y"]
        viewer.zoom = state["zoom"]
        viewer.zone_counters = state["zone_counters"]
        viewer.zone_names = state["zone_names"]
        viewer.show_page()
