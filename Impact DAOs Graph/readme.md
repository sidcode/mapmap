# V1 Impact DAOs Social Graph

<img width="697" alt="image" src="https://user-images.githubusercontent.com/42869436/157341516-c30094ac-63a3-444c-9e70-e88ad2a436ae.png">

### Getting started
- Add your Twitter API credientials to `credentials.py`
- Get a list of Project Names and Twitter Handles (see example of `data/twitter_list.csv`)

### Getting data from Twitter
- Execute the script `build_database.py` passing the pathname of the csv file above as an argument
- New projects will be added to `data/impact_dao_data.json` 
- This may take a while because of Twitter API's rate limits

### Building the social graph 
- Open up the Jupyter notebook `Impact DAOs Network Analysis.ipynb`
- It does some quick brute-force social network analysis -- you can tweek the algorithm
- Exports the data in a variety of formats, including a json social graph and csv files that can be loaded in Notion or Flourish

## Requirements

- tweepy 4.6.0 (and Twitter API access -- free)
- python-louvain 0.16 (https://python-louvain.readthedocs.io/en/latest/)
