# Solutions

> [!WARNING]
> **Try each task on your own first.** You learn operations by instrumenting the code yourself, watching a pipeline fail and working out why, and reading a Terraform plan before you apply it. Copying these files makes the checks green, but you will miss what the lab is for, and you will need these ideas for the quiz and the project.
>
> Before you open a solution:
> 1. Read the task's **Stuck?** tips in the main [README](../README.md).
> 2. Run the failing test on its own (for example `python3 -m pytest tests/test_metrics.py -x`) and read the error message.
> 3. Ask a classmate or the TA.

If you are still stuck, open **only the task you are stuck on**, read it until you understand each line, then close it and write your own version.

| Task | Solution |
|---|---|
| 1. Instrument the service | [`app/metrics.py`](app/metrics.py) and the `check()` function in [`app/main.py`](app/main.py) |
| 2. Complete the pipeline | the `deploy` job at the end of [`ci-cd.yml`](ci-cd.yml) |
| 3. Create the infrastructure | [`infra/scrape.tf`](infra/scrape.tf) |
| 4. Analyze | `histogram_quantile(0.99, sum by (le) (rate(spam_inference_seconds_bucket[5m])))` |

The stretch goals have no solutions here.
