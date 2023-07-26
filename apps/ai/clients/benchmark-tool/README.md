# Text-2-SQL Benchmark Tool

The benchmark engine is a tool that helps measure the performance (accuracy, speed and cost) of the core Dataherald engine. The tool comes pre-loaded with test-sets and users can start the engine, load examples and run benchmark tests by running a single script


## How to run the tool

### Installation and execution
Users simply have to install the dependencies listed in requirements.txt and then run the script location in run-tests.sh

The script will start the Dataherald engine located in apps/server/dataherald in a docker instance, load context into the store and then run the benchmark tests.

All test sets and output results are stored are jsonlines format files.

### Configuration Options
Users can see the list of configuration options by running the following command:

python3 apps/ai/clients/benchmark-tool/main.py --help

However the main configuration elements are 
-f FILE, --file   The file containing the benchmark tests. (default: v2_real_estate.jsonl)
-u UPLOAD, --upload Upload the results to the S3 bucket. (default: False)
-o OUTPUT, --output The directory to save the benchmark results file (default: apps/ai/clients/benchmark-tool/test_results/)
-p PERCENT, --percent The percentage of the test set to use as context. (default: 0.1)
-s SIZE, --size What percent of the test suite to use in the test (default: 1)

### Result output
By default the results are stored as jsonlines files in the apps/ai/clients/benchmark-tool/test_results/ folder. A copy is also saved to the S3 bucket at https://s3.console.aws.amazon.com/s3/buckets/k2-benchmark-results?region=us-east-1&tab=objects