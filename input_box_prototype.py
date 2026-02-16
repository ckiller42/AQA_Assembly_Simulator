import arcade
import arcade.gui as gui
from arcade.gui import UIOnClickEvent


class QuitButton(arcade.gui.UIFlatButton):
    def on_click(self, event: UIOnClickEvent):
        arcade.exit()


class MyWindow(arcade.Window):
    def __init__(self):
        # Set up the window
        super().__init__(400,300,"UI Example",resizable=True)
        self.manager = gui.UIManager()
        self.manager.enable()

        arcade.set_background_color(arcade.color.BEIGE)
        # creating labels and input fields
        self.label = arcade.gui.UILabel(
            text="Look here for change",
            text_color=arcade.color.DARK_RED,
            width=350,
            height=40,
            font_size=24,
            font_name="Kenny Future"
        )
        self.input_field = gui.UIInputText(
            color=arcade.color.DARK_BLUE_GRAY,
            font_size=18,
            width=200,
            text="Type here"
        )
        submit_button = gui.UIFlatButton(
            color=arcade.color.DARK_BLUE_GRAY,
            text='Submit'
        )
        # set event and save the text being typed
        @submit_button.event("on_click")
        def on_click_submit(event):
            print(f'Click event caught: {event}')
            self.update_text()

        # submit_button.on_click = self.on_click

        self.v_box = gui.UIBoxLayout()
        self.v_box.add(self.label.with_space_around(bottom=20))
        self.v_box.add(self.input_field)
        self.v_box.add(submit_button)
        self.v_box.add(QuitButton(text="Quit"))

        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                child=self.v_box
            )
        )

    def update_text(self):
        print(f"updating the label with input text '{self.input_field.text}'")
        self.label.text = self.input_field.text

    def on_draw(self):
        self.clear()
        arcade.start_render()
        self.manager.draw()


window = MyWindow()
arcade.run()
