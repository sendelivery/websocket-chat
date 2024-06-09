from unittest.mock import Mock, patch
import pytest
import urwid
from client.lib.ui.custom_widgets import Chatlog, InputBox, InfoPanel, DequeWalker


class TestChatlog:
    def test_can_append_messages_to_log(self):
        # Given
        cl = Chatlog()

        args1 = ("User1", "Message1", "dummy_attribute")
        args2 = ("User2", "Message2", "dummy_attribute")
        args3 = ("User3", "Message3", "dummy_attribute")

        # When
        cl.append(*args1)
        cl.append(*args2)
        cl.append(*args3)

        # Then
        assert len(cl.contents) == 3

        text: urwid.Text = cl.walker.contents[0]
        assert text.text == "User1: Message1"

        text = cl.walker.contents[1]
        assert text.text == "User2: Message2"

        text = cl.walker.contents[2]
        assert text.text == "User3: Message3"

    def test_can_append_to_log_and_focus_messages(self):
        cl = Chatlog()

        args1 = ("User1", "Message1", "dummy_attribute")
        args2 = ("User2", "Message2", "dummy_attribute")
        args3 = ("User3", "Message3", "dummy_attribute")

        cl.append_and_set_focus(*args1)
        text_widget_1: urwid.Text = cl.walker.contents[-1]

        assert text_widget_1.text == "User1: Message1"
        assert cl.focus == text_widget_1

        cl.append_and_set_focus(*args2)
        text_widget_2: urwid.Text = cl.walker.contents[-1]

        assert text_widget_2.text == "User2: Message2"
        assert cl.focus == text_widget_2

        cl.append_and_set_focus(*args3)
        text_widget_3: urwid.Text = cl.walker.contents[-1]

        assert text_widget_3.text == "User3: Message3"
        assert cl.focus == text_widget_3


class TestInputBox:
    def test_does_nothing_and_empties_text_if_no_on_enter(self):
        # Given
        inputbox = InputBox()

        # Default implementation of on_enter should be a function that returns None.
        # Unfortunately testing for side effects isn't straightforward so we'll have to be happy
        # with this assertion.
        assert inputbox.on_enter() is None

        inputbox.set_edit_text("A message I'm about to send.")

        # When
        inputbox.keypress((5, 5), "enter")

        # Then
        assert inputbox.get_edit_text() == ""

    def test_calls_configured_callback_on_enter(self):
        # Given
        mock_callback = Mock(return_value=None)
        message = "A message I'm about to send."

        inputbox = InputBox()
        inputbox.set_on_enter(mock_callback)
        inputbox.set_edit_text(message)

        # When
        inputbox.keypress((5, 5), "enter")

        # Then
        assert mock_callback.called
        mock_callback.assert_called_once_with(message)

    def test_does_not_call_configured_callback_on_enter_if_edit_text_is_empty(self):
        # Given
        mock_callback = Mock(return_value=None)
        message = ""

        inputbox = InputBox()
        inputbox.set_on_enter(mock_callback)
        inputbox.set_edit_text(message)

        # When
        inputbox.keypress((5, 5), "enter")

        # Then
        mock_callback.assert_not_called

    def test_handles_a_key_as_expected(self):
        # Given
        inputbox = InputBox()

        assert inputbox.get_edit_text() == ""

        # When
        inputbox.keypress((5, 5), "e")

        # Then
        assert inputbox.get_edit_text() == "e"

    def test_validate_raises_ValueError_if_edit_text_empty(self):
        # Given
        message = ""
        inputbox = InputBox()

        # When & Then
        with pytest.raises(ValueError):
            inputbox._validate(message)


class TestInfoPanel:
    def test_disconnect_button_closes_console_display(self):
        # Given
        infopanel = InfoPanel()

        # When & Then
        with pytest.raises(urwid.ExitMainLoop):
            infopanel.disconnect.keypress((5, 5), "enter")


