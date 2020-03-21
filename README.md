# Software Engineering Project: Derivative Trades System

This application was built in a group of 5 students with the purpose of providing an application that takes user inputs on details of a derivative trades, and stores them in a system. 
The system will be able to query the data using a front-end webpage and returns the values in a table, or as a "daily report" format, which outlines all the trades that have been made in a single day - this format can be either a csv or pdf format.

### Technologies
* Front End: Bootstrap, JQuery
* Back-End: Python, Flask, SQL/SQLite

### Requirements
- Python 3.8 or later

### How to Run
```bash
cd back-end
pip install -r requirements.txt
python run.py
```
Then open the link printed by the program in Firefox. The link will look like:
```
> Address http://0.0.0.0:8002 <
```

###### Group Project Requirements
  1. Allow a user to enter the details of a derivative trade, edit a previous trade or delete a trade that should not have been entered.
  2. Generate a daily report of trades, for the regulatory body.
  3. Detect possible errors and alert the user that corrections may be needed.
  4. Learn from historical data, current market data and historical user interactions potential boundaries for values in the trades.
  5. Learn common mistakes and their corrections, and begin to automatically correct them for the user.
  6. Adjust learned behaviours based on user feedback, user input and new data.
