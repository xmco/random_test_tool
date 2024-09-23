# Usage Examples

### Recommended usage

In order to get a comprehensive  summary of a run, the `html` output option can be used.

```Shell
random-test-tool -d random_generator_samples/python_random_bytes -o html
```

The report will display 
- A summary table for each processed file or chunk of data
- A summary table for the whole run
- A graphical representation of the resulting distribution of the tests

To get a full picture of a random number generator, you should use at least 500 chunks of data, in order
to get confidence interval estimation. 
Each chunk should be around 1M numbers so every test works properly.

![Usage](img/test_report.gif)

For individual chunks of data, it is expected that some tests will fail from time to time. However, if a 
test is displayed red on the summary table, it is an argument for the data to be not-random.
If a test is "SUSPECT" (yellow on the result table), it does not necessarily indicate that the data is not random.
In fact, only a "KO" should decide the user on the non-randomness of the data. Many "SUSPECT" tests should act
as an indication to run the suite on another sample in order to confirm or infirm the non randomness.


### Examples

A report from a run on 600M bytes generated from python `os.urandom` split in 600 chunks:
[python_os_random](examples/python_crypto_example.html)

A report from a run on 10M integers generated from bash `$RANDOM` split in 10 chunks:
[bash_random](examples/bash_random_example.html)