class TestDequeWalker:
    @pytest.fixture
    def walker_with_wrap(self) -> DequeWalker:
        return DequeWalker(wrap_around=True, maxlen=3)

    @pytest.fixture
    def walker_no_wrap(self) -> DequeWalker:
        return DequeWalker(wrap_around=False, maxlen=3)

    def test_append_beyond_maxlen_pops_from_left(self, walker_no_wrap):
        # Given
        testdata = ["1", "2", "3", "4"]

        # When
        for message in testdata:
            t = urwid.Text(message)
            walker_no_wrap.append(t)

        # Then
        assert len(walker_no_wrap.contents) == 3

        for text_widget in walker_no_wrap.contents:
            assert text_widget.text != testdata[0]

    @patch("client.lib.ui.custom_widgets.deque_walker.u.ListWalker._modified")
    def test_set_focus_updates_focus_and_calls_modified(
        self, mock_modified_func, walker_no_wrap
    ):
        # Given
        walker_no_wrap.append("widget0")
        walker_no_wrap.append("widget1")
        assert mock_modified_func.call_count == 0

        # When
        walker_no_wrap.set_focus(1)

        # Then
        assert walker_no_wrap.focus == 1
        assert mock_modified_func.call_count == 1

    def test_set_focus_updates_focus_throws_for_invalid_position(self, walker_no_wrap):
        # Given
        walker_no_wrap.append("widget0")

        # When & Then
        with pytest.raises(IndexError):
            walker_no_wrap.set_focus(1)

    def test_next_position_returns_expected_position(
        self, walker_no_wrap, walker_with_wrap
    ):
        # Happy path, no wrap
        # Given
        walker_no_wrap.append("widget0")
        walker_no_wrap.append("widget1")
        walker_no_wrap.append("widget2")

        # When
        pos = walker_no_wrap.next_position(1)

        # Then
        assert pos == 2

        # Happy path, with wrap
        # Given
        walker_with_wrap.append("widget0")
        walker_with_wrap.append("widget1")
        walker_with_wrap.append("widget2")

        # When
        pos = walker_with_wrap.next_position(1)
        wrapped_pos_edge = walker_with_wrap.next_position(3)
        wrapped_pos_extraneous = walker_with_wrap.next_position(30)

        # Then
        assert pos == 2
        assert wrapped_pos_edge == 0
        assert wrapped_pos_extraneous == 0

    def test_next_position_throws_for_invalid_position(self, walker_no_wrap):
        # Given
        walker_no_wrap.append("widget1")

        # When & Then
        with pytest.raises(IndexError):
            walker_no_wrap.next_position(40)

    def test_prev_position_returns_expected_position(
        self, walker_no_wrap, walker_with_wrap
    ):
        # Happy path, no wrap
        # Given
        walker_no_wrap.append("widget0")
        walker_no_wrap.append("widget1")
        walker_no_wrap.append("widget2")

        # When
        pos = walker_no_wrap.prev_position(1)

        # Then
        assert pos == 0

        # Happy path, with wrap
        # Given
        walker_with_wrap.append("widget0")
        walker_with_wrap.append("widget1")
        walker_with_wrap.append("widget2")

        # When
        pos = walker_with_wrap.prev_position(1)
        wrapped_pos_left_edge = walker_with_wrap.prev_position(0)
        wrapped_pos_right_edge = walker_with_wrap.prev_position(3)
        wrapped_pos_extraneous = walker_with_wrap.prev_position(30)

        # Then
        assert pos == 0
        assert wrapped_pos_left_edge == 2
        assert wrapped_pos_right_edge == 2
        assert wrapped_pos_extraneous == 29

    def test_prev_position_throws_for_invalid_position(self, walker_no_wrap):
        # Given
        walker_no_wrap.append("widget1")

        # When & Then
        with pytest.raises(IndexError):
            walker_no_wrap.prev_position(-40)
