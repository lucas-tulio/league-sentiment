league-sentiment
================

Sentiment Analysis on Reddit's League of Legends comments.

#### Requirements

* MySQL
* Php 5.4
* Python 2.7
* Python NLTK

#### Database Setup

1. Run `database/create-database.sql` in your MySQL instance

1. Run all the insert scripts inside the database dir.

The `results-queries.sql` file contains the queries used by the python scripts to organize and query the results. I made it just as an easier way to see what's going on. The same statements can be found in the `reader/results.py` script.

#### Sentiment Analysis Setup

1. Install Python pip: `apt-get install python-pip`

1. Install PyMySQL: `pip install PyMySQL`

1. Install Textblob: `pip install -U textblob`

1. Install python dev: `apt-get install build-essential python-dev`

1. Install Numpy: `pip install -U numpy`

1. Install PyYAML and NLTK: `pip install -U pyyaml nltk`

1. Install the necessary NLTK extension by running: `python` `import nltk` `nltk.download()`. Then, select option "d" and enter the package name: `maxent_ne_chunker`. The download may take a while. Don't give up.

1. Still in the nltk downloader, get the following packages: `maxent_treebank_pos_tagger`, `words` and `punkt`.

#### How to build/use the website

1. Check the README.md file inside /site.

#### How to use the Sentiment Analysis

**Collecting data**

1. Open the file `reader/reader.py`

1. Find "User Agent" and enter a user agent there. Reddit will block your requests if this field is empty or not descriptive enough.

1. Run `python reader/reader.py`. The script will automatically save threads and their comments until stopped.

**Analysis:**

Run `python reader/processor.py`. It works by looping through all the comments recorded by the reader script, figuring out which subjects are being talked about and scoring them on positive or negative. These results are saved in the `entities` table.

After the processor is done, run `reader/results.py` to aggregate the results into the `results` table. The website reads this table to show its results.

#### References

* Bird, Steven, Edward Loper and Ewan Klein (2009), Natural Language Processing with Python. O’Reilly Media Inc.
