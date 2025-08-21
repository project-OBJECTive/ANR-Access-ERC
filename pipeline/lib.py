import datetime, json, time, os, pandas as pd, requests
from mistralai import Mistral
from openai import OpenAI
from typing import List


def mistralai_batch_execution(
        tasks: dict,
        client: Mistral, model: str, file_name: str, task_name: str
    ) -> list:

    # Local saving of batch files (for checking)
    if not os.path.exists('../batch_files'): os.mkdir('../batch_files')
    now_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    input_path = f"../batch_files/{task_name}_input_{now_str}.jsonl"
    output_path = f"../batch_files/{task_name}_output_{now_str}.jsonl"
    error_path = f"../batch_files/{task_name}_error_{now_str}.jsonl"

    print('Creating the batch file...')
    with open(input_path, "w") as f:
        for entry in tasks:
            f.write(json.dumps(entry) + "\n")

    print('Uploading the batch file...')
    file_infos = client.files.upload(file={"file_name": f"{file_name}.jsonl", "content": open(input_path, 'rb') }, purpose="batch")

    print('Creating the batch job...')
    batch_job = client.batch.jobs.create(
        input_files=[file_infos.id],
        model=model,
        endpoint="/v1/chat/completions",
        metadata={"task": task_name}
    )

    # Wait for the batch to proceed
    while batch_job.status in ["QUEUED", "RUNNING"]:
        batch_job = client.batch.jobs.get(job_id=batch_job.id)
        nb_fail = batch_job.failed_requests
        nb_succ = batch_job.succeeded_requests
        advan = round((nb_fail + nb_succ) / batch_job.total_requests, 4) * 100            
        infos = f'> Status: {batch_job.status} - Failed: {nb_fail} - Successful: {nb_succ} - Advancement: {round(advan)}%                  '
        print(infos, end="\r")
        time.sleep(2)
    print(f"Batch job {batch_job.id} completed with status: {batch_job.status}")

    # Error file
    print('Downloading result error file...')
    if batch_job.error_file is not None:
        error_file = client.files.download(file_id=batch_job.error_file)
        file = open(error_path, 'w')
        for chunk in error_file.stream:
            file.write(chunk.decode("utf-8", errors="replace"))
        file.close()
        raise Exception(f'There was an error in executing batch, see error file <{error_path}> for more information.')

    # Output
    print('Downloading result output file...')
    if batch_job.output_file is not None:
        output_file = client.files.download(file_id=batch_job.output_file)
        file = open(output_path, 'w')
        for chunk in output_file.stream:
            file.write(chunk.decode("utf-8", errors="replace"))
        file.close()

    # Read the output file 
    results = []
    file = open(output_path, 'r')
    for line in file.readlines():
        results.append(json.loads(line.strip()))
    file.close()

    # Sort results by given ids
    results = sorted(results, key=lambda x: x['custom_id'])

    # Get answers out of object
    answers = []
    for result in results:
        answers.append(result['response']['body']['choices'][0]['message']['content'])
        
    return answers


