import time
import datetime

def generate_id() -> str:
    "Generate a uuid base on the current time"

    # The seed (now's timestamp in ms)
    timestamp_ms = int(time.time() * 1000)

    # The used alphabet
    BASE64_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"

    # Generate the id
    result = ""
    while timestamp_ms:
        timestamp_ms, remainder = divmod(timestamp_ms, 62)
        result = BASE64_ALPHABET[remainder] + result

    # Make sure that the id generation took at least 1 ms, 
    # Doing so, we ensure that each generated ids are different
    time.sleep(0.001)

    return 'i' + result[::-1]


log_file_path = "./eta.log"
class Eta:
    """Object to follow execution advancement."""

    def __init__(self, silent_mode=False, short_mode=True) -> None:
        self.begin_time: float = 0
        self.length = 0
        self.current_count = 0
        self.last_display_time: float = 0
        self.text = ""
        self.str_len = 0
        self.last_printed = ""
        self.silent_mode = silent_mode
        self.short_mode = short_mode

    def begin(self, length: int, text: str) -> None:
        """Start a counter."""

        if self.silent_mode:
            open(log_file_path, "a").close()

        self.length = length
        self.current_count = 0
        self.text = text

        now = datetime.datetime.now().timestamp()
        self.begin_time = now

        to_print = (
            # self.text + " - Elapsed: [00h00m00s] - ETA: [??h??m??s] - " + percent(0) + " - Total planned: [??h??m??s] - Index: 0 of " + str(length)
            self.text
            + f" - 00h00m00s [--------------------] ??h??m??s of ??h??m??s (0 of {str(length)})"
        )
        end = " " * max(0, self.str_len - len(to_print)) + "\r"
        if not self.silent_mode:
            print('[ETA] ' + to_print, end=end)
        else:
            with open(log_file_path, "a") as file:
                file.write(to_print + "\n")

        self.last_printed = to_print
        self.str_len = len(to_print) if len(to_print) > self.str_len else self.str_len

        self.last_display_time = now

    def iter(self, count: int = 0) -> None:
        """On an iteration."""

        if count != 0:
            self.current_count = count
        else:
            self.current_count += 1
        now = datetime.datetime.now().timestamp()

        timeSinceLastDisplay = now - self.last_display_time

        if timeSinceLastDisplay < 1:
            return

        time_spent = now - self.begin_time
        percent_spent = self.current_count / self.length

        if percent_spent != 0:
            time_left = (time_spent / percent_spent) - time_spent
        else:
            time_left = 0

        # Calculations
        hours_elapsed = int(time_spent / 3600)
        minutes_elapsed = int((time_spent - (3600 * hours_elapsed)) / 60)
        seconds_elapsed = int(round(time_spent - (60 * minutes_elapsed + 3600 * hours_elapsed)))
        hours_left = int(time_left / 3600)
        minutes_left = int((time_left - (3600 * hours_left)) / 60)
        seconds_left = int(round(time_left - (60 * minutes_left + 3600 * hours_left)))
        hours_total = int((time_left + time_spent) / 3600)
        minutes_total = int(((time_left + time_spent) - (3600 * hours_total)) / 60)
        seconds_total = int(round((time_left + time_spent) - (60 * minutes_total + 3600 * hours_total)))

        # Stringify to right format
        hours_elapsed_str = "{:0>2.0f}".format(hours_elapsed)
        minutes_elapsed_str = "{:0>2.0f}".format(minutes_elapsed)
        seconds_elapsed_str = "{:0>2.0f}".format(seconds_elapsed)
        hours_left_str = "{:0>2.0f}".format(hours_left)
        minutes_left_str = "{:0>2.0f}".format(minutes_left)
        seconds_left_str = "{:0>2.0f}".format(seconds_left)
        hours_total_str = "{:0>2.0f}".format(hours_total)
        minutes_total_str = "{:0>2.0f}".format(minutes_total)
        seconds_total_str = "{:0>2.0f}".format(seconds_total)

        percent_passed = int((percent_spent * 100) / 5) * "#"
        percent_coming = (20 - len(percent_passed)) * "-"

        # to_print = (
        # self.text
        # + f" - Elapsed: [{hours_elapsed_str}h{minutes_elapsed_str}m{seconds_elapsed_str}s] - ETA [{hours_left_str}h{minutes_left_str}m{seconds_left_str}s] - "
        # + percent(percent_spent)
        # + f" - Total planned: [{hours_total_str}h{minutes_total_str}m{seconds_total_str}s] - Index: {self.current_count} of {self.length}"
        #     self.text + f" - {hours_elapsed_str}h{minutes_elapsed_str}m{seconds_elapsed_str}s [{percent_passed}{percent_coming}] {hours_left_str}h{minutes_left_str}m{seconds_left_str}s of {hours_total_str}h{minutes_total_str}m{seconds_total_str}s ({self.current_count} of {str(self.length)})"
        # )

        to_print = self.text
        if not self.short_mode:
            to_print += f"- {hours_elapsed_str}h{minutes_elapsed_str}m{seconds_elapsed_str}s"
        to_print += f" [{percent_passed}{percent_coming}] {hours_left_str}h{minutes_left_str}m{seconds_left_str}s"
        if not self.short_mode:
            to_print += f" of {hours_total_str}h{minutes_total_str}m{seconds_total_str}s"
        to_print += f" ({self.current_count} of {str(self.length)})"

        end = " " * max(0, self.str_len - len(to_print)) + "\r"

        if not self.silent_mode:
            print('[ETA] ' + to_print, end=end)
        else:
            file = open(log_file_path, "r")
            content = file.read()
            file.close()
            content = content.replace(self.last_printed, to_print)
            file = open(log_file_path, "w")
            file.write(content)
            file.close()

        self.last_printed = to_print
        self.str_len = len(to_print) if len(to_print) > self.str_len else self.str_len

        self.last_display_time = now

    def end(self, hide=False) -> None:
        """Finalize an ETA counting."""

        if hide:
            print(" " * self.str_len, end="\r")
            return

        now = datetime.datetime.now().timestamp()

        # Calculations
        total_time = now - self.begin_time
        avg_iter_by_sec = self.length / total_time
        total_hours = int(total_time / 3600)
        total_minutes = int((total_time - (3600 * total_hours)) / 60)
        total_sec = int(total_time - (60 * total_minutes + 3600 * total_hours))

        # Stringify to right format
        total_hours_str = "{:0>2.0f}".format(total_hours)
        total_minutes_str = "{:0>2.0f}".format(total_minutes)
        total_sec_str = "{:0>2.0f}".format(total_sec)

        to_print = (
            self.text
            + f" - {self.length} iterations in {total_hours_str}h{total_minutes_str}m{total_sec_str}s ({round(avg_iter_by_sec, 1)} iter/sec)"
        )
        end = " " * max(0, self.str_len - len(to_print)) + "\n"

        if not self.silent_mode:
            print('[ETA] ' + to_print, end=end)
        else:
            file = open(log_file_path, "r")
            content = file.read()
            file.close()
            content = content.replace(self.last_printed, to_print)
            file = open(log_file_path, "w")
            file.write(content)
            file.close()

        self.last_printed = to_print
        self.str_len = len(to_print) if len(to_print) > self.str_len else self.str_len

    def print(self, string: str) -> None:
        """Print out a log, without messing with the ETA display."""

        end = " " * max(0, self.str_len - len(string)) + "\n"
        to_print = self.last_printed

        if not self.silent_mode:
            print(string, end=end)
            end = " " * max(0, self.str_len - len(to_print)) + "\r"
            print(to_print, end=end)
        else:
            with open(log_file_path, "a") as file:
                file.write(to_print)
        self.str_len = len(self.last_printed) if len(self.last_printed) > self.str_len else self.str_len


def to_literal(string: str, language: str = None) -> None:
    text = ("'" + string.replace("\\", "\\\\").replace("'", "\\'").strip() + "'")
    if language: 
        text += "@" + language
    return text