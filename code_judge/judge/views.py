from django.shortcuts import render
import tempfile
import subprocess
import time
import os

def custom_test(request):
    context = {"code": "", "input_data": "", "output": "", "error": "", "time": "", "language": "cpp"}

    if request.method == "POST":
        code = request.POST['code']
        language = request.POST['language']
        input_data = request.POST['input']
        time_limit = float(request.POST.get('time_limit', 2.0))  # default = 2.0 sec

        context.update({"code": code, "input_data": input_data, "language": language})

        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                if language == 'cpp':
                    code_file = f"{temp_dir}/main.cpp"
                    with open(code_file, 'w') as f:
                        f.write(code)
                    binary_file = f"{temp_dir}/main.out"
                    compile_cmd = ["g++", code_file, "-o", binary_file]
                    subprocess.run(compile_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                    start = time.time()
                    run = subprocess.run(
                        [binary_file],
                        input=input_data.encode(),
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        timeout=time_limit
                    )
                    end = time.time()

                elif language == 'py':
                    code_file = f"{temp_dir}/main.py"
                    with open(code_file, 'w') as f:
                        f.write(code)

                    start = time.time()
                    run = subprocess.run(
                        ["python3", code_file],
                        input=input_data.encode(),
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        timeout=time_limit
                    )
                    end = time.time()

                context["output"] = run.stdout.decode()[:255]
                context["error"] = run.stderr.decode()
                context["time"] = f"{end - start:.3f}"

            except subprocess.TimeoutExpired:
                context["output"] = ""
                context["error"] = "Time Limit Exceeded"
                context["time"] = f">{time_limit:.1f}"

            except subprocess.CalledProcessError as e:
                context["output"] = ""
                context["error"] = f"Compilation Error:\n{e.stderr.decode()}"

    return render(request, "judge/index.html", context)