def openai_batch_execution(
        tasks: dict,
        client: OpenAI, endpoint: str, task_name: str,
    ) -> list:

    # Local saving of batch files (for checking)
    if not os.path.exists('../batch_files'): os.mkdir('../batch_files')
    now_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    input_path = f"../batch_files/{task_name}_input_{now_str}.jsonl"
    output_path = f"../batch_files/{task_name}_output_{now_str}.jsonl"
    error_path = f"../batch_files/{task_name}_error_{now_str}.jsonl"
    
    print('Creating the batch file...')
    with open(input_path, "w") as f:
        for entry in tasks:
            f.write(json.dumps(entry) + "\n")

    print('Uploading the batch file...')
    file_infos = client.files.create(file=open(input_path, 'rb'), purpose='batch')

    print('Creating the batch job...')
    batch_job = client.batches.create(
        input_file_id=file_infos.id,
        completion_window="24h",
        endpoint=endpoint,
        metadata={"job_type": task_name}
    )

    while batch_job.status in ["validating", "in_progress", "finalizing", "cancelling"]:
        batch_job = client.batches.retrieve(job_id=batch_job.id)
        nb_fail = batch_job.request_counts.failed
        nb_succ = batch_job.request_counts.completed
        advan = round((nb_fail + nb_succ) / batch_job.request_counts.total, 4) * 100   
        infos = f'> Status: {batch_job.status} - Failed: {nb_fail} - Successful: {nb_succ} - Advancement: {advan}%                  '
        print(infos, end="\r")
        time.sleep(2)

    if batch_job.error_file_id:
        print('Downloading error file...')
        output = client.files.content(batch_job.error_file_id)
        file = open(error_path, 'w')
        file.write(output.text)
        file.close()

    if batch_job.output_file_id:
        print('Downloading output file...')
        output = client.files.content(batch_job.output_file_id)
        file = open(output_path, 'w')
        file.write(output.text)
        file.close()

    # Build objects
    lines = output.text.split('\n')
    results = []
    for line in lines:
        results.append(json.loads(line))

    # Sort results by given ids
    results = sorted(results, key=lambda x: x['custom_id'])

    # Get answers out of object
    answers = []
    for result in results:
        answers.append(result['response']['body']['choices'][0]['message']['content'])
        
    return answers


def percent(nb: float) -> str:
    """Format the number sent into a % number, eg 0.012 into "01.2%" """
    the_number = round(100 * nb, 2)
    the_string = "{: >6.2f}%".format(the_number)
    return the_string


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


def clean_elements(existing_arr: List[str]) -> List[str]:
    # Remove empty
    existing_arr = list(filter(lambda s: s != '', existing_arr))
    # Deduplicate
    existing_arr = list(set(existing_arr))
    # Sort correctly
    existing_arr.sort()
    # Return
    return existing_arr


def clean_elements_str(existing_str: str) -> str:
    if existing_str.endswith('.'): 
        existing_str = existing_str[:-1]
    existing_arr = existing_str.split(', ')
    existing_arr = clean_elements(existing_arr)
    return ', '.join(existing_arr)


def add_element(existing_str: str, new_element: str) -> str:
    # Initiate the array
    existing_arr = existing_str.split(', ') if existing_str and existing_str != "" else []
    # Add the new one
    existing_arr.append(new_element.lower().strip())
    # Clean 
    existing_arr = clean_elements(existing_arr)
    # Build & return
    return ', '.join(existing_arr)


def remove_element(existing_str: str, to_remove: str) -> str:
    # Initiate the array
    existing_arr = existing_str.split(', ') if existing_str and existing_str != "" else []
    # Look for the element
    new_arr = []
    for elt in existing_arr:
        if to_remove not in elt: 
            new_arr.append(elt)
    # Clean 
    new_arr = clean_elements(new_arr)
    # Build & return
    return ', '.join(new_arr)


def has_element(existing_str: str, element: str) -> bool:
    existing_arr = existing_str.split(', ') if pd.notna(existing_str) and existing_str != "" else []
    return element in existing_arr



def try_parse_int(value: float | str | int):
    """Parse as int if possible, otherwise returns the given value, untouched."""
    try: return int(float(value))
    except (ValueError, TypeError): return value


def query_sparql(endpoint_url: str, sparql_query: str) -> pd.DataFrame:

    # Prepare request
    headers = { "Accept": "application/sparql-results+json" }
    params = { "query": sparql_query }

    # Execute request
    response = requests.get(endpoint_url, headers=headers, params=params)
    response.raise_for_status()  # Raise error if request failed
    
    # Parse response
    data = response.json()
    vars = data["head"]["vars"]
    results = data["results"]["bindings"]

    # Create a DataFrame
    rows = []
    for result in results:
        row = {var: result.get(var, {}).get("value") for var in vars}
        rows.append(row)

    return pd.DataFrame(rows